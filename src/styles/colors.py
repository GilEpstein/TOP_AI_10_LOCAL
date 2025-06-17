# -*- coding: utf-8 -*-
"""
הגדרות צבעים מודרניים - בהשראת הפוסט
"""

class Colors:
    """צבעים מודרניים וחיים"""
    
    # צבעי רקע מרכזיים
    PRIMARY_BG = "linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #3b82f6 100%)"
    SECONDARY_BG = "linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%)"
    
    # צבעי הדגשה
    ACCENT_BLUE = "#3b82f6"
    ACCENT_GREEN = "#10b981"
    ACCENT_ORANGE = "#f59e0b"
    ACCENT_PURPLE = "#8b5cf6"
    
    # צבעי ביצועים
    PROFIT_GREEN = "#22c55e"
    LOSS_RED = "#ef4444"
    NEUTRAL_GRAY = "#64748b"
    
    # צבעי טקסט
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#e2e8f0"
    TEXT_MUTED = "#94a3b8"
    
    # צבעי כרטיסים
    CARD_BG = "rgba(255,255,255,0.1)"
    CARD_BORDER = "rgba(255,255,255,0.2)"
    CARD_HOVER = "rgba(255,255,255,0.15)"
    
    # גרדיאנטים מיוחדים
    GRADIENT_PROFIT = "linear-gradient(135deg, #22c55e 0%, #16a34a 100%)"
    GRADIENT_LOSS = "linear-gradient(135deg, #ef4444 0%, #dc2626 100%)"
    GRADIENT_BUTTON = "linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)"
    
    @classmethod
    def get_performance_color(cls, value):
        """מחזיר צבע לפי ביצועים"""
        if value > 0:
            return cls.PROFIT_GREEN
        elif value < 0:
            return cls.LOSS_RED
        else:
            return cls.NEUTRAL_GRAY
    
    @classmethod
    def get_gradient_by_performance(cls, value):
        """מחזיר גרדיאנט לפי ביצועים"""
        if value > 0:
            return cls.GRADIENT_PROFIT
        elif value < 0:
            return cls.GRADIENT_LOSS
        else:
            return "linear-gradient(135deg, #64748b 0%, #475569 100%)"