"""
Shift Times Handler - Specialized handler for shift time management.
Handles all shift time related actions and operations.
"""

from Config.shift_times import shift_time_manager
from Config.menus import MENU_CONFIGS
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode


class ShiftTimesHandler:
    """Handles all shift time related operations and actions."""
    
    def __init__(self, telegram_client):
        self.telegram_client = telegram_client
        self.shift_manager = shift_time_manager
    
    async def can_handle(self, data: str) -> bool:
        """Check if this handler can process the given callback data."""
        shift_time_actions = [
            "edit_shift_times", "edit_morning_shift", "edit_afternoon_shift", 
            "edit_night_shift", "reset_shift_times"
        ]
        
        return (
            data in shift_time_actions or
            data.startswith(("edit_start_", "edit_end_", "save_shift_", "cancel_edit_"))
        )
    
    async def handle_callback(self, query, data: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Handle shift time callback actions."""
        
        # Main shift time editing menu
        if data == "edit_shift_times":
            await self._show_shift_times_menu(query)
            return True
        
        # Individual shift editing menus
        elif data in ["edit_morning_shift", "edit_afternoon_shift", "edit_night_shift"]:
            shift_type = data.replace("edit_", "").replace("_shift", "")
            await self._show_individual_shift_menu(query, shift_type)
            return True
        
        # Edit specific time components
        elif data.startswith("edit_start_"):
            shift_type = data.replace("edit_start_", "")
            await self._handle_edit_start_time(query, shift_type, context)
            return True
        
        elif data.startswith("edit_end_"):
            shift_type = data.replace("edit_end_", "")
            await self._handle_edit_end_time(query, shift_type, context)
            return True
        
        # Save/Cancel actions
        elif data.startswith("save_shift_"):
            shift_type = data.replace("save_shift_", "")
            await self._handle_save_shift(query, shift_type, context)
            return True
        
        elif data.startswith("cancel_edit_"):
            shift_type = data.replace("cancel_edit_", "")
            await self._handle_cancel_edit(query, shift_type)
            return True
        
        # Reset all shift times
        elif data == "reset_shift_times":
            await self._handle_reset_all_times(query)
            return True
        
        return False  # Action not handled by this handler
    
    async def handle_text_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Handle text input for shift time editing."""
        
        waiting_for = context.user_data.get('waiting_for')
        
        if not waiting_for or not waiting_for.startswith(('start_time_', 'end_time_')):
            return False

        time_input = update.message.text.strip()
        
        # Validate time format
        if not self._validate_time_format(time_input):
            await update.message.reply_text(
                "❌ פורמט שעה לא תקין!\n\n"
                "השתמש בפורמט HH:MM (לדוגמה: 08:30)",
                reply_markup=self.telegram_client.inline_kb([
                    self.telegram_client.inline_buttons_row([("❌ ביטול", "edit_shift_times")])
                ])
            )
            return True

        # Parse the waiting action
        if waiting_for.startswith('start_time_'):
            shift_type = waiting_for.replace('start_time_', '')
            field = 'start'
        else:  # end_time_
            shift_type = waiting_for.replace('end_time_', '')
            field = 'end'
        
        # Store pending change
        if 'pending_shift_changes' not in context.user_data:
            context.user_data['pending_shift_changes'] = {}
        if shift_type not in context.user_data['pending_shift_changes']:
            context.user_data['pending_shift_changes'][shift_type] = {}
        
        context.user_data['pending_shift_changes'][shift_type][field] = time_input
        
        # Clear waiting state
        del context.user_data['waiting_for']
        
        # Show confirmation
        await self._show_time_confirmation(update, shift_type, context)
        return True
    
    async def _show_shift_times_menu(self, query):
        """Show the main shift times editing menu."""
        menu_config = MENU_CONFIGS["edit_shift_times"]
        
        # Build proper keyboard
        button_rows = []
        for row in menu_config["buttons"]:
            button_row = self.telegram_client.inline_buttons_row(row)
            button_rows.append(button_row)
        
        await query.edit_message_text(
            menu_config["title"],
            reply_markup=self.telegram_client.inline_kb(button_rows),
            parse_mode=ParseMode.HTML
        )
    
    async def _show_individual_shift_menu(self, query, shift_type: str):
        """Show menu for editing a specific shift."""
        menu_config = MENU_CONFIGS[f"edit_{shift_type}_shift"]()
        
        # Build proper keyboard
        button_rows = []
        for row in menu_config["buttons"]:
            button_row = self.telegram_client.inline_buttons_row(row)
            button_rows.append(button_row)
        
        await query.edit_message_text(
            menu_config["title"],
            reply_markup=self.telegram_client.inline_kb(button_rows),
            parse_mode=ParseMode.HTML
        )
    
    async def _handle_edit_start_time(self, query, shift_type: str, context: ContextTypes.DEFAULT_TYPE):
        """Handle editing start time for a shift."""
        current_times = self.shift_manager.get_shift_times()
        current_start = current_times[shift_type]["start"]
        
        await query.edit_message_text(
            f"⏰ <b>עריכת שעת התחלה - {current_times[shift_type]['name']}</b>\n\n"
            f"שעת התחלה נוכחית: {current_start}\n\n"
            f"שלח שעת התחלה החדשה בפורמט HH:MM\n"
            f"לדוגמה: 08:00",
            reply_markup=self.telegram_client.inline_kb([
                self.telegram_client.inline_buttons_row([("❌ ביטול", f"edit_{shift_type}_shift")])
            ]),
            parse_mode=ParseMode.HTML
        )
        
        # Store the action in context for the next message
        context.user_data['waiting_for'] = f'start_time_{shift_type}'
    
    async def _handle_edit_end_time(self, query, shift_type: str, context: ContextTypes.DEFAULT_TYPE):
        """Handle editing end time for a shift."""
        current_times = self.shift_manager.get_shift_times()
        current_end = current_times[shift_type]["end"]
        
        await query.edit_message_text(
            f"⏰ <b>עריכת שעת סיום - {current_times[shift_type]['name']}</b>\n\n"
            f"שעת סיום נוכחית: {current_end}\n\n"
            f"שלח שעת סיום החדשה בפורמט HH:MM\n"
            f"לדוגמה: 16:00",
            reply_markup=self.telegram_client.inline_kb([
                self.telegram_client.inline_buttons_row([("❌ ביטול", f"edit_{shift_type}_shift")])
            ]),
            parse_mode=ParseMode.HTML
        )
        
        # Store the action in context for the next message
        context.user_data['waiting_for'] = f'end_time_{shift_type}'
    
    async def _handle_save_shift(self, query, shift_type: str, context: ContextTypes.DEFAULT_TYPE):
        """Save the current shift configuration."""
        pending_changes = context.user_data.get('pending_shift_changes', {})
        
        if shift_type in pending_changes:
            changes = pending_changes[shift_type]
            success = self.shift_manager.update_shift_time(
                shift_type,
                changes.get('start'),
                changes.get('end')
            )
            
            if success:
                await query.edit_message_text(
                    f"✅ <b>נשמר בהצלחה!</b>\n\n"
                    f"זמני המשמרת עודכנו:\n"
                    f"{self.shift_manager.get_shift_times_display()}",
                    reply_markup=self.telegram_client.inline_kb([
                        self.telegram_client.inline_buttons_row([("🔙 חזרה לעריכת זמנים", "edit_shift_times")])
                    ]),
                    parse_mode=ParseMode.HTML
                )
            else:
                await query.edit_message_text(
                    f"❌ <b>שגיאה בשמירה</b>\n\n"
                    f"לא הצלחתי לשמור את השינויים.\n"
                    f"נסה שוב.",
                    reply_markup=self.telegram_client.inline_kb([
                        self.telegram_client.inline_buttons_row([("🔄 נסה שוב", f"edit_{shift_type}_shift")])
                    ]),
                    parse_mode=ParseMode.HTML
                )
            
            # Clear pending changes
            if shift_type in pending_changes:
                del pending_changes[shift_type]
        else:
            await query.edit_message_text(
                f"ℹ️ אין שינויים לשמירה.",
                reply_markup=self.telegram_client.inline_kb([
                    [("🔙 חזרה", f"edit_{shift_type}_shift")]
                ]),
                parse_mode=ParseMode.HTML
            )
    
    async def _handle_cancel_edit(self, query, shift_type: str):
        """Cancel editing and return to shift menu."""
        await self._show_individual_shift_menu(query, shift_type)
    
    async def _handle_reset_all_times(self, query):
        """Reset all shift times to defaults."""
        self.shift_manager.reset_shift_times()
        
        await query.edit_message_text(
            f"↩️ <b>זמני משמרות אופסו</b>\n\n"
            f"כל זמני המשמרות חזרו לברירת המחדל:\n\n"
            f"{self.shift_manager.get_shift_times_display()}",
            reply_markup=self.telegram_client.inline_kb([
                self.telegram_client.inline_buttons_row([("🔙 חזרה לעריכת זמנים", "edit_shift_times")])
            ]),
            parse_mode=ParseMode.HTML
        )
    
    async def _show_time_confirmation(self, update: Update, shift_type: str, context: ContextTypes.DEFAULT_TYPE):
        """Show confirmation after time input."""
        
        current_times = self.shift_manager.get_shift_times()
        pending = context.user_data['pending_shift_changes'][shift_type]
        
        new_start = pending.get('start', current_times[shift_type]['start'])
        new_end = pending.get('end', current_times[shift_type]['end'])
        
        confirmation_text = (
            f"✅ <b>זמן עודכן</b>\n\n"
            f"משמרת {current_times[shift_type]['name']}:\n"
            f"{current_times[shift_type]['emoji']} {new_start}-{new_end}\n\n"
            f"שמור את השינויים או המשך לערוך:"
        )
        
        try:
            await update.message.reply_text(
                confirmation_text,
                reply_markup=self.telegram_client.inline_kb([
                    self.telegram_client.inline_buttons_row([
                        ("💾 שמור", f"save_shift_{shift_type}"),
                        ("✏️ המשך עריכה", f"edit_{shift_type}_shift")
                    ]),
                    self.telegram_client.inline_buttons_row([("❌ בטל", f"cancel_edit_{shift_type}")])
                ]),
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            print(f"Error sending confirmation: {e}")
            # Try a simple fallback message
            await update.message.reply_text(f"Time updated to {new_start}-{new_end}")
    
    def _validate_time_format(self, time_str: str) -> bool:
        """Validate time format (HH:MM)."""
        try:
            from datetime import datetime
            datetime.strptime(time_str, "%H:%M")
            return True
        except ValueError:
            return False
    
    def get_shift_times_display(self) -> str:
        """Get formatted shift times display."""
        return self.shift_manager.get_shift_times_display()
    
    def get_shift_duration(self, shift_type: str) -> float:
        """Get shift duration in hours."""
        return self.shift_manager.get_shift_duration(shift_type)
    
    def is_time_in_shift(self, time_str: str, shift_type: str) -> bool:
        """Check if time falls within a shift."""
        return self.shift_manager.is_time_in_shift(time_str, shift_type)
    
    async def reset_all_shift_times(self, query):
        """Reset all shift times to defaults - used by PreferencesHandler."""
        self.shift_manager.reset_shift_times()
        
        await query.edit_message_text(
            f"↩️ <b>זמני משמרות אופסו</b>\n\n"
            f"כל זמני המשמרות חזרו לברירת המחדל:\n\n"
            f"{self.shift_manager.get_shift_times_display()}",
            reply_markup=self.telegram_client.inline_kb([
                self.telegram_client.inline_buttons_row([("🔙 חזרה להעדפות", "preferences_menu")])
            ]),
            parse_mode=ParseMode.HTML
        )
    
    def get_shift_times_summary(self) -> str:
        """Get a formatted summary of current shift times."""
        return self.shift_manager.get_shift_times_display()
