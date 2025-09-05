"""
Configuration

Application settings and environment configuration with NACOS integration.
"""

import os
import base64
from typing import Optional, List, Literal
from pydantic_settings import BaseSettings
from pydantic import Field

# AWS SDK for KMS decryption
try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError
except ImportError:
    boto3 = None
    BotoCoreError = ClientError = Exception

# NACOS SDK for configuration management
try:
    import nacos
except ImportError:
    nacos = None


def decrypt_password(enc_password: str) -> str:
    """
    Use AWS KMS to decrypt encrypted password
    Expected format: ENC(encrypted base64 string)
    
    Args:
        enc_password: encrypted password string
        
    Returns:
        str: decrypted password
        
    Raises:
        RuntimeError: raised when decryption fails
    """
    if not enc_password.startswith("ENC(") or not enc_password.endswith(")"):
        return enc_password  # non-encrypted format, return directly
    
    trimmed = enc_password[4:-1]
    try:
        decoded = base64.b64decode(trimmed)
    except Exception as e:
        raise RuntimeError("Base64 decode failed") from e
    
    # 使用完整的 ARN 格式，与正确运行的代码保持一致
    kms_key_id = os.environ.get("KMS_KEY_ID", "a")
    if not kms_key_id:
        raise RuntimeError("Missing required environment variable: KMS_KEY_ID")
    
    if not boto3:
        raise RuntimeError("boto3 is required for KMS decryption but not installed")
    
    try:
        kms_client = boto3.client("kms")
        # 不传递 KeyId 参数，让 KMS 自动识别密钥
        response = kms_client.decrypt(KeyId=kms_key_id, CiphertextBlob=decoded)
        plaintext = response["Plaintext"]
        return plaintext.decode("utf-8")
    except base64.binascii.Error as e:
        raise RuntimeError("Base64 decode failed: please check if input is valid base64 string") from e
    except ClientError as e:
        error_msg = e.response.get('Error', {}).get('Message', str(e))
        if 'incorrect key' in error_msg.lower():
            raise RuntimeError("Key mismatch: please confirm KeyID matches the one used for encryption") from e
        else:
            raise RuntimeError(f"AWS API error: {error_msg}") from e
    except (BotoCoreError, Exception) as e:
        raise RuntimeError(f"KMS decryption failed: {str(e)}") from e


def load_nacos_config() -> bool:
    """
    Pull configuration from NACOS and inject into os.environ
    
    Returns:
        bool: whether the configuration is successfully loaded from NACOS
    """
    nacos_addr = os.environ.get("NACOS_ADDR")
    nacos_data_id = os.environ.get("NACOS_DATA_ID")
    use_nacos = nacos and nacos_addr and nacos_data_id
    
    if not use_nacos:
        return False
    
    nacos_username = os.environ.get("NACOS_USERNAME")
    nacos_password = os.environ.get("NACOS_PASSWORD")
    nacos_group = os.environ.get("NACOS_GROUP", "DEFAULT_GROUP")
    nacos_namespace = os.environ.get("NACOS_NAMESPACE", "COCO")
    
    try:
        client = nacos.NacosClient(
            nacos_addr,
            namespace=nacos_namespace,
            username=nacos_username,
            password=nacos_password
        )
        
        config_str = client.get_config(nacos_data_id, nacos_group)
        if config_str:
            config_count = 0
            for line in config_str.splitlines():
                if line.strip() and not line.strip().startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # check if it is an encrypted password field
                    if key.lower().endswith("password") and value.startswith("ENC("):
                        try:
                            value = decrypt_password(value)
                        except Exception as e:
                            print(f"[NACOS] 密码解密失败 {key}: {e}")
                            continue
                    
                    os.environ[key] = value
                    config_count += 1
            
            print(f"[CONFIG] 已从 NACOS 拉取 {config_count} 项配置")
            return True
        else:
            print("[NACOS] 未获取到配置内容")
            return False
            
    except Exception as e:
        print(f"[NACOS] 拉取配置失败: {e}")
        return False


class SettingsLocal(BaseSettings):
    """
    Local .env configuration: only used for local development debugging
    Use traditional <.env> file loading method
    """
    # Server settings
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: str = Field(default="info", description="Log level")
    environment: str = Field(default="development", description="Application environment")

    # Database settings
    database__url: str = Field(default="postgresql://ai_agents_user:ai_agents_password@localhost:5432/ai_agents", description="Database connection URL")
    database__echo: bool = Field(default=False, description="Enable SQL query logging")
    
    # Connection Pool Configuration
    database__pool_size: int = Field(default=15, description="Connection pool size")
    database__max_overflow: int = Field(default=25, description="Maximum overflow connections")
    database__pool_timeout: int = Field(default=60, description="Pool timeout in seconds")
    database__pool_recycle: int = Field(default=3600, description="Pool recycle time in seconds")
    database__pool_pre_ping: bool = Field(default=True, description="Enable pool pre-ping")
    database__pool_reset_on_return: str = Field(default="commit", description="Pool reset on return strategy")
    
    # Connection Timeout Configuration (basic)
    database__connect_timeout: int = Field(default=10, description="Connection timeout in seconds")

    # Redis settings
    redis__url: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    redis__host: str = Field(default="localhost", description="Redis host")
    redis__port: int = Field(default=6379, description="Redis port")
    redis__db: int = Field(default=0, description="Redis database number")
    redis__password: Optional[str] = Field(default=None, description="Redis password")
    
    # Redis SSL and timeout settings
    redis__ssl: bool = Field(default=False, description="Enable SSL/TLS for Redis connection")
    redis__connect_timeout: int = Field(default=3000, description="Redis connection timeout in milliseconds")
    redis__socket_timeout: int = Field(default=3000, description="Redis socket timeout in milliseconds")
    
    # Redis connection pool settings
    redis__pool_max_connections: int = Field(default=8, description="Maximum number of connections in pool")
    redis__pool_max_idle: int = Field(default=8, description="Maximum number of idle connections in pool")
    redis__pool_min_idle: int = Field(default=0, description="Minimum number of idle connections in pool")
    redis__pool_max_wait: int = Field(default=-1, description="Maximum wait time for connection (-1 for infinite)")

    # API settings
    api__title: str = Field(default="AI Agents", description="API title")
    api__description: str = Field(default="Intelligent agent system", description="API description")
    api__version: str = Field(default="0.1.0", description="API version")
    api__docs_url: str = Field(default="/docs", description="API documentation URL")
    api__redoc_url: str = Field(default="/redoc", description="ReDoc documentation URL")

    # CORS settings - stored as strings, converted to lists via properties
    cors__allow_origins: str = Field(default="*", description="Allowed origins for CORS (comma-separated)")
    cors__allow_credentials: bool = Field(default=False, description="Allow credentials in CORS")
    cors__allow_methods: str = Field(default="GET,POST,PUT", description="Allowed HTTP methods (comma-separated)")
    cors__allow_headers: str = Field(default="*", description="Allowed headers (comma-separated)")

    # AI API Keys
    ai__openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    ai__anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")
    ai__google_api_key: Optional[str] = Field(default=None, description="Google API key (for GoogleModel)")
    ai__openrouter_api_key: Optional[str] = Field(default=None, description="OpenRouter API key")
    
    # Specific Model Configurations (only provider and model name)
    # GPT-4.1 Mini
    ai__gpt41_mini__provider: str = Field(default="openai", description="Provider for GPT-4.1 Mini")
    ai__gpt41_mini__model_name: str = Field(default="gpt-4.1-mini", description="Model name for GPT-4.1 Mini")
    
    # GPT-4.1
    ai__gpt41__provider: str = Field(default="openai", description="Provider for GPT-4.1")
    ai__gpt41__model_name: str = Field(default="gpt-4.1", description="Model name for GPT-4.1")

    # GPT-5
    ai__gpt5__provider: str = Field(default="openai", description="Provider for GPT-5")
    ai__gpt5__model_name: str = Field(default="gpt-5", description="Model name for GPT-5")

    # GPT-5 Mini
    ai__gpt5_mini__provider: str = Field(default="openai", description="Provider for GPT-5 Mini")
    ai__gpt5_mini__model_name: str = Field(default="gpt-5-mini", description="Model name for GPT-5 Mini")

    # GPT-5 Chat
    ai__gpt5_chat__provider: str = Field(default="openai", description="Provider for GPT-5 Chat")
    ai__gpt5_chat__model_name: str = Field(default="gpt-5-chat", description="Model name for GPT-5 Chat")
    
    # Gemini 2.5 Pro
    ai__gemini25_pro__provider: str = Field(default="google", description="Provider for Gemini 2.5 Pro")
    ai__gemini25_pro__model_name: str = Field(default="gemini-2.5-pro", description="Model name for Gemini 2.5 Pro")
    
    # Claude-4 Sonnet
    ai__claude4_sonnet__provider: str = Field(default="anthropic", description="Provider for Claude-4 Sonnet")
    ai__claude4_sonnet__model_name: str = Field(default="claude-4-sonnet", description="Model name for Claude-4 Sonnet")
    
    # Gemini 2.5 Flash Lite
    ai__gemini25_flash_lite__provider: str = Field(default="openrouter", description="Provider for Gemini 2.5 Flash Lite")
    ai__gemini25_flash_lite__model_name: str = Field(default="google/gemini-2.5-flash-lite", description="Model name for Gemini 2.5 Flash Lite")
    
    # Gemini 2.5 Flash
    ai__gemini25_flash__provider: str = Field(default="openrouter", description="Provider for Gemini 2.5 Flash")
    ai__gemini25_flash__model_name: str = Field(default="google/gemini-2.5-flash", description="Model name for Gemini 2.5 Flash")

    # GPT OSS 20B
    ai__gpt_oss_20b__provider: str = Field(default="openrouter", description="Provider for GPT OSS 20B")
    ai__gpt_oss_20b__model_name: str = Field(default="openai/gpt-oss-20b", description="Model name for GPT OSS 20B")

    # GPT OSS 120B
    ai__gpt_oss_120b__provider: str = Field(default="openrouter", description="Provider for GPT OSS 120B")
    ai__gpt_oss_120b__model_name: str = Field(default="openai/gpt-oss-120b", description="Model name for GPT OSS 120B")

    # Grok 3 Mini
    ai__grok_3_mini__provider: str = Field(default="openrouter", description="Provider for Grok 3 Mini")
    ai__grok_3_mini__model_name: str = Field(default="x-ai/grok-3-mini", description="Model name for Grok 3 Mini")

    # Grok 2 1212
    ai__grok_2_1212__provider: str = Field(default="openrouter", description="Provider for Grok 2 1212")
    ai__grok_2_1212__model_name: str = Field(default="x-ai/grok-2-1212", description="Model name for Grok 2 1212")

    # Kimi K2
    ai__kimi_k2__provider: str = Field(default="openrouter", description="Provider for Kimi K2")
    ai__kimi_k2__model_name: str = Field(default="moonshotai/kimi-k2", description="Model name for Kimi K2")

    # DeepSeek Chat V3.1
    ai__deepseek_chat_v31__provider: str = Field(default="openrouter", description="Provider for DeepSeek Chat V3.1")
    ai__deepseek_chat_v31__model_name: str = Field(default="deepseek/deepseek-chat-v3.1", description="Model name for DeepSeek Chat V3.1")

    # GLM 4.5
    ai__glm_45__provider: str = Field(default="openrouter", description="Provider for GLM 4.5")
    ai__glm_45__model_name: str = Field(default="z-ai/glm-4.5", description="Model name for GLM 4.5")

    # File upload settings
    upload_max_size: int = Field(default=10 * 1024 * 1024, description="Maximum file upload size in bytes (10MB)")
    upload_allowed_extensions: str = Field(default=".pdf,.txt,.docx", description="Allowed file extensions (comma-separated)")

    # Lock configuration
    redis_lock__retry_sleep_interval: float = Field(default=0.1, description="Lock retry sleep interval in seconds")

    # Logfire settings
    logfire__enabled: bool = Field(default=False, description="Enable Logfire logging")
    logfire__service_name: str = Field(default="agent-project-template", description="Logfire service name")
    logfire__environment: str = Field(default="development", description="Logfire environment")
    logfire__token: Optional[str] = Field(default=None, description="Logfire token")
    logfire__disable_scrubbing: Optional[bool] = Field(default=False, description="Disable Logfire scrubbing")
    # logfire__sample_rate: Optional[float] = Field(default=None, description="Sampling rate for logfire (0.0 to 1.0)")  # 暂不支持

    # Helper properties to convert string fields to lists
    @property
    def cors_allow_origins_list(self) -> List[str]:
        """Convert CORS allow origins string to list."""
        if not self.cors__allow_origins.strip():
            return ["*"]
        if ',' in self.cors__allow_origins:
            return [origin.strip() for origin in self.cors__allow_origins.split(',') if origin.strip()]
        return [self.cors__allow_origins.strip()]

    @property
    def cors_allow_methods_list(self) -> List[str]:
        """Convert CORS allow methods string to list."""
        if not self.cors__allow_methods.strip():
            return ["GET", "POST", "PUT"]
        if ',' in self.cors__allow_methods:
            return [method.strip() for method in self.cors__allow_methods.split(',') if method.strip()]
        return [self.cors__allow_methods.strip()]

    @property
    def cors_allow_headers_list(self) -> List[str]:
        """Convert CORS allow headers string to list."""
        if not self.cors__allow_headers.strip():
            return ["*"]
        if ',' in self.cors__allow_headers:
            return [header.strip() for header in self.cors__allow_headers.split(',') if header.strip()]
        return [self.cors__allow_headers.strip()]

    @property
    def upload_allowed_extensions_list(self) -> List[str]:
        """Convert upload allowed extensions string to list."""
        if not self.upload_allowed_extensions.strip():
            return [".pdf", ".txt", ".docx"]
        if ',' in self.upload_allowed_extensions:
            return [ext.strip() for ext in self.upload_allowed_extensions.split(',') if ext.strip()]
        return [self.upload_allowed_extensions.strip()]

    def model_post_init(self, __context):
        self.log_level = self.log_level.lower()
        # Set logfire environment to match application environment if not explicitly set
        if self.logfire__environment is None:
            self.logfire__environment = self.environment

    model_config = {
        "env_prefix": "AI_AGENTS_",   # Prefix for environment variables
        "case_sensitive": False,
        "env_file": ".env",  # local development uses .env file
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }


class Settings(BaseSettings):
    """
    NACOS/environment variable configuration: production environment is used first
    Does not depend on the .env file, completely load configuration from environment variables
    """
    # Server settings
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: str = Field(default="info", description="Log level")
    environment: str = Field(default="production", description="Application environment")

    # Database settings
    database__url: str = Field(default="postgresql://ai_agents_user:ai_agents_password@localhost:5432/ai_agents", description="Database connection URL")
    database__echo: bool = Field(default=False, description="Enable SQL query logging")
    
    # Connection Pool Configuration
    database__pool_size: int = Field(default=15, description="Connection pool size")
    database__max_overflow: int = Field(default=25, description="Maximum overflow connections")
    database__pool_timeout: int = Field(default=60, description="Pool timeout in seconds")
    database__pool_recycle: int = Field(default=3600, description="Pool recycle time in seconds")
    database__pool_pre_ping: bool = Field(default=True, description="Enable pool pre-ping")
    database__pool_reset_on_return: str = Field(default="commit", description="Pool reset on return strategy")
    
    # Connection Timeout Configuration (basic)
    database__connect_timeout: int = Field(default=10, description="Connection timeout in seconds")

    # Redis settings
    redis__url: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    redis__host: str = Field(default="localhost", description="Redis host")
    redis__port: int = Field(default=6379, description="Redis port")
    redis__db: int = Field(default=0, description="Redis database number")
    redis__password: Optional[str] = Field(default=None, description="Redis password")
    
    # Redis SSL and timeout settings
    redis__ssl: bool = Field(default=False, description="Enable SSL/TLS for Redis connection")
    redis__connect_timeout: int = Field(default=3000, description="Redis connection timeout in milliseconds")
    redis__socket_timeout: int = Field(default=3000, description="Redis socket timeout in milliseconds")
    
    # Redis connection pool settings
    redis__pool_max_connections: int = Field(default=8, description="Maximum number of connections in pool")
    redis__pool_max_idle: int = Field(default=8, description="Maximum number of idle connections in pool")
    redis__pool_min_idle: int = Field(default=0, description="Minimum number of idle connections in pool")
    redis__pool_max_wait: int = Field(default=-1, description="Maximum wait time for connection (-1 for infinite)")

    # API settings
    api__title: str = Field(default="AI Agents", description="API title")
    api__description: str = Field(default="Intelligent agent system", description="API description")
    api__version: str = Field(default="0.1.0", description="API version")
    api__docs_url: str = Field(default="/docs", description="API documentation URL")
    api__redoc_url: str = Field(default="/redoc", description="ReDoc documentation URL")

    # CORS settings - stored as strings, converted to lists via properties
    cors__allow_origins: str = Field(default="*", description="Allowed origins for CORS (comma-separated)")
    cors__allow_credentials: bool = Field(default=False, description="Allow credentials in CORS")
    cors__allow_methods: str = Field(default="GET,POST,PUT", description="Allowed HTTP methods (comma-separated)")
    cors__allow_headers: str = Field(default="*", description="Allowed headers (comma-separated)")

    # AI API Keys
    ai__openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    ai__anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")
    ai__google_api_key: Optional[str] = Field(default=None, description="Google API key (for GoogleModel)")
    ai__openrouter_api_key: Optional[str] = Field(default=None, description="OpenRouter API key")
    
    # Specific Model Configurations (only provider and model name)
    # GPT-4.1 Mini
    ai__gpt41_mini__provider: str = Field(default="openrouter", description="Provider for GPT-4.1 Mini")
    ai__gpt41_mini__model_name: str = Field(default="openai/gpt-4.1-mini", description="Model name for GPT-4.1 Mini")
    
    # GPT-4.1
    ai__gpt41__provider: str = Field(default="openrouter", description="Provider for GPT-4.1")
    ai__gpt41__model_name: str = Field(default="openai/gpt-4.1", description="Model name for GPT-4.1")

    # GPT-5
    ai__gpt5__provider: str = Field(default="openrouter", description="Provider for GPT-5")
    ai__gpt5__model_name: str = Field(default="openai/gpt-5", description="Model name for GPT-5")

    # GPT-5 Mini
    ai__gpt5_mini__provider: str = Field(default="openrouter", description="Provider for GPT-5 Mini")
    ai__gpt5_mini__model_name: str = Field(default="openai/gpt-5-mini", description="Model name for GPT-5 Mini")

    # GPT-5 Chat
    ai__gpt5_chat__provider: str = Field(default="openrouter", description="Provider for GPT-5 Chat")
    ai__gpt5_chat__model_name: str = Field(default="openai/gpt-5-chat", description="Model name for GPT-5 Chat")
    
    # Gemini 2.5 Pro
    ai__gemini25_pro__provider: str = Field(default="openrouter", description="Provider for Gemini 2.5 Pro")
    ai__gemini25_pro__model_name: str = Field(default="google/gemini-2.5-pro", description="Model name for Gemini 2.5 Pro")
    
    # Claude-4 Sonnet
    ai__claude4_sonnet__provider: str = Field(default="openrouter", description="Provider for Claude-4 Sonnet")
    ai__claude4_sonnet__model_name: str = Field(default="anthropic/claude-sonnet-4", description="Model name for Claude-4 Sonnet")
    
    # Gemini 2.5 Flash Lite
    ai__gemini25_flash_lite__provider: str = Field(default="openrouter", description="Provider for Gemini 2.5 Flash Lite")
    ai__gemini25_flash_lite__model_name: str = Field(default="google/gemini-2.5-flash-lite", description="Model name for Gemini 2.5 Flash Lite")
    
    # Gemini 2.5 Flash
    ai__gemini25_flash__provider: str = Field(default="openrouter", description="Provider for Gemini 2.5 Flash")
    ai__gemini25_flash__model_name: str = Field(default="google/gemini-2.5-flash", description="Model name for Gemini 2.5 Flash")

    # GPT OSS 20B
    ai__gpt_oss_20b__provider: str = Field(default="openrouter", description="Provider for GPT OSS 20B")
    ai__gpt_oss_20b__model_name: str = Field(default="openai/gpt-oss-20b", description="Model name for GPT OSS 20B")

    # GPT OSS 120B
    ai__gpt_oss_120b__provider: str = Field(default="openrouter", description="Provider for GPT OSS 120B")
    ai__gpt_oss_120b__model_name: str = Field(default="openai/gpt-oss-120b", description="Model name for GPT OSS 120B")

    # Grok 3 Mini
    ai__grok_3_mini__provider: str = Field(default="openrouter", description="Provider for Grok 3 Mini")
    ai__grok_3_mini__model_name: str = Field(default="x-ai/grok-3-mini", description="Model name for Grok 3 Mini")

    # Grok 2 1212
    ai__grok_2_1212__provider: str = Field(default="openrouter", description="Provider for Grok 2 1212")
    ai__grok_2_1212__model_name: str = Field(default="x-ai/grok-2-1212", description="Model name for Grok 2 1212")

    # Kimi K2
    ai__kimi_k2__provider: str = Field(default="openrouter", description="Provider for Kimi K2")
    ai__kimi_k2__model_name: str = Field(default="moonshotai/kimi-k2", description="Model name for Kimi K2")

    # DeepSeek Chat V3.1
    ai__deepseek_chat_v31__provider: str = Field(default="openrouter", description="Provider for DeepSeek Chat V3.1")
    ai__deepseek_chat_v31__model_name: str = Field(default="deepseek/deepseek-chat-v3.1", description="Model name for DeepSeek Chat V3.1")

    # GLM 4.5
    ai__glm_45__provider: str = Field(default="openrouter", description="Provider for GLM 4.5")
    ai__glm_45__model_name: str = Field(default="z-ai/glm-4.5", description="Model name for GLM 4.5")

    # File upload settings
    upload_max_size: int = Field(default=10 * 1024 * 1024, description="Maximum file upload size in bytes (10MB)")
    upload_allowed_extensions: str = Field(default=".pdf,.txt,.docx", description="Allowed file extensions (comma-separated)")

    # Lock configuration
    redis_lock__retry_sleep_interval: float = Field(default=0.1, description="Lock retry sleep interval in seconds")

    # Logfire settings
    logfire__enabled: bool = Field(default=False, description="Enable Logfire logging")
    logfire__service_name: str = Field(default="agent-project-template", description="Logfire service name")
    logfire__environment: str = Field(default="production", description="Logfire environment")
    logfire__token: Optional[str] = Field(default=None, description="Logfire token")
    logfire__disable_scrubbing: Optional[bool] = Field(default=False, description="Disable Logfire scrubbing")

    # Helper properties to convert string fields to lists
    @property
    def cors_allow_origins_list(self) -> List[str]:
        """Convert CORS allow origins string to list."""
        if not self.cors__allow_origins.strip():
            return ["*"]
        if ',' in self.cors__allow_origins:
            return [origin.strip() for origin in self.cors__allow_origins.split(',') if origin.strip()]
        return [self.cors__allow_origins.strip()]

    @property
    def cors_allow_methods_list(self) -> List[str]:
        """Convert CORS allow methods string to list."""
        if not self.cors__allow_methods.strip():
            return ["GET", "POST", "PUT"]
        if ',' in self.cors__allow_methods:
            return [method.strip() for method in self.cors__allow_methods.split(',') if method.strip()]
        return [self.cors__allow_methods.strip()]

    @property
    def cors_allow_headers_list(self) -> List[str]:
        """Convert CORS allow headers string to list."""
        if not self.cors__allow_headers.strip():
            return ["*"]
        if ',' in self.cors__allow_headers:
            return [header.strip() for header in self.cors__allow_headers.split(',') if header.strip()]
        return [self.cors__allow_headers.strip()]

    @property
    def upload_allowed_extensions_list(self) -> List[str]:
        """Convert upload allowed extensions string to list."""
        if not self.upload_allowed_extensions.strip():
            return [".pdf", ".txt", ".docx"]
        if ',' in self.upload_allowed_extensions:
            return [ext.strip() for ext in self.upload_allowed_extensions.split(',') if ext.strip()]
        return [self.upload_allowed_extensions.strip()]

    def model_post_init(self, __context):
        self.log_level = self.log_level.lower()
        # Set logfire environment to match application environment if not explicitly set
        if self.logfire__environment is None:
            self.logfire__environment = self.environment

    model_config = {
        "env_prefix": "AI_AGENTS_",   # Prefix for environment variables
        "case_sensitive": False,
        # do not use .env file, completely rely on environment variables
        "extra": "ignore"
    }

def create_settings():
    """
    Create configuration instance, automatically select configuration source based on environment
    
    Returns:
        Settings | SettingsLocal: configuration instance
    """
    try:
        nacos_addr = os.environ.get("NACOS_ADDR")
        use_nacos = nacos_addr is not None
        
        if use_nacos:
            print("[CONFIG] 使用 NACOS 配置源")
            # 先尝试从NACOS加载配置
            load_nacos_config()
            settings_instance = Settings()
        else:
            print("[CONFIG] 使用本地 .env 配置源")
            settings_instance = SettingsLocal()
        
        print(f"[CONFIG] 配置加载成功")
        print(f"  环境: {settings_instance.environment}")
        print(f"  调试模式: {settings_instance.debug}")
        print(f"  日志级别: {settings_instance.log_level}")
        
        # check critical configurations
        api_keys_count = sum(1 for key in [
            settings_instance.ai__openai_api_key,
            settings_instance.ai__anthropic_api_key,
            settings_instance.ai__google_api_key,
            settings_instance.ai__openrouter_api_key
        ] if key)
        print(f"  已配置 AI API 密钥: {api_keys_count}/4")
        
        return settings_instance
        
    except Exception as e:
        print(f"[CONFIG] 配置加载失败: {e}")
        print("请确保所有必需的环境变量都已设置，使用 AI_AGENTS_ 前缀")
        raise RuntimeError(f"配置加载失败: {e}") from e


# Global configuration instance - keep compatibility with existing code
settings = create_settings() 