# config.py - הגדרות מערכת

from datetime import datetime

# תאריך בסיס להשקעה
BASE_DATE = "2025-06-12"
INVESTMENT_PER_STOCK = 100  # דולר

# שם התיק (נדרש לדוחות)
PORTFOLIO_NAME = "TOP AI 10"

# מחירי בסיס ב-12.6.2025 (יתעדכנו אוטומטית)
BASE_PRICES = {
    # תיק AI
    "ANET": 95.77,
    "AVGO": 256.07,
    "ASML": 786.21,
    "CEG": 300.38,
    "CRWD": 481.73,
    "NVDA": 145.00,
    "PLTR": 135.19,
    "TSLA": 319.11,
    "TSM": 215.43,
    "VRT": 114.50,

    # מדדי השוק
    "SPY": 603.75,
    "QQQ": 533.66,
    "TQQQ": 75.69
}

# רשימת מניות תיק AI
AI_STOCKS = ["ANET", "AVGO", "ASML", "CEG", "CRWD", "NVDA", "PLTR", "TSLA", "TSM", "VRT"]

# מדדי השוק להשוואה
BENCHMARKS = ["SPY", "QQQ", "TQQQ"]

# הגדרות דוח (לא חובה לשימוש ישיר)
REPORT_SETTINGS = {
    'portfolio_name': PORTFOLIO_NAME,
    'currency': 'USD',
    'update_frequency': 'daily'  # daily, weekly, monthly
}
