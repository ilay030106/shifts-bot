import asyncio
from telegram import Bot, Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from Config.config import TELEGRAM_BOT_TOKEN

class TelegramClient:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TelegramClient, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            if not TELEGRAM_BOT_TOKEN:
                raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")
            self.bot = Bot(TELEGRAM_BOT_TOKEN)
            self.last_messages = {}  # שמירת ההודעה האחרונה לכל משתמש
            TelegramClient._initialized = True

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """שומר את ההודעה האחרונה מהמשתמש"""
        user_id = update.effective_user.id
        text = update.message.text
        self.last_messages[user_id] = text
        print(f"📩 User {user_id}: {text}")

    async def start_listening(self):
        """מתחיל להאזין להודעות נכנסות ושומר את ההודעה האחרונה"""
        app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        print("🤖 Bot is now listening for messages...")
        await app.run_polling()

    def get_last_message(self, user_id: int):
        """מחזיר את ההודעה האחרונה של משתמש מסוים אם קיימת"""
        return self.last_messages.get(user_id, None)
