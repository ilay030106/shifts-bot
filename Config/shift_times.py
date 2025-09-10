"""
Shift time management utilities.
Handles default shift times, user preferences, and time validation.
"""

import json
import os
from datetime import datetime, time
from typing import Dict, Any, Optional, Tuple

class ShiftTimeManager:
    """Manages shift time configurations and user preferences."""
    
    def __init__(self, config_file: str = "user_shift_times.json"):
        self.config_file = config_file
        self.default_times = {
            "morning": {
                "name": "בוקר"[::-1],  # Correct way to reverse string
                "start": "07:00",
                "end": "15:00",
                "emoji": "🌅"
            },
            "afternoon": {
                "name": "אמצע"[::-1],  # Correct way to reverse string
                "start": "15:00", 
                "end": "23:00",
                "emoji": "🌇"
            },
            "night": {
                "name": "לילה"[::-1],  # Correct way to reverse string
                "start": "23:00",
                "end": "07:00",
                "emoji": "🌙"
            }
        }
        self.user_times = self._load_user_times()
    
    def _load_user_times(self) -> Dict[str, Any]:
        """Load user customized shift times from file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        return {}
    
    def _save_user_times(self):
        """Save user customized shift times to file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_times, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving shift times: {e}")
    
    def get_shift_times(self) -> Dict[str, Any]:
        """Get current shift times (user preferences or defaults)."""
        result = {}
        for shift_type, default_config in self.default_times.items():
            if shift_type in self.user_times:
                # Merge user times with default structure
                result[shift_type] = {**default_config, **self.user_times[shift_type]}
            else:
                result[shift_type] = default_config.copy()
        return result
    
    def get_shift_times_display(self) -> str:
        """Generate formatted shift times display text."""
        current_times = self.get_shift_times()
        lines = []
        for shift_type, config in current_times.items():
            lines.append(f"• {config['emoji']} {config['name']}: {config['start']}-{config['end']}")
        return "\n".join(lines)
    
    def update_shift_time(self, shift_type: str, start_time: str = None, end_time: str = None) -> bool:
        """Update shift time for a specific shift type."""
        if shift_type not in self.default_times:
            return False
        
        if not self._validate_time_format(start_time) or not self._validate_time_format(end_time):
            return False
        
        if shift_type not in self.user_times:
            self.user_times[shift_type] = {}
        
        if start_time:
            self.user_times[shift_type]["start"] = start_time
        if end_time:
            self.user_times[shift_type]["end"] = end_time
        
        self._save_user_times()
        return True
    
    def reset_shift_times(self):
        """Reset all shift times to defaults."""
        self.user_times = {}
        self._save_user_times()
    
    def reset_shift_time(self, shift_type: str):
        """Reset specific shift type to default."""
        if shift_type in self.user_times:
            del self.user_times[shift_type]
            self._save_user_times()
    
    def _validate_time_format(self, time_str: str) -> bool:
        """Validate time format (HH:MM)."""
        if not time_str:
            return True  # Allow None/empty for optional parameters
        
        try:
            datetime.strptime(time_str, "%H:%M")
            return True
        except ValueError:
            return False
    
    def get_shift_duration(self, shift_type: str) -> Optional[float]:
        """Get shift duration in hours."""
        times = self.get_shift_times()
        if shift_type not in times:
            return None
        
        try:
            start = datetime.strptime(times[shift_type]["start"], "%H:%M").time()
            end = datetime.strptime(times[shift_type]["end"], "%H:%M").time()
            
            # Handle overnight shifts (like night shift)
            if end < start:
                # Next day
                start_minutes = start.hour * 60 + start.minute
                end_minutes = (end.hour + 24) * 60 + end.minute
            else:
                start_minutes = start.hour * 60 + start.minute
                end_minutes = end.hour * 60 + end.minute
            
            return (end_minutes - start_minutes) / 60
        
        except ValueError:
            return None
    
    def is_time_in_shift(self, check_time: str, shift_type: str) -> bool:
        """Check if a given time falls within a shift window."""
        times = self.get_shift_times()
        if shift_type not in times:
            return False
        
        try:
            check = datetime.strptime(check_time, "%H:%M").time()
            start = datetime.strptime(times[shift_type]["start"], "%H:%M").time()
            end = datetime.strptime(times[shift_type]["end"], "%H:%M").time()
            
            if end < start:  # Overnight shift
                return check >= start or check <= end
            else:
                return start <= check <= end
        
        except ValueError:
            return False
    
    def get_shift_type_for_time(self, check_time: str) -> Optional[str]:
        """Get which shift type a given time belongs to."""
        for shift_type in self.default_times.keys():
            if self.is_time_in_shift(check_time, shift_type):
                return shift_type
        return None

# Global instance for easy access
shift_time_manager = ShiftTimeManager()
