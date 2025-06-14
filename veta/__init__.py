"""
Veta - A Python package for LEAS (Levels of Emotional Awareness Scale) analysis.
"""

from .logger import get_logger, setup_logging
from .survey import Survey
from .respondent import Respondent
from .item import Item
from .wordlist import Wordlist
from .auto_self_other_item import attempt_auto_self_other

__version__ = "1.0.0"
__all__ = [
    "Survey",
    "Respondent", 
    "Item",
    "Wordlist",
    "attempt_auto_self_other",
    "get_logger",
    "setup_logging"
]
