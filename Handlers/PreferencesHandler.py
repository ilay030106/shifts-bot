"""
Preferences Handler - Main orchestrator for all preference-related handlers.
Coordinates shift times, reminders, and timezone handlers.
"""

import logging
from .Preferences import ShiftTimesHandler, RemindersHandler, TimezoneHandler
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode


class PreferencesHandler:
    """Main handler that orchestrates all preference-related sub-handlers."""
    
    def __init__(self, telegram_client):
        self.telegram_client = telegram_client
        
        # Initialize specialized handlers
        self.shift_times_handler = ShiftTimesHandler(telegram_client)
        self.reminders_handler = RemindersHandler(telegram_client)
        self.timezone_handler = TimezoneHandler(telegram_client)
        
        # Map preference types to handlers
        self.handlers = {
            'shift_times': self.shift_times_handler,
            'reminders': self.reminders_handler,
            'timezone': self.timezone_handler,
        }
    
    async def can_handle(self, data: str) -> bool:
        """Check if any preference handler can process the given callback data."""
        
        # Check if any sub-handler can handle this data
        for handler in self.handlers.values():
            if await handler.can_handle(data):
                return True
        
        # Also handle main preference navigation
        preference_actions = [
            "settings_shift_times", "settings_reminders", 
            "settings_timezone",
            "reset_all_preferences"
        ]
        
        return data in preference_actions
    
    async def handle_callback(self, query, data: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Route callback to appropriate sub-handler or handle main navigation."""
        logger = logging.getLogger(__name__)
        logger.debug("PreferencesHandler: Received callback data: %s", data)
        
        # Try each sub-handler first
        for handler_name, handler in self.handlers.items():
            can_handle = await handler.can_handle(data)
            logger.debug("PreferencesHandler: %s can_handle(%s): %s", handler_name, data, can_handle)
            if can_handle:
                logger.debug("PreferencesHandler: Routing to %s", handler_name)
                return await handler.handle_callback(query, data, context)
        
        # Handle main preference navigation
        if data.startswith("settings_"):
            await self._handle_preference_navigation(query, data)
            return True
        
        elif data == "reset_all_preferences":
            await self.reset_all_preferences(query)
            return True
        
        return False  # Couldn't handle this data
    
    async def handle_text_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Route text input to appropriate sub-handler."""
        try:
            # Check what the user is waiting for
            waiting_for = context.user_data.get('waiting_for', '')
            
            # Route to shift times handler if relevant
            if waiting_for.startswith(('start_time_', 'end_time_')):
                return await self.shift_times_handler.handle_text_input(update, context)
            
            # Route to reminders handler if relevant
            if waiting_for.startswith('reminder_'):
                return await self.reminders_handler.handle_text_input(update, context)
            
            # Route to timezone handler if relevant
            if waiting_for.startswith('timezone_'):
                return await self.timezone_handler.handle_text_input(update, context)
            
            return False  # No handler could process this input
        except Exception as e:
            logging.getLogger(__name__).exception("ERROR in PreferencesHandler.handle_text_input: %s", e)
            return False
    
    async def _handle_preference_navigation(self, query, data: str):
        """Handle main preference menu navigation."""
        from Config.menus import MENU_CONFIGS
        
        if data in MENU_CONFIGS:
            menu_config = MENU_CONFIGS[data]
            
            # Handle callable menu configs (like shift edit menus)
            if callable(menu_config):
                menu_config = menu_config()
            
            # Format titles with dynamic content
            title = menu_config["title"]
            if data == "settings_shift_times":
                title = title.format(
                    shift_times_display=self.shift_times_handler.get_shift_times_display()
                )
            elif data == "settings_reminders":
                title = title.format(
                    reminders_display=self.reminders_handler.get_reminders_display()
                )
            elif data == "settings_timezone":
                title = title.format(
                    timezone_display=self.timezone_handler.get_timezone_display()
                )
            
            # Build proper keyboard
            button_rows = []
            for row in menu_config["buttons"]:
                button_row = self.telegram_client.inline_buttons_row(row)
                button_rows.append(button_row)
            
            await query.edit_message_text(
                title,
                reply_markup=self.telegram_client.inline_kb(button_rows),
                parse_mode=ParseMode.HTML
            )
        else:
            # Fallback for unknown preference actions
            await query.edit_message_text(
                f"⚙️ <b>העדפות</b>\n\n"
                f"פעולה: {data}\n"
                f"(הפעולה הזו עדיין בפיתוח)",
                reply_markup=self.telegram_client.inline_kb([
                    self.telegram_client.inline_buttons_row([("🔙 חזרה להעדפות", "preferences_menu")])
                ]),
                parse_mode=ParseMode.HTML
            )
    
    # Helper methods for future expansion
    
    def get_shift_times_handler(self):
        """Get the shift times handler instance."""
        return self.shift_times_handler
    
    def get_reminders_handler(self):
        """Get the reminders handler instance."""
        return self.reminders_handler
    
    def get_timezone_handler(self):
        """Get the timezone handler instance."""
        return self.timezone_handler
    
    async def reset_all_preferences(self, query):
        """Reset all preferences to defaults."""
        # Reset all preferences through their handlers
        await self.shift_times_handler.reset_all_shift_times(query)
        await self.reminders_handler.reset_all_reminders(query)
        await self.timezone_handler.reset_timezone(query)
        
        await query.edit_message_text(
            f"↩️ <b>העדפות אופסו</b>\n\n"
            f"כל ההעדפות חזרו לברירת המחדל.",
            reply_markup=self.telegram_client.inline_kb([
                self.telegram_client.inline_buttons_row([("🔙 חזרה להעדפות", "preferences_menu")])
            ]),
            parse_mode=ParseMode.HTML
        )
    
    def get_preferences_summary(self) -> str:
        """Get a summary of current preferences."""
        summary_parts = []
        
        # Add shift times summary
        shift_summary = self.shift_times_handler.get_shift_times_summary()
        summary_parts.append(f"⏰ **זמני משמרות:**\n{shift_summary}")
        
        # Add other preference summaries
        reminders_summary = self.reminders_handler.get_reminders_summary()
        summary_parts.append(f"🔔 **התראות:**\n{reminders_summary}")
        
        timezone_summary = self.timezone_handler.get_timezone_summary()
        summary_parts.append(f"🌍 **אזור זמן:**\n{timezone_summary}")
        
        return "\n\n".join(summary_parts)
