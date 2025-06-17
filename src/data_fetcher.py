#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
משיכת נתונים מ-Yahoo Finance עבור תיק TOP AI 10
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time
import config

class DataFetcher:
    """מחלקה למשיכת נתוני מניות ומדדים"""
    
    def __init__(self):
        self.ai_stocks = config.AI_STOCKS
        self.benchmarks = config.BENCHMARKS
        self.all_symbols = self.ai_stocks + self.benchmarks
        
    def get_current_prices(self):
        """משך מחירים נוכחיים לכל הסמלים"""
        print("🌐 מושך נתונים מ-Yahoo Finance...")
        
        current_prices = {}
        failed_symbols = []
        
        for symbol in self.all_symbols:
            try:
                print(f"   📊 מושך נתונים עבור {symbol}...")
                
                # יצירת אובייקט ticker
                ticker = yf.Ticker(symbol)
                
                # משיכת נתונים לחודש האחרון
                hist = ticker.history(period="1mo")
                
                if hist.empty:
                    print(f"   ⚠️ אין נתונים עבור {symbol}")
                    failed_symbols.append(symbol)
                    continue
                
                # מחיר נוכחי (סגירה אחרונה)
                current_price = hist['Close'].iloc[-1]
                
                # נתונים נוספים
                info = {
                    'current_price': round(float(current_price), 2),
                    'volume': int(hist['Volume'].iloc[-1]) if not hist['Volume'].empty else 0,
                    'last_update': datetime.now().isoformat()
                }
                
                # אם יש מספיק נתונים, נחשב שינוי חודשי
                if len(hist) > 1:
                    month_start_price = hist['Close'].iloc[0]
                    monthly_change = ((current_price - month_start_price) / month_start_price) * 100
                    info['monthly_change'] = round(float(monthly_change), 2)
                else:
                    info['monthly_change'] = 0.0
                
                current_prices[symbol] = info
                
                # המתנה קצרה כדי לא לעמוס על ה-API
                time.sleep(0.1)
                
            except Exception as e:
                print(f"   ❌ שגיאה במשיכת נתונים עבור {symbol}: {e}")
                failed_symbols.append(symbol)
                continue
        
        # דוח על הצלחות וכישלונות
        success_count = len(current_prices)
        total_count = len(self.all_symbols)
        
        print(f"\n✅ נמשכו נתונים עבור {success_count}/{total_count} סמלים")
        
        if failed_symbols:
            print(f"❌ כישלון במשיכת נתונים עבור: {', '.join(failed_symbols)}")
        
        return current_prices
    
    def get_historical_data(self, symbol, start_date, end_date=None):
        """משך נתונים היסטוריים לסמל ספציפי"""
        try:
            if end_date is None:
                end_date = datetime.now().strftime("%Y-%m-%d")
            
            ticker = yf.Ticker(symbol)
            hist = ticker.history(start=start_date, end=end_date)
            
            if hist.empty:
                return None
            
            return hist
            
        except Exception as e:
            print(f"❌ שגיאה במשיכת נתונים היסטוריים עבור {symbol}: {e}")
            return None
    
    def get_base_date_prices(self):
        """משך מחירים מתאריך הבסיס (12.6.2025)"""
        print(f"📅 מושך מחירים מתאריך הבסיס: {config.BASE_DATE}")
        
        base_prices = {}
        
        for symbol in self.all_symbols:
            try:
                # נסה למשוך נתונים מתאריך הבסיס
                hist = self.get_historical_data(symbol, config.BASE_DATE)
                
                if hist is not None and not hist.empty:
                    # קח את מחיר הסגירה הקרוב ביותר לתאריך הבסיס
                    base_price = hist['Close'].iloc[0]
                    base_prices[symbol] = round(float(base_price), 2)
                else:
                    # אם אין נתונים היסטוריים, השתמש במחיר מהקונפיג
                    if symbol in config.BASE_PRICES:
                        base_prices[symbol] = config.BASE_PRICES[symbol]
                        print(f"   ⚠️ משתמש במחיר מהקונפיג עבור {symbol}")
                    else:
                        print(f"   ❌ אין מחיר בסיס עבור {symbol}")
                
            except Exception as e:
                print(f"   ❌ שגיאה במשיכת מחיר בסיס עבור {symbol}: {e}")
                # השתמש במחיר מהקונפיג כגיבוי
                if symbol in config.BASE_PRICES:
                    base_prices[symbol] = config.BASE_PRICES[symbol]
        
        return base_prices
    
    def validate_data(self, price_data):
        """בדיקת תקינות הנתונים שנמשכו"""
        issues = []
        
        # בדיקה שכל הסמלים החשובים קיימים
        for symbol in self.ai_stocks:
            if symbol not in price_data:
                issues.append(f"חסר נתונים עבור מניה: {symbol}")
            elif price_data[symbol]['current_price'] <= 0:
                issues.append(f"מחיר לא תקין עבור {symbol}: {price_data[symbol]['current_price']}")
        
        for symbol in self.benchmarks:
            if symbol not in price_data:
                issues.append(f"חסר נתונים עבור מדד: {symbol}")
        
        # בדיקת שינויים קיצוניים (מעל 50% ביום אחד)
        for symbol, data in price_data.items():
            if abs(data.get('monthly_change', 0)) > 50:
                issues.append(f"שינוי קיצוני ב-{symbol}: {data['monthly_change']}%")
        
        if issues:
            print("⚠️ בעיות בנתונים:")
            for issue in issues:
                print(f"   - {issue}")
        else:
            print("✅ כל הנתונים תקינים")
        
        return len(issues) == 0
    
    def get_market_status(self):
        """בדיקת סטטוס השוק (פתוח/סגור)"""
        try:
            # נשתמש ב-SPY כמדד לסטטוס השוק
            ticker = yf.Ticker("SPY")
            info = ticker.info
            
            market_state = info.get('marketState', 'UNKNOWN')
            
            status_map = {
                'REGULAR': 'פתוח',
                'CLOSED': 'סגור',
                'PRE': 'טרום פתיחה',
                'POST': 'אחרי סגירה',
                'PREPRE': 'לפני פתיחה',
                'POSTPOST': 'אחרי סגירה'
            }
            
            return status_map.get(market_state, market_state)
            
        except Exception as e:
            print(f"❌ שגיאה בבדיקת סטטוס השוק: {e}")
            return "לא ידוע"