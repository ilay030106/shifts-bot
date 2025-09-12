
#!/usr/bin/env python3
"""
Interactive test script for TelegramClient.

This script:
- Instantiates the TelegramClient singleton
- Registers a few basic handlers (/start, text echo, callback queries)
- Starts polling and prints simple instructions

Stop with Ctrl+C.
"""

from __future__ import annotations

import asyncio
import traceback
from typing import Optional

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from Clients.TelegramClient import TelegramClient
from Config.config import TELEGRAM_BOT_TOKEN


# -----------------------------
# Handlers used in the test
# -----------------------------
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message with an inline keyboard to test callbacks."""
    client = TelegramClient()
    # Use the simpler inline_kb method with explicit button creation
    kb = client.inline_kb([
        client.inline_buttons_row([
            ("Settings", "settings"),
            ("Availability", "availability"),
            ("Documentation", "docs"),
        ])
    ])
    await update.effective_chat.send_message(
        "Welcome! This is a test bot.\n"
        "- Send any text and I'll echo it.\n"
        "- Tap a button below to test callback queries.",
        reply_markup=kb,
    )


async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Echo the text and demonstrate last-message cache via /last."""
    text = update.message.text if update.message else ""
    await update.effective_chat.send_message(f"Echo: {text}")


async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks by acknowledging and editing the original message."""
    q = update.callback_query
    if not q:
        return
    await q.answer()
    await q.edit_message_text(f"You clicked: <b>{q.data}</b>", parse_mode=ParseMode.HTML)


async def on_error(update: Optional[object], context: ContextTypes.DEFAULT_TYPE):
    """Basic async error logger (required by PTB v20+)."""
    err = getattr(context, "error", None)
    import logging
    logging.getLogger(__name__).error("[ERROR] Exception in handler: %s", err)
    if err:
        traceback.print_exception(type(err), err, err.__traceback__)


def test_telegram_client() -> bool:
    """Configure the TelegramClient and start polling for a manual test session."""
    import logging
    logger = logging.getLogger(__name__)
    logger.info("🤖 Testing TelegramClient (polling mode)...")

    if not TELEGRAM_BOT_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN is missing. Define it in your environment or .env file.")
        return False

    try:
        client = TelegramClient()
        logger.info("✅ TelegramClient initialized successfully")

        # Register handlers
        client.add_command_handler("start", cmd_start)
        client.add_text_handler(on_text)
        client.add_callback_query_handler(on_callback)
        client.add_error_handler(on_error)

        logger.info("📱 How to test: open Telegram and interact with the bot (interactive).")

        # Blocking run until Ctrl+C (clears webhook automatically)
        client.run_polling(drop_pending_updates=True)
        return True

    except KeyboardInterrupt:
        logger.info("🛑 Stopping (KeyboardInterrupt)...")
        return True
    except Exception as e:
        logger.exception("❌ Test failed with error: %s", e)
        traceback.print_exc()
        return False


def main():
    import logging
    logger = logging.getLogger(__name__)
    logger.info("💬  SHIFTS-BOT TELEGRAM CLIENT TEST")

    logger.info("This script will start your bot in polling mode and wait for messages.")
    logger.info("Make sure you have TELEGRAM_BOT_TOKEN configured and an Internet connection.")

    response = input("\nContinue and start polling? (y/N): ").strip().lower()
    if response not in ("y", "yes"):
        logger.info("❌ Test cancelled by user.")
        return

    success = test_telegram_client()

    if success:
        logger.info("🎉 TELEGRAM TEST COMPLETED (bot stopped)")
    else:
        logger.error("❌ TELEGRAM TEST FAILED")


if __name__ == "__main__":
    main()
