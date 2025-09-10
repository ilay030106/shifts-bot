"""
Templates Handler - Specialized handler for shift templates.
Handles shift description templates and custom templates.
"""

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
import json
import os


class TemplatesHandler:
    """Handles shift template preferences."""
    
    def __init__(self, telegram_client):
        self.telegram_client = telegram_client
        self.config_file = "user_templates.json"
        self.default_templates = {
            "morning": {
                "name": "משמרת בוקר",
                "template": "משמרת בוקר 🌅\n{start_time}-{end_time}\n📍 {location}\n📝 {notes}"
            },
            "afternoon": {
                "name": "משמרת אמצע",
                "template": "משמרת אמצע 🌇\n{start_time}-{end_time}\n📍 {location}\n📝 {notes}"
            },
            "night": {
                "name": "משמרת לילה", 
                "template": "משמרת לילה 🌙\n{start_time}-{end_time}\n📍 {location}\n📝 {notes}"
            },
            "custom": []  # List of custom user templates
        }
        self.user_templates = self._load_templates()
    
    def _load_templates(self):
        """Load user template preferences."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    result = self.default_templates.copy()
                    result.update(loaded)
                    return result
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        return self.default_templates.copy()
    
    def _save_templates(self):
        """Save template preferences to file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_templates, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving templates: {e}")
    
    async def can_handle(self, data: str) -> bool:
        """Check if this handler can process the given callback data."""
        return data.startswith("edit_templates") or data in [
            "edit_morning_template", "edit_afternoon_template", "edit_night_template",
            "add_custom_template", "delete_custom_template", "reset_templates",
            "show_template_variables"
        ] or data.startswith(("template_", "delete_template_"))
    
    async def handle_callback(self, query, data: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Handle template callback actions."""
        
        if data == "edit_templates":
            await self._show_templates_menu(query)
            return True
        
        elif data in ["edit_morning_template", "edit_afternoon_template", "edit_night_template"]:
            template_type = data.replace("edit_", "").replace("_template", "")
            await self._show_edit_template(query, template_type, context)
            return True
        
        elif data == "add_custom_template":
            await self._show_add_custom_template(query, context)
            return True
        
        elif data.startswith("delete_template_"):
            template_id = int(data.replace("delete_template_", ""))
            await self._delete_custom_template(query, template_id)
            return True
        
        elif data == "show_template_variables":
            await self._show_template_variables(query)
            return True
        
        elif data == "reset_templates":
            await self._reset_templates(query)
            return True
        
        return False
    
    async def handle_text_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Handle text input for template editing."""
        waiting_for = context.user_data.get('waiting_for')
        
        if not waiting_for or not waiting_for.startswith('template_'):
            return False
        
        template_text = update.message.text.strip()
        
        if waiting_for.startswith('template_edit_'):
            template_type = waiting_for.replace('template_edit_', '')
            await self._save_template_edit(update, template_type, template_text, context)
            return True
        
        elif waiting_for == 'template_custom_name':
            context.user_data['custom_template_name'] = template_text
            await self._ask_for_custom_template_content(update, context)
            return True
        
        elif waiting_for == 'template_custom_content':
            await self._save_custom_template(update, template_text, context)
            return True
        
        return False
    
    async def _show_templates_menu(self, query):
        """Show the templates configuration menu."""
        custom_count = len(self.user_templates.get("custom", []))
        
        buttons = [
            [
                ("🌅 ערוך תבנית בוקר", "edit_morning_template"),
                ("🌇 ערוך תבנית אמצע", "edit_afternoon_template")
            ],
            [
                ("🌙 ערוך תבנית לילה", "edit_night_template"),
                ("➕ הוסף תבנית מותאמת", "add_custom_template")
            ]
        ]
        
        if custom_count > 0:
            buttons.append([("🗑️ מחק תבניות מותאמות", "show_delete_templates")])
        
        buttons.extend([
            [("ℹ️ משתנים זמינים", "show_template_variables")],
            [
                ("↩️ איפוס לברירת מחדל", "reset_templates"),
                ("🔙 חזרה להעדפות", "settings_templates")
            ]
        ])
        
        await query.edit_message_text(
            f"📝 <b>הגדרות תבניות</b>\n\n"
            f"תבניות זמינות:\n"
            f"• תבנית בוקר\n"
            f"• תבנית אמצע\n" 
            f"• תבנית לילה\n"
            f"• תבניות מותאמות: {custom_count}\n\n"
            f"בחר פעולה:",
            reply_markup=self.telegram_client.inline_kb(buttons),
            parse_mode=ParseMode.HTML
        )
    
    async def _show_edit_template(self, query, template_type: str, context: ContextTypes.DEFAULT_TYPE):
        """Show template editing interface."""
        template_data = self.user_templates[template_type]
        
        await query.edit_message_text(
            f"📝 <b>עריכת {template_data['name']}</b>\n\n"
            f"תבנית נוכחית:\n"
            f"<code>{template_data['template']}</code>\n\n"
            f"שלח תבנית חדשה או השתמש במשתנים זמינים:",
            reply_markup=self.telegram_client.inline_kb([
                [("ℹ️ משתנים זמינים", "show_template_variables")],
                [("❌ ביטול", "edit_templates")]
            ]),
            parse_mode=ParseMode.HTML
        )
        
        context.user_data['waiting_for'] = f'template_edit_{template_type}'
    
    async def _show_add_custom_template(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Show interface to add custom template."""
        await query.edit_message_text(
            f"➕ <b>הוספת תבנית מותאמת</b>\n\n"
            f"שלח שם לתבנית החדשה:",
            reply_markup=self.telegram_client.inline_kb([
                [("❌ ביטול", "edit_templates")]
            ]),
            parse_mode=ParseMode.HTML
        )
        
        context.user_data['waiting_for'] = 'template_custom_name'
    
    async def _ask_for_custom_template_content(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ask for custom template content."""
        template_name = context.user_data.get('custom_template_name', 'תבנית חדשה')
        
        await update.message.reply_text(
            f"📝 <b>תבנית: {template_name}</b>\n\n"
            f"עכשיו שלח את תוכן התבנית.\n"
            f"אתה יכול להשתמש במשתנים כמו:\n"
            f"• {{start_time}} - שעת התחלה\n"
            f"• {{end_time}} - שעת סיום\n"
            f"• {{location}} - מיקום\n"
            f"• {{notes}} - הערות",
            reply_markup=self.telegram_client.inline_kb([
                [("❌ ביטול", "edit_templates")]
            ]),
            parse_mode=ParseMode.HTML
        )
        
        context.user_data['waiting_for'] = 'template_custom_content'
    
    async def _save_template_edit(self, update: Update, template_type: str, template_text: str, context: ContextTypes.DEFAULT_TYPE):
        """Save edited template."""
        self.user_templates[template_type]["template"] = template_text
        self._save_templates()
        
        # Clear waiting state
        if 'waiting_for' in context.user_data:
            del context.user_data['waiting_for']
        
        await update.message.reply_text(
            f"✅ <b>תבנית עודכנה</b>\n\n"
            f"תבנית חדשה:\n"
            f"<code>{template_text}</code>",
            reply_markup=self.telegram_client.inline_kb([
                [("🔙 חזרה לתבניות", "edit_templates")]
            ]),
            parse_mode=ParseMode.HTML
        )
    
    async def _save_custom_template(self, update: Update, template_text: str, context: ContextTypes.DEFAULT_TYPE):
        """Save new custom template."""
        template_name = context.user_data.get('custom_template_name', 'תבנית חדשה')
        
        new_template = {
            "name": template_name,
            "template": template_text
        }
        
        self.user_templates["custom"].append(new_template)
        self._save_templates()
        
        # Clear context
        for key in ['waiting_for', 'custom_template_name']:
            if key in context.user_data:
                del context.user_data[key]
        
        await update.message.reply_text(
            f"✅ <b>תבנית נוצרה</b>\n\n"
            f"שם: {template_name}\n"
            f"תוכן:\n<code>{template_text}</code>",
            reply_markup=self.telegram_client.inline_kb([
                [("🔙 חזרה לתבניות", "edit_templates")]
            ]),
            parse_mode=ParseMode.HTML
        )
    
    async def _show_template_variables(self, query):
        """Show available template variables."""
        variables_text = (
            "ℹ️ <b>משתנים זמינים בתבניות</b>\n\n"
            "<b>משתנים בסיסיים:</b>\n"
            "• <code>{start_time}</code> - שעת התחלה\n"
            "• <code>{end_time}</code> - שעת סיום\n"
            "• <code>{date}</code> - תאריך\n"
            "• <code>{location}</code> - מיקום\n"
            "• <code>{notes}</code> - הערות\n\n"
            "<b>משתנים נוספים:</b>\n"
            "• <code>{shift_type}</code> - סוג משמרת\n"
            "• <code>{duration}</code> - אורך המשמרת\n"
            "• <code>{day_name}</code> - שם היום\n\n"
            "<b>דוגמה:</b>\n"
            "<code>משמרת {shift_type} 🌅\n"
            "{date} ({day_name})\n"
            "⏰ {start_time}-{end_time}\n"
            "📍 {location}</code>"
        )
        
        await query.edit_message_text(
            variables_text,
            reply_markup=self.telegram_client.inline_kb([
                [("🔙 חזרה", "edit_templates")]
            ]),
            parse_mode=ParseMode.HTML
        )
    
    async def _reset_templates(self, query):
        """Reset all templates to defaults."""
        self.user_templates = self.default_templates.copy()
        self._save_templates()
        
        await query.edit_message_text(
            f"↩️ <b>תבניות אופסו</b>\n\n"
            f"כל התבניות חזרו לברירת המחדל.",
            reply_markup=self.telegram_client.inline_kb([
                [("🔙 חזרה", "edit_templates")]
            ]),
            parse_mode=ParseMode.HTML
        )
    
    def get_template(self, template_type: str) -> str:
        """Get template content."""
        return self.user_templates.get(template_type, {}).get("template", "")
    
    def format_template(self, template_type: str, **kwargs) -> str:
        """Format template with provided variables."""
        template = self.get_template(template_type)
        if not template:
            return ""
        
        try:
            return template.format(**kwargs)
        except KeyError as e:
            return f"Template error: Missing variable {e}"
    
    def get_templates_display(self) -> str:
        """Get formatted templates display."""
        custom_count = len(self.user_templates.get("custom", []))
        return f"תבניות: בוקר, אמצע, לילה + {custom_count} מותאמות"
