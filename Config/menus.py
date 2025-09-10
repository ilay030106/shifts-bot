"""
Menu configuration and text constants for the shifts bot.
Centralizes all UI text and menu structures.
"""

# =============================================================================
# MAIN MENUS SECTION
# =============================================================================

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

# =============================================================================
# SETTINGS SUBMENUS SECTION
# =============================================================================

SETTINGS_SHIFT_TIMES = {
    "title": (
        "⚙️ <b>הגדרות → זמני משמרות</b>\n\n"
        "הגדר את זמני המשמרות שלך:\n"
        "• בוקר: 07:00-15:00\n"
        "• צהריים: 15:00-23:00\n"
        "• לילה: 23:00-07:00\n\n"
        "(כאן תהיה אפשרות לערוך)"
    ),
    "buttons": [
        [
            ("ערוך זמנים", "edit_shift_times"),
            ("🔙 חזרה להגדרות", "defaults_menu")
        ]
    ]
}

SETTINGS_REMINDERS = {
    "title": (
        "⚙️ <b>הגדרות → התראות</b>\n\n"
        "הגדרות התראות:\n"
        "• התראה 30 דקות לפני\n"
        "• התראה 15 דקות לפני\n\n"
        "(כאן תהיה אפשרות לערוך)"
    ),
    "buttons": [
        [
            ("ערוך התראות", "edit_reminders"),
            ("🔙 חזרה להגדרות", "defaults_menu")
        ]
    ]
}

SETTINGS_TIMEZONE = {
    "title": (
        "⚙️ <b>הגדרות → אזור זמן</b>\n\n"
        "אזור זמן נוכחי: Asia/Jerusalem\n\n"
        "(כאן תהיה אפשרות לשנות)"
    ),
    "buttons": [
        [
            ("שנה אזור זמן", "edit_timezone"),
            ("🔙 חזרה להגדרות", "defaults_menu")
        ]
    ]
}

SETTINGS_TEMPLATES = {
    "title": (
        "⚙️ <b>הגדרות → תבניות</b>\n\n"
        "תבניות עבור תיאור משמרות:\n"
        "• משמרת בוקר\n"
        "• משמרת ערב\n"
        "• משמרת לילה\n\n"
        "(כאן תהיה אפשרות לערוך)"
    ),
    "buttons": [
        [
            ("ערוך תבניות", "edit_templates"),
            ("🔙 חזרה להגדרות", "defaults_menu")
        ]
    ]
}

# =============================================================================
# AVAILABILITY SUBMENUS SECTION
# =============================================================================

AVAILABILITY_THIS_WEEK = {
    "title": (
        "📅 <b>זמינות → השבוע הזה</b>\n\n"
        "בודק זמינות לשבוע הנוכחי...\n"
        "(כאן יוצג הלוח זמינות)"
    ),
    "buttons": [
        [
            ("רענן", "availability_this_week"),
            ("🔙 חזרה לזמינות", "menu_availability")
        ]
    ]
}

AVAILABILITY_NEXT_WEEK = {
    "title": (
        "📅 <b>זמינות → השבוע הקרוב</b>\n\n"
        "בודק זמינות ל-7 הימים הקרובים...\n"
        "(כאן יוצג הלוח זמינות)"
    ),
    "buttons": [
        [
            ("רענן", "availability_next_week"),
            ("🔙 חזרה לזמינות", "menu_availability")
        ]
    ]
}

AVAILABILITY_CUSTOM = {
    "title": (
        "📅 <b>זמינות → טווח מותאם</b>\n\n"
        "בחר טווח תאריכים מותאם אישית:\n"
        "(כאן תהיה אפשרות לבחור תאריכים)"
    ),
    "buttons": [
        [
            ("בחר תאריכים", "select_date_range"),
            ("🔙 חזרה לזמינות", "menu_availability")
        ]
    ]
}

# =============================================================================
# DOCUMENTATION SUBMENUS SECTION  
# =============================================================================

DOCS_ADD = {
    "title": (
        "📝 <b>תיעוד → הוספת</b>\n\n"
        "הוספת משמרת חדשה:\n"
        "1. בחר תאריך\n"
        "2. בחר זמן\n"
        "3. בחר סוג משמרת\n\n"
        "(כאן יתחיל תהליך הוספת משמרת)"
    ),
    "buttons": [
        [
            ("התחל הוספה", "start_add_shift"),
            ("🔙 חזרה לתיעוד משמרות", "menu_docs")
        ]
    ]
}

DOCS_UPDATE = {
    "title": (
        "📝 <b>תיעוד → עדכון</b>\n\n"
        "עדכון משמרת קיימת:\n"
        "בחר משמרת לעדכון...\n\n"
        "(כאן תוצג רשימת משמרות)"
    ),
    "buttons": [
        [
            ("הצג משמרות", "list_shifts"),
            ("🔙 חזרה לתיעוד משמרות", "menu_docs")
        ]
    ]
}

DOCS_DELETE = {
    "title": (
        "📝 <b>תיעוד → מחיקת</b>\n\n"
        "מחיקת משמרת:\n"
        "בחר משמרת למחיקה...\n\n"
        "(כאן תוצג רשימת משמרות)"
    ),
    "buttons": [
        [
            ("הצג משמרות", "list_shifts_delete"),
            ("🔙 חזרה לתיעוד משמרות", "menu_docs")
        ]
    ]
}

# =============================================================================
# GENERAL TEXT AND HELPERS SECTION
# =============================================================================

# Help text
HELP_TEXT = (
    "❓ <b>עזרה</b>\n\n"
    "• <b>הגדרות ברירת מחדל</b>: שינוי זמני משמרות, התראות וכו'\n"
    "• <b>זמינות</b>: בדיקה איזה משמרות אפשר לעבוד\n"
    "• <b>תיעוד משמרות</b>: הוסף או ערוך משמרות\n\n"
    "השתמש ב-/start כדי לחזור לתפריט הראשי."
)

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

# =============================================================================
# MENU LOOKUP TABLE
# =============================================================================

# Mapping callback data to menu configurations for easy lookup
MENU_CONFIGS = {
    # Main menus
    "menu_main": MAIN_MENU,
    "defaults_menu": DEFAULTS_MENU,
    "menu_availability": AVAILABILITY_MENU,
    "menu_docs": DOCS_MENU,
    
    # Settings submenus
    "settings_shift_times": SETTINGS_SHIFT_TIMES,
    "settings_reminders": SETTINGS_REMINDERS,
    "settings_timezone": SETTINGS_TIMEZONE,
    "settings_templates": SETTINGS_TEMPLATES,
    
    # Availability submenus
    "availability_this_week": AVAILABILITY_THIS_WEEK,
    "availability_next_week": AVAILABILITY_NEXT_WEEK,
    "availability_custom": AVAILABILITY_CUSTOM,
    
    # Documentation submenus
    "docs_add": DOCS_ADD,
    "docs_update": DOCS_UPDATE,
    "docs_delete": DOCS_DELETE,
}
