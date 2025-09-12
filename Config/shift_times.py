"""
Shift time management utilities.
Handles default shift times, user preferences, and time validation.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

class ShiftTimeManager:
    """Manages shift time configurations and user preferences."""

    def __init__(self, config_file: str = "user_shift_times.json"):
        self.config_file = config_file

        # Define default shift configurations
        self.default_times = {
            "morning": {"name": "בוקר", "start": "08:00", "end": "16:00", "emoji": "🌅"},
            "noon": {"name": "צהריים", "start": "12:00", "end": "20:00", "emoji": "🌇"},
            "evening": {"name": "ערב", "start": "16:00", "end": "00:00", "emoji": "🌆"}
        }

        # Initialize user times
        self.user_times = {k: v.copy() for k, v in self.default_times.items()}
        self._load_user_times()

    def _load_user_times(self):
        """Load user preferences and merge with defaults."""
        if not os.path.exists(self.config_file):
            self._save_user_times()
            return

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for shift_type, config in data.items():
                    if shift_type in self.user_times and isinstance(config, dict):
                        # Update only start/end times if valid
                        if self._is_valid_time(config.get("start")):
                            self.user_times[shift_type]["start"] = config["start"]
                        if self._is_valid_time(config.get("end")):
                            self.user_times[shift_type]["end"] = config["end"]
        except (json.JSONDecodeError, Exception):
            pass  # Use defaults if file is corrupted

        self._save_user_times()

    def _save_user_times(self):
        """Save current user_times to file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_times, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _is_valid_time(self, time_str: str) -> bool:
        """Validate time format (HH:MM)."""
        if not time_str:
            return False
        try:
            datetime.strptime(time_str, "%H:%M")
            return True
        except ValueError:
            return False

    def get_shift_times(self) -> Dict[str, Any]:
        """Get current shift times."""
        return self.user_times

    def get_shift_times_display(self) -> str:
        """Generate formatted shift times display text."""
        return "\n".join(
            f"• {config['emoji']} {config['name']}: {config['start']}-{config['end']}"
            for config in self.user_times.values()
        )

    def update_shift_time(self, shift_type: str, start_time: str = None, end_time: str = None) -> bool:
        """Update shift time for a specific shift type."""
        if shift_type not in self.user_times:
            return False

        if start_time and not self._is_valid_time(start_time):
            return False
        if end_time and not self._is_valid_time(end_time):
            return False

        if start_time:
            self.user_times[shift_type]["start"] = start_time
        if end_time:
            self.user_times[shift_type]["end"] = end_time

        self._save_user_times()
        return True

    def reset_shift_times(self):
        """Reset all shift times to defaults."""
        for shift_type, default_config in self.default_times.items():
            self.user_times[shift_type].update({
                "start": default_config["start"],
                "end": default_config["end"]
            })
        self._save_user_times()

    def reset_shift_time(self, shift_type: str):
        """Reset specific shift type to default."""
        if shift_type in self.default_times:
            self.user_times[shift_type].update({
                "start": self.default_times[shift_type]["start"],
                "end": self.default_times[shift_type]["end"]
            })
            self._save_user_times()

    def get_shift_duration(self, shift_type: str) -> Optional[float]:
        """Get shift duration in hours."""
        if shift_type not in self.user_times:
            return None

        try:
            start = datetime.strptime(self.user_times[shift_type]["start"], "%H:%M")
            end = datetime.strptime(self.user_times[shift_type]["end"], "%H:%M")

            # Handle overnight shifts
            if end < start:
                end = end.replace(day=end.day + 1)

            return (end - start).total_seconds() / 3600
        except ValueError:
            return None

    def is_time_in_shift(self, check_time: str, shift_type: str) -> bool:
        """Check if a given time falls within a shift window."""
        if shift_type not in self.user_times:
            return False

        try:
            check = datetime.strptime(check_time, "%H:%M").time()
            start = datetime.strptime(self.user_times[shift_type]["start"], "%H:%M").time()
            end = datetime.strptime(self.user_times[shift_type]["end"], "%H:%M").time()

            if end < start:  # Overnight shift
                return check >= start or check <= end
            return start <= check <= end
        except ValueError:
            return False

    def get_shift_type_for_time(self, check_time: str) -> Optional[str]:
        """Get which shift type a given time belongs to."""
        for shift_type in self.user_times:
            if self.is_time_in_shift(check_time, shift_type):
                return shift_type
        return None

# Global instance for easy access
shift_time_manager = ShiftTimeManager()