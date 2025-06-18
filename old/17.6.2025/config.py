# config.py - הגדרות מערכת

from datetime import datetime

# תאריך בסיס להשקעה
BASE_DATE = "2025-06-12"
INVESTMENT_PER_STOCK = 100  # דולר

# שם התיק (נדרש לדוחות)
PORTFOLIO_NAME = "TOP AI 10"

# מחירי בסיס ב-12.6.2025 (יתמלאו אוטומטית ממקור נתונים חיצוני)
BASE_PRICES = {
    # תיק AI (אלו ישמשו כדוגמה בלבד אם שליפה נכשלת, אך עדיף יהיו ריקים בתחילה)
    # הם יישלפו בזמן אמת עבור תאריך הבסיס
}

# רשימת מניות תיק AI
AI_STOCKS = [
    "ANET", "AVGO", "ASML", "CEG", "CRWD",
    "NVDA", "PLTR", "TSLA", "TSM", "VRT"
]

# מדדי השוק להשוואה
BENCHMARK_SYMBOLS = ["SPY", "QQQ", "TQQQ"]

# כל הסימבולים שצריך לנטר
ALL_SYMBOLS = list(set(AI_STOCKS + BENCHMARK_SYMBOLS))