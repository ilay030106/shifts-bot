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
        
        # Define default shift configurations
        self.default_times = {
            "morning": {
                "name": "בוקר",  
                "start": "08:00",
                "end": "16:00",
                "emoji": "🌅"
            },
            "noon": {
                "name": "צהריים",  
                "start": "12:00", 
                "end": "20:00",
                "emoji": "🌇"
            },
            "evening": {
                "name": "ערב",  
                "start": "16:00",
                "end": "00:00",
                "emoji": "🌆"
            }
        }
        
        # Load and initialize user times
        self._initialize_user_times()
    
    def _initialize_user_times(self):
        """Initialize user_times with proper structure."""
        # Start with a copy of default times
        self.user_times = {}
        for shift_type, config in self.default_times.items():
            self.user_times[shift_type] = config.copy()
        
        # Load saved user preferences and override start/end times if valid
        loaded_times = self._load_user_times()
        for shift_type in self.user_times.keys():
            if shift_type in loaded_times:
                saved_config = loaded_times[shift_type]
                if isinstance(saved_config, dict):
                    # Update start time if present and valid
                    if "start" in saved_config and self._validate_time_format(saved_config["start"]):
                        self.user_times[shift_type]["start"] = saved_config["start"]
                    
                    # Update end time if present and valid
                    if "end" in saved_config and self._validate_time_format(saved_config["end"]):
                        self.user_times[shift_type]["end"] = saved_config["end"]
        
        # Save the complete structure to ensure file consistency
        self._save_user_times()
    
    def _load_user_times(self) -> Dict[str, Any]:
        """Load user customized shift times from file."""
        result = {}
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    if isinstance(loaded_data, dict):
                        result = loaded_data
            except (json.JSONDecodeError, FileNotFoundError, Exception):
                # If file is corrupted or unreadable, start fresh
                result = {}
        
        return result
    
    def _save_user_times(self):
        """Save current user_times to file."""
        try:
            # Create a clean version with only the necessary data
            save_data = {}
            for shift_type, config in self.user_times.items():
                save_data[shift_type] = {
                    "name": config["name"],
                    "start": config["start"],
                    "end": config["end"],
                    "emoji": config["emoji"]
                }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving shift times: {e}")
    
    def get_shift_times(self) -> Dict[str, Any]:
        """Get current shift times."""
        return self.user_times
    
    def get_shift_times_display(self) -> str:
        """Generate formatted shift times display text."""
        lines = []
        for config in self.user_times.values():
            line = f"• {config['emoji']} {config['name']}: {config['start']}-{config['end']}"
            lines.append(line)
        return "\n".join(lines)
    
    def update_shift_time(self, shift_type: str, start_time: str = None, end_time: str = None) -> bool:
        """Update shift time for a specific shift type."""
        result = False
        
        if shift_type in self.user_times:
            valid_start = True
            valid_end = True
            
            if start_time is not None:
                valid_start = self._validate_time_format(start_time)
            
            if end_time is not None:
                valid_end = self._validate_time_format(end_time)
            
            if valid_start and valid_end:
                if start_time is not None:
                    self.user_times[shift_type]["start"] = start_time
                
                if end_time is not None:
                    self.user_times[shift_type]["end"] = end_time
                
                self._save_user_times()
                result = True
        
        return result
    
    def reset_shift_times(self):
        """Reset all shift times to defaults."""
        for shift_type, default_config in self.default_times.items():
            self.user_times[shift_type]["start"] = default_config["start"]
            self.user_times[shift_type]["end"] = default_config["end"]
        
        self._save_user_times()
    
    def reset_shift_time(self, shift_type: str):
        """Reset specific shift type to default."""
        if shift_type in self.user_times and shift_type in self.default_times:
            default_config = self.default_times[shift_type]
            self.user_times[shift_type]["start"] = default_config["start"]
            self.user_times[shift_type]["end"] = default_config["end"]
            self._save_user_times()
    
    def _validate_time_format(self, time_str: str) -> bool:
        """Validate time format (HH:MM)."""
        result = True
        
        if time_str is None or time_str == "":
            result = True  # Allow None/empty for optional parameters
        else:
            try:
                datetime.strptime(time_str, "%H:%M")
                result = True
            except ValueError:
                result = False
        
        return result
    
    def get_shift_duration(self, shift_type: str) -> Optional[float]:
        """Get shift duration in hours."""
        result = None
        
        if shift_type in self.user_times:
            try:
                start_str = self.user_times[shift_type]["start"]
                end_str = self.user_times[shift_type]["end"]
                
                start = datetime.strptime(start_str, "%H:%M").time()
                end = datetime.strptime(end_str, "%H:%M").time()
                
                start_minutes = start.hour * 60 + start.minute
                end_minutes = end.hour * 60 + end.minute
                
                # Handle overnight shifts
                if end < start:
                    end_minutes += 24 * 60  # Add 24 hours
                
                result = (end_minutes - start_minutes) / 60.0
                
            except (ValueError, KeyError):
                result = None
        
        return result
    
    def is_time_in_shift(self, check_time: str, shift_type: str) -> bool:
        """Check if a given time falls within a shift window."""
        result = False
        
        if shift_type in self.user_times:
            try:
                check = datetime.strptime(check_time, "%H:%M").time()
                start = datetime.strptime(self.user_times[shift_type]["start"], "%H:%M").time()
                end = datetime.strptime(self.user_times[shift_type]["end"], "%H:%M").time()
                
                if end < start:  # Overnight shift
                    result = check >= start or check <= end
                else:
                    result = start <= check <= end
                    
            except (ValueError, KeyError):
                result = False
        
        return result
    
    def get_shift_type_for_time(self, check_time: str) -> Optional[str]:
        """Get which shift type a given time belongs to."""
        result = None
        
        for shift_type in self.user_times.keys():
            if self.is_time_in_shift(check_time, shift_type):
                result = shift_type
                break  # Found matching shift, no need to continue
        
        return result

# Global instance for easy access
shift_time_manager = ShiftTimeManager()