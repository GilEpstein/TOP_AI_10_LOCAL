#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
יצירת דוחות HTML לתיק TOP AI 10
"""

import os
from datetime import datetime
import config 
# אין צורך ב-matplotlib.pyplot עבור דוח סיכום HTML, אז נמחק את הייבוא שלו.
# import matplotlib.pyplot as plt 

def safe_strftime(dt, format_str):
    """פונקציה בטוחה לעיצוב תאריך"""
    try:
        return dt.strftime(format_str)
    except UnicodeEncodeError:
        return dt.strftime('%d/%m/%Y %H:%M')

def performance_color_class(value):
    """מחזיר מחלקת CSS לצבע לפי ביצועים"""
    if value > 0:
        return "positive"
    elif value < 0:
        return "negative"
    else:
        return "neutral"

def format_currency(value):
    """מעצב ערך כספי עם סימן $ ובדיקת מינוס/פלוס בצד שמאל."""
    if value is None:
        return "-"
    sign = ""
    if value > 0:
        sign = "+"
    elif value < 0:
        sign = "-"
    return f"{sign}${abs(value):,.2f}"

def format_percentage(value):
    """מעצב ערך כאחוז עם בדיקת מינוס/פלוס בצד שמאל."""
    if value is None:
        return "-"
    sign = ""
    if value > 0:
        sign = "+"
    elif value < 0:
        sign = "-"
    return f"{sign}{abs(value):.2f}%"


class ReportGenerator:
    """מחלקה ליצירת דוחות HTML"""
    
    def __init__(self):
        self.portfolio_name = config.PORTFOLIO_NAME 
        self.base_date = config.BASE_DATE 

    def generate_main_report(self, performance_data):
        """יוצר את הדוח הראשי"""
        portfolio = performance_data['portfolio_summary']
        stocks = performance_data['stocks_performance']
        benchmarks = performance_data['benchmarks']
        outperformance = performance_data['outperformance']
        
        profit_card_class = "profit-card" if portfolio['total_profit'] >= 0 else "loss-card"
        
        # CSS styles
        css = """
        <style>
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #f0f2f5 0%, #e0e6ed 100%);
            margin: 0;
            padding: 20px;
            color: #333;
            direction: rtl; /* RTL support */
            text-align: right; /* Align text to the right */
        }
        .container {
            max-width: 1000px;
            margin: 20px auto;
            background: #ffffff;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            padding: 30px;
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 20px;
            border-bottom: 3px solid #eee;
            padding-bottom: 15px;
        }
        .date-info {
            text-align: center;
            font-size: 0.9em;
            color: #7f8c8d;
            margin-bottom: 30px;
        }
        .summary-cards {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-around;
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: #f9f9f9;
            border-radius: 10px;
            padding: 25px;
            flex: 1;
            min-width: 280px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
            text-align: center;
            transition: transform 0.2s ease-in-out;
        }
        .card:hover {
            transform: translateY(-5px);
        }
        .profit-card {
            border-bottom: 5px solid #28a745;
        }
        .loss-card {
            border-bottom: 5px solid #dc3545;
        }
        .card h2 {
            color: #34495e;
            font-size: 1.4em;
            margin-top: 0;
            margin-bottom: 15px;
        }
        .card .value {
            font-size: 2.2em;
            font-weight: bold;
            margin-bottom: 10px;
            color: #007bff;
        }
        .card .percentage {
            font-size: 1.5em;
            font-weight: bold;
        }
        .positive {
            color: #28a745;
        }
        .negative {
            color: #dc3545;
        }
        .neutral {
            color: #6c757d;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 30px;
            background: #ffffff;
            border-radius: 10px;
            overflow: hidden; /* Ensures rounded corners for inner elements */
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        }
        th, td {
            padding: 15px;
            text-align: right;
            border-bottom: 1px solid #f0f0f0;
        }
        th {
            background-color: #e9ecef;
            color: #495057;
            font-weight: bold;
            text-transform: uppercase;
            font-size: 0.9em;
        }
        tr:nth-child(even) {
            background-color: #f8fafd;
        }
        tr:hover {
            background-color: #eef4f9;
        }
        .table-section-title {
            font-size: 1.8em;
            color: #2c3e50;
            margin-top: 40px;
            margin-bottom: 20px;
            text-align: center;
        }
        .links {
            text-align: center;
            margin-top: 40px;
            font-size: 1.1em;
        }
        .links a {
            display: inline-block;
            margin: 0 15px;
            padding: 12px 25px;
            background-color: #007bff;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            transition: background-color 0.3s ease;
            box-shadow: 0 4px 10px rgba(0, 123, 255, 0.2);
        }
        .links a:hover {
            background-color: #0056b3;
            transform: translateY(-2px);
        }
        .footer {
            text-align: center;
            margin-top: 50px;
            font-size: 0.8em;
            color: #a0a0a0;
        }
        </style>
        """

        report_html = f"""
        <!DOCTYPE html>
        <html lang="he" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{self.portfolio_name} - דוח ביצועים</title>
            {css}
        </head>
        <body>
            <div class="container">
                <h1>{self.portfolio_name} - דוח ביצועים יומי</h1>
                <p class="date-info">
                    נכון לתאריך: {performance_data['hebrew_date']} | שעה: {safe_strftime(datetime.fromisoformat(performance_data['timestamp']), '%H:%M:%S')}
                    <br>
                    תאריך בסיס להשקעה: {self.base_date} ({performance_data['days_since_investment']} ימים מאז ההשקעה הראשונית)
                </p>

                <div class="summary-cards">
                    <div class="card {profit_card_class}">
                        <h2>שווי נוכחי</h2>
                        <div class="value">{format_currency(portfolio['current_value'])}</div>
                    </div>
                    <div class="card {profit_card_class}">
                        <h2>השקעה מקורית</h2>
                        <div class="value">{format_currency(portfolio['original_investment'])}</div>
                    </div>
                    <div class="card {profit_card_class}">
                        <h2>רווח / הפסד כולל</h2>
                        <div class="value {performance_color_class(portfolio['total_profit'])}">
                            {format_currency(portfolio['total_profit'])}
                        </div>
                        <div class="percentage {performance_color_class(portfolio['total_return'])}">
                            ({format_percentage(portfolio['total_return'])})
                        </div>
                    </div>
                </div>

                <h2 class="table-section-title">ביצועי מניות התיק</h2>
                <table>
                    <thead>
                        <tr>
                            <th>סמל</th>
                            <th>מחיר בסיס</th>
                            <th>כמות</th>
                            <th>מחיר נוכחי</th>
                            <th>שווי נוכחי</th>
                            <th>רווח/הפסד</th>
                            <th>% תשואה</th>
                        </tr>
                    </thead>
                    <tbody>
                        { "".join([f"""
                        <tr>
                            <td>{stock['symbol']}</td>
                            <td>{format_currency(stock['base_price'])}</td>
                            <td>{stock['quantity']:.2f}</td>
                            <td>{format_currency(stock['current_price'])}</td>
                            <td>{format_currency(stock['current_value'])}</td>
                            <td class="{performance_color_class(stock['profit_loss'])}">{format_currency(stock['profit_loss'])}</td>
                            <td class="{performance_color_class(stock['return_percent'])}">{format_percentage(stock['return_percent'])}</td>
                        </tr>
                        """ for stock in stocks.values()]) }
                    </tbody>
                </table>

                <h2 class="table-section-title">השוואה למדדי השוק</h2>
                <table>
                    <thead>
                        <tr>
                            <th>מדד</th>
                            <th>תשואת מדד (מאז תאריך הבסיס)</th>
                            <th>תשואת תיק (מאז תאריך הבסיס)</th>
                            <th>עדיפות התיק ($)</th>
                            <th>עדיפות התיק (%)</th>
                        </tr>
                    </thead>
                    <tbody>
                        { "".join([f"""
                        <tr>
                            <td>{symbol}</td>
                            <td class="{performance_color_class(data['benchmark_return'])}">{format_percentage(data['benchmark_return'])}</td>
                            <td class="{performance_color_class(data['portfolio_return'])}">{format_percentage(data['portfolio_return'])}</td>
                            <td class="{performance_color_class(data['outperformance'])}">{format_currency(data['outperformance'] / 100 * portfolio['original_investment'])}</td>
                            <td class="{performance_color_class(data['outperformance'])}">{format_percentage(data['outperformance'])}</td>
                        </tr>
                        """ for symbol, data in outperformance.items()]) }
                    </tbody>
                </table>

                <div class="links">
                    <a href="history.html">📈 צפה בהיסטוריית התיק</a>
                    <a href="summary.html">📸 דוח סיכום לשיתוף</a>
                </div>

                <div class="footer">
                    דו"ח זה נוצר אוטומטית על ידי מערכת מעקב התיקים של {self.portfolio_name}.
                </div>
            </div>
        </body>
        </html>
        """
        return report_html

    def generate_history_report(self, history_data):
        """יוצר את דוח היסטוריית התיק"""
        if not history_data:
            return self._generate_empty_history_report()

        # CSS styles for history report
        css = """
        <style>
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #f0f2f5 0%, #e0e6ed 100%);
            margin: 0;
            padding: 20px;
            color: #333;
            direction: rtl; /* RTL support */
            text-align: right; /* Align text to the right */
        }
        .container {
            max-width: 1200px;
            margin: 20px auto;
            background: #ffffff;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            padding: 30px;
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 20px;
            border-bottom: 3px solid #eee;
            padding-bottom: 15px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 30px;
            background: #ffffff;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        }
        th, td {
            padding: 12px 15px;
            text-align: right;
            border-bottom: 1px solid #f0f0f0;
            font-size: 0.9em;
        }
        th {
            background-color: #e9ecef;
            color: #495057;
            font-weight: bold;
            text-transform: uppercase;
        }
        tr:nth-child(even) {
            background-color: #f8fafd;
        }
        tr:hover {
            background-color: #eef4f9;
        }
        .positive {
            color: #28a745;
            font-weight: bold;
        }
        .negative {
            color: #dc3545;
            font-weight: bold;
        }
        .neutral {
            color: #6c757d;
        }
        .links {
            text-align: center;
            margin-top: 40px;
            font-size: 1.1em;
        }
        .links a {
            display: inline-block;
            margin: 0 15px;
            padding: 12px 25px;
            background-color: #007bff;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            transition: background-color 0.3s ease;
            box-shadow: 0 4px 10px rgba(0, 123, 255, 0.2);
        }
        .links a:hover {
            background-color: #0056b3;
            transform: translateY(-2px);
        }
        .footer {
            text-align: center;
            margin-top: 50px;
            font-size: 0.8em;
            color: #a0a0a0;
        }
        </style>
        """

        report_html = f"""
        <!DOCTYPE html>
        <html lang="he" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{self.portfolio_name} - היסטוריית ביצועים</title>
            {css}
        </head>
        <body>
            <div class="container">
                <h1>📈 היסטוריית ביצועים: {self.portfolio_name}</h1>
                <table>
                    <thead>
                        <tr>
                            <th>תאריך</th>
                            <th>שווי תיק</th>
                            <th>רווח כולל</th>
                            <th>% תשואה</th>
                            <th>ימים שהושקעו</th>
                            <th>תשואת SPY</th>
                            <th>תשואת QQQ</th>
                            <th>תשואת TQQQ</th>
                            <th>עדיפות מול SPY (%)</th>
                            <th>עדיפות מול QQQ (%)</th>
                            <th>עדיפות מול TQQQ (%)</th>
                        </tr>
                    </thead>
                    <tbody>
                        { "".join([f"""
                        <tr>
                            <td>{entry['date']}</td>
                            <td>{format_currency(entry['portfolio_value'])}</td>
                            <td class="{performance_color_class(entry['total_profit'])}">{format_currency(entry['total_profit'])}</td>
                            <td class="{performance_color_class(entry['total_return'])}">{format_percentage(entry['total_return'])}</td>
                            <td>{entry['days_invested']}</td>
                            <td class="{performance_color_class(entry['benchmarks_returns'].get('SPY', 0))}">{format_percentage(entry['benchmarks_returns'].get('SPY', 0))}</td>
                            <td class="{performance_color_class(entry['benchmarks_returns'].get('QQQ', 0))}">{format_percentage(entry['benchmarks_returns'].get('QQQ', 0))}</td>
                            <td class="{performance_color_class(entry['benchmarks_returns'].get('TQQQ', 0))}">{format_percentage(entry['benchmarks_returns'].get('TQQQ', 0))}</td>
                            <td class="{performance_color_class(entry['outperformance'].get('SPY', 0))}">{format_percentage(entry['outperformance'].get('SPY', 0))}</td>
                            <td class="{performance_color_class(entry['outperformance'].get('QQQ', 0))}">{format_percentage(entry['outperformance'].get('QQQ', 0))}</td>
                            <td class="{performance_color_class(entry['outperformance'].get('TQQQ', 0))}">{format_percentage(entry['outperformance'].get('TQQQ', 0))}</td>
                        </tr>
                        """ for entry in history_data]) }
                    </tbody>
                </table>
                <div class="links">
                    <a href="index.html">🏠 חזרה לדוח הראשי</a>
                    <a href="summary.html">📸 דוח סיכום לשיתוף</a>
                </div>
                <div class="footer">
                    דו"ח זה נוצר אוטומטית על ידי מערכת מעקב התיקים של {self.portfolio_name}.
                </div>
            </div>
        </body>
        </html>
        """
        return report_html

    def _generate_empty_history_report(self):
        """דוח היסטוריה ריק"""
        return f"""<!DOCTYPE html>
<html dir="rtl" lang="he">
<head>
    <meta charset="UTF-8">
    <title>היסטוריית {self.portfolio_name}</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; padding: 40px; text-align: center; direction: rtl; background: linear-gradient(135deg, #f0f2f5 0%, #e0e6ed 100%); margin: 0; min-height: 100vh; display: flex; align-items: center; justify-content: center; }}
        .container {{ background: white; border-radius: 20px; padding: 60px; max-width: 600px; margin: 0 auto; box-shadow: 0 20px 40px rgba(0,0,0,0.1); color: #333; }}
        h1 {{ color: #2c3e50; margin-bottom: 20px; font-size: 2.2em; }}
        p {{ font-size: 1.2em; color: #555; }}
        .links a {{ display: inline-block; padding: 12px 25px; margin: 15px 10px; background-color: #007bff; color: white; text-decoration: none; border-radius: 8px; transition: background-color 0.3s ease; box-shadow: 0 4px 10px rgba(0, 123, 255, 0.2); }}
        .links a:hover {{ background-color: #0056b3; transform: translateY(-2px); }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📈 היסטוריית התיק 📊</h1>
        <p>אין נתונים היסטוריים זמינים כרגע.</p>
        <p>הפעל את הסקריפט מספר פעמים כדי לצבור היסטוריית ביצועים.</p>
        <div class="links">
            <a href="index.html">🏠 חזרה לדוח הראשי</a>
            <a href="summary.html">📸 דוח סיכום לשיתוף</a>
        </div>
    </div>
</body>
</html>"""
        
    def generate_summary_image_report(self, performance_data):
        """יוצר את דוח הסיכום הקצר לשיתוף כקובץ HTML ומחזיר את המחרוזת."""
        
        portfolio_summary = performance_data['portfolio_summary']
        outperformance_data = performance_data['outperformance']
        
        report_html = f"""
        <!DOCTYPE html>
        <html lang="he" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{self.portfolio_name} - סיכום ביצועים לשיתוף</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background-color: #f0f2f5; display: flex; justify-content: center; align-items: center; min-height: 100vh; }}
                .share-card {{
                    background-color: #ffffff;
                    border-radius: 12px;
                    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
                    width: 400px;
                    padding: 30px;
                    text-align: center;
                    color: #333;
                    position: relative;
                    overflow: hidden;
                }}
                .share-card h1 {{
                    font-size: 1.8em;
                    color: #2c3e50;
                    margin-bottom: 10px;
                    border-bottom: 2px solid #e0e0e0;
                    padding-bottom: 10px;
                }}
                .share-card h2 {{
                    font-size: 1.3em;
                    color: #34495e;
                    margin-top: 20px;
                    margin-bottom: 15px;
                }}
                .main-metric {{
                    font-size: 2.8em;
                    font-weight: bold;
                    margin: 15px 0;
                    line-height: 1.2;
                }}
                .positive {{ color: #28a745; }}
                .negative {{ color: #dc3545; }}
                .neutral {{ color: #6c757d; }}
                .date-info {{
                    font-size: 0.9em;
                    color: #7f8c8d;
                    margin-bottom: 20px;
                }}
                .benchmark-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                }}
                .benchmark-table th, .benchmark-table td {{
                    padding: 10px;
                    border: 1px solid #eee;
                    text-align: right;
                    font-size: 0.95em;
                }}
                .benchmark-table th {{
                    background-color: #f8f9fa;
                    font-weight: bold;
                    color: #555;
                }}
                .benchmark-table td:nth-child(2) {{ font-weight: bold; }} /* Make portfolio return bold */
                .signature {{
                    font-size: 0.8em;
                    color: #a0a0a0;
                    margin-top: 30px;
                    padding-top: 10px;
                    border-top: 1px dashed #e0e0e0;
                }}
                .icon {{
                    /* margin-left: 5px; */ /* הסרנו את המרווח כדי לקרב את החץ לאחוז */
                }}
            </style>
        </head>
        <body>
            <div class="share-card">
                <h1>📈 סיכום ביצועים: {self.portfolio_name}</h1>
                <div class="date-info">
                    נכון ל: {performance_data['hebrew_date']} | החל מ: {self.base_date} ({performance_data['days_since_investment']} ימים)
                </div>

                <h2>תשואה כוללת של התיק</h2>
                <div class="main-metric {performance_color_class(portfolio_summary['total_return'])}">
                    {format_percentage(portfolio_summary['total_return'])}
                    <br>
                    ({format_currency(portfolio_summary['total_profit'])})
                </div>

                <h2>השוואה למדדי השוק</h2>
                <table class="benchmark-table">
                    <thead>
                        <tr>
                            <th>מדד</th>
                            <th>תשואת המדד</th>
                            <th>עדיפות התיק (%)</th>
                            <th>עדיפות התיק ($)</th>
                        </tr>
                    </thead>
                    <tbody>
                        { "".join([f"""
                        <tr>
                            <td>{symbol}</td>
                            <td class="{performance_color_class(data['benchmark_return'])}">{format_percentage(data['benchmark_return'])}</td>
                            <td class="{performance_color_class(data['outperformance'])}">
                                {format_percentage(data['outperformance'])} <span class="icon">{"⬆️" if data['outperformance'] > 0 else "⬇️" if data['outperformance'] < 0 else "↔️"}</span>
                            </td>
                            <td class="{performance_color_class(data['outperformance'])}">
                                {format_currency(data['outperformance'] / 100 * portfolio_summary['original_investment'])}
                            </td>
                        </tr>
                        """ for symbol, data in outperformance_data.items()]) }
                    </tbody>
                </table>
                <p class="signature">
                    מעקב ביצועים אוטומטי
                </p>
            </div>
        </body>
        </html>
        """
        
        return report_html