"""
Reminders Handler - Specialized handler for reminder settings.
Handles all reminder-related preferences and configuration.
"""

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
import os
import logging
from utils import atomic_read_json, atomic_write_json


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
        data = atomic_read_json(self.config_file, default=None)
        if data is None:
            return self.default_reminders.copy()
        return data
    
    def _save_reminders(self):
        """Save reminder preferences to file."""
        try:
            atomic_write_json(self.config_file, self.user_reminders)
        except Exception as e:
            logging.getLogger(__name__).exception("Error saving reminders: %s", e)
    
    async def can_handle(self, data: str) -> bool:
        """Check if this handler can process the given callback data."""
        return data.startswith("edit_reminders") or data.startswith("add_reminder_") or data.startswith("remove_reminder_") or data in [
            "toggle_reminders", "add_reminder", "remove_reminder", "show_remove_reminders",
            "toggle_sound", "reset_reminders", "add_custom_reminder"
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
        
        elif data.startswith("add_reminder_"):
            minutes = int(data.replace("add_reminder_", ""))
            await self._add_reminder(query, minutes)
            return True
        
        elif data == "show_remove_reminders":
            await self._show_remove_reminders_menu(query)
            return True
        
        elif data == "add_custom_reminder":
            await self._show_custom_reminder_input(query, context)
            return True
        
        elif data.startswith("remove_reminder_"):
            minutes = int(data.replace("remove_reminder_", ""))
            await self._remove_reminder(query, minutes)
            return True
        
        elif data == "reset_reminders":
            await self._reset_reminders(query)
            return True
    
    async def _show_reminders_menu(self, query):
        """Show the reminders configuration menu."""
        formatted_reminders = [self._format_time(m) for m in self.user_reminders["before_shift"]]
        reminders_list = ", ".join(formatted_reminders) if formatted_reminders else "אין התראות"
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
    
    async def _add_reminder(self, query, minutes: int):
        """Add a new reminder."""
        if minutes not in self.user_reminders["before_shift"]:
            self.user_reminders["before_shift"].append(minutes)
            self.user_reminders["before_shift"].sort()
            self._save_reminders()
            
            await query.edit_message_text(
                f"✅ <b>התראה של {minutes} דקות נוספה</b>",
                reply_markup=self.telegram_client.inline_kb([
                    [("🔙 חזרה", "edit_reminders")]
                ]),
                parse_mode=ParseMode.HTML
            )
        else:
            await query.edit_message_text(
                f"⚠️ התראה של {minutes} דקות כבר קיימת",
                reply_markup=self.telegram_client.inline_kb([
                    [("🔙 חזרה", "edit_reminders")]
                ]),
                parse_mode=ParseMode.HTML
            )
    
    async def _show_remove_reminders_menu(self, query):
        """Show menu to remove existing reminders."""
        if not self.user_reminders["before_shift"]:
            await query.edit_message_text(
                f"❌ <b>אין התראות להסרה</b>\n\n"
                f"אין התראות מוגדרות כרגע.",
                reply_markup=self.telegram_client.inline_kb([
                    [("🔙 חזרה", "edit_reminders")]
                ]),
                parse_mode=ParseMode.HTML
            )
            return
        
        buttons = []
        for minutes in self.user_reminders["before_shift"]:
            formatted_time = self._format_time(minutes)
            buttons.append((f"🗑️ הסר: {formatted_time}", f"remove_reminder_{minutes}"))
        
        # Group buttons into rows of 2
        button_rows = [buttons[i:i+2] for i in range(0, len(buttons), 2)]
        
        # Convert each row to inline keyboard format
        keyboard_rows = [self.telegram_client.inline_buttons_row(row) for row in button_rows]
        
        # Back button
        keyboard_rows.append(self.telegram_client.inline_buttons_row([("🔙 חזרה", "edit_reminders")]))
        
        await query.edit_message_text(
            f"🗑️ <b>הסר התראות</b>\n\n"
            f"בחר איזו התראה להסיר:",
            reply_markup=self.telegram_client.inline_kb(keyboard_rows),
            parse_mode=ParseMode.HTML
        )
    
    async def _show_custom_reminder_input(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Show input prompt for custom reminder time."""
        # Set waiting_for to indicate custom reminder input mode
        context.user_data['waiting_for'] = 'reminder_custom'
        
        await query.edit_message_text(
            f"⏰ <b>התראה מותאמת אישית</b>\n\n"
            f"הקלד זמן התראה או 'ביטול' כדי לחזור:\n\n"
            f"פורמטים נתמכים:\n"
            f"• דקות: 45, 120m, 2h\n"
            f"• שעות: 5h, 12h\n"
            f"• ימים: 2d, 7d\n\n"
            f"דוגמאות:\n"
            f"• 30 - 30 דקות לפני\n"
            f"• 2h - 2 שעות לפני\n"
            f"• 3d - 3 ימים לפני\n"
            f"• ביטול - חזרה לתפריט",
            reply_markup=self.telegram_client.inline_kb([
                [("🔙 חזרה", "edit_reminders")]
            ]),
            parse_mode=ParseMode.HTML
        )
    
    async def _remove_reminder(self, query, minutes: int):
        """Remove a specific reminder."""
        if minutes in self.user_reminders["before_shift"]:
            self.user_reminders["before_shift"].remove(minutes)
            self._save_reminders()
            
            formatted_time = self._format_time(minutes)
            await query.edit_message_text(
                f"✅ <b>התראה של {formatted_time} הוסרה</b>",
                reply_markup=self.telegram_client.inline_kb([
                    [("🔙 חזרה", "edit_reminders")]
                ]),
                parse_mode=ParseMode.HTML
            )
        else:
            formatted_time = self._format_time(minutes)
            await query.edit_message_text(
                f"❌ התראה של {formatted_time} לא נמצאה",
                reply_markup=self.telegram_client.inline_kb([
                    [("🔙 חזרה", "edit_reminders")]
                ]),
                parse_mode=ParseMode.HTML
            )
    
    async def _reset_reminders(self, query):
        """Reset reminders to defaults."""
        import copy
        self.user_reminders = copy.deepcopy(self.default_reminders)
        logging.getLogger(__name__).debug("Resetting reminders to: %s", self.user_reminders)
        self._save_reminders()
        
        formatted_defaults = [self._format_time(m) for m in self.default_reminders["before_shift"]]
        defaults_list = ", ".join(formatted_defaults)
        
        await query.edit_message_text(
            f"↩️ <b>התראות אופסו לברירת המחדל</b>\n\n"
            f"התראות: {defaults_list}",
            reply_markup=self.telegram_client.inline_kb([
                [("🔙 חזרה", "edit_reminders")]
            ]),
            parse_mode=ParseMode.HTML
        )
    
    async def reset_all_reminders(self, query=None):
        """Reset reminders to defaults without showing message (for reset all)."""
        import copy
        self.user_reminders = copy.deepcopy(self.default_reminders)
        self._save_reminders()
        logging.getLogger(__name__).debug("Reset all reminders to: %s", self.user_reminders)
    
    async def handle_text_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Handle text input for reminder settings."""
        user_data = context.user_data
        text = update.message.text.strip().lower()
        
        # Check if user is in custom reminder input mode
        if user_data.get('waiting_for') == 'reminder_custom':
            # Clear the waiting_for
            user_data['waiting_for'] = None
            
            if text == 'ביטול' or text == 'cancel':
                await update.message.reply_text(
                    f"❌ <b>בוטל</b>\n\n"
                    f"הקלד /preferences כדי לחזור להעדפות.",
                    parse_mode=ParseMode.HTML
                )
                return True
            
            try:
                # Parse the time input
                minutes = self._parse_time_input(text)
                
                # Validate range (1 minute to 30 days)
                if minutes < 1 or minutes > 43200:  # 30 days max
                    await update.message.reply_text(
                        f"❌ <b>זמן לא תקין</b>\n\n"
                        f"זמן התראה חייב להיות בין דקה אחת ל-30 ימים.\n\n"
                        f"הקלד /preferences כדי לחזור להעדפות.",
                        parse_mode=ParseMode.HTML
                    )
                    return True
                
                # Check if reminder already exists
                if minutes in self.user_reminders["before_shift"]:
                    formatted_time = self._format_time(minutes)
                    await update.message.reply_text(
                        f"⚠️ <b>התראה כבר קיימת</b>\n\n"
                        f"התראה של {formatted_time} כבר מוגדרת.\n\n"
                        f"הקלד /preferences כדי לחזור להעדפות.",
                        parse_mode=ParseMode.HTML
                    )
                    return True
                
                # Add the reminder
                self.user_reminders["before_shift"].append(minutes)
                self.user_reminders["before_shift"].sort()
                self._save_reminders()
                
                formatted_time = self._format_time(minutes)
                await update.message.reply_text(
                    f"✅ <b>התראה נוספה בהצלחה</b>\n\n"
                    f"התראה חדשה: {formatted_time} לפני המשמרת\n\n"
                    f"הקלד /preferences כדי לחזור להעדפות.",
                    parse_mode=ParseMode.HTML
                )
                return True
                
            except ValueError:
                await update.message.reply_text(
                    f"❌ <b>קלט לא תקין</b>\n\n"
                    f"אנא הקלד מספר דקות תקין (1-1440):\n\n"
                    f"דוגמאות:\n"
                    f"• 45 - התראה 45 דקות לפני\n"
                    f"• 120 - התראה 2 שעות לפני\n\n"
                    f"הקלד /preferences כדי לחזור להעדפות.",
                    parse_mode=ParseMode.HTML
                )
                return True
        
        return False
    
    async def _remove_reminder(self, query, minutes: int):
        """Remove a reminder time."""
        if minutes in self.user_reminders["before_shift"]:
            self.user_reminders["before_shift"].remove(minutes)
            self._save_reminders()
            
            await query.edit_message_text(
                f"✅ <b>התראה הוסרה</b>\n\n"
                f"התראה של {self._format_time(minutes)} לפני המשמרת הוסרה בהצלחה.",
                reply_markup=self.telegram_client.inline_kb([
                    [("🔙 חזרה להגדרות התראות", "edit_reminders")]
                ]),
                parse_mode=ParseMode.HTML
            )
        else:
            await query.edit_message_text(
                f"❌ <b>שגיאה</b>\n\n"
                f"התראה של {minutes} דקות לא נמצאה.",
                reply_markup=self.telegram_client.inline_kb([
                    [("🔙 חזרה להגדרות התראות", "edit_reminders")]
                ]),
                parse_mode=ParseMode.HTML
            )
    
        return False
    
    def _parse_time_input(self, text: str) -> int:
        """Parse time input in various formats and return minutes.
        
        Supported formats:
        - "45" or "45m" -> 45 minutes
        - "2h" -> 120 minutes
        - "3d" -> 4320 minutes
        """
        text = text.strip().lower()
        
        # Handle days
        if text.endswith('d') or 'days' in text or 'יום' in text or 'ימים' in text:
            if text.endswith('d'):
                num = int(text[:-1])
            elif 'days' in text:
                num = int(text.replace('days', '').strip())
            elif 'יום' in text:
                num = int(text.replace('יום', '').strip())
            elif 'ימים' in text:
                num = int(text.replace('ימים', '').strip())
            else:
                raise ValueError("Invalid days format")
            return num * 24 * 60  # Convert days to minutes
        
        # Handle hours
        if text.endswith('h') or 'hours' in text or 'שעות' in text or 'שעה' in text:
            if text.endswith('h'):
                num = int(text[:-1])
            elif 'hours' in text:
                num = int(text.replace('hours', '').strip())
            elif 'שעות' in text:
                num = int(text.replace('שעות', '').strip())
            elif 'שעה' in text:
                num = int(text.replace('שעה', '').strip())
            else:
                raise ValueError("Invalid hours format")
            return num * 60  # Convert hours to minutes
        
        # Handle minutes (default)
        if text.endswith('m') or 'minutes' in text or 'דקות' in text or 'דקה' in text:
            if text.endswith('m'):
                num = int(text[:-1])
            elif 'minutes' in text:
                num = int(text.replace('minutes', '').strip())
            elif 'דקות' in text:
                num = int(text.replace('דקות', '').strip())
            elif 'דקה' in text:
                num = int(text.replace('דקה', '').strip())
            else:
                raise ValueError("Invalid minutes format")
        else:
            # Assume plain number is minutes
            num = int(text)
        
        return num
    
    def _format_time(self, minutes: int) -> str:
        """Format minutes into human-readable time string."""
        if minutes >= 1440:  # 24 hours or more
            days = minutes // 1440
            return f"לפני {days} ימים" if days > 1 else f"לפני {days} יום"
        elif minutes >= 60:  # 1 hour or more
            hours = minutes // 60
            return f"לפני {hours} שעות" if hours > 1 else f"לפני {hours} שעה"
        else:  # less than 1 hour
            return f"לפני {minutes} דקות"
    
    def get_reminders_display(self) -> str:
        """Get formatted reminders display."""
        if not self.user_reminders["enabled"]:
            return "התראות: כבויות"
        
        formatted_reminders = [self._format_time(m) for m in sorted(self.user_reminders["before_shift"], reverse=True)]
        reminders = ", ".join(formatted_reminders)
        return f"התראות: {reminders or 'אין'}"
