from .TelegramClient import TelegramClient
from .CalenderClient import CalenderClient
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from Config.menus import (
    MAIN_MENU, DEFAULTS_MENU, AVAILABILITY_MENU, DOCS_MENU,
    HELP_TEXT, BACK_BUTTONS, MENU_CONFIGS
)


class MainClient:
    def __init__(self):
        self.telegram_client = TelegramClient()
        self.calendar_client = CalenderClient()
        self.telegram_client.add_command_handler("start", self.cmd_start)
        self.telegram_client.add_callback_query_handler(self.on_callback)
        self.telegram_client.add_error_handler(self.on_error)

    def _build_menu(self, menu_config):
        """Build a keyboard from menu configuration."""
        return self.telegram_client.inline_kb([
            self.telegram_client.inline_buttons_row(row)
            for row in menu_config["buttons"]
        ])

    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send the main menu."""
        await update.effective_chat.send_message(
            MAIN_MENU["title"],
            reply_markup=self._build_menu(MAIN_MENU),
            parse_mode=ParseMode.HTML
        )
    async def on_error(self, update, context):
        """Basic error handler."""
        print(f"[ERROR] {context.error}")

    async def on_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button clicks and show different menus."""
        query = update.callback_query
        if not query:
            return
        
        await query.answer()  # Acknowledge the button press
        data = query.data
        
        # Route to different menus based on callback data
        if data == "menu_main":
            await query.edit_message_text(
                MAIN_MENU["title"],
                reply_markup=self._build_menu(MAIN_MENU),
                parse_mode=ParseMode.HTML
            )
        
        elif data == "defaults_menu":
            await query.edit_message_text(
                DEFAULTS_MENU["title"],
                reply_markup=self._build_menu(DEFAULTS_MENU),
                parse_mode=ParseMode.HTML
            )
        
        elif data == "menu_availability":
            await query.edit_message_text(
                AVAILABILITY_MENU["title"],
                reply_markup=self._build_menu(AVAILABILITY_MENU),
                parse_mode=ParseMode.HTML
            )
        
        elif data == "menu_docs":
            await query.edit_message_text(
                DOCS_MENU["title"],
                reply_markup=self._build_menu(DOCS_MENU),
                parse_mode=ParseMode.HTML
            )
        
        elif data == "menu_help":
            await query.edit_message_text(
                HELP_TEXT,
                reply_markup=self.telegram_client.inline_kb([
                    self.telegram_client.inline_buttons_row([BACK_BUTTONS["main"]])
                ]),
                parse_mode=ParseMode.HTML
            )
        
        # Handle specific actions within submenus - use centralized menu configs
        elif data in MENU_CONFIGS:
            # Direct menu lookup - much cleaner!
            menu_config = MENU_CONFIGS[data]
            await query.edit_message_text(
                menu_config["title"],
                reply_markup=self._build_menu(menu_config),
                parse_mode=ParseMode.HTML
            )
        
        # Handle actions that don't have direct menu configs yet
        else:
            await self._handle_unknown_action(query, data)

    async def _handle_unknown_action(self, query, data):
        """Handle actions that don't have specific menu configs yet."""
        # This is a fallback for actions like edit_shift_times, start_add_shift, etc.
        await query.edit_message_text(
            f"� <b>פעולה: {data}</b>\n\n"
            f"פעולה זו עדיין בפיתוח...\n"
            f"(כאן תהיה הלוגיקה הספציפית)",
            reply_markup=self.telegram_client.inline_kb([
                self.telegram_client.inline_buttons_row([BACK_BUTTONS["main"]])
            ]),
            parse_mode=ParseMode.HTML
        )


    def run(self):
        """Start the bot."""
        print("🤖 Starting Shifts Bot...")
        print("✅ Handlers registered. Use /start in Telegram.")
        print("Press Ctrl+C to stop.")
        self.telegram_client.run_polling(drop_pending_updates=True)


