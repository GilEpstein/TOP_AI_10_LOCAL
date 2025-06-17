#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TOP AI 10 Portfolio Tracker
מערכת מעקב ביצועים לתיק השקעות AI מול מדדי השוק
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# הוספת נתיב src לייבוא
sys.path.append(str(Path(__file__).parent / "src"))

from data_fetcher import DataFetcher
from calculator import PerformanceCalculator
from report_generator import ReportGenerator
from utils import setup_directories, save_json, load_json
import config

def main():
    """פונקציה ראשית"""
    print("🚀 מתחיל מעקב תיק TOP AI 10...")
    print(f"📅 תאריך בסיס: {config.BASE_DATE}")
    print(f"💰 השקעה: ${config.INVESTMENT_PER_STOCK} למניה")
    
    try:
        # הכנת תיקיות
        setup_directories()
        
        # משיכת נתונים מ-Yahoo Finance
        print("\n📊 משך נתונים מ-Yahoo Finance...")
        data_fetcher = DataFetcher()
        current_prices = data_fetcher.get_current_prices()
        
        if not current_prices:
            print("❌ שגיאה במשיכת נתונים!")
            return
            
        print(f"✅ נמשכו נתונים עבור {len(current_prices)} סמלים")
        
        # חישוב ביצועים
        print("\n🧮 מחשב ביצועים...")
        calculator = PerformanceCalculator()
        performance_data = calculator.calculate_all_performance(current_prices)
        
        # שמירת נתונים
        save_json(performance_data, "data/latest_data.json")
        
        # עדכון היסטוריה
        calculator.update_history(performance_data)
        
        # יצירת דוחות
        print("\n📝 יוצר דוחות HTML...")
        report_gen = ReportGenerator()
        
        # דוח ראשי
        main_report = report_gen.generate_main_report(performance_data)
        with open("reports/index.html", "w", encoding="utf-8") as f:
            f.write(main_report)
        
        # דוח היסטוריה
        history_data = load_json("data/portfolio_history.json")
        if history_data:
            history_report = report_gen.generate_history_report(history_data)
            with open("reports/history.html", "w", encoding="utf-8") as f:
                f.write(history_report)
        
        # דוח מקוצר לשיתוף
        summary_report = report_gen.generate_summary_image_report(performance_data)
        with open("reports/summary.html", "w", encoding="utf-8") as f:
            f.write(summary_report)
        
        print("\n✅ הושלם בהצלחה!")
        print("📁 דוחות נשמרו:")
        print("   🏠 דוח ראשי: reports/index.html")
        print("   📈 היסטוריה: reports/history.html") 
        print("   📷 תמונת סיכום: reports/summary.html")
        print("🌐 פתח את reports/index.html בדפדפן")
        
        # פתיחה אוטומטית בדפדפן (אופציונלי)
        import webbrowser
        webbrowser.open(f"file://{os.path.abspath('reports/index.html')}")
        
    except Exception as e:
        print(f"❌ שגיאה: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()