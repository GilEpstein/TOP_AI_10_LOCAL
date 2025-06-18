#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
פונקציות עזר למערכת TOP AI 10
"""

import os
import json
from datetime import datetime
from pathlib import Path

def setup_directories():
    """יוצר תיקיות נדרשות אם לא קיימות"""
    directories = ['data', 'reports', 'reports/assets']
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("📁 תיקיות הוכנו בהצלחה")

def save_json(data, filepath):
    """שומר נתונים לקובץ JSON"""
    try:
        # יצירת תיקייה אם לא קיימת
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"💾 נתונים נשמרו: {filepath}")
        return True
        
    except Exception as e:
        print(f"❌ שגיאה בשמירת {filepath}: {e}")
        return False

def load_json(filepath):
    """טוען נתונים מקובץ JSON"""
    try:
        if not os.path.exists(filepath):
            return None
            
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📂 נתונים נטענו: {filepath}")
        return data
        
    except Exception as e:
        print(f"❌ שגיאה בטעינת {filepath}: {e}")
        return None

def format_currency(amount):
    """מעצב מספר כמטבע"""
    return f"${amount:,.2f}"

def format_percentage(percentage):
    """מעצב אחוזים עם סימן"""
    sign = "+" if percentage >= 0 else ""
    return f"{sign}{percentage:.2f}%"

def days_since_investment():
    """מחשב כמה ימים עברו מתאריך ההשקעה"""
    from config import BASE_DATE
    
    base_date = datetime.strptime(BASE_DATE, "%Y-%m-%d")
    current_date = datetime.now()
    
    delta = current_date - base_date
    return delta.days

def get_hebrew_date(date_obj=None):
    """מחזיר תאריך בעברית"""
    if date_obj is None:
        date_obj = datetime.now()
    
    hebrew_months = {
        1: 'ינואר', 2: 'פברואר', 3: 'מרץ', 4: 'אפריל',
        5: 'מאי', 6: 'יוני', 7: 'יולי', 8: 'אוגוסט',
        9: 'ספטמבר', 10: 'אוקטובר', 11: 'נובמבר', 12: 'דצמבר'
    }
    
    return f"{date_obj.day} {hebrew_months[date_obj.month]} {date_obj.year}"

def performance_color_class(value):
    """מחזיר מחלקת CSS לצבע לפי ביצועים"""
    if value > 0:
        return "positive"
    elif value < 0:
        return "negative"
    else:
        return "neutral"

def print_summary(performance_data):
    """מדפיס סיכום לקונסול"""
    portfolio = performance_data['portfolio_summary']
    
    print("\n" + "="*50)
    print("📊 סיכום ביצועי תיק TOP AI 10")
    print("="*50)
    print(f"💰 ערך נוכחי: {format_currency(portfolio['current_value'])}")
    print(f"💵 השקעה מקורית: {format_currency(portfolio['original_investment'])}")
    print(f"📈 רווח/הפסד: {format_currency(portfolio['total_profit'])} ({format_percentage(portfolio['total_return'])})")
    print(f"📅 ימים מההשקעה: {days_since_investment()}")
    
    print("\n🏆 השוואה מול מדדי השוק:")
    for benchmark, data in performance_data['benchmarks'].items():
        outperformance = portfolio['total_return'] - data['return_percent']
        status = "🔥 מנצח" if outperformance > 0 else "📉 מפסיד"
        print(f"   {benchmark}: {status} ב-{format_percentage(abs(outperformance))}")
    
    print("="*50)