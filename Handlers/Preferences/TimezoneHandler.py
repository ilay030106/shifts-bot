"""
Timezone Handler - Specialized handler for timezone settings.
Handles timezone selection and configuration.
"""

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
import json
import os
from datetime import datetime
import pytz


class TimezoneHandler:
    """Handles timezone-related preferences."""
    
    def __init__(self, telegram_client):
        self.telegram_client = telegram_client
        self.config_file = "user_timezone.json"
        self.default_timezone = "Asia/Jerusalem"
        self.user_timezone = self._load_timezone()
        
        # Common timezones for Israel region
        self.common_timezones = {
            "Asia/Jerusalem": "ירושלים (ישראל)",
            "Europe/London": "לונדון (GMT)",
            "Europe/Paris": "פריז (CET)",
            "America/New_York": "ניו יורק (EST)",
            "America/Los_Angeles": "לוס אנג'לס (PST)",
            "Asia/Dubai": "דובאי (GST)",
            "Asia/Tokyo": "טוקיו (JST)"
        }
    
    def _load_timezone(self):
        """Load user timezone preference."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('timezone', self.default_timezone)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        return self.default_timezone
    
    def _save_timezone(self):
        """Save timezone preference to file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump({'timezone': self.user_timezone}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving timezone: {e}")
    
    async def can_handle(self, data: str) -> bool:
        """Check if this handler can process the given callback data."""
        return data.startswith("edit_timezone") or data.startswith("set_timezone_") or data in [
            "show_common_timezones", "reset_timezone", "show_all_timezones"
        ]
    
    async def handle_callback(self, query, data: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Handle timezone callback actions."""
        
        if data == "edit_timezone":
            await self._show_timezone_menu(query)
            return True
        
        elif data == "show_common_timezones":
            await self._show_common_timezones(query)
            return True
        
        elif data == "show_all_timezones":
            await self._show_all_timezones(query, context)
            return True
        
        elif data.startswith("set_timezone_"):
            timezone = data.replace("set_timezone_", "").replace("_", "/")
            await self._set_timezone(query, timezone)
            return True
        
        elif data == "reset_timezone":
            await self._reset_timezone(query)
            return True
        
        return False
    
    async def _show_timezone_menu(self, query):
        """Show the timezone configuration menu."""
        current_tz = pytz.timezone(self.user_timezone)
        current_time = datetime.now(current_tz).strftime("%H:%M")
        display_name = self.common_timezones.get(self.user_timezone, self.user_timezone)
        
        buttons = [
            [
                ("🌍 אזורי זמן נפוצים", "show_common_timezones"),
                ("🗺️ כל אזורי הזמן", "show_all_timezones")
            ],
            [
                ("↩️ איפוס לברירת מחדל", "reset_timezone"),
                ("🔙 חזרה להעדפות", "settings_timezone")
            ]
        ]
        
        await query.edit_message_text(
            f"🕐 <b>הגדרות אזור זמן</b>\n\n"
            f"אזור זמן נוכחי: {display_name}\n"
            f"שעה נוכחית: {current_time}\n\n"
            f"בחר פעולה:",
            reply_markup=self.telegram_client.inline_kb(buttons),
            parse_mode=ParseMode.HTML
        )
    
    async def _show_common_timezones(self, query):
        """Show common timezones selection."""
        buttons = []
        
        for tz, display_name in self.common_timezones.items():
            current_mark = "✅ " if tz == self.user_timezone else ""
            callback_data = f"set_timezone_{tz.replace('/', '_')}"
            buttons.append([(f"{current_mark}{display_name}", callback_data)])
        
        buttons.append([("🔙 חזרה", "edit_timezone")])
        
        await query.edit_message_text(
            f"🌍 <b>אזורי זמן נפוצים</b>\n\n"
            f"בחר אזור זמן:",
            reply_markup=self.telegram_client.inline_kb(buttons),
            parse_mode=ParseMode.HTML
        )
    
    async def _show_all_timezones(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Show paginated list of all timezones."""
        page = context.user_data.get('timezone_page', 0)
        per_page = 8
        
        all_timezones = sorted(pytz.common_timezones)
        start_idx = page * per_page
        end_idx = start_idx + per_page
        page_timezones = all_timezones[start_idx:end_idx]
        
        buttons = []
        for tz in page_timezones:
            current_mark = "✅ " if tz == self.user_timezone else ""
            callback_data = f"set_timezone_{tz.replace('/', '_')}"
            display_name = tz.replace('_', ' ')
            buttons.append([(f"{current_mark}{display_name}", callback_data)])
        
        # Navigation buttons
        nav_buttons = []
        if page > 0:
            nav_buttons.append(("⬅️ הקודם", f"timezone_page_{page-1}"))
        if end_idx < len(all_timezones):
            nav_buttons.append(("הבא ➡️", f"timezone_page_{page+1}"))
        
        if nav_buttons:
            buttons.append(nav_buttons)
        
        buttons.append([("🔙 חזרה", "edit_timezone")])
        
        await query.edit_message_text(
            f"🗺️ <b>כל אזורי הזמן</b>\n\n"
            f"עמוד {page + 1} מתוך {(len(all_timezones) + per_page - 1) // per_page}\n"
            f"בחר אזור זמן:",
            reply_markup=self.telegram_client.inline_kb(buttons),
            parse_mode=ParseMode.HTML
        )
    
    async def _set_timezone(self, query, timezone: str):
        """Set the user's timezone."""
        try:
            # Validate timezone
            pytz.timezone(timezone)
            self.user_timezone = timezone
            self._save_timezone()
            
            display_name = self.common_timezones.get(timezone, timezone)
            current_time = datetime.now(pytz.timezone(timezone)).strftime("%H:%M")
            
            await query.edit_message_text(
                f"✅ <b>אזור זמן עודכן</b>\n\n"
                f"אזור זמן חדש: {display_name}\n"
                f"שעה נוכחית: {current_time}",
                reply_markup=self.telegram_client.inline_kb([
                    [("🔙 חזרה להגדרות זמן", "edit_timezone")]
                ]),
                parse_mode=ParseMode.HTML
            )
        
        except pytz.UnknownTimeZoneError:
            await query.edit_message_text(
                f"❌ <b>אזור זמן לא תקין</b>\n\n"
                f"אזור הזמן '{timezone}' לא קיים.",
                reply_markup=self.telegram_client.inline_kb([
                    [("🔙 חזרה", "edit_timezone")]
                ]),
                parse_mode=ParseMode.HTML
            )
    
    async def _reset_timezone(self, query):
        """Reset timezone to default."""
        self.user_timezone = self.default_timezone
        self._save_timezone()
        
        display_name = self.common_timezones[self.default_timezone]
        
        await query.edit_message_text(
            f"↩️ <b>אזור זמן אופס</b>\n\n"
            f"אזור זמן: {display_name}",
            reply_markup=self.telegram_client.inline_kb([
                [("🔙 חזרה", "edit_timezone")]
            ]),
            parse_mode=ParseMode.HTML
        )
    
    def get_current_timezone(self) -> str:
        """Get current timezone string."""
        return self.user_timezone
    
    def get_current_time(self) -> str:
        """Get current time in user's timezone."""
        tz = pytz.timezone(self.user_timezone)
        return datetime.now(tz).strftime("%H:%M")
    
    async def handle_text_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Handle text input for timezone settings."""
        # Placeholder - implement as needed for timezone text input
        return False
    
    def get_timezone_display(self) -> str:
        """Get formatted timezone display."""
        display_name = self.common_timezones.get(self.user_timezone, self.user_timezone)
        return f"אזור זמן: {display_name}"
