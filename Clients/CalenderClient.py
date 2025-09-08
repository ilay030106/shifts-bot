import os.path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from dateutil import parser
from ..Config.config import DEFAULT_TIME_ZONE  # e.g. "Asia/Jerusalem"

# Use events scope since you create/update events in this MVP
SCOPES = ["https://www.googleapis.com/auth/calendar.events"]


class CalenderClient:
    """
    CalenderClient handles authentication and connection to the Google Calendar API.

    Singleton implementation ensures only one instance exists.

    Attributes:
        service: The Google Calendar API service object for making requests.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CalenderClient, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Initializes the CalenderClient by authenticating the user and creating a Google Calendar API service object.
        Loads credentials from token.json if available, otherwise starts the OAuth flow.
        The service object is stored in self.service for further calendar operations.
        """
        if hasattr(self, "service"):
            return  # Prevent re-initialization

        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        self.service = build("calendar", "v3", credentials=creds)
        self._default_tz = ZoneInfo(DEFAULT_TIME_ZONE)

    # ----------------------------
    # Helpers
    # ----------------------------
    def _ensure_aware(self, dt: datetime) -> datetime:
        """
        Ensure a datetime is timezone-aware. If naive, attach the default timezone.
        """
        if dt.tzinfo is None:
            return dt.replace(tzinfo=self._default_tz)
        return dt

    def _parse_event_bound(self, value: str, is_end: bool) -> datetime:
        """
        Parse a Google Calendar event boundary which may be either:
        - dateTime: ISO string with time and offset
        - date: All-day event (no time). In GCal, end.date is exclusive (next day's midnight).
        """
        if "T" in value:
            # Regular timed event
            return parser.isoparse(value)

        # All-day event (value is YYYY-MM-DD), interpret in default tz
        d = parser.isoparse(value).date()
        start_of_day = datetime(d.year, d.month, d.day, tzinfo=self._default_tz)
        if is_end:
            # end is exclusive -> midnight of the next day
            return start_of_day + timedelta(days=1)
        else:
            return start_of_day

    # ----------------------------
    # Public API
    # ----------------------------
    def create_new_event(self, desc, start_dateTime, end_dateTime, reminders=None, time_zone=DEFAULT_TIME_ZONE):
        """
        Create a new calendar event with optional reminders.

        Args:
            desc (str): Event summary/title.
            start_dateTime (str): Start time in ISO 8601 format.
            end_dateTime (str): End time in ISO 8601 format.
            reminders (list[int] | None): List of reminder minutes before event (e.g., [15, 30]).
            time_zone (str): Timezone ID for the event (e.g., "Asia/Jerusalem").

        Returns:
            dict: Created event object.
        """
        event = {
            "summary": desc,
            "start": {
                "dateTime": start_dateTime,
                "timeZone": time_zone,
            },
            "end": {
                "dateTime": end_dateTime,
                "timeZone": time_zone,
            },
        }

        if reminders:
            event["reminders"] = {
                "useDefault": False,
                "overrides": [{"method": "popup", "minutes": m} for m in reminders],
            }
        else:
            event["reminders"] = {"useDefault": True}

        created_event = self.service.events().insert(calendarId="primary", body=event).execute()
        return created_event

    def is_overlapping(self, start_dt: datetime, end_dt: datetime, calendar_id: str = "primary"):
        """
        Check whether a proposed event overlaps existing events.

        Args:
            start_dt (datetime): Proposed event start (timezone-aware or naive).
            end_dt   (datetime): Proposed event end   (timezone-aware or naive).
            calendar_id (str): Calendar to check. Default is "primary".

        Returns:
            tuple[bool, list[dict]]: (has_conflict, conflicting_events)
        """
        start_dt = self._ensure_aware(start_dt)
        end_dt = self._ensure_aware(end_dt)

        # Broaden the search slightly to catch events spanning the window edges.
        search_min = (start_dt - timedelta(days=1)).isoformat()
        search_max = (end_dt + timedelta(days=1)).isoformat()

        events_result = (
            self.service.events()
            .list(
                calendarId=calendar_id,       # correct param name
                timeMin=search_min,           # ISO strings
                timeMax=search_max,           # ISO strings
                singleEvents=True,
                orderBy="startTime",
                maxResults=2500,
            )
            .execute()
        )
        events = events_result.get("items", [])

        conflicts = []
        for ev in events:
            ev_start_raw = ev["start"].get("dateTime", ev["start"].get("date"))
            ev_end_raw = ev["end"].get("dateTime", ev["end"].get("date"))
            if not ev_start_raw or not ev_end_raw:
                continue

            ev_start_dt = self._parse_event_bound(ev_start_raw, is_end=False)
            ev_end_dt = self._parse_event_bound(ev_end_raw, is_end=True)

            # Overlap rule: [start_dt, end_dt) intersects [ev_start_dt, ev_end_dt)
            if start_dt < ev_end_dt and end_dt > ev_start_dt:
                conflicts.append(ev)

        return (len(conflicts) > 0, conflicts)

    def get_upcoming_events(self, dt: datetime, days: int = 7, calendar_id: str = "primary"):
        """
        Get upcoming events for a fixed window starting at dt.

        Args:
            dt (datetime): Start of the window (timezone-aware or naive).
            days (int): Number of days to look ahead. Default: 7.
            calendar_id (str): Calendar to query. Default: "primary".

        Returns:
            list[dict]: List of event resources within the window.
        """
        dt = self._ensure_aware(dt)
        time_min = dt.isoformat()
        time_max = (dt + timedelta(days=days)).isoformat()

        items = []
        page_token = None
        while True:
            resp = (
                self.service.events()
                .list(
                    calendarId=calendar_id,
                    timeMin=time_min,
                    timeMax=time_max,
                    singleEvents=True,
                    orderBy="startTime",
                    maxResults=2500,
                    pageToken=page_token,
                )
                .execute()
            )
            items.extend(resp.get("items", []))
            page_token = resp.get("nextPageToken")
            if not page_token:
                break

        return items
