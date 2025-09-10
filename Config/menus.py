"""
Menu configuration and text constants for the shifts bot.
Centralizes all UI text and menu structures.
"""

# Main menu configuration
MAIN_MENU = {
    "title": "🤖 <b>בוט משמרות</b>\n\nבחר אופציה:",
    "buttons": [
        [
            ("הגדרות ברירת מחדל", "defaults_menu"),
            ("זמינות", "menu_availability")
        ],
        [
            ("תיעוד משמרות", "menu_docs"),
            ("עזרה", "menu_help")
        ]
    ]
}

# Settings/Defaults menu
DEFAULTS_MENU = {
    "title": "⚙️ <b>הגדרות ברירת מחדל</b>\n\nשינוי ברירת המחדל שלך:",
    "buttons": [
        [
            ("זמני משמרות", "settings_shift_times"),
            ("התראות", "settings_reminders")
        ],
        [
            ("אזור זמן", "settings_timezone"),
            ("תבניות", "settings_templates")
        ],
        [
            ("🔙 חזרה לתפריט הראשי", "menu_main")
        ]
    ]
}

# Availability menu
AVAILABILITY_MENU = {
    "title": "📅 <b>בדוק זמינות</b>\n\nבחר טווח זמן:",
    "buttons": [
        [
            ("השבוע הזה", "availability_this_week"),
            ("בשבוע הקרוב (7 ימים)", "availability_next_week")
        ],
        [
            ("טווח מותאם אישית", "availability_custom"),
            ("🔙 חזרה לתפריט הראשי", "menu_main")
        ]
    ]
}

# Documentation menu
DOCS_MENU = {
    "title": "📝 <b>תיעוד משמרות</b>\n\nנהל את המשמרות:",
    "buttons": [
        [
            ("הוסף משמרת", "docs_add"),
            ("עדכן משמרת", "docs_update")
        ],
        [
            ("מחק משמרת", "docs_delete"),
            ("🔙 חזרה לתפריט הראשי", "menu_main")
        ]
    ]
}

# Help text
HELP_TEXT = (
    "❓ <b>עזרה</b>\n\n"
    "• <b>הגדרות ברירת מחדל</b>: שינוי זמני משמרות, התראות וכו'\n"
    "• <b>זמינות</b>: בדיקה איזה משמרות אפשר לעבוד\n"
    "• <b>תיעוד משמרות</b>: הוסף או ערוך משמרות\n\n"
    "השתמש ב-/start כדי לחזור לתפריט הראשי."
)

# Dynamic menu texts (use format strings)
SUBMENU_TEMPLATES = {
    "settings": "⚙️ <b>הגדרות → {action}</b>\n\nשנה הגדרות {action} כאן...",
    "availability": "📅 <b>זמינות → {action}</b>\n\nבדיקת זמינות {action}...",
    "docs": "📝 <b>תיעוד → {action}</b>\n\nמוכן לבצע {action} משמרת..."
}

# Back button configurations
BACK_BUTTONS = {
    "main": ("🔙 חזרה לתפריט הראשי", "menu_main"),
    "settings": ("🔙 חזרה להגדרות", "defaults_menu"),
    "availability": ("🔙 חזרה לזמינות", "menu_availability"),
    "docs": ("🔙 חזרה לתיעוד משמרות", "menu_docs")
}

# Action name translations (for display purposes)
ACTION_NAMES = {
    "shift_times": "זמני משמרות",
    "reminders": "התראות", 
    "timezone": "אזור זמן",
    "templates": "תבניות",
    "this_week": "השבוע הזה",
    "next_week": "השבוע הקרוב",
    "custom": "טווח מותאם",
    "add": "הוספת",
    "update": "עדכון",
    "delete": "מחיקת"
}
