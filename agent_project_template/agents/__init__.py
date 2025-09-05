"""
Agents Package

This package contains the reusable, pre-configured AI agent instances.
Each agent is defined in its own file using pydantic-ai's native Agent syntax.
"""

from .resume_parser import (
    resume_parser_agent,
    professional_parser_agent,
    project_parser_agent,
    basic_parser_agent,
    handle_resume_parser,
    handle_professional_parser,
    handle_project_parser,
    handle_basic_parser
)
from .jd_parser import jd_parser_agent
from .resume_chat import resume_chat_agent, handle_resume_chat, ChatChunk

__all__ = [
    "resume_parser_agent",
    "professional_parser_agent",
    "project_parser_agent",
    "basic_parser_agent",
    "handle_resume_parser",
    "handle_professional_parser",
    "handle_project_parser",
    "handle_basic_parser",
    "jd_parser_agent",
    "resume_chat_agent",
    "handle_resume_chat",
    "ChatChunk"
]
