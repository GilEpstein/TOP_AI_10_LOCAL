#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
יצירת דוחות HTML לתיק TOP AI 10
"""

import os
from datetime import datetime
import config
import plotly.graph_objects as go
import pandas as pd

# --- פונקציות עזר לעיצוב וטיפול בנתונים ---

def safe_strftime(dt, format_str):
    """פונקציה בטוחה לעיצוב תאריך"""
    try:
        return dt.strftime(format_str)
    except UnicodeEncodeError:
        return dt.strftime('%d/%m/%Y %H:%M')

def performance_color_class(value):
    """מחזיר מחלקת CSS לצבע לפי ביצועים"""
    if value is None: # Handle None values for color class gracefully
        return "neutral"
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
    
    # Check if the value is negative and format accordingly
    if value < 0:
        return f"-${abs(value):,.2f}"
    elif value > 0:
        return f"+${value:,.2f}"
    else: # value == 0
        return f"${value:,.2f}"

def format_percentage(value):
    """מעצב ערך כאחוז עם בדיקת מינוס/פלוס בצד שמאל."""
    if value is None:
        return "-"
    
    # Check if the value is negative and format accordingly
    if value < 0:
        return f"-{abs(value):.2f}%"
    elif value > 0:
        return f"+{value:.2f}%"
    else: # value == 0
        return f"{value:.2f}%"

class ReportGenerator:
    def __init__(self):
        pass

    def generate_main_report(self, data):
        """
        מייצר את דוח ה-HTML הראשי של ביצועי התיק.
        """
        date = data['date']
        timestamp = datetime.fromisoformat(data['timestamp'])
        portfolio_value = data['portfolio_value']
        total_profit = data['total_profit']
        total_return = data['total_return']
        days_invested = data['days_invested']
        outperformance = data['outperformance']
        stocks_performance = data['stocks_performance']
        
        # Extract benchmark prices from the 'data' dictionary
        benchmarks_current_prices = data.get('benchmarks_current_prices', {})
        benchmarks_base_prices = data.get('benchmarks_base_prices', {})

        html_content = f"""
        <!DOCTYPE html>
        <html lang="he" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>דוח ביצועי תיק - {config.PORTFOLIO_NAME}</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #f4f7f6;
                    color: #333;
                    line-height: 1.6;
                }}
                .container {{
                    max-width: 900px;
                    margin: 30px auto;
                    background-color: #ffffff;
                    padding: 30px 40px;
                    border-radius: 12px;
                    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
                    border-top: 5px solid #007bff;
                }}
                h1, h2, h3 {{
                    color: #007bff;
                    text-align: center;
                    margin-bottom: 25px;
                    font-weight: 600;
                }}
                .header-info {{
                    text-align: center;
                    margin-bottom: 30px;
                    font-size: 1.1em;
                    color: #555;
                }}
                .main-metrics {{
                    display: flex;
                    justify-content: space-around;
                    flex-wrap: wrap;
                    gap: 20px;
                    margin-bottom: 40px;
                    text-align: center;
                }}
                .metric-box {{
                    background-color: #e0f2f7;
                    padding: 20px;
                    border-radius: 8px;
                    flex: 1;
                    min-width: 200px;
                    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
                }}
                .metric-box h3 {{
                    color: #0056b3;
                    margin-top: 0;
                    font-size: 1.2em;
                }}
                .metric-box .value {{
                    font-size: 2.2em;
                    font-weight: bold;
                    color: #007bff;
                    display: block;
                    margin-top: 5px;
                }}
                .positive {{ color: #28a745; }}
                .negative {{ color: #dc3545; }}
                .neutral {{ color: #6c757d; }}

                .stocks-table, .benchmarks-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 30px;
                    margin-bottom: 40px;
                    text-align: right;
                }}
                .stocks-table th, .benchmarks-table th {{
                    background-color: #007bff;
                    color: white;
                    padding: 12px 15px;
                    border: 1px solid #ddd;
                    text-align: center;
                }}
                .stocks-table td, .benchmarks-table td {{
                    padding: 10px 15px;
                    border: 1px solid #eee;
                    text-align: center;
                }}
                .stocks-table tbody tr:nth-child(even), .benchmarks-table tbody tr:nth-child(even) {{
                    background-color: #f8f8f8;
                }}
                .links {{
                    text-align: center;
                    margin-top: 40px;
                    margin-bottom: 20px;
                }}
                .links a {{
                    display: inline-block;
                    margin: 0 15px;
                    padding: 10px 20px;
                    background-color: #007bff;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    transition: background-color 0.3s ease;
                }}
                .links a:hover {{
                    background-color: #0056b3;
                }}
                .disclaimer {{
                    font-size: 0.9em;
                    color: #777;
                    text-align: center;
                    margin-top: 30px;
                    padding-top: 15px;
                    border-top: 1px solid #eee;
                }}
                .footer {{
                    text-align: center;
                    font-size: 0.85em;
                    color: #888;
                    margin-top: 20px;
                    padding-bottom: 10px;
                }}
                .comparison-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                    gap: 20px;
                    justify-content: center;
                }}
                .comparison-item {{
                    background-color: #e0f7fa;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.07);
                    text-align: center;
                }}
                .comparison-item h3 {{
                    color: #007bff;
                    margin-top: 0;
                    font-size: 1.3em;
                }}
                .comparison-item p {{
                    margin: 8px 0;
                }}
                .comparison-item .value {{
                    font-size: 1.8em;
                    font-weight: bold;
                }}
                /* New styles for base/current price display */
                .price-info {{
                    font-size: 0.75em; /* Smaller font for prices */
                    color: #666;
                    margin-top: 5px;
                    line-height: 1.2;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>דוח ביצועי תיק {config.PORTFOLIO_NAME}</h1>
                <div class="header-info">
                    <p>תאריך הדוח: {safe_strftime(timestamp, '%d/%m/%Y %H:%M')}</p>
                    <p>תאריך בסיס ההשקעה: {config.BASE_DATE}</p>
                    <p>ימים שהושקעו: {days_invested}</p>
                </div>

                <div class="main-metrics">
                    <div class="metric-box">
                        <h3>שווי תיק נוכחי</h3>
                        <span class="value">{format_currency(portfolio_value)}</span>
                    </div>
                    <div class="metric-box">
                        <h3>רווח / הפסד כולל</h3>
                        <span class="value {performance_color_class(total_profit)}">{format_currency(total_profit)}</span>
                    </div>
                    <div class="metric-box">
                        <h3>תשואה כוללת</h3>
                        <span class="value {performance_color_class(total_return)}">{format_percentage(total_return)}</span>
                    </div>
                </div>

                <h2>ביצועי מניות בודדות</h2>
                <table class="stocks-table">
                    <thead>
                        <tr>
                            <th>סימבול</th>
                            <th>כמות יחידות</th>
                            <th>מחיר בסיס</th>
                            <th>מחיר נוכחי</th>
                            <th>שווי נוכחי</th>
                            <th>רווח/הפסד</th>
                            <th>תשואה %</th>
                        </tr>
                    </thead>
                    <tbody>
                        {"".join([
                            f"""
                            <tr>
                                <td>{stock['symbol']}</td>
                                <td>{stock['quantity']:.2f}</td>
                                <td>{format_currency(stock['base_price'])}</td>
                                <td>{format_currency(stock['current_price'])}</td>
                                <td>{format_currency(stock['current_value'])}</td>
                                <td class="{performance_color_class(stock['profit_loss'])}">{format_currency(stock['profit_loss'])}</td>
                                <td class="{performance_color_class(stock['percentage_return'])}">{format_percentage(stock['percentage_return'])}</td>
                            </tr>
                            """ for stock in stocks_performance
                        ])}
                    </tbody>
                </table>

                <h2 style="margin-top: 40px; color: #007bff;">תשואה עודפת מול מדדי ייחוס</h2>
                <div class="comparison-grid">
        """
        for symbol, data_outperformance in outperformance.items():
            benchmark_return = data_outperformance['benchmark_return']
            portfolio_return = data_outperformance['portfolio_return']
            outperf = data_outperformance['outperformance']

            # Get base and current prices for the benchmark
            base_price_benchmark = benchmarks_base_prices.get(symbol)
            current_price_benchmark = benchmarks_current_prices.get(symbol)
            
            price_info_html = ""
            if base_price_benchmark is not None and current_price_benchmark is not None:
                price_info_html = f"""
                <p class="price-info">בסיס: {format_currency(base_price_benchmark)} | נוכחי: {format_currency(current_price_benchmark)}</p>
                """

            html_content += f"""
                    <div class="comparison-item">
                        <h3>{symbol}</h3>
                        <p style="font-size: 1em;">תשואת מדד: <span class="{performance_color_class(benchmark_return)}">{format_percentage(benchmark_return)}</span></p>
                        {price_info_html} <p style="font-size: 1.0em;">תשואת תיק: <span class="{performance_color_class(portfolio_return)}">{format_percentage(portfolio_return)}</span></p>
                        <p style="font-size: 1.4em; font-weight: bold;">תשואה עודפת: <span class="value {performance_color_class(outperf)}">{format_percentage(outperf)}</span></p>
                    </div>
            """
        html_content += """
                </div>
            </div>
            <div class="links">
                <a href="index.html">🏠 דף הבית</a>
                <a href="history.html">📈 היסטוריית תיק</a>
                <a href="summary.html">📸 סיכום לשיתוף</a>
                <a href="graphs.html">📊 גרפים</a>
            </div>
        
                <div class="disclaimer">
                    <p>הערה: נתוני הביצועים והמדדים המוצגים בדוח זה הם לצרכים אינפורמטיביים ואינם מהווים ייעוץ פיננסי.</p>
                </div>
                <div class="footer">
                    דו"ח זה נוצר אוטומטית על ידי מערכת מעקב התיקים של TOP AI 10. &copy; 2025.
                </div>
            </body>
        </html>
        """
        return html_content

    def generate_history_report(self, history_data):
        """
        מייצר את דוח ה-HTML המציג את היסטוריית ביצועי התיק.
        """
        history_rows = ""
        # iterate in reverse order to show most recent first
        for entry in sorted(history_data, key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'), reverse=True):
            date_formatted = datetime.strptime(entry['date'], '%Y-%m-%d').strftime('%d %B %Y')
            
            # Ensure safe access to nested keys, provide default values
            portfolio_value = entry.get('portfolio_value', 0)
            total_profit = entry.get('total_profit', 0)
            total_return = entry.get('total_return', 0)
            days_invested = entry.get('days_invested', 0)
            
            benchmarks = entry.get('benchmarks_returns', {})
            spy_return = benchmarks.get('SPY', None)
            qqq_return = benchmarks.get('QQQ', None)
            tqqq_return = benchmarks.get('TQQQ', None)

            history_rows += f"""
                    <tr>
                        <td>{date_formatted}</td>
                        <td>{format_currency(portfolio_value)}</td>
                        <td class="{performance_color_class(total_profit)}">{format_currency(total_profit)}</td>
                        <td class="{performance_color_class(total_return)}">{format_percentage(total_return)}</td>
                        <td>{days_invested}</td>
                        <td class="{performance_color_class(spy_return)}">{format_percentage(spy_return)}</td>
                        <td class="{performance_color_class(qqq_return)}">{format_percentage(qqq_return)}</td>
                        <td class="{performance_color_class(tqqq_return)}">{format_percentage(tqqq_return)}</td>
                    </tr>
            """

        html_content = f"""
        <!DOCTYPE html>
        <html lang="he" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>היסטוריית ביצועי תיק - {config.PORTFOLIO_NAME}</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #f4f7f6;
                    color: #333;
                    line-height: 1.6;
                }}
                .container {{
                    max-width: 900px;
                    margin: 30px auto;
                    background-color: #ffffff;
                    padding: 30px 40px;
                    border-radius: 12px;
                    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
                    border-top: 5px solid #007bff;
                }}
                h1, h2, h3 {{
                    color: #007bff;
                    text-align: center;
                    margin-bottom: 25px;
                    font-weight: 600;
                }}
                .header-info {{
                    text-align: center;
                    margin-bottom: 30px;
                    font-size: 1.1em;
                    color: #555;
                }}
                .history-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 30px;
                    margin-bottom: 40px;
                    text-align: right;
                }}
                .history-table th {{
                    background-color: #007bff;
                    color: white;
                    padding: 12px 15px;
                    border: 1px solid #ddd;
                    text-align: center;
                }}
                .history-table td {{
                    padding: 10px 15px;
                    border: 1px solid #eee;
                    text-align: center;
                }}
                .history-table tbody tr:nth-child(even) {{
                    background-color: #f8f8f8;
                }}
                .positive {{ color: #28a745; }}
                .negative {{ color: #dc3545; }}
                .neutral {{ color: #6c757d; }}
                .links {{
                    text-align: center;
                    margin-top: 40px;
                    margin-bottom: 20px;
                }}
                .links a {{
                    display: inline-block;
                    margin: 0 15px;
                    padding: 10px 20px;
                    background-color: #007bff;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    transition: background-color 0.3s ease;
                }}
                .links a:hover {{
                    background-color: #0056b3;
                }}
                .disclaimer {{
                    font-size: 0.9em;
                    color: #777;
                    text-align: center;
                    margin-top: 30px;
                    padding-top: 15px;
                    border-top: 1px solid #eee;
                }}
                .footer {{
                    text-align: center;
                    font-size: 0.85em;
                    color: #888;
                    margin-top: 20px;
                    padding-bottom: 10px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>היסטוריית ביצועי תיק {config.PORTFOLIO_NAME}</h1>
                <div class="header-info">
                    <p>מציג את ביצועי התיק לאורך זמן.</p>
                </div>

                <table class="history-table">
                    <thead>
                        <tr>
                            <th>תאריך</th>
                            <th>שווי תיק</th>
                            <th>רווח/הפסד</th>
                            <th>תשואה %</th>
                            <th>ימים הושקעו</th>
                            <th>SPY תשואה %</th>
                            <th>QQQ תשואה %</th>
                            <th>TQQQ תשואה %</th>
                        </tr>
                    </thead>
                    <tbody>
                        {history_rows}
                    </tbody>
                </table>

                <div class="links">
                    <a href="index.html">🏠 דף הבית</a>
                    <a href="history.html">📈 היסטוריית תיק</a>
                    <a href="summary.html">📸 סיכום לשיתוף</a>
                    <a href="graphs.html">📊 גרפים</a>
                </div>
            
                <div class="disclaimer">
                    <p>הערה: נתוני הביצועים והמדדים המוצגים בדוח זה הם לצרכים אינפורמטיביים ואינם מהווים ייעוץ פיננסי.</p>
                </div>
                <div class="footer">
                    דו"ח זה נוצר אוטומטית על ידי מערכת מעקב התיקים של TOP AI 10. &copy; 2025.
                </div>
            </body>
        </html>
        """
        return html_content

    def generate_summary_image_report(self, data):
        """
        מייצר דוח HTML פשוט המיועד לצילום מסך/שיתוף, עם סיכום ביצועים בלבד.
        """
        date = data['date']
        timestamp = datetime.fromisoformat(data['timestamp'])
        total_return = data['total_return']
        outperformance = data['outperformance']
        
        # Get base and current prices for the benchmark for summary
        benchmarks_current_prices = data.get('benchmarks_current_prices', {})
        benchmarks_base_prices = data.get('benchmarks_base_prices', {})

        html_content = f"""
        <!DOCTYPE html>
        <html lang="he" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>סיכום לשיתוף - {config.PORTFOLIO_NAME}</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #f4f7f6;
                    color: #333;
                    line-height: 1.6;
                }}
                .container {{
                    max-width: 900px;
                    margin: 30px auto;
                    background-color: #ffffff;
                    padding: 30px 40px;
                    border-radius: 12px;
                    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
                    border-top: 5px solid #007bff;
                }}
                h1, h2, h3 {{
                    color: #007bff;
                    text-align: center;
                    margin-bottom: 25px;
                    font-weight: 600;
                }}
                .header-info {{
                    text-align: center;
                    margin-bottom: 30px;
                    font-size: 1.1em;
                    color: #555;
                }}
                .main-metrics {{
                    display: flex;
                    justify-content: space-around;
                    flex-wrap: wrap;
                    gap: 20px;
                    margin-bottom: 40px;
                    text-align: center;
                }}
                .metric-box {{
                    background-color: #e0f2f7;
                    padding: 20px;
                    border-radius: 8px;
                    flex: 1;
                    min-width: 200px;
                    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
                }}
                .metric-box h3 {{
                    color: #0056b3;
                    margin-top: 0;
                    font-size: 1.2em;
                }}
                .metric-box .value {{
                    font-size: 2.2em;
                    font-weight: bold;
                    color: #007bff;
                    display: block;
                    margin-top: 5px;
                }}
                .positive {{ color: #28a745; }}
                .negative {{ color: #dc3545; }}
                .neutral {{ color: #6c757d; }}
                .comparison-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                    gap: 20px;
                    justify-content: center;
                }}
                .comparison-item {{
                    background-color: #e0f7fa;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.07);
                    text-align: center;
                }}
                .comparison-item h3 {{
                    color: #007bff;
                    margin-top: 0;
                    font-size: 1.3em;
                }}
                .comparison-item p {{
                    margin: 8px 0;
                }}
                .comparison-item .value {{
                    font-size: 1.8em;
                    font-weight: bold;
                }}
                .links {{
                    text-align: center;
                    margin-top: 40px;
                    margin-bottom: 20px;
                }}
                .links a {{
                    display: inline-block;
                    margin: 0 15px;
                    padding: 10px 20px;
                    background-color: #007bff;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    transition: background-color 0.3s ease;
                }}
                .links a:hover {{
                    background-color: #0056b3;
                }}
                .disclaimer {{
                    font-size: 0.9em;
                    color: #777;
                    text-align: center;
                    margin-top: 30px;
                    padding-top: 15px;
                    border-top: 1px solid #eee;
                }}
                .footer {{
                    text-align: center;
                    font-size: 0.85em;
                    color: #888;
                    margin-top: 20px;
                    padding-bottom: 10px;
                }}
                /* New styles for base/current price display */
                .price-info {{
                    font-size: 0.75em; /* Smaller font for prices */
                    color: #666;
                    margin-top: 5px;
                    line-height: 1.2;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>סיכום ביצועים - {config.PORTFOLIO_NAME}</h1>
                <div class="header-info">
                    <p>תאריך הדוח: {safe_strftime(timestamp, '%d/%m/%Y %H:%M')}</p>
                </div>

                <div class="main-metrics">
                    <div class="metric-box" style="flex: none; width: 80%;">
                        <h3>תשואה כוללת של התיק</h3>
                        <span class="value {performance_color_class(total_return)}">{format_percentage(total_return)}</span>
                    </div>
                </div>

                <h2 style="margin-top: 40px; color: #007bff;">השוואה למדדי ייחוס</h2>
                <div class="comparison-grid">
        """
        for symbol, data_outperformance in outperformance.items():
            benchmark_return = data_outperformance['benchmark_return']
            portfolio_return = data_outperformance['portfolio_return']
            outperf = data_outperformance['outperformance']

            # Get base and current prices for the benchmark for summary
            base_price_benchmark = benchmarks_base_prices.get(symbol)
            current_price_benchmark = benchmarks_current_prices.get(symbol)
            
            price_info_html = ""
            if base_price_benchmark is not None and current_price_benchmark is not None:
                price_info_html = f"""
                <p class="price-info">בסיס: {format_currency(base_price_benchmark)} | נוכחי: {format_currency(current_price_benchmark)}</p>
                """

            html_content += f"""
                    <div class="comparison-item" style="padding: 15px;">
                        <h3>{symbol}</h3>
                        <p style="font-size: 1em;">תשואת מדד: <span class="{performance_color_class(benchmark_return)}">{format_percentage(benchmark_return)}</span></p>
                        {price_info_html} <p style="font-size: 1.0em;">תשואת תיק: <span class="{performance_color_class(portfolio_return)}">{format_percentage(portfolio_return)}</span></p>
                        <p style="font-size: 1.4em; font-weight: bold;">תשואה עודפת: <span class="value {performance_color_class(outperf)}">{format_percentage(outperf)}</span></p>
                    </div>
            """
        html_content += """
                </div>
            </div>
            <div class="links">
                <a href="index.html">🏠 דף הבית</a>
                <a href="history.html">📈 היסטוריית תיק</a>
                <a href="summary.html">📸 סיכום לשיתוף</a>
                <a href="graphs.html">📊 גרפים</a>
            </div>
        
                <div class="disclaimer">
                    <p>הערה: נתוני הביצועים והמדדים המוצגים בדוח זה הם לצרכים אינפורמטיביים ואינם מהווים ייעוץ פיננסי.</p>
                </div>
                <div class="footer">
                    דו"ח זה נוצר אוטומטית על ידי מערכת מעקב התיקים של TOP AI 10. &copy; 2025.
                </div>
            </body>
        </html>
        """
        return html_content

    def generate_graphs_report(self, history_data):
        """
        מייצר דוח HTML המכיל גרפים אינטראקטיביים של ביצועי התיק והמדדים לאורך זמן.
        """
        # Ensure data is sorted by date for correct plotting
        sorted_history = sorted(history_data, key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'))

        dates = [entry['date'] for entry in sorted_history]
        portfolio_returns = [entry['total_return'] for entry in sorted_history]
        spy_returns = [entry['benchmarks_returns'].get('SPY', None) for entry in sorted_history]
        qqq_returns = [entry['benchmarks_returns'].get('QQQ', None) for entry in sorted_history]
        tqqq_returns = [entry['benchmarks_returns'].get('TQQQ', None) for entry in sorted_history]

        # Convert None to NaN for Plotly to handle missing data gracefully
        df = pd.DataFrame({
            'Date': dates,
            'Portfolio': portfolio_returns,
            'SPY': spy_returns,
            'QQQ': qqq_returns,
            'TQQQ': tqqq_returns
        }).set_index('Date')
        
        # Plotting Portfolio Performance
        fig_portfolio = go.Figure()
        fig_portfolio.add_trace(go.Scatter(x=df.index, y=df['Portfolio'], mode='lines+markers', name='תשואת תיק'))
        fig_portfolio.update_layout(
            title={'text': 'התפתחות ביצועי תיק לאורך זמן', 'x':0.5},
            xaxis_title='תאריך',
            yaxis_title='תשואה (%)',
            hovermode="x unified",
            height=600,
            font=dict(family="Segoe UI, Tahoma, Geneva, Verdana, sans-serif", size=12, color="#333"),
            legend_title_text='מקרא'
        )
        
        # Plotting Portfolio vs Benchmarks
        fig_comparison = go.Figure()
        fig_comparison.add_trace(go.Scatter(x=df.index, y=df['Portfolio'], mode='lines+markers', name='תיק TOP AI 10'))
        fig_comparison.add_trace(go.Scatter(x=df.index, y=df['SPY'], mode='lines+markers', name='SPY'))
        fig_comparison.add_trace(go.Scatter(x=df.index, y=df['QQQ'], mode='lines+markers', name='QQQ'))
        fig_comparison.add_trace(go.Scatter(x=df.index, y=df['TQQQ'], mode='lines+markers', name='TQQQ'))
        fig_comparison.update_layout(
            title={'text': 'השוואת ביצועי תיק ומדדים לאורך זמן', 'x':0.5},
            xaxis_title='תאריך',
            yaxis_title='ערך / תשואה (%)',
            hovermode="x unified",
            height=600,
            font=dict(family="Segoe UI, Tahoma, Geneva, Verdana, sans-serif", size=12, color="#333"),
            legend_title_text='מקרא'
        )

        plot_portfolio_div = fig_portfolio.to_html(full_html=False, include_plotlyjs='cdn')
        plot_comparison_div = fig_comparison.to_html(full_html=False, include_plotlyjs='cdn')


        html_content = f"""
        <!DOCTYPE html>
        <html lang="he" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>גרפים - {config.PORTFOLIO_NAME}</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #f4f7f6;
                    color: #333;
                    line-height: 1.6;
                }}
                .container {{
                    max-width: 900px;
                    margin: 30px auto;
                    background-color: #ffffff;
                    padding: 30px 40px;
                    border-radius: 12px;
                    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
                    border-top: 5px solid #007bff;
                }}
                h1, h2, h3 {{
                    color: #007bff;
                    text-align: center;
                    margin-bottom: 25px;
                    font-weight: 600;
                }}
                .header-info {{
                    text-align: center;
                    margin-bottom: 30px;
                    font-size: 1.1em;
                    color: #555;
                }}
                .links {{
                    text-align: center;
                    margin-top: 40px;
                    margin-bottom: 20px;
                }}
                .links a {{
                    display: inline-block;
                    margin: 0 15px;
                    padding: 10px 20px;
                    background-color: #007bff;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    transition: background-color 0.3s ease;
                }}
                .links a:hover {{
                    background-color: #0056b3;
                }}
                .disclaimer {{
                    font-size: 0.9em;
                    color: #777;
                    text-align: center;
                    margin-top: 30px;
                    padding-top: 15px;
                    border-top: 1px solid #eee;
                }}
                .footer {{
                    text-align: center;
                    font-size: 0.85em;
                    color: #888;
                    margin-top: 20px;
                    padding-bottom: 10px;
                }}
                .chart-container {{
                    margin-bottom: 40px;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    padding: 15px;
                    background-color: #fff;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>גרפים - {config.PORTFOLIO_NAME}</h1>
                <div class="header-info">
                    <p>הצגה חזותית של ביצועי התיק והשוואות למדדים לאורך זמן.</p>
                </div>

                <div class="chart-container">
                    <h2>התפתחות ביצועי התיק</h2>
                    {plot_portfolio_div}
                </div>

                <div class="chart-container">
                    <h2>השוואת ביצועים למדדי ייחוס</h2>
                    {plot_comparison_div}
                </div>

            </div>
            <div class="links">
                <a href="index.html">🏠 דף הבית</a>
                <a href="history.html">📈 היסטוריית תיק</a>
                <a href="summary.html">📸 סיכום לשיתוף</a>
                <a href="graphs.html">📊 גרפים</a>
            </div>
        
                <div class="disclaimer">
                    <p>הערה: נתוני הביצועים והמדדים המוצגים בדוח זה הם לצרכים אינפורמטיביים ואינם מהווים ייעוץ פיננסי.</p>
                </div>
                <div class="footer">
                    דו"ח זה נוצר אוטומטית על ידי מערכת מעקב התיקים של TOP AI 10. &copy; 2025.
                </div>
            </body>
        </html>
        """
        return html_content