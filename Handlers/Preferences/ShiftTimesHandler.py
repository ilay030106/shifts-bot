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
            "edit_shift_times", "edit_morning_shift", "edit_noon_shift", 
            "edit_evening_shift", "reset_shift_times"
        ]
        
        return (
            data in shift_time_actions or
            data.startswith(("edit_times_", "edit_start_", "edit_end_", "save_shift_", "cancel_edit_"))
        )
    
    async def handle_callback(self, query, data: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Handle shift time callback actions."""
        
        # Main shift time editing menu
        if data == "edit_shift_times":
            await self._show_shift_times_menu(query)
            return True
        
        # Individual shift editing menus
        elif data in ["edit_morning_shift", "edit_noon_shift", "edit_evening_shift"]:
            shift_type = data.replace("edit_", "").replace("_shift", "")
            await self._show_combined_shift_editor(query, shift_type, context)
            return True
        
        # Edit specific time components
        elif data.startswith("edit_times_"):
            shift_type = data.replace("edit_times_", "")
            await self._show_combined_shift_editor(query, shift_type, context)
            return True
        
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
            await self._handle_cancel_edit(query, shift_type, context)
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
            # Extract shift type from waiting_for
            if waiting_for.startswith('start_time_'):
                shift_type = waiting_for.replace('start_time_', '')
            else:
                shift_type = waiting_for.replace('end_time_', '')
                
            await update.message.reply_text(
                "❌ פורמט שעה לא תקין!\n\n"
                "השתמש בפורמט HH:MM (לדוגמה: 08:30)",
                reply_markup=self.telegram_client.inline_kb([
                    self.telegram_client.inline_buttons_row([
                        ("🔄 נסה שוב", f"edit_times_{shift_type}"),
                        ("❌ ביטול", f"cancel_edit_{shift_type}")
                    ])
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
        
        # Show updated combined editor instead of confirmation
        await self._show_combined_shift_editor_via_message(update, shift_type, context)
        return True
    
    async def _show_combined_shift_editor_via_message(self, update: Update, shift_type: str, context: ContextTypes.DEFAULT_TYPE):
        """Show combined editor via message (for text input responses)."""
        current_times = self.shift_manager.user_times
        shift_config = current_times[shift_type]
        
        # Get pending changes if any
        pending_changes = context.user_data.get('pending_shift_changes', {}).get(shift_type, {})
        current_start = pending_changes.get('start', shift_config['start'])
        current_end = pending_changes.get('end', shift_config['end'])
        
        # Calculate duration based on current/pending times
        start_time = current_start
        end_time = current_end
        
        try:
            from datetime import datetime
            start_dt = datetime.strptime(start_time, "%H:%M")
            end_dt = datetime.strptime(end_time, "%H:%M")
            
            # Handle overnight shifts
            if end_dt < start_dt:
                end_dt = end_dt.replace(day=end_dt.day + 1)
            
            duration_hours = (end_dt - start_dt).total_seconds() / 3600
            duration_text = f"{duration_hours:.1f} שעות"
        except:
            duration_text = "לא זמין"
        
        editor_text = (
            f"⏰ <b>עריכת משמרת {shift_config['name']}</b>\n\n"
            f"{shift_config['emoji']} <b>זמני נוכחיים:</b>\n"
            f"• התחלה: {current_start}\n"
            f"• סיום: {current_end}\n"
            f"• משך: {duration_text}\n\n"
            f"בחר מה לערוך:"
        )
        
        buttons = [
            self.telegram_client.inline_buttons_row([
                ("⏰ ערוך התחלה", f"edit_start_{shift_type}"),
                ("⏰ ערוך סיום", f"edit_end_{shift_type}")
            ]),
            self.telegram_client.inline_buttons_row([
                ("💾 שמור שינויים", f"save_shift_{shift_type}"),
                ("❌ בטל", f"cancel_edit_{shift_type}")
            ]),
            self.telegram_client.inline_buttons_row([
                ("🔙 חזרה לכל המשמרות", "edit_shift_times")
            ])
        ]
        
        await update.message.reply_text(
            editor_text,
            reply_markup=self.telegram_client.inline_kb(buttons),
            parse_mode=ParseMode.HTML
        )
    
    async def _show_shift_times_menu(self, query):
        """Show the main shift times editing menu."""
        menu_config = MENU_CONFIGS["edit_shift_times"]
        
        # Format the title with current shift times
        formatted_title = menu_config["title"].format(
            shift_times_display=self.shift_manager.get_shift_times_display()
        )
        
        # Build proper keyboard
        button_rows = []
        for row in menu_config["buttons"]:
            button_row = self.telegram_client.inline_buttons_row(row)
            button_rows.append(button_row)
        
        await query.edit_message_text(
            formatted_title,
            reply_markup=self.telegram_client.inline_kb(button_rows),
            parse_mode=ParseMode.HTML
        )
    
    async def _show_combined_shift_editor(self, query, shift_type: str, context: ContextTypes.DEFAULT_TYPE):
        """Show combined editor for both start and end times."""
        current_times = self.shift_manager.user_times
        shift_config = current_times[shift_type]
        
        # Get pending changes if any
        pending_changes = context.user_data.get('pending_shift_changes', {}).get(shift_type, {})
        current_start = pending_changes.get('start', shift_config['start'])
        current_end = pending_changes.get('end', shift_config['end'])
        
        # Calculate duration based on current/pending times
        start_time = current_start
        end_time = current_end
        
        try:
            from datetime import datetime
            start_dt = datetime.strptime(start_time, "%H:%M")
            end_dt = datetime.strptime(end_time, "%H:%M")
            
            # Handle overnight shifts
            if end_dt < start_dt:
                end_dt = end_dt.replace(day=end_dt.day + 1)
            
            duration_hours = (end_dt - start_dt).total_seconds() / 3600
            duration_text = f"{duration_hours:.1f} שעות"
        except:
            duration_text = "לא זמין"
        
        editor_text = (
            f"⏰ <b>עריכת משמרת {shift_config['name']}</b>\n\n"
            f"{shift_config['emoji']} <b>זמני נוכחיים:</b>\n"
            f"• התחלה: {current_start}\n"
            f"• סיום: {current_end}\n"
            f"• משך: {duration_text}\n\n"
            f"בחר מה לערוך:"
        )
        
        buttons = [
            self.telegram_client.inline_buttons_row([
                ("⏰ ערוך התחלה", f"edit_start_{shift_type}"),
                ("⏰ ערוך סיום", f"edit_end_{shift_type}")
            ]),
            self.telegram_client.inline_buttons_row([
                ("💾 שמור שינויים", f"save_shift_{shift_type}"),
                ("❌ בטל", f"cancel_edit_{shift_type}")
            ]),
            self.telegram_client.inline_buttons_row([
                ("🔙 חזרה לכל המשמרות", "edit_shift_times")
            ])
        ]
        
        await query.edit_message_text(
            editor_text,
            reply_markup=self.telegram_client.inline_kb(buttons),
            parse_mode=ParseMode.HTML
        )
    
    async def _handle_edit_start_time(self, query, shift_type: str, context: ContextTypes.DEFAULT_TYPE):
        """Handle editing start time for a shift."""
        current_times = self.shift_manager.user_times
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
        current_times = self.shift_manager.user_times
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
                # Clear pending changes
                if shift_type in pending_changes:
                    del pending_changes[shift_type]
                
                await query.edit_message_text(
                    f"✅ <b>נשמר בהצלחה!</b>\n\n"
                    f"זמני המשמרת עודכנו:\n"
                    f"{self.shift_manager.get_shift_times_display()}",
                    reply_markup=self.telegram_client.inline_kb([
                        self.telegram_client.inline_buttons_row([
                            ("🔄 ערוך שוב", f"edit_times_{shift_type}"),
                            ("🔙 חזרה לכל המשמרות", "edit_shift_times")
                        ])
                    ]),
                    parse_mode=ParseMode.HTML
                )
            else:
                await query.edit_message_text(
                    f"❌ <b>שגיאה בשמירה</b>\n\n"
                    f"לא הצלחתי לשמור את השינויים.\n"
                    f"נסה שוב.",
                    reply_markup=self.telegram_client.inline_kb([
                        self.telegram_client.inline_buttons_row([
                            ("🔄 נסה שוב", f"edit_times_{shift_type}"),
                            ("❌ בטל", f"cancel_edit_{shift_type}")
                        ])
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
    
    async def _handle_cancel_edit(self, query, shift_type: str, context: ContextTypes.DEFAULT_TYPE = None):
        """Cancel editing and clear pending changes."""
        # Clear any pending changes for this shift
        pending_changes = context.user_data.get('pending_shift_changes', {}) if context else {}
        if shift_type in pending_changes:
            del pending_changes[shift_type]
        
        await self._show_combined_shift_editor(query, shift_type, context or {})
    
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
        
        current_times = self.shift_manager.user_times
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
            import logging
            logging.getLogger(__name__).exception("Error sending confirmation: %s", e)
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
