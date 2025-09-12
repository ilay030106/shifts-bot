#!/usr/bin/env python3
"""
Entry point for the Shifts Bot.
"""

import logging
from Clients.MainClient import MainClient


# Configure root logger for the application
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

# Silence overly-verbose HTTP libraries and third-party noise
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('aiohttp').setLevel(logging.WARNING)
logging.getLogger('http').setLevel(logging.WARNING)

if __name__ == "__main__":
    bot = MainClient()
    bot.run()
