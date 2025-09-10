#!/usr/bin/env python3
"""
Test script for CalendarClient functionality.
This script demonstrates basic operations like creating events, checking for overlaps,
and retrieving upcoming events.
"""

import sys
import os
# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from Clients.CalenderClient import CalenderClient
from Config.config import DEFAULT_TIME_ZONE
from utils import to_iso8601
import traceback

def test_calendar_client():
    """Test the CalendarClient functionality."""
    print("🚀 Testing CalendarClient...")
    
    try:
        # Initialize the calendar client (singleton)
        client = CalenderClient()
        print("✅ CalendarClient initialized successfully")
        
        # Test 1: Get upcoming events
        print("\n📅 Test 1: Getting upcoming events...")
        now = datetime.now()
        upcoming_events = client.get_upcoming_events(now, days=7)
        print(f"✅ Found {len(upcoming_events)} upcoming events in the next 7 days")
        
        if upcoming_events:
            print("📋 Upcoming events:")
            for i, event in enumerate(upcoming_events[:3]):  # Show first 3 events
                summary = event.get('summary', 'No title')
                start_time = event.get('start', {}).get('dateTime', event.get('start', {}).get('date', 'Unknown'))
                print(f"   {i+1}. {summary} - {start_time}")
        
        # Test 2: Check for overlaps (using a future time to avoid conflicts)
        print("\n🔍 Test 2: Checking for overlaps...")
        test_start = now + timedelta(days=30)  # 30 days from now
        test_end = test_start + timedelta(hours=1)
        
        has_conflict, conflicts = client.is_overlapping(test_start, test_end)
        print(f"✅ Overlap check completed. Conflicts found: {has_conflict}")
        
        if has_conflict:
            print(f"⚠️  Found {len(conflicts)} conflicting events")
        
        # Test 3: Create a test event (30 days from now to avoid real conflicts)
        print("\n📝 Test 3: Creating a test event...")
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
        
        print(f"✅ Test event created successfully!")
        print(f"   Event ID: {created_event.get('id')}")
        print(f"   Event Link: {created_event.get('htmlLink', 'N/A')}")
        
        # Test 4: Verify the singleton pattern
        print("\n🔄 Test 4: Testing singleton pattern...")
        client2 = CalenderClient()
        print(f"✅ Same instance check: {client is client2}")
        
        print("\n🎉 All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        print("\n📋 Full traceback:")
        traceback.print_exc()
        return False

def main():
    """Main function to run the tests."""
    print("=" * 60)
    print("🗓️  SHIFTS-BOT CALENDAR CLIENT TEST")
    print("=" * 60)
    
    print("\n⚠️  IMPORTANT: This test will create a real calendar event!")
    print("   The event will be scheduled 30 days from now to avoid conflicts.")
    print("   Make sure you have:")
    print("   1. credentials.json file in the project root")
    print("   2. Internet connection")
    print("   3. Google Calendar API enabled")
    
    response = input("\nContinue with testing? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("❌ Test cancelled by user.")
        return
    
    success = test_calendar_client()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 TEST COMPLETED SUCCESSFULLY!")
    else:
        print("❌ TEST FAILED!")
    print("=" * 60)

if __name__ == "__main__":
    main()
