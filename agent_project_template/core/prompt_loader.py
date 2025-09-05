"""
Prompt Loader Utility

This module provides a utility for loading prompt text from files
in the `prompts` directory.
"""
import os
from functools import lru_cache
from ai_agents.core.exceptions import InternalServiceException
from ai_agents.core.error_codes import InternalServiceErrorCode

# Get the absolute path to the 'prompts' directory
# This makes the loader independent of where the script is run
PROMPT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'prompts')

@lru_cache(maxsize=128)
def load_prompt(prompt_name: str) -> str:
    """
    Load a prompt from the 'prompts' directory.

    Args:
        prompt_name (str): The filename of the prompt (e.g., 'resume_parser.txt')

    Returns:
        str: The content of the prompt file.

    Raises:
        InternalServiceException: If the prompt file is not found.
    """
    file_path = os.path.join(PROMPT_DIR, prompt_name)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise InternalServiceException(
            InternalServiceErrorCode.SERVICE_INIT_FAILED,
            detail=f"Prompt file not found at: {file_path}"
        )
    except Exception as e:
        raise InternalServiceException(
            InternalServiceErrorCode.SERVICE_INIT_FAILED,
            detail=f"Failed to load prompt file {prompt_name}: {str(e)}"
        ) 