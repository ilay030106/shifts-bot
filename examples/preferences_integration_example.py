"""
Integration example showing how to use the modular PreferencesHandler in MainClient.
This demonstrates the clean separation of concerns with specialized handlers.
"""

from Handlers import PreferencesHandler
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode


class MainClientExample:
    """Example showing how to integrate the modular PreferencesHandler."""
    
    def __init__(self, telegram_client, calendar_client):
        self.telegram_client = telegram_client
        self.calendar_client = calendar_client
        
        # Initialize the preferences handler (which manages all sub-handlers)
        self.preferences_handler = PreferencesHandler(telegram_client)
        
    async def on_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Main callback query handler with clean routing."""
        query = update.callback_query
        await query.answer()
        data = query.data
        
        # 1. Handle main navigation
        if data == "menu_main":
            await self._show_main_menu(query)
            return
        
        # 2. Route preferences to PreferencesHandler (which handles all sub-handlers)
        if await self.preferences_handler.can_handle(data):
            await self.preferences_handler.handle_callback(query, data, context)
            return
        
        # 3. Handle other main sections (availability, docs, etc.)
        elif data in ["menu_availability", "menu_docs", "menu_help"]:
            await self._handle_main_sections(query, data)
            return
        
        # 4. Fallback for unknown actions
        else:
            await self._handle_unknown_action(query, data)
    
    async def on_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text input with routing to appropriate handlers."""
        
        # Route preference-related text input to PreferencesHandler
        if await self.preferences_handler.handle_text_input(update, context):
            return  # Successfully handled
        
        # Handle other text input (like general commands, etc.)
        await self._handle_general_text(update, context)
    
    async def _show_main_menu(self, query):
        """Show the main menu."""
        from Config.menus import MAIN_MENU
        
        await query.edit_message_text(
            MAIN_MENU["title"],
            reply_markup=self.telegram_client.inline_kb(MAIN_MENU["buttons"]),
            parse_mode=ParseMode.HTML
        )
    
    async def _handle_main_sections(self, query, data):
        """Handle main menu sections (availability, docs, help)."""
        from Config.menus import MENU_CONFIGS
        
        if data in MENU_CONFIGS:
            menu_config = MENU_CONFIGS[data]
            await query.edit_message_text(
                menu_config["title"],
                reply_markup=self.telegram_client.inline_kb(menu_config["buttons"]),
                parse_mode=ParseMode.HTML
            )
    
    async def _handle_unknown_action(self, query, data):
        """Handle unknown callback actions."""
        await query.edit_message_text(
            f"🔧 <b>פעולה: {data}</b>\n\n"
            f"פעולה זו עדיין בפיתוח...",
            reply_markup=self.telegram_client.inline_kb([
                [("🔙 חזרה לתפריט הראשי", "menu_main")]
            ]),
            parse_mode=ParseMode.HTML
        )
    
    async def _handle_general_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle general text messages that aren't preference-related."""
        await update.message.reply_text(
            "💬 הודעה התקבלה!\n\n"
            "השתמש ב-/start כדי לפתוח את התפריט.",
            reply_markup=self.telegram_client.inline_kb([
                [("🏠 תפריט ראשי", "menu_main")]
            ])
        )
    
    # Helper methods to access specific handlers
    
    def get_shift_times_handler(self):
        """Get direct access to shift times handler if needed."""
        return self.preferences_handler.get_shift_times_handler()
    
    async def get_preferences_summary(self) -> str:
        """Get a complete preferences summary."""
        return self.preferences_handler.get_preferences_summary()


# Example usage in your actual MainClient:
"""
from Handlers import PreferencesHandler

class MainClient:
    def __init__(self):
        # ... your existing setup ...
        self.preferences_handler = PreferencesHandler(self.telegram_client)
    
    async def on_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        data = query.data
        
        # Route preferences to the handler
        if await self.preferences_handler.can_handle(data):
            await self.preferences_handler.handle_callback(query, data, context)
            return
        
        # ... handle other sections ...
    
    async def on_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Route text input to preferences handler
        if await self.preferences_handler.handle_text_input(update, context):
            return
        
        # ... handle other text input ...
"""
