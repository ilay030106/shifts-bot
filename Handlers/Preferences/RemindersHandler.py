"""
Reminders Handler - Specialized handler for reminder settings.
Handles all reminder-related preferences and configuration.
"""

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
import json
import os


class RemindersHandler:
    """Handles all reminder-related preferences."""
    
    def __init__(self, telegram_client):
        self.telegram_client = telegram_client
        self.config_file = "user_reminders.json"
        self.default_reminders = {
            "before_shift": [30, 15],  # Minutes before shift
            "enabled": True,
            "sound_enabled": True
        }
        self.user_reminders = self._load_reminders()
    
    def _load_reminders(self):
        """Load user reminder preferences."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        return self.default_reminders.copy()
    
    def _save_reminders(self):
        """Save reminder preferences to file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_reminders, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving reminders: {e}")
    
    async def can_handle(self, data: str) -> bool:
        """Check if this handler can process the given callback data."""
        return data.startswith("edit_reminders") or data in [
            "toggle_reminders", "add_reminder", "remove_reminder", 
            "toggle_sound", "reset_reminders"
        ]
    
    async def handle_callback(self, query, data: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Handle reminder callback actions."""
        
        if data == "edit_reminders":
            await self._show_reminders_menu(query)
            return True
        
        elif data == "toggle_reminders":
            await self._toggle_reminders(query)
            return True
        
        elif data == "toggle_sound":
            await self._toggle_sound(query)
            return True
        
        elif data == "add_reminder":
            await self._show_add_reminder_menu(query, context)
            return True
        
        elif data.startswith("remove_reminder_"):
            minutes = int(data.replace("remove_reminder_", ""))
            await self._remove_reminder(query, minutes)
            return True
        
        elif data == "reset_reminders":
            await self._reset_reminders(query)
            return True
        
        return False
    
    async def _show_reminders_menu(self, query):
        """Show the reminders configuration menu."""
        reminders_list = ", ".join([f"{m} דק'" for m in self.user_reminders["before_shift"]])
        status = "פעיל" if self.user_reminders["enabled"] else "כבוי"
        sound_status = "פעיל" if self.user_reminders["sound_enabled"] else "כבוי"
        
        buttons = [
            [
                ("🔔 הפעל/כבה התראות", "toggle_reminders"),
                ("🔊 הפעל/כבה צליל", "toggle_sound")
            ],
            [
                ("➕ הוסף התראה", "add_reminder"),
                ("🗑️ הסר התראות", "show_remove_reminders")
            ],
            [
                ("↩️ איפוס לברירת מחדל", "reset_reminders"),
                ("🔙 חזרה להעדפות", "settings_reminders")
            ]
        ]
        
        await query.edit_message_text(
            f"🔔 <b>הגדרות התראות</b>\n\n"
            f"סטטוס: {status}\n"
            f"צליל: {sound_status}\n"
            f"התראות: {reminders_list or 'אין'}\n\n"
            f"בחר פעולה:",
            reply_markup=self.telegram_client.inline_kb(buttons),
            parse_mode=ParseMode.HTML
        )
    
    async def _toggle_reminders(self, query):
        """Toggle reminders on/off."""
        self.user_reminders["enabled"] = not self.user_reminders["enabled"]
        self._save_reminders()
        
        status = "הופעלו" if self.user_reminders["enabled"] else "כובו"
        await query.edit_message_text(
            f"🔔 <b>התראות {status}</b>",
            reply_markup=self.telegram_client.inline_kb([
                [("🔙 חזרה", "edit_reminders")]
            ]),
            parse_mode=ParseMode.HTML
        )
    
    async def _toggle_sound(self, query):
        """Toggle sound on/off."""
        self.user_reminders["sound_enabled"] = not self.user_reminders["sound_enabled"]
        self._save_reminders()
        
        status = "הופעל" if self.user_reminders["sound_enabled"] else "כובה"
        await query.edit_message_text(
            f"🔊 <b>צליל התראות {status}</b>",
            reply_markup=self.telegram_client.inline_kb([
                [("🔙 חזרה", "edit_reminders")]
            ]),
            parse_mode=ParseMode.HTML
        )
    
    async def _show_add_reminder_menu(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Show menu to add new reminder."""
        buttons = [
            [("5 דקות", "add_reminder_5"), ("10 דקות", "add_reminder_10")],
            [("15 דקות", "add_reminder_15"), ("30 דקות", "add_reminder_30")],
            [("60 דקות", "add_reminder_60"), ("מותאם אישית", "add_custom_reminder")],
            [("🔙 חזרה", "edit_reminders")]
        ]
        
        await query.edit_message_text(
            f"⏰ <b>הוסף התראה חדשה</b>\n\n"
            f"בחר כמה דקות לפני המשמרת:",
            reply_markup=self.telegram_client.inline_kb(buttons),
            parse_mode=ParseMode.HTML
        )
    
    async def _remove_reminder(self, query, minutes: int):
        """Remove a specific reminder."""
        if minutes in self.user_reminders["before_shift"]:
            self.user_reminders["before_shift"].remove(minutes)
            self._save_reminders()
            
            await query.edit_message_text(
                f"✅ <b>התראה של {minutes} דקות הוסרה</b>",
                reply_markup=self.telegram_client.inline_kb([
                    [("🔙 חזרה", "edit_reminders")]
                ]),
                parse_mode=ParseMode.HTML
            )
        else:
            await query.edit_message_text(
                f"❌ התראה של {minutes} דקות לא נמצאה",
                reply_markup=self.telegram_client.inline_kb([
                    [("🔙 חזרה", "edit_reminders")]
                ]),
                parse_mode=ParseMode.HTML
            )
    
    async def _reset_reminders(self, query):
        """Reset reminders to defaults."""
        self.user_reminders = self.default_reminders.copy()
        self._save_reminders()
        
        await query.edit_message_text(
            f"↩️ <b>התראות אופסו לברירת המחדל</b>\n\n"
            f"התראות: 30, 15 דקות לפני המשמרת",
            reply_markup=self.telegram_client.inline_kb([
                [("🔙 חזרה", "edit_reminders")]
            ]),
            parse_mode=ParseMode.HTML
        )
    
    def get_reminders_display(self) -> str:
        """Get formatted reminders display."""
        if not self.user_reminders["enabled"]:
            return "התראות: כבויות"
        
        reminders = ", ".join([f"{m} דק'" for m in sorted(self.user_reminders["before_shift"], reverse=True)])
        return f"התראות: {reminders or 'אין'}"
