"""
Timezone Handler - Specialized handler for timezone settings.
Handles timezone selection and configuration.
"""

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError, available_timezones
import logging
from utils import atomic_read_json, atomic_write_json


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
        data = atomic_read_json(self.config_file, default={'timezone': self.default_timezone})
        return data.get('timezone', self.default_timezone)
    
    def _save_timezone(self):
        """Save timezone preference to file."""
        try:
            atomic_write_json(self.config_file, {'timezone': self.user_timezone})
        except Exception:
            logging.getLogger(__name__).exception("Error saving timezone")
    
    async def can_handle(self, data: str) -> bool:
        """Check if this handler can process the given callback data."""
        return data.startswith("edit_timezone") or data.startswith("set_timezone_") or data.startswith("timezone_page_") or data in [
            "settings_timezone", "show_common_timezones", "reset_timezone", "show_all_timezones"
        ]
    
    async def handle_callback(self, query, data: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Handle timezone callback actions."""
        logging.getLogger(__name__).debug("TimezoneHandler: Received callback data: %s", data)
        if data == "settings_timezone":
            logging.getLogger(__name__).debug("Handling settings_timezone")
            await self._show_timezone_menu(query, context)
            return True
        
        elif data == "edit_timezone":
            logging.getLogger(__name__).debug("Handling edit_timezone")
            await self._show_timezone_menu(query, context)
            return True
        
        elif data == "show_common_timezones":
            await self._show_common_timezones(query, context)
            return True
        
        elif data == "show_all_timezones":
            # Reset to first page when opening the menu
            context.user_data['timezone_page'] = 0
            await self._show_all_timezones(query, context)
            return True
        
        elif data.startswith("set_timezone_"):
            timezone = data.replace("set_timezone_", "").replace("_", "/")
            await self._set_timezone(query, timezone, context)
            return True
        
        elif data.startswith("timezone_page_"):
            page_num = int(data.replace("timezone_page_", ""))
            context.user_data['timezone_page'] = page_num
            await self._show_all_timezones(query, context)
            return True
        
        elif data == "reset_timezone":
            await self.reset_timezone(query, context)
            return True
    
    async def _show_timezone_menu(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Show the timezone configuration menu."""
        current_tz = ZoneInfo(self.user_timezone)
        current_time = datetime.now(current_tz).strftime("%H:%M")
        display_name = self.common_timezones.get(self.user_timezone, self.user_timezone)
        
        # Set timezone config mode for text input
        context.user_data['timezone_config_mode'] = True
        
        buttons = [
            self.telegram_client.inline_buttons_row([
                ("🌍 אזורי זמן נפוצים", "show_common_timezones"),
                ("🗺️ כל אזורי הזמן", "show_all_timezones")
            ]),
            self.telegram_client.inline_buttons_row([
                ("↩️ איפוס לברירת מחדל", "reset_timezone"),
                ("🔙 חזרה להעדפות", "preferences_menu")
            ])
        ]
        
        await query.edit_message_text(
            f"🕐 <b>הגדרות אזור זמן</b>\n\n"
            f"אזור זמן נוכחי: {display_name}\n"
            f"שעה נוכחית: {current_time}\n\n"
            f"בחר פעולה או <b>הקלד אזור זמן</b> (לדוגמה: America/New_York):",
            reply_markup=self.telegram_client.inline_kb(buttons),
            parse_mode=ParseMode.HTML
        )
    
    async def _show_common_timezones(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Show common timezones selection."""
        # Set timezone config mode for text input
        context.user_data['timezone_config_mode'] = True
        
        buttons = []
        
        for tz, display_name in self.common_timezones.items():
            current_mark = "✅ " if tz == self.user_timezone else ""
            callback_data = f"set_timezone_{tz.replace('/', '_')}"
            buttons.append((f"{current_mark}{display_name}", callback_data))
        
        # Group buttons into rows of 2
        button_rows = [buttons[i:i+2] for i in range(0, len(buttons), 2)]
        
        # Convert each row to inline keyboard format
        keyboard_rows = [self.telegram_client.inline_buttons_row(row) for row in button_rows]
        
        # Back button
        keyboard_rows.append(self.telegram_client.inline_buttons_row([("🔙 חזרה", "edit_timezone")]))
        
        await query.edit_message_text(
            f"🌍 <b>אזורי זמן נפוצים</b>\n\n"
            f"בחר אזור זמן או <b>הקלד אזור זמן</b> (לדוגמה: Europe/London):",
            reply_markup=self.telegram_client.inline_kb(keyboard_rows),
            parse_mode=ParseMode.HTML
        )
    
    async def _show_all_timezones(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Show paginated list of all timezones."""
        # Set timezone config mode for text input
        context.user_data['timezone_config_mode'] = True
        
        page = context.user_data.get('timezone_page', 0)
        per_page = 8
        
        # available_timezones() returns a set of available tz names
        all_timezones = sorted(available_timezones())
        start_idx = page * per_page
        end_idx = start_idx + per_page
        page_timezones = all_timezones[start_idx:end_idx]
        
        buttons = []
        for tz in page_timezones:
            current_mark = "✅ " if tz == self.user_timezone else ""
            callback_data = f"set_timezone_{tz.replace('/', '_')}"
            display_name = tz.replace('_', ' ')
            buttons.append((f"{current_mark}{display_name}", callback_data))
        
        # Group buttons into rows of 2
        button_rows = [buttons[i:i+2] for i in range(0, len(buttons), 2)]
        
        # Convert each row to inline keyboard format
        keyboard_rows = [self.telegram_client.inline_buttons_row(row) for row in button_rows]
        
        
        # Navigation buttons
        if page > 0 or end_idx < len(all_timezones):
            nav_row = []
            if page > 0:
                nav_row.append(("⬅️ הקודם", f"timezone_page_{page-1}"))
            if end_idx < len(all_timezones):
                nav_row.append(("הבא ➡️", f"timezone_page_{page+1}"))
            if nav_row:
                keyboard_rows.append(self.telegram_client.inline_buttons_row(nav_row))
        
        # Back button
        keyboard_rows.append(self.telegram_client.inline_buttons_row([("🔙 חזרה", "edit_timezone")]))
        
        await query.edit_message_text(
            f"🗺️ <b>כל אזורי הזמן</b>\n\n"
            f"עמוד {page + 1} מתוך {(len(all_timezones) + per_page - 1) // per_page}\n"
            f"בחר אזור זמן או <b>הקלד אזור זמן</b> (לדוגמה: Asia/Tokyo):",
            reply_markup=self.telegram_client.inline_kb(keyboard_rows),
            parse_mode=ParseMode.HTML
        )
    
    async def _set_timezone(self, query, timezone: str, context: ContextTypes.DEFAULT_TYPE):
        """Set the user's timezone."""
        try:
            # Validate timezone
            ZoneInfo(timezone)
            self.user_timezone = timezone
            self._save_timezone()
            
            # Clear timezone config mode
            context.user_data['timezone_config_mode'] = False
            
            display_name = self.common_timezones.get(timezone, timezone)
            current_time = datetime.now(ZoneInfo(timezone)).strftime("%H:%M")
            
            await query.edit_message_text(
                f"✅ <b>אזור זמן עודכן</b>\n\n"
                f"אזור זמן חדש: {display_name}\n"
                f"שעה נוכחית: {current_time}",
                reply_markup=self.telegram_client.inline_kb([
                    [("🔙 חזרה להגדרות זמן", "edit_timezone")]
                ]),
                parse_mode=ParseMode.HTML
            )
        
        except ZoneInfoNotFoundError:
            await query.edit_message_text(
                f"❌ <b>אזור זמן לא תקין</b>\n\n"
                f"אזור הזמן '{timezone}' לא קיים.",
                reply_markup=self.telegram_client.inline_kb([
                    [("🔙 חזרה", "edit_timezone")]
                ]),
                parse_mode=ParseMode.HTML
            )
    
    async def reset_timezone(self, query, context: ContextTypes.DEFAULT_TYPE = None):
        """Reset timezone to default."""
        self.user_timezone = self.default_timezone
        self._save_timezone()
        
        if context:
            # Clear timezone config mode
            context.user_data['timezone_config_mode'] = False
            
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
        tz = ZoneInfo(self.user_timezone)
        return datetime.now(tz).strftime("%H:%M")
    
    async def handle_text_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Handle text input for timezone settings."""
        user_data = context.user_data
        text = update.message.text.strip()
        
        # Check if user is in timezone configuration mode
        if user_data.get('timezone_config_mode'):
            try:
                # Validate timezone
                ZoneInfo(text)

                # Set the timezone
                self.user_timezone = text
                self._save_timezone()

                display_name = self.common_timezones.get(text, text)
                current_time = datetime.now(ZoneInfo(text)).strftime("%H:%M")

                # Clear the config mode
                user_data['timezone_config_mode'] = False

                await update.message.reply_text(
                    f"✅ <b>אזור זמן עודכן</b>\n\n"
                    f"אזור זמן חדש: {display_name}\n"
                    f"שעה נוכחית: {current_time}\n\n"
                    f"הקלד /preferences כדי לחזור להעדפות.",
                    parse_mode=ParseMode.HTML
                )
                return True

            except ZoneInfoNotFoundError:
                await update.message.reply_text(
                    f"❌ <b>אזור זמן לא תקין</b>\n\n"
                    f"אזור הזמן '{text}' לא קיים.\n\n"
                    f"דוגמאות לאזורי זמן תקינים:\n"
                    f"• America/New_York\n"
                    f"• Europe/London\n"
                    f"• Asia/Tokyo\n"
                    f"• Australia/Sydney\n\n"
                    f"נסה שוב או חזור לתפריט הכפתורים.",
                    parse_mode=ParseMode.HTML
                )
                return True
        
        return False
    
    def get_timezone_display(self) -> str:
        """Get formatted timezone display."""
        display_name = self.common_timezones.get(self.user_timezone, self.user_timezone)
        return f"אזור זמן: {display_name}"
