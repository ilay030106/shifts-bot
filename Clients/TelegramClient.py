import asyncio
from typing import Callable, Optional, Iterable, Sequence, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, MessageHandler, CommandHandler, ContextTypes, filters, BaseHandler, CallbackQueryHandler
)
from Config.config import TELEGRAM_BOT_TOKEN


class TelegramClient:
    """
    TelegramClient: chat-only wrapper around python-telegram-bot.

    - Builds a single Application instance
    - Provides helper methods to register handlers
    - Starts polling/webhook (no business logic included)
    - Keeps optional last_messages cache per user
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TelegramClient, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if TelegramClient._initialized:
            return

        if not TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")

        # Build a single Application for the bot
        self.app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

        # Simple per-user last message cache (optional utility)
        self.last_messages = {}

        # Default text handler that only records last messages (can be removed/overridden)
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

        TelegramClient._initialized = True

    # -----------------------------
    # Registration helpers
    # -----------------------------
    def add_text_handler(self, callback: Callable[[Update, ContextTypes.DEFAULT_TYPE], None], *, allow_commands: bool = False):
        f = filters.TEXT if allow_commands else (filters.TEXT & ~filters.COMMAND)
        self.app.add_handler(MessageHandler(f, callback))

    def add_command_handler(self, command: str, callback: Callable[[Update, ContextTypes.DEFAULT_TYPE], None]):
        self.app.add_handler(CommandHandler(command, callback))

    def add_callback_query_handler(self, callback: Callable[[Update, ContextTypes.DEFAULT_TYPE], None], *, pattern: Optional[str] = None):
        """Convenience to add a CallbackQueryHandler."""
        self.app.add_handler(CallbackQueryHandler(callback, pattern=pattern))

    def add_error_handler(self, callback: Callable[[object, ContextTypes.DEFAULT_TYPE], None]):
        """Register a global error handler (signature: (update, context))."""
        self.app.add_error_handler(callback)

    def add_handler(self, handler: BaseHandler):
        """Register any custom handler (ConversationHandler, etc.)."""
        self.app.add_handler(handler)

    # -----------------------------
    # Lifecycle: Polling
    # -----------------------------
    def run_polling(self, *, drop_pending_updates: bool = True):
        """Start polling in the foreground (blocking)."""
        print("🤖 Bot is now listening for messages (polling)...")
        # run_polling handles event loop creation internally
        self.app.run_polling(drop_pending_updates=drop_pending_updates)

    async def start_polling_async(self, *, drop_pending_updates: bool = True):
        """Async alternative to start polling (advanced usage)."""
        print("🤖 Bot is now listening for messages (polling, async)...")
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling(drop_pending_updates=drop_pending_updates)
        # Caller can await self.app.updater.idle()

    async def stop_polling_async(self):
        """Gracefully stop polling and shutdown the application."""
        await self.app.updater.stop()
        await self.app.stop()
        await self.app.shutdown()

    # -----------------------------
    # Lifecycle: Webhook
    # -----------------------------
    def run_webhook(
        self,
        *,
        listen = "0.0.0.0",
        port = 8000,
        url_path = "/webhook",
        webhook_url = None,
        secret_token= None,
        drop_pending_updates = True,
    ):
        """
        Run the bot using webhook mode (blocking).

        Provide a public webhook_url (e.g., from reverse proxy) and optional secret_token.
        """
        print(f"🤖 Bot is now listening via webhook on {listen}:{port}{url_path}...")
        self.app.run_webhook(
            listen=listen,
            port=port,
            url_path=url_path,
            webhook_url=webhook_url,
            secret_token=secret_token,
            drop_pending_updates=drop_pending_updates,
        )

    # -----------------------------
    # Utilities
    # -----------------------------
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Default text handler: store user's last message (no business logic)."""
        if not update.effective_user or not update.message:
            return
        user_id = update.effective_user.id
        text = update.message.text or ""
        self.last_messages[user_id] = text
        print(f"📩 User {user_id}: {text}")

    async def send_message(self, chat_id: int, text: str, *, reply_markup: Optional[Any] = None, parse_mode: Optional[str] = None):
        """Helper to send a message via the app's bot."""
        await self.app.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup, parse_mode=parse_mode)

    def get_last_message(self, user_id: int) -> Optional[str]:
        """Return the last message of a specific user, if any."""
        return self.last_messages.get(user_id)

    # -----------------------------
    # Inline keyboard helpers
    # -----------------------------
    @staticmethod
    def inline_kb(rows: Sequence[Sequence[InlineKeyboardButton]]):
        """
        Build an InlineKeyboardMarkup from rows of InlineKeyboardButton objects.

        Parameters:
        - rows: sequence of rows, each a sequence of InlineKeyboardButton

        Returns:
        - InlineKeyboardMarkup ready to pass as reply_markup

        Example:
        - TelegramClient.inline_kb([[InlineKeyboardButton("OK", callback_data="ok")]])
        """
        return InlineKeyboardMarkup(rows)

    @staticmethod
    def inline_buttons_row(buttons: Iterable[tuple[str, str]]):
        """
        Create a row (list) of InlineKeyboardButton from (text, callback_data) tuples.

        Parameters:
        - buttons: iterable of (text, callback_data)

        Returns:
        - list[InlineKeyboardButton]

        Example:
        - TelegramClient.inline_buttons_row([("Yes", "yes"), ("No", "no")])
        """
        return [InlineKeyboardButton(text, callback_data=data) for text, data in buttons]

    # -----------------------------
    # Simpler keyboard helpers
    # -----------------------------
    @staticmethod
    def kb(rows: Sequence[Sequence["str | tuple[str, str]"]]):
        """
        Build a keyboard from simple values.

        Accepts rows of items where each item is either:
        - a string (used for both text and callback_data), or
        - a (text, callback_data) tuple

        Parameters:
        - rows: e.g., [["Settings", ("Docs", "documentation")]]

        Returns:
        - InlineKeyboardMarkup

        Examples:
        - TelegramClient.kb([["A", "B"]])                     # callback_data == text
        - TelegramClient.kb([["Settings", ("Docs", "docs")]]) # custom data for Docs
        """
        built: list[list[InlineKeyboardButton]] = []
        for row in rows:
            btn_row: list[InlineKeyboardButton] = []
            for item in row:
                if isinstance(item, tuple):
                    text, data = item
                else:
                    text = data = str(item)
                btn_row.append(InlineKeyboardButton(text, callback_data=data))
            built.append(btn_row)
        return InlineKeyboardMarkup(built)

    @staticmethod
    def row(*buttons: "str | tuple[str, str]"):
        """
        Create a single row of buttons from strings or (text, callback_data) tuples.

        Parameters:
        - buttons: items like "Settings" or ("Docs", "documentation")

        Returns:
        - list[InlineKeyboardButton]

        Example:
        - TelegramClient.row("Settings", ("Docs", "docs"))
        """
        out: list[InlineKeyboardButton] = []
        for item in buttons:
            if isinstance(item, tuple):
                text, data = item
            else:
                text = data = str(item)
            out.append(InlineKeyboardButton(text, callback_data=data))
        return out
