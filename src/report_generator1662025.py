#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
יצירת דוחות HTML לתיק TOP AI 10
"""

from datetime import datetime
from utils import format_currency, format_percentage, performance_color_class
import config

def safe_strftime(dt, format_str):
    """פונקציה בטוחה לעיצוב תאריך"""
    try:
        return dt.strftime(format_str)
    except UnicodeEncodeError:
        return dt.strftime('%d/%m/%Y %H:%M')

class ReportGenerator:
    """מחלקה ליצירת דוחות HTML"""
    
    def __init__(self):
        self.portfolio_name = config.REPORT_SETTINGS['portfolio_name']
        self.currency = config.REPORT_SETTINGS['currency']
    
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
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            direction: rtl;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #2c3e50 0%, #4a5568 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 800;
        }
        .nav-links {
            margin-top: 20px;
        }
        .nav-links a {
            display: inline-block;
            padding: 12px 20px;
            background: rgba(255,255,255,0.2);
            color: white;
            text-decoration: none;
            border-radius: 20px;
            margin: 0 8px;
            transition: all 0.3s ease;
            font-weight: 500;
        }
        .nav-links a:hover {
            background: rgba(255,255,255,0.3);
        }
        .nav-links a.current {
            background: rgba(255,255,255,0.4);
            font-weight: 700;
        }
        .summary-section {
            padding: 50px;
            background: #f8f9fa;
            text-align: center;
        }
        .summary-title {
            font-size: 2.5em;
            color: #2c3e50;
            margin-bottom: 40px;
            font-weight: 700;
        }
        .summary-cards {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            max-width: 1000px;
            margin: 0 auto;
        }
        .summary-card {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        .summary-card:hover {
            transform: translateY(-10px);
        }
        .summary-card h3 {
            font-size: 1.1em;
            color: #6c757d;
            margin-bottom: 15px;
            font-weight: 600;
        }
        .summary-card .value {
            font-size: 2.2em;
            font-weight: 700;
            margin-bottom: 10px;
            direction: ltr;
            text-align: center;
        }
        .summary-card .profit {
            font-size: 1.3em;
            font-weight: 600;
            direction: ltr;
            text-align: center;
        }
        .profit-card {
            border-left: 5px solid #10b981;
        }
        .loss-card {
            border-left: 5px solid #ef4444;
        }
        .positive {
            color: #10b981 !important;
        }
        .negative {
            color: #ef4444 !important;
        }
        .section {
            padding: 40px;
        }
        .section-title {
            font-size: 2em;
            color: #2c3e50;
            margin-bottom: 30px;
            text-align: center;
            font-weight: 700;
        }
        .comparison-table, .portfolio-table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        .comparison-table th, .portfolio-table th {
            background: #2c3e50;
            color: white;
            padding: 15px;
            text-align: center;
            font-weight: 600;
        }
        .comparison-table td, .portfolio-table td {
            padding: 15px;
            text-align: center;
            border-bottom: 1px solid #eee;
        }
        .comparison-table tr:hover, .portfolio-table tr:hover {
            background-color: #f8f9fa;
        }
        .stock-symbol {
            font-weight: 700;
            color: #2c3e50;
            font-size: 1.1em;
        }
        .number-cell {
            direction: ltr;
            text-align: center;
            font-weight: 500;
        }
        .outperform-badge {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 0.85em;
            font-weight: 600;
            color: white;
        }
        .outperform-badge.winning {
            background: #10b981;
        }
        .outperform-badge.losing {
            background: #ef4444;
        }
        .footer {
            background: #2c3e50;
            color: white;
            text-align: center;
            padding: 30px;
        }
        @media (max-width: 1200px) {
            .summary-cards {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        @media (max-width: 768px) {
            .summary-cards {
                grid-template-columns: 1fr;
                gap: 15px;
            }
        }
        </style>
        """
        
        # HTML header
        html = f"""<!DOCTYPE html>
<html dir="rtl" lang="he">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.portfolio_name} - דוח ביצועים</title>
    {css}
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 {self.portfolio_name} 📊</h1>
            <p>מעקב ביצועים מ-{config.BASE_DATE}</p>
            <p>📅 {performance_data['hebrew_date']}</p>
            <div class="nav-links">
                <a href="index.html" class="current">📊 דוח נוכחי</a>
                <a href="history.html">📈 היסטוריה</a>
                <a href="summary.html">📷 תמונת סיכום</a>
            </div>
        </div>
        
        <div class="summary-section">
            <h2 class="summary-title">סיכום התיק</h2>
            <div class="summary-cards">
                <div class="summary-card">
                    <h3>💰 ערך נוכחי</h3>
                    <div class="value">{format_currency(portfolio['current_value'])}</div>
                </div>
                <div class="summary-card">
                    <h3>🏦 השקעה מקורית</h3>
                    <div class="value">{format_currency(portfolio['original_investment'])}</div>
                </div>
                <div class="summary-card {profit_card_class}">
                    <h3>📈 רווח/הפסד</h3>
                    <div class="value {performance_color_class(portfolio['total_profit'])}">{format_currency(portfolio['total_profit'])}</div>
                    <div class="profit {performance_color_class(portfolio['total_return'])}">{format_percentage(portfolio['total_return'])}</div>
                </div>
                <div class="summary-card">
                    <h3>⏰ ימים מההשקעה</h3>
                    <div class="value">{portfolio['days_invested']}</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2 class="section-title">🏆 השוואה מול מדדי השוק</h2>
            <table class="comparison-table">
                <thead>
                    <tr>
                        <th>אסטרטגיה</th>
                        <th>השקעה</th>
                        <th>ערך נוכחי</th>
                        <th>רווח/הפסד</th>
                        <th>% תשואה</th>
                        <th>מול תיק AI</th>
                    </tr>
                </thead>
                <tbody>
                    <tr style="background-color: #e3f2fd;">
                        <td class="stock-symbol">🤖 {self.portfolio_name}</td>
                        <td class="number-cell">{format_currency(portfolio['original_investment'])}</td>
                        <td class="number-cell">{format_currency(portfolio['current_value'])}</td>
                        <td class="number-cell {performance_color_class(portfolio['total_profit'])}">{format_currency(portfolio['total_profit'])}</td>
                        <td class="number-cell {performance_color_class(portfolio['total_return'])}">{format_percentage(portfolio['total_return'])}</td>
                        <td class="number-cell">-</td>
                    </tr>"""
        
        # Add benchmark rows
        benchmark_names = {"SPY": "🇺🇸 S&P 500", "QQQ": "🚀 NASDAQ 100", "TQQQ": "⚡ NASDAQ 3x"}
        
        for symbol, data in benchmarks.items():
            outperf_data = outperformance[symbol]
            outperf_value = outperf_data['outperformance']
            badge_class = "winning" if outperf_value > 0 else "losing"
            badge_text = f"מנצח ב-{abs(outperf_value):.1f}%" if outperf_value > 0 else f"מפסיד ב-{abs(outperf_value):.1f}%"
            name = benchmark_names.get(symbol, symbol)
            
            html += f"""
                    <tr>
                        <td class="stock-symbol">{name}</td>
                        <td class="number-cell">{format_currency(data['investment'])}</td>
                        <td class="number-cell">{format_currency(data['current_value'])}</td>
                        <td class="number-cell {performance_color_class(data['profit_loss'])}">{format_currency(data['profit_loss'])}</td>
                        <td class="number-cell {performance_color_class(data['return_percent'])}">{format_percentage(data['return_percent'])}</td>
                        <td class="number-cell"><span class="outperform-badge {badge_class}">{badge_text}</span></td>
                    </tr>"""
        
        html += """
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2 class="section-title">💼 פירוט מניות התיק</h2>
            <table class="portfolio-table">
                <thead>
                    <tr>
                        <th>מניה</th>
                        <th>כמות</th>
                        <th>מחיר בסיס</th>
                        <th>מחיר נוכחי</th>
                        <th>השקעה</th>
                        <th>ערך נוכחי</th>
                        <th>רווח/הפסד</th>
                        <th>% תשואה</th>
                    </tr>
                </thead>
                <tbody>"""
        
        # Add stock rows
        for symbol, data in stocks.items():
            profit_class = performance_color_class(data['profit_loss'])
            return_class = performance_color_class(data['return_percent'])
            
            html += f"""
                    <tr>
                        <td class="stock-symbol">{symbol}</td>
                        <td class="number-cell">{data['quantity']:.2f}</td>
                        <td class="number-cell">{format_currency(data['base_price'])}</td>
                        <td class="number-cell">{format_currency(data['current_price'])}</td>
                        <td class="number-cell">{format_currency(data['investment'])}</td>
                        <td class="number-cell">{format_currency(data['current_value'])}</td>
                        <td class="number-cell {profit_class}">{format_currency(data['profit_loss'])}</td>
                        <td class="number-cell {return_class}">{format_percentage(data['return_percent'])}</td>
                    </tr>"""
        
        # Footer
        html += f"""
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>🤖 דוח זה נוצר אוטומטית</p>
            <p>עודכן: {safe_strftime(datetime.now(), '%d/%m/%Y %H:%M')}</p>
            <p>🏆 מניה מובילה: {portfolio['best_performer']['symbol']} ({portfolio['best_performer']['return']:.1f}%)</p>
            <p>📉 מניה נמוכה: {portfolio['worst_performer']['symbol']} ({portfolio['worst_performer']['return']:.1f}%)</p>
            <p style="margin-top: 15px;">
                <a href="history.html" style="color: #74b9ff; text-decoration: none;">📈 צפה בהיסטוריה המלאה</a> | 
                <a href="summary.html" style="color: #74b9ff; text-decoration: none;">📷 הורד תמונת סיכום</a>
            </p>
        </div>
    </div>
</body>
</html>"""
        
        return html
    
    def generate_history_report(self, history_data):
        """יוצר דוח היסטוריה"""
        if not history_data:
            return self._generate_empty_history_report()
        
        sorted_history = sorted(history_data, key=lambda x: x['timestamp'])
        
        html = f"""<!DOCTYPE html>
<html dir="rtl" lang="he">
<head>
    <meta charset="UTF-8">
    <title>היסטוריית {self.portfolio_name}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            direction: rtl;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding: 20px;
            background: #2c3e50;
            color: white;
            border-radius: 15px;
        }}
        .header h1 {{
            font-size: 2.5em;
            color: white;
            margin-bottom: 20px;
        }}
        .nav-links a {{
            display: inline-block;
            padding: 10px 20px;
            background: rgba(255,255,255,0.2);
            color: white;
            text-decoration: none;
            border-radius: 20px;
            margin: 0 10px;
        }}
        .nav-links a:hover {{
            background: rgba(255,255,255,0.3);
        }}
        .nav-links a.current {{
            background: rgba(255,255,255,0.4);
        }}
        .history-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        .history-table th {{
            background: #2c3e50;
            color: white;
            padding: 15px;
            text-align: center;
        }}
        .history-table td {{
            padding: 12px;
            text-align: center;
            border-bottom: 1px solid #eee;
        }}
        .positive {{ color: #10b981; }}
        .negative {{ color: #ef4444; }}
        .number-cell {{ direction: ltr; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📈 היסטוריית התיק 📊</h1>
            <div class="nav-links">
                <a href="index.html">📊 דוח נוכחי</a>
                <a href="history.html" class="current">📈 היסטוריה</a>
                <a href="summary.html">📷 תמונת סיכום</a>
            </div>
        </div>
        
        <p style="text-align: center; font-size: 1.2em; margin-bottom: 30px;">
            📊 רשומות: {len(sorted_history)}
        </p>
        
        <table class="history-table">
            <thead>
                <tr>
                    <th>תאריך</th>
                    <th>ערך התיק</th>
                    <th>רווח/הפסד</th>
                    <th>% תשואה</th>
                </tr>
            </thead>
            <tbody>"""
        
        for record in sorted_history:
            html += f"""
                <tr>
                    <td><strong>{record['date']}</strong></td>
                    <td class="number-cell">{format_currency(record['portfolio_value'])}</td>
                    <td class="number-cell {performance_color_class(record['total_profit'])}">{format_currency(record['total_profit'])}</td>
                    <td class="number-cell {performance_color_class(record['total_return'])}">{format_percentage(record['total_return'])}</td>
                </tr>"""
        
        html += f"""
            </tbody>
        </table>
        
        <div style="text-align: center; margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 10px;">
            <p>עודכן: {safe_strftime(datetime.now(), '%d/%m/%Y %H:%M')}</p>
            <p style="margin-top: 10px;">
                <a href="index.html" style="color: #2c3e50; text-decoration: none;">📊 חזור לדוח הראשי</a> | 
                <a href="summary.html" style="color: #2c3e50; text-decoration: none;">📷 תמונת סיכום</a>
            </p>
        </div>
    </div>
</body>
</html>"""
        
        return html
    
    def generate_summary_image_report(self, performance_data):
        """יוצר דוח מקוצר"""
        portfolio = performance_data['portfolio_summary']
        
        html = f"""<!DOCTYPE html>
<html dir="rtl" lang="he">
<head>
    <meta charset="UTF-8">
    <title>סיכום {self.portfolio_name}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            direction: rtl;
            width: 800px;
            height: 600px;
            margin: 0;
        }}
        .summary-container {{
            background: white;
            border-radius: 20px;
            padding: 40px;
            height: 100%;
            box-shadow: 0 20px 40px rgba(0,0,0,0.2);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .header h1 {{
            font-size: 2.5em;
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        .nav-links {{
            text-align: center;
            margin-bottom: 20px;
        }}
        .nav-links a {{
            display: inline-block;
            padding: 8px 15px;
            background: #f0f0f0;
            color: #333;
            text-decoration: none;
            border-radius: 15px;
            margin: 0 5px;
            font-size: 0.9em;
        }}
        .nav-links a.current {{
            background: #2c3e50;
            color: white;
        }}
        .main-stats {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-box {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
        .stat-box h3 {{
            color: #6c757d;
            margin-bottom: 10px;
        }}
        .stat-box .value {{
            font-size: 1.8em;
            font-weight: 700;
            direction: ltr;
        }}
        .positive {{ color: #10b981; }}
        .negative {{ color: #ef4444; }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="summary-container">
        <div class="header">
            <h1>🚀 {self.portfolio_name} 📊</h1>
            <p>📅 {performance_data['hebrew_date']}</p>
        </div>
        
        <div class="nav-links">
            <a href="index.html">📊 דוח נוכחי</a>
            <a href="history.html">📈 היסטוריה</a>
            <a href="summary.html" class="current">📷 תמונת סיכום</a>
        </div>
        
        <div class="main-stats">
            <div class="stat-box">
                <h3>💎 ערך נוכחי</h3>
                <div class="value">{format_currency(portfolio['current_value'])}</div>
            </div>
            <div class="stat-box">
                <h3>📈 רווח/הפסד</h3>
                <div class="value {performance_color_class(portfolio['total_profit'])}">{format_currency(portfolio['total_profit'])}</div>
                <div class="{performance_color_class(portfolio['total_return'])}" style="font-size: 1.2em; margin-top: 5px;">
                    {format_percentage(portfolio['total_return'])}
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>🤖 דוח אוטומטי • ⏰ {portfolio['days_invested']} ימים מההשקעה</p>
            <p style="margin-top: 10px; font-size: 0.9em;">📷 תמונה מותאמת לשיתוף</p>
        </div>
    </div>
</body>
</html>"""
        
        return html
    
    def _generate_empty_history_report(self):
        """דוח היסטוריה ריק"""
        return f"""<!DOCTYPE html>
<html dir="rtl" lang="he">
<head>
    <meta charset="UTF-8">
    <title>היסטוריית {self.portfolio_name}</title>
</head>
<body style="font-family: Arial; padding: 40px; text-align: center; direction: rtl; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); margin: 0; min-height: 100vh;">
    <div style="background: white; border-radius: 20px; padding: 60px; max-width: 600px; margin: 0 auto; box-shadow: 0 20px 40px rgba(0,0,0,0.1);">
        <h1 style="color: #2c3e50; margin-bottom: 20px;">📈 היסטוריית התיק 📊</h1>
        <div style="margin-bottom: 30px;">
            <a href="index.html" style="display: inline-block; padding: 10px 20px; background: #2c3e50; color: white; text-decoration: none; border-radius: 20px; margin: 0 10px;">📊 דוח נוכחי</a>
            <a href="summary.html" style="display: inline-block; padding: 10px 20px; background: #2c3e50; color: white; text-decoration: none; border-radius: 20px; margin: 0 10px;">📷 תמונת סיכום</a>
        </div>
        <p style="font-size: 1.5em; color: #666; margin: 40px 0;">ההיסטוריה תתצבר עם הזמן 📊</p>
        <p style="color: #999;">הפעל את המערכת מספר פעמים כדי לבנות היסטוריה</p>
    </div>
</body>
</html>"""