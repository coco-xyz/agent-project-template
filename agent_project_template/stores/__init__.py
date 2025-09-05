"""
Stores Package

Supporting Components - Data persistence and state management.
"""

# Main store interface (backward compatibility)
from .resume_store import ResumeStore

# Models
from .models.resume_dialogue import ResumeDialogues
from .models.resume import Resume

# CRUD operations
from .crud.resume_dialogue_crud import ResumeDialogueCrud
from .crud.resume_crud import ResumeCrud

__all__ = [
    # Main store interface
    "ResumeStore",
    # Models
    "ResumeDialogues",
    "Resume", 
    # CRUD operations
    "ResumeDialogueCrud",
    "ResumeCrud"
]
