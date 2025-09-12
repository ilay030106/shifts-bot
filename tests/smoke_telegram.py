#!/usr/bin/env python3
"""Non-interactive smoke test for TelegramClient.

This will instantiate the client, register handlers, call keyboard helpers,
and exit without starting polling or network activity.
"""
from Clients.TelegramClient import TelegramClient
import logging

def run_smoke():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("tests.smoke_telegram")

    try:
        client = TelegramClient()
        logger.info("TelegramClient instantiated")

        # Test keyboard helpers
        kb = client.inline_kb([client.inline_buttons_row([("A","a"), ("B","b")])])
        logger.info("Built inline keyboard: %s", kb)

        # Register no-op handlers (functions) without starting the bot
        async def dummy(update, context):
            return

        client.add_command_handler("start", dummy)
        client.add_text_handler(dummy)
        client.add_callback_query_handler(dummy)
        client.add_error_handler(dummy)
        logger.info("Registered handlers (no network started)")

        # Verify last_messages storage works
        client.last_messages[12345] = "hello"
        assert client.get_last_message(12345) == "hello"
        logger.info("last_messages works")

        logger.info("SMOKE TEST PASSED: TelegramClient basic API OK")
        return True
    except Exception as e:
        logger.exception("SMOKE TEST FAILED: %s", e)
        return False

if __name__ == '__main__':
    run_smoke()
