#!/usr/bin/env python3
"""
Entry point for the Shifts Bot.
"""

from Clients.MainClient import MainClient

if __name__ == "__main__":
    bot = MainClient()
    bot.run()
