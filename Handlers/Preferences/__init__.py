"""
Preferences handlers package - Contains all preference-related specialized handlers.

Handlers:
- ShiftTimesHandler: Manages shift time configurations
- RemindersHandler: Manages reminder settings
- TimezoneHandler: Manages timezone preferences
- TemplatesHandler: Manages shift templates

Usage:
    from Handlers.Preferences import ShiftTimesHandler
    from Handlers.Preferences import RemindersHandler
"""

from .ShiftTimesHandler import ShiftTimesHandler
from .RemindersHandler import RemindersHandler
from .TimezoneHandler import TimezoneHandler
from .TemplatesHandler import TemplatesHandler

__all__ = [
    'ShiftTimesHandler',
    'RemindersHandler',
    'TimezoneHandler',
    'TemplatesHandler',
]
