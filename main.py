#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
קובץ ראשי המפעיל את יצירת הדוחות לתיק TOP AI 10.
"""

import os
import json
import webbrowser
from datetime import datetime, timedelta # Corrected import for datetime and timedelta
import config
from report_generator import ReportGenerator
import yfinance as yf
import pandas as pd

# --- הגדרת נתיבים וקבועים ---
OUTPUT_DIR = "reports"
HISTORY_FILE = "history_data.json"

# וודא שתיקיית הדוחות קיימת
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- פונקציות עזר כלליות ---
def save_json(data, filepath):
    """שומר נתונים לקובץ JSON."""
    try:
        dir_name = os.path.dirname(filepath)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    except IOError as e:
        print(f"שגיאת כתיבה לקובץ {filepath}: {e}")

def load_json(filepath):
    """טוען נתונים מקובץ JSON."""
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        return []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"שגיאת פענוח JSON מקובץ {filepath}: {e}")
        return []
    except IOError as e:
        print(f"שגיאת קריאה מקובץ {filepath}: {e}")
        return []

# --- פונקציה למשיכת נתונים אמיתיים מ-Yahoo Finance ---
def fetch_prices_from_yahoo(symbols, date_str=None):
    """
    מושך מחירי סגירה עבור סימבולים בתאריך ספציפי (או נתוני סגירה אחרונים).
    :param symbols: רשימת סימבולי מניות/מדדים.
    :param date_str: אופציונלי. תאריך ספציפי בפורמט 'YYYY-MM-DD' למשוך עבורו מחיר סגירה.
                     אם לא ניתן, ימשוך את מחיר הסגירה האחרון (היום).
    :return: מילון של {symbol: close_price}.
    """
    prices = {}
    if not symbols:
        return prices

    if date_str:
        start_date_dt = datetime.strptime(date_str, '%Y-%m-%d')
        # yfinance download end date is exclusive, so add a day
        end_date_dt = start_date_dt + timedelta(days=1)
        
        print(f"מושך מחירי סגירה עבור תאריך {date_str}...")
        try:
            # Removed show_errors=True as it's not supported by all yfinance versions
            data = yf.download(symbols, start=start_date_dt.strftime('%Y-%m-%d'), 
                               end=end_date_dt.strftime('%Y-%m-%d'), progress=False)
            
            if not data.empty and 'Close' in data.columns:
                for symbol in symbols:
                    if symbol in data['Close'].columns: # Multi-stock dataframe
                        if not data['Close'][symbol].empty:
                            prices[symbol] = data['Close'][symbol].iloc[0] # Get the first (and hopefully only) close price for that day
                    elif isinstance(data['Close'], pd.Series) and data['Close'].name == symbol: # Single stock series
                        if not data['Close'].empty:
                            prices[symbol] = data['Close'].iloc[0]
            else:
                print(f"אזהרה: לא נמצאו נתוני סגירה עבור {', '.join(symbols)} בתאריך {date_str}. בדוק סימבולים ותאריך.")

        except Exception as e:
            print(f"שגיאה במשיכת נתונים היסטוריים מ-Yahoo Finance עבור {', '.join(symbols)} בתאריך {date_str}: {e}")
            
    else: # Fetch latest close price (for today's data)
        print("מושך מחירי סגירה עדכניים (אחרונים) מ-Yahoo Finance...")
        try:
            # Removed show_errors=True
            data = yf.download(symbols, period='1d', interval='1d', progress=False)
            if not data.empty and 'Close' in data.columns:
                for symbol in symbols:
                    if symbol in data['Close'].columns: # Multi-stock dataframe
                        if not data['Close'][symbol].empty:
                            prices[symbol] = data['Close'][symbol].iloc[-1] # Last available close
                    elif isinstance(data['Close'], pd.Series) and data['Close'].name == symbol: # Single stock series
                        if not data['Close'].empty:
                            prices[symbol] = data['Close'].iloc[-1]
            else:
                print(f"אזהרה: לא נמצאו נתוני סגירה עדכניים עבור {', '.join(symbols)}. בדוק סימבולים.")
        except Exception as e:
            print(f"שגיאה במשיכת נתונים עדכניים מ-Yahoo Finance עבור {', '.join(symbols)}: {e}")
    
    # Ensure all symbols have a price, even if None
    for symbol in symbols:
        if symbol not in prices:
            prices[symbol] = None # Set to None if price couldn't be fetched

    return prices


# --- פונקציות חישוב ביצועים ---
def calculate_performance(base_prices, current_prices, investment_per_stock, ai_stocks, benchmarks_symbols):
    """
    מחשב את ביצועי התיק הכוללים, מניות בודדות ומדדי ייחוס.
    """
    total_investment = len(ai_stocks) * investment_per_stock
    current_portfolio_value = 0
    stocks_performance = []

    for symbol in ai_stocks:
        base_price = base_prices.get(symbol)
        current_price = current_prices.get(symbol)

        if base_price is not None and current_price is not None and base_price != 0:
            quantity = investment_per_stock / base_price
            current_value = quantity * current_price
            profit_loss = current_value - investment_per_stock
            percentage_return = (profit_loss / investment_per_stock) * 100

            current_portfolio_value += current_value
            stocks_performance.append({
                'symbol': symbol,
                'base_price': base_price,
                'current_price': current_price,
                'quantity': quantity,
                'investment_amount': investment_per_stock,
                'current_value': current_value,
                'profit_loss': profit_loss,
                'percentage_return': percentage_return
            })
        else:
            print(f"אזהרה: נתוני מחיר חסרים או לא חוקיים עבור {symbol}. מניה זו לא תיכלל בחישובים, או תוצג כ-0.")
            stocks_performance.append({
                'symbol': symbol,
                'base_price': base_price or 0,
                'current_price': current_price or 0,
                'quantity': 0,
                'investment_amount': investment_per_stock,
                'current_value': 0,
                'profit_loss': 0,
                'percentage_return': 0
            })

    total_profit = current_portfolio_value - total_investment
    total_return = (total_profit / total_investment) * 100 if total_investment != 0 else 0

    benchmarks_returns = {}
    outperformance = {}

    for symbol in benchmarks_symbols:
        base_price = base_prices.get(symbol)
        current_price = current_prices.get(symbol)
        if base_price is not None and current_price is not None and base_price != 0:
            benchmark_return = ((current_price - base_price) / base_price) * 100
            benchmarks_returns[symbol] = benchmark_return
            outperformance[symbol] = {
                'benchmark_return': benchmark_return,
                'portfolio_return': total_return,
                'outperformance': total_return - benchmark_return
            }
        else:
            benchmarks_returns[symbol] = None
            outperformance[symbol] = {
                'benchmark_return': None,
                'portfolio_return': total_return,
                'outperformance': None
            }

    return {
        'portfolio_value': current_portfolio_value,
        'total_profit': total_profit,
        'total_return': total_return,
        'stocks_performance': stocks_performance,
        'benchmarks_returns': benchmarks_returns,
        'outperformance': outperformance
    }

def main():
    today_date = datetime.now()
    today_date_str = today_date.strftime('%Y-%m-%d')
    base_date_dt = datetime.strptime(config.BASE_DATE, '%Y-%m-%d')
    
    # 1. טען נתונים היסטוריים
    history_data = load_json(HISTORY_FILE)

    # 2. וודא שרשומת הבסיס קיימת ומכילה את מחירי הבסיס
    base_date_record_exists = False
    
    # Always attempt to fetch base prices from Yahoo Finance for BASE_DATE
    print(f"מנסה למשוך מחירי בסיס עבור {config.BASE_DATE} מ-Yahoo Finance.")
    fetched_base_prices = fetch_prices_from_yahoo(config.ALL_SYMBOLS, config.BASE_DATE)
    
    if all(price is not None for price in fetched_base_prices.values()):
        effective_base_prices = fetched_base_prices
        
        # If record didn't exist, create/update it now with fetched prices
        # First, check if a base record already exists to avoid duplication
        existing_base_record_index = -1
        for i, record in enumerate(history_data):
            if record['date'] == config.BASE_DATE:
                existing_base_record_index = i
                break

        if existing_base_record_index == -1: # Base record does not exist, create it
            initial_portfolio_value = len(config.AI_STOCKS) * config.INVESTMENT_PER_STOCK
            
            initial_stocks_performance = []
            for symbol in config.AI_STOCKS:
                initial_stocks_performance.append({
                    'symbol': symbol,
                    'base_price': effective_base_prices.get(symbol, 0),
                    'current_price': effective_base_prices.get(symbol, 0), # At base date, current_price = base_price
                    'quantity': config.INVESTMENT_PER_STOCK / effective_base_prices.get(symbol, 1) if effective_base_prices.get(symbol, 1) != 0 else 0,
                    'investment_amount': config.INVESTMENT_PER_STOCK,
                    'current_value': config.INVESTMENT_PER_STOCK,
                    'profit_loss': 0.0,
                    'percentage_return': 0.0
                })
            
            # Store base prices for benchmarks in base record
            initial_benchmarks_base_prices = {
                symbol: effective_base_prices.get(symbol) for symbol in config.BENCHMARK_SYMBOLS
            }

            base_date_record = {
                "date": config.BASE_DATE,
                "timestamp": datetime.combine(base_date_dt, datetime.min.time()).isoformat(),
                "portfolio_value": initial_portfolio_value,
                "total_profit": 0.0,
                "total_return": 0.0,
                "days_invested": 0,
                "benchmarks_returns": {
                    "SPY": 0.0, "QQQ": 0.0, "TQQQ": 0.0
                },
                "outperformance": {
                    "SPY": {"benchmark_return": 0.0, "portfolio_return": 0.0, "outperformance": 0.0},
                    "QQQ": {"benchmark_return": 0.0, "portfolio_return": 0.0, "outperformance": 0.0},
                    "TQQQ": {"benchmark_return": 0.0, "portfolio_return": 0.0, "outperformance": 0.0}
                },
                "stocks_performance": initial_stocks_performance,
                "benchmarks_base_prices": initial_benchmarks_base_prices 
            }
            history_data.insert(0, base_date_record)
            print("✅ רשומת תאריך בסיס נוצרה והוכנסה להיסטוריה עם מחירי בסיס אמיתיים.")
        else:
            print("✅ מחירי בסיס נמשכו מחדש בהצלחה עבור רשומת תאריך בסיס קיימת.")
            
    else:
        print("❌ אזהרה חמורה: לא ניתן למשוך מחירי בסיס עבור כל הסימבולים מ-Yahoo Finance. החישובים לא יהיו מדויקים!")
        print("אנא וודא חיבור לאינטרנט ושהסימבולים ('ANET', 'AVGO', 'ASML', 'CEG', 'CRWD', 'NVDA', 'PLTR', 'TSLA', 'TSM', 'VRT', 'SPY', 'QQQ', 'TQQQ') תקינים עבור Yahoo Finance.")
        
    if not effective_base_prices or not all(price is not None for price in effective_base_prices.values()):
        print("❌ שגיאה: מחירי בסיס חיוניים חסרים. לא ניתן להמשיך בחישובים מדויקים.")
        return 

    # 3. הבא מחירי סגירה עדכניים עבור היום
    current_prices = fetch_prices_from_yahoo(config.ALL_SYMBOLS)

    # בדוק אם מחירי היום הנוכחי נמשכו בהצלחה
    if not all(price is not None for price in current_prices.values()):
        print("❌ שגיאה: לא ניתן למשוך מחירי סגירה עדכניים עבור כל הסימבולים. החישובים לא יהיו מדויקים!")
        print("אנא וודא חיבור לאינטרנט ושהסימבולים תקינים עבור Yahoo Finance.")
        return 

    # 4. חשב ביצועים עבור התאריך הנוכחי
    calculated_performance = calculate_performance(
        effective_base_prices, 
        current_prices,
        config.INVESTMENT_PER_STOCK,
        config.AI_STOCKS,
        config.BENCHMARK_SYMBOLS
    )

    # חשב ימים שהושקעו מהתאריך base_date
    days_invested = (today_date - base_date_dt).days
    if days_invested < 0: days_invested = 0

    # Add benchmark prices to current_day_record
    benchmarks_current_prices = {
        symbol: current_prices.get(symbol) for symbol in config.BENCHMARK_SYMBOLS
    }
    benchmarks_base_prices_for_report = {
        symbol: effective_base_prices.get(symbol) for symbol in config.BENCHMARK_SYMBOLS
    }

    # צור את מבנה הנתונים המלא לרשומה של היום הנוכחי, כולל כל המידע הנדרש לדוחות
    current_day_record = {
        "date": today_date_str,
        "timestamp": datetime.now().isoformat(),
        "portfolio_value": calculated_performance['portfolio_value'],
        "total_profit": calculated_performance['total_profit'],
        "total_return": calculated_performance['total_return'],
        "days_invested": days_invested,
        "benchmarks_returns": calculated_performance['benchmarks_returns'],
        "outperformance": calculated_performance['outperformance'],
        "stocks_performance": calculated_performance['stocks_performance'],
        "benchmarks_current_prices": benchmarks_current_prices,
        "benchmarks_base_prices": benchmarks_base_prices_for_report
    }

    # 5. בדוק אם כבר קיימת רשומה עבור התאריך הנוכחי ועדכן או הוסף
    record_exists_for_today = False
    for i, record in enumerate(history_data):
        if record['date'] == today_date_str:
            history_data[i] = current_day_record # עדכן רשומה קיימת
            record_exists_for_today = True
            print(f"🔄 עדכון רשומה קיימת עבור {today_date_str} בהיסטוריה.")
            break
    
    if not record_exists_for_today:
        history_data.append(current_day_record) # הוסף רשומה חדשה
        print(f"➕ מוסיף רשומה חדשה עבור {today_date_str} להיסטוריה.")

    # 6. מיין את הנתונים לפי תאריך לפני השמירה
    history_data.sort(key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'))

    save_json(history_data, HISTORY_FILE)
    print(f"✅ היסטוריית נתונים נשמרה ב: {HISTORY_FILE}")

    # 7. צור מופע של ReportGenerator
    report_generator = ReportGenerator()
    print("✅ ReportGenerator אתחול בהצלחה.")

    # 8. הפק את הדוחות ושמור אותם לקבצים
    # השתמש ב-current_day_record המלא עבור יצירת הדוח הראשי והסיכום
    reports_to_generate = {
        "index.html": report_generator.generate_main_report(current_day_record),
        "history.html": report_generator.generate_history_report(history_data),
        "summary.html": report_generator.generate_summary_image_report(current_day_record),
        "graphs.html": report_generator.generate_graphs_report(history_data)
    }

    for filename, html_content in reports_to_generate.items():
        file_path = os.path.join(OUTPUT_DIR, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"📄 דוח נוצר: {file_path}")

    print("✨ כל הדוחות נוצרו בהצלחה!")

    # --- קוד שיפתח את הדוח באופן אוטומטי ---
    try:
        main_report_path = os.path.join(OUTPUT_DIR, "index.html")
        if os.path.exists(main_report_path):
            webbrowser.open(f"file:///{os.path.abspath(main_report_path)}")
            print(f"🌐 הדוח הראשי נפתח אוטומטית: {os.path.abspath(main_report_path)}")
        else:
            print(f"אזהרה: קובץ הדוח הראשי לא נמצא בנתיב: {main_report_path}")
    except Exception as e:
        print(f"שגיאה בניסיון לפתוח את הדוח בדפדפן: {e}")

if __name__ == "__main__":
    main()