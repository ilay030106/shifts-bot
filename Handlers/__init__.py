"""
Handlers package - Contains specialized handlers for different bot functionalities.

Main Handlers:
- PreferencesHandler: Main orchestrator for all preference-related operations

Preferences Sub-handlers (in Handlers.Preferences):
- ShiftTimesHandler: Specialized handler for shift time management
- RemindersHandler: Specialized handler for reminder settings
- TimezoneHandler: Specialized handler for timezone preferences
- TemplatesHandler: Specialized handler for shift templates

Usage:
    from Handlers import PreferencesHandler
    
    preferences = PreferencesHandler(telegram_client)
    
    # Or access sub-handlers directly:
    from Handlers.Preferences import ShiftTimesHandler
"""

from .PreferencesHandler import PreferencesHandler

# Re-export preferences sub-handlers for convenience
from .Preferences import (
    ShiftTimesHandler,
    RemindersHandler, 
    TimezoneHandler,
    TemplatesHandler
)

__all__ = [
    'PreferencesHandler',
    'ShiftTimesHandler',
    'RemindersHandler',
    'TimezoneHandler', 
    'TemplatesHandler',
]
