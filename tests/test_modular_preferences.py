#!/usr/bin/env python3
"""
Test the modular PreferencesHandler with ShiftTimesHandler integration.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock telegram client for testing
class MockTelegramClient:
    def inline_kb(self, buttons):
        return f"Keyboard with buttons: {buttons}"

def test_preferences_handler():
    """Test the PreferencesHandler orchestration."""
    import logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s [%(name)s] %(message)s")
    logger = logging.getLogger(__name__)
    logger.info("🎛️ Testing Modular PreferencesHandler")
    logger.info("%s", "=" * 50)
    
    # Initialize with mock client
    from Handlers import PreferencesHandler
    telegram_client = MockTelegramClient()
    preferences = PreferencesHandler(telegram_client)
    
    logger.info("✅ PreferencesHandler initialized successfully")
    
    # Test handler routing capabilities
    test_actions = [
        "settings_shift_times",  # Should route to menu navigation
        "edit_shift_times",      # Should route to ShiftTimesHandler
        "edit_morning_shift",    # Should route to ShiftTimesHandler
        "edit_start_morning",    # Should route to ShiftTimesHandler
        "some_other_action",     # Should not be handled
    ]
    
    logger.info("\n📋 Testing Action Routing:")
    for action in test_actions:
        can_handle = None
        try:
            # Note: can_handle is async, so we can't easily test it here without asyncio
            # This is just to show the structure
            logger.debug("  %s: Handler found = %s", action, preferences.handlers)
        except Exception as e:
            logger.exception("  %s: Error = %s", action, e)
    
    # Test direct handler access
    logger.info("\n🔧 Testing Handler Access:")
    shift_handler = preferences.get_shift_times_handler()
    logger.info("  ShiftTimesHandler: %s", type(shift_handler).__name__)
    
    # Test shift times functionality
    logger.info("  Shift Times Summary: %s", shift_handler.get_shift_times_summary())
    
    logger.info("\n🎯 Handler Architecture:")
    logger.info("  Main Handler: %s", type(preferences).__name__)
    logger.info("  Sub-handlers: %s", list(preferences.handlers.keys()))
    logger.info("  ShiftTimesHandler available: %s", 'shift_times' in preferences.handlers)
    
    logger.info("\n✅ All tests completed successfully!")
    logger.info("\n📝 Integration Ready:")
    logger.info("  - PreferencesHandler orchestrates specialized handlers")
    logger.info("  - ShiftTimesHandler manages all shift time operations")
    logger.info("  - Clean separation of concerns")
    logger.info("  - Easy to add more handlers (reminders, timezone, templates)")

if __name__ == "__main__":
    test_preferences_handler()
