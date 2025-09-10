from .TelegramClient import TelegramClient
from .CalenderClient import CalenderClient
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from Config.menus import (
    MAIN_MENU, DEFAULTS_MENU, AVAILABILITY_MENU, DOCS_MENU,
    HELP_TEXT, SUBMENU_TEMPLATES, BACK_BUTTONS, ACTION_NAMES
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
        
        # Handle specific actions within submenus
        elif data.startswith("settings_"):
            action = data.replace("settings_", "")
            action_name = ACTION_NAMES.get(action, action)
            await query.edit_message_text(
                SUBMENU_TEMPLATES["settings"].format(action=action_name),
                reply_markup=self.telegram_client.inline_kb([
                    self.telegram_client.inline_buttons_row([BACK_BUTTONS["settings"]])
                ]),
                parse_mode=ParseMode.HTML
            )
        
        elif data.startswith("availability_"):
            action = data.replace("availability_", "")
            action_name = ACTION_NAMES.get(action, action)
            await query.edit_message_text(
                SUBMENU_TEMPLATES["availability"].format(action=action_name),
                reply_markup=self.telegram_client.inline_kb([
                    self.telegram_client.inline_buttons_row([BACK_BUTTONS["availability"]])
                ]),
                parse_mode=ParseMode.HTML
            )
        
        elif data.startswith("docs_"):
            action = data.replace("docs_", "")
            action_name = ACTION_NAMES.get(action, action)
            await query.edit_message_text(
                SUBMENU_TEMPLATES["docs"].format(action=action_name),
                reply_markup=self.telegram_client.inline_kb([
                    self.telegram_client.inline_buttons_row([BACK_BUTTONS["docs"]])
                ]),
                parse_mode=ParseMode.HTML
            )

    def run(self):
        """Start the bot."""
        print("🤖 Starting Shifts Bot...")
        print("✅ Handlers registered. Use /start in Telegram.")
        print("Press Ctrl+C to stop.")
        self.telegram_client.run_polling(drop_pending_updates=True)


