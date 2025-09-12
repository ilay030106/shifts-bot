"""
Menu configuration and text constants for the shifts bot.
Centralizes all UI text and menu structures.
"""

from .shift_times import shift_time_manager

# =============================================================================
# DEFAULT SHIFT TIME WINDOWS
# =============================================================================

# Access shift times through the manager
def get_shift_times_display():
    """Generate formatted shift times display text."""
    return shift_time_manager.get_shift_times_display()

# =============================================================================
# MAIN MENUS SECTION
# =============================================================================

# Main menu configuration
MAIN_MENU = {
    "title": "🤖 <b>בוט משמרות</b>\n\nבחר אופציה:",
    "buttons": [
        [
            ("העדפות", "preferences_menu"),
            ("זמינות", "menu_availability")
        ],
        [
            ("תיעוד משמרות", "menu_docs"),
            ("עזרה", "menu_help")
        ]
    ]
}

# Preferences menu
PREFERENCES_MENU = {
    "title": "⚙️ <b>העדפות</b>\n\nשינוי ההעדפות שלך:",
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
# PREFERENCES SUBMENUS SECTION
# =============================================================================

PREFERENCES_SHIFT_TIMES = {
    "title": (
        "⚙️ <b>העדפות → זמני משמרות</b>\n\n"
        "הגדר את זמני המשמרות שלך:\n"
        "{shift_times_display}\n\n"
        "(כאן תהיה אפשרות לערוך)"
    ),
    "buttons": [
        [
            ("ערוך זמנים", "edit_shift_times"),
            ("🔙 חזרה להעדפות", "preferences_menu")
        ]
    ]
}

# Edit shift times menu
EDIT_SHIFT_TIMES_MENU = {
    "title": (
        "⚙️ <b>עריכת זמני משמרות</b>\n\n"
        "בחר איזה משמרת לערוך:\n"
        "{shift_times_display}"
    ),
    "buttons": [
        [
            ("🌅 ערוך בוקר", "edit_morning_shift"),
            ("🌇 ערוך אמצע", "edit_afternoon_shift")
        ],
        [
            
            ("↩️ איפוס לברירת מחדל", "reset_shift_times")
        ],
        [
            ("🔙 חזרה", "settings_shift_times")
        ]
    ]
}

# Individual shift editing menus
def create_shift_edit_menu(shift_type: str):
    """Create a menu for editing a specific shift type."""
    all_times = shift_time_manager.user_times
    config = all_times[shift_type]
    return {
        "title": (
            f"⚙️ <b>עריכת משמרת {config['name']}</b>\n\n"
            f"זמן נוכחי: {config['emoji']} {config['start']}-{config['end']}\n\n"
            "בחר מה לערוך:"
        ),
        "buttons": [
            [
                ("🕐 שנה שעת התחלה", f"edit_start_{shift_type}"),
                ("🕑 שנה שעת סיום", f"edit_end_{shift_type}")
            ],
            [
                ("💾 שמור שינויים", f"save_shift_{shift_type}"),
                ("❌ בטל שינויים", f"cancel_edit_{shift_type}")
            ],
            [
                ("🔙 חזרה", "edit_shift_times")
            ]
        ]
    }

PREFERENCES_REMINDERS = {
    "title": (
        "⚙️ <b>העדפות → התראות</b>\n\n"
        "הגדרות התראות:\n"
        "• התראה 30 דקות לפני\n"
        "• התראה 15 דקות לפני\n\n"
        "(כאן תהיה אפשרות לערוך)"
    ),
    "buttons": [
        [
            ("ערוך התראות", "edit_reminders"),
            ("🔙 חזרה להעדפות", "preferences_menu")
        ]
    ]
}

PREFERENCES_TIMEZONE = {
    "title": (
        "⚙️ <b>העדפות → אזור זמן</b>\n\n"
        "אזור זמן נוכחי: Asia/Jerusalem\n\n"
        "(כאן תהיה אפשרות לשנות)"
    ),
    "buttons": [
        [
            ("שנה אזור זמן", "edit_timezone"),
            ("🔙 חזרה להעדפות", "preferences_menu")
        ]
    ]
}

PREFERENCES_TEMPLATES = {
    "title": (
        "⚙️ <b>העדפות → תבניות</b>\n\n"
        "תבניות עבור תיאור משמרות:\n"
        "• משמרת בוקר\n"
        "• משמרת ערב\n"
        "• משמרת לילה\n\n"
        "(כאן תהיה אפשרות לערוך)"
    ),
    "buttons": [
        [
            ("ערוך תבניות", "edit_templates"),
            ("🔙 חזרה להעדפות", "preferences_menu")
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
    "• <b>העדפות</b>: שינוי זמני משמרות, התראות וכו'\n"
    "• <b>זמינות</b>: בדיקה איזה משמרות אפשר לעבוד\n"
    "• <b>תיעוד משמרות</b>: הוסף או ערוך משמרות\n\n"
    "השתמש ב-/start כדי לחזור לתפריט הראשי."
)

# Back button configurations
BACK_BUTTONS = {
    "main": ("🔙 חזרה לתפריט הראשי", "menu_main"),
    "preferences": ("🔙 חזרה להעדפות", "preferences_menu"),
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
    "preferences_menu": PREFERENCES_MENU,
    "menu_availability": AVAILABILITY_MENU,
    "menu_docs": DOCS_MENU,
    
    # Preferences submenus
    "settings_shift_times": PREFERENCES_SHIFT_TIMES,
    "settings_reminders": PREFERENCES_REMINDERS,
    "settings_timezone": PREFERENCES_TIMEZONE,
    "settings_templates": PREFERENCES_TEMPLATES,
    
    # Shift time editing menus
    "edit_shift_times": EDIT_SHIFT_TIMES_MENU,
    "edit_morning_shift": lambda: create_shift_edit_menu("morning"),
    "edit_afternoon_shift": lambda: create_shift_edit_menu("afternoon"), 
    
    
    # Availability submenus
    "availability_this_week": AVAILABILITY_THIS_WEEK,
    "availability_next_week": AVAILABILITY_NEXT_WEEK,
    "availability_custom": AVAILABILITY_CUSTOM,
    
    # Documentation submenus
    "docs_add": DOCS_ADD,
    "docs_update": DOCS_UPDATE,
    "docs_delete": DOCS_DELETE,
}
