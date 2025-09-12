#!/usr/bin/env python3
"""
Test script for CalendarClient functionality.
This script demonstrates basic operations like creating events, checking for overlaps,
and retrieving upcoming events.
"""

from datetime import datetime, timedelta
from Clients.CalenderClient import CalenderClient
from Config.config import DEFAULT_TIME_ZONE
from utils import to_iso8601
import traceback
import json

def test_calendar_client():
    """Test the CalendarClient functionality."""
    import logging
    logger = logging.getLogger(__name__)
    logger.info("🚀 Testing CalendarClient...")
    try:
        # Initialize the calendar client (singleton)
        client = CalenderClient()
        logger.info("✅ CalendarClient initialized successfully")

        # Test 1: Get upcoming events
        logger.info("\n📅 Test 1: Getting upcoming events...")
        now = datetime.now()
        upcoming_events = client.get_upcoming_events(now, days=7)
        logger.info("✅ Found %d upcoming events in the next 7 days", len(upcoming_events))

        if upcoming_events:
            logger.info("📋 Upcoming events (showing up to 5):")
            for i, event in enumerate(upcoming_events[:5]):  # Show first 5 events
                summary = event.get('summary', 'No title')
                start = event.get('start', {})
                end = event.get('end', {})
                start_time = start.get('dateTime', start.get('date', 'Unknown'))
                end_time = end.get('dateTime', end.get('date', 'Unknown'))
                event_id = event.get('id', 'N/A')
                desc = event.get('description', '')
                location = event.get('location', '')
                attendees = event.get('attendees', [])
                reminders = event.get('reminders', {})
                logger.info("--- Event %d ---", i+1)
                logger.info("  ID: %s", event_id)
                logger.info("  Title: %s", summary)
                logger.info("  Start: %s", start_time)
                logger.info("  End: %s", end_time)
                if location:
                    logger.info("  Location: %s", location)
                if desc:
                    logger.info("  Description: %s", desc)
                if attendees:
                    logger.info("  Attendees: %d", len(attendees))
                if reminders:
                    logger.info("  Reminders: %s", json.dumps(reminders, ensure_ascii=False))

        # Test 2: Check for overlaps (using a future time to avoid conflicts)
        logger.info("\n🔍 Test 2: Checking for overlaps...")
        test_start = now + timedelta(days=30)  # 30 days from now
        test_end = test_start + timedelta(hours=1)

        has_conflict, conflicts = client.is_overlapping(test_start, test_end)
        logger.info("✅ Overlap check completed. Conflicts found: %s", has_conflict)

        if has_conflict:
            logger.warning("⚠️  Found %d conflicting events", len(conflicts))
            for j, ev in enumerate(conflicts[:5]):
                s = ev.get('summary', 'No title')
                st = ev.get('start', {}).get('dateTime', ev.get('start', {}).get('date', 'Unknown'))
                en = ev.get('end', {}).get('dateTime', ev.get('end', {}).get('date', 'Unknown'))
                logger.warning("  Conflict %d: %s (%s - %s)", j+1, s, st, en)

        # Test 3: Create a test event (30 days from now to avoid real conflicts)
        logger.info("\n📝 Test 3: Creating a test event...")
        test_event_start = to_iso8601(
            test_start.year, test_start.month, test_start.day,
            test_start.hour, test_start.minute, 0,
            DEFAULT_TIME_ZONE
        )
        test_event_end = to_iso8601(
            test_end.year, test_end.month, test_end.day,
            test_end.hour, test_end.minute, 0,
            DEFAULT_TIME_ZONE
        )

        created_event = client.create_new_event(
            desc="🧪 Test Event - Calendar Bot Test",
            start_dateTime=test_event_start,
            end_dateTime=test_event_end,
            reminders=[15, 30],  # 15 and 30 minute reminders
            time_zone=DEFAULT_TIME_ZONE
        )

        logger.info("✅ Test event created successfully!")
        # Print the created event details
        try:
            logger.info("Created event details:\n%s", json.dumps(created_event, ensure_ascii=False, indent=2))
        except Exception:
            logger.info("   Event ID: %s", created_event.get('id'))
            logger.info("   Event Link: %s", created_event.get('htmlLink', 'N/A'))

        # Test 4: Verify the singleton pattern
        logger.info("\n🔄 Test 4: Testing singleton pattern...")
        client2 = CalenderClient()
        logger.info("✅ Same instance check: %s", client is client2)

        logger.info("\n🎉 All tests completed successfully!")
        return True

    except Exception as e:
        logger.exception("❌ Test failed with error: %s", e)
        traceback.print_exc()
        return False

def main():
    """Main function to run the tests."""
    import logging
    # Ensure INFO-level logs are visible when running this script directly
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s [%(name)s] %(message)s")
    logger = logging.getLogger(__name__)
    logger.info("%s", "=" * 60)
    logger.info("🗓️  SHIFTS-BOT CALENDAR CLIENT TEST")
    logger.info("%s", "=" * 60)
    
    logger.warning("\n⚠️  IMPORTANT: This test will create a real calendar event!")
    logger.info("   The event will be scheduled 30 days from now to avoid conflicts.")
    logger.info("   Make sure you have:")
    logger.info("   1. credentials.json file in the project root")
    logger.info("   2. Internet connection")
    logger.info("   3. Google Calendar API enabled")
    
    response = input("\nContinue with testing? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        logger.info("❌ Test cancelled by user.")
        return
    
    success = test_calendar_client()
    
    logger.info("\n%s", "=" * 60)
    if success:
        logger.info("🎉 TEST COMPLETED SUCCESSFULLY!")
    else:
        logger.error("❌ TEST FAILED!")
    logger.info("%s", "=" * 60)

if __name__ == "__main__":
    main()
