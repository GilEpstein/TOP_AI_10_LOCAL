#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
יצירת דוחות HTML לתיק TOP AI 10
"""

import os
from datetime import datetime
import config
import plotly.graph_objects as go
import plotly.io as pio # ייבוא חדש עבור plotly.io
import pandas as pd

# --- פונקציות עזר לעיצוב וטיפול בנתונים ---

def safe_strftime(dt, format_str):
    """פונקציה בטוחה לעיצוב תאריך"""
    try:
        return dt.strftime(format_str)
    except UnicodeEncodeError:
        # Fallback to a safe, purely numeric format in case of encoding issues
        return dt.strftime('%d/%m/%Y %H:%M')

def performance_color_class(value):
    """מחזיר מחלקת CSS לצבע לפי ביצועים"""
    if value is None:
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
    if value >= 0:
        return f"+${value:,.2f}"
    else:
        return f"-$%s" % f"{abs(value):,.2f}"

def format_percentage(value):
    """מעצב ערך כאחוזים עם סימן +/- ובדיקת מינוס/פלוס."""
    if value is None:
        return "-"
    if value > 0:
        return f"+{value:,.2f}%"
    else:
        return f"{value:,.2f}%"

class ReportGenerator:
    def __init__(self):
        self.portfolio_name = config.PORTFOLIO_NAME
        self.base_date = config.BASE_DATE # **חדש: תאריך הבסיס נלקח מקונפיג**

    def _get_base_html(self, title, extra_head_content=""):
        """מחזיר את מבנה ה-HTML הבסיסי."""
        return f"""
        <!DOCTYPE html>
        <html lang="he" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title} - {self.portfolio_name}</title>
            <style>
                /* סגנונות CSS */
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
                    padding-bottom: 20px;
                    border-bottom: 1px solid #eee;
                }}
                .header-info p {{
                    margin: 5px 0;
                    font-size: 1.1em;
                    color: #555;
                }}
                .main-metrics {{
                    display: flex;
                    justify-content: space-around;
                    flex-wrap: wrap;
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                .metric-box {{
                    background-color: #e9f5ff;
                    border: 1px solid #cce5ff;
                    border-radius: 8px;
                    padding: 20px;
                    text-align: center;
                    flex: 1;
                    min-width: 200px;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
                }}
                .metric-box h3 {{
                    margin-top: 0;
                    color: #0056b3;
                    font-size: 1.2em;
                }}
                .metric-box .value {{
                    font-size: 2.2em;
                    font-weight: 700;
                    color: #007bff;
                    margin-top: 10px;
                }}
                .positive {{
                    color: #28a745; /* ירוק */
                }}
                .negative {{
                    color: #dc3545; /* אדום */
                }}
                .neutral {{
                    color: #6c757d; /* אפור */
                }}
                .stock-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 30px;
                }}
                .stock-table th, .stock-table td {{
                    border: 1px solid #ddd;
                    padding: 12px;
                    text-align: left;
                }}
                .stock-table th {{
                    background-color: #f8f9fa;
                    color: #495057;
                    font-weight: 600;
                }}
                .stock-table tr:nth-child(even) {{
                    background-color: #f2f2f2;
                }}
                .stock-table tr:hover {{
                    background-color: #e9e9e9;
                }}
                .stock-table td:first-child {{
                    font-weight: bold;
                }}
                .comparison-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin-top: 30px;
                    text-align: center;
                }}
                .comparison-item {{
                    background-color: #f0f8ff;
                    border: 1px solid #d4eeff;
                    border-radius: 8px;
                    padding: 15px;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
                }}
                .comparison-item h3 {{
                    color: #0056b3;
                    margin-top: 0;
                }}
                .comparison-item .value {{
                    font-size: 1.8em;
                    font-weight: 700;
                }}
                .links {{
                    text-align: center;
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
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
                    text-align: center;
                    font-size: 0.9em;
                    color: #777;
                    margin-top: 50px;
                    padding-top: 20px;
                    border-top: 1px dashed #ddd;
                }}
                .footer {{
                    text-align: center;
                    font-size: 0.8em;
                    color: #999;
                    margin-top: 20px;
                    padding-top: 10px;
                    border-top: 1px solid #eee;
                }}
                /* סגנונות ספציפיים לדף הסיכום (תמונה) */
                .summary-container {{
                    max-width: 600px;
                    margin: 30px auto;
                    background-color: #ffffff;
                    padding: 30px;
                    border-radius: 12px;
                    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
                    border-top: 5px solid #007bff;
                    text-align: center; /* כדי למרכז את התוכן */
                }}
                .summary-header {{
                    font-size: 1.8em;
                    font-weight: bold;
                    color: #007bff;
                    margin-bottom: 20px;
                }}
                .summary-metric {{
                    margin-bottom: 15px;
                }}
                .summary-metric .label {{
                    font-size: 1.1em;
                    color: #555;
                }}
                .summary-metric .value {{
                    font-size: 2.5em;
                    font-weight: bold;
                    margin-top: 5px;
                }}
                .share-button {{
                    background-color: #28a745;
                    color: white;
                    padding: 12px 25px;
                    border-radius: 5px;
                    text-decoration: none;
                    font-size: 1.2em;
                    margin-top: 30px;
                    display: inline-block;
                }}
                .share-button:hover {{
                    background-color: #218838;
                }}
                .screenshot-instructions {{
                    font-size: 0.9em;
                    color: #777;
                    margin-top: 20px;
                }}
                /* סגנונות לגרפים */
                .chart-container {{
                    margin-top: 30px;
                    background-color: #fff;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
                }}
            </style>
            {extra_head_content}
        </head>
        <body>
            <div class="container">
        """

    def _get_footer_html(self):
        """מחזיר את קטע ה-HTML של הפוטר."""
        current_year = datetime.now().year
        return f"""
                <div class="disclaimer">
                    <p>הערה: נתוני הביצועים והמדדים המוצגים בדוח זה הם לצרכים אינפורמטיביים ואינם מהווים ייעוץ פיננסי.</p>
                </div>
                <div class="footer">
                    דו"ח זה נוצר אוטומטית על ידי מערכת מעקב התיקים של {self.portfolio_name}. &copy; {current_year}
                </div>
            </div>
        </body>
        </html>
        """

    def generate_main_report(self, current_performance):
        """מייצר את הדוח הראשי (index.html)."""
        html_content = self._get_base_html("דוח ביצועי תיק")

        # Extract data for display
        portfolio_value = format_currency(current_performance['portfolio_value'])
        total_profit = format_currency(current_performance['total_profit'])
        total_return = format_percentage(current_performance['total_return'])
        days_invested = current_performance['days_invested']
        date_str = datetime.strptime(current_performance['date'], '%Y-%m-%d').strftime('%d/%m/%Y')
        timestamp_dt = datetime.fromisoformat(current_performance['timestamp'])
        time_str = safe_strftime(timestamp_dt, '%H:%M')

        html_content += f"""
                <h1>דוח ביצועי תיק - {self.portfolio_name}</h1>
                <div class="header-info">
                    <p>נכון לתאריך: {date_str} בשעה: {time_str}</p>
                    <p>השוואה לתאריך התחלה: {datetime.strptime(self.base_date, '%Y-%m-%d').strftime('%d/%m/%Y')}</p>
                    <p>ימים שהושקעו: {days_invested}</p>
                </div>

                <div class="main-metrics">
                    <div class="metric-box">
                        <h3>שווי תיק נוכחי</h3>
                        <p class="value">{portfolio_value}</p>
                    </div>
                    <div class="metric-box">
                        <h3>סה"כ רווח/הפסד</h3>
                        <p class="value {performance_color_class(current_performance['total_profit'])}">{total_profit}</p>
                    </div>
                    <div class="metric-box">
                        <h3>תשואה כוללת</h3>
                        <p class="value {performance_color_class(current_performance['total_return'])}">{total_return}</p>
                    </div>
                </div>

                <h2>ביצועי מניות בודדות</h2>
                <table class="stock-table">
                    <thead>
                        <tr>
                            <th>סימבול</th>
                            <th>מחיר בסיס</th>
                            <th>מחיר נוכחי</th>
                            <th>כמות</th>
                            <th>השקעה מקורית</th>
                            <th>שווי נוכחי</th>
                            <th>רווח/הפסד</th>
                            <th>תשואה %</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        for stock in current_performance['stocks_performance']:
            html_content += f"""
                        <tr>
                            <td>{stock['symbol']}</td>
                            <td>{format_currency(stock['base_price'])}</td>
                            <td>{format_currency(stock['current_price'])}</td>
                            <td>{stock['quantity']:.4f}</td>
                            <td>{format_currency(stock['investment_amount'])}</td>
                            <td>{format_currency(stock['current_value'])}</td>
                            <td class="{performance_color_class(stock['profit_loss'])}">{format_currency(stock['profit_loss'])}</td>
                            <td class="{performance_color_class(stock['percentage_return'])}">{format_percentage(stock['percentage_return'])}</td>
                        </tr>
            """
        html_content += """
                    </tbody>
                </table>

                <h2 style="margin-top: 40px; color: #007bff;">תשואה עודפת מול מדדי ייחוס</h2>
                <div class="comparison-grid">
        """
        outperformance_data = current_performance.get('outperformance', {})
        for symbol, data in outperformance_data.items():
            html_content += f"""
                    <div class="comparison-item">
                        <h3>{symbol}</h3>
                        <p>תשואת מדד: <span class="{performance_color_class(data['benchmark_return'])}">{format_percentage(data['benchmark_return'])}</span></p>
                        <p>תשואת תיק: <span class="{performance_color_class(data['portfolio_return'])}">{format_percentage(data['portfolio_return'])}</span></p>
                        <p class="value {performance_color_class(data['outperformance'])}">תשואה עודפת: {format_percentage(data['outperformance'])}</p>
                    </div>
            """
        html_content += """
                </div>

                <div class="links">
                    <a href="index.html">🏠 דף הבית</a>
                    <a href="history.html">📈 היסטוריית תיק</a>
                    <a href="summary.html">📸 סיכום לשיתוף</a>
                    <a href="graphs.html">📊 גרפים</a>
                </div>
        """
        html_content += self._get_footer_html()
        return html_content

    def generate_history_report(self, history_data):
        """מייצר את דוח ההיסטוריה (history.html)."""
        html_content = self._get_base_html("היסטוריית ביצועי תיק")
        html_content += f"""
                <h1>היסטוריית ביצועי תיק - {self.portfolio_name}</h1>
                <p class="header-info">סקירה של נתוני ביצועים לאורך זמן.</p>
                <p class="header-info">השוואה לתאריך התחלה: {datetime.strptime(self.base_date, '%Y-%m-%d').strftime('%d/%m/%Y')}</p>
                <table class="stock-table">
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
        """
        hebrew_months = {
            1: "ינואר", 2: "פברואר", 3: "מרץ", 4: "אפריל",
            5: "מאי", 6: "יוני", 7: "יולי", 8: "אוגוסט",
            9: "ספטמבר", 10: "אוקטובר", 11: "נובמבר", 12: "דצמבר"
        }

        for record in history_data:
            dt_object = datetime.strptime(record['date'], '%Y-%m-%d')
            month_name_hebrew = hebrew_months.get(dt_object.month, str(dt_object.month))
            date_str = f"{dt_object.day} {month_name_hebrew} {dt_object.year}"

            portfolio_value = format_currency(record['portfolio_value'])
            total_profit = format_currency(record['total_profit'])
            total_return = format_percentage(record['total_return'])
            days_invested = record['days_invested']
            
            spy_return = format_percentage(record.get('benchmarks_returns', {}).get('SPY'))
            qqq_return = format_percentage(record.get('benchmarks_returns', {}).get('QQQ'))
            tqqq_return = format_percentage(record.get('benchmarks_returns', {}).get('TQQQ'))

            html_content += f"""
                    <tr>
                        <td>{date_str}</td>
                        <td>{portfolio_value}</td>
                        <td class="{performance_color_class(record['total_profit'])}">{total_profit}</td>
                        <td class="{performance_color_class(record['total_return'])}">{total_return}</td>
                        <td>{days_invested}</td>
                        <td class="{performance_color_class(record.get('benchmarks_returns', {}).get('SPY'))}">{spy_return}</td>
                        <td class="{performance_color_class(record.get('benchmarks_returns', {}).get('QQQ'))}">{qqq_return}</td>
                        <td class="{performance_color_class(record.get('benchmarks_returns', {}).get('TQQQ'))}">{tqqq_return}</td>
                    </tr>
            """
        html_content += """
                </tbody>
            </table>

            <div class="links">
                <a href="index.html">🏠 דף הבית</a>
                <a href="history.html">📈 היסטוריית תיק</a>
                <a href="summary.html">📸 סיכום לשיתוף</a>
                <a href="graphs.html">📊 גרפים</a>
            </div>
        """
        html_content += self._get_footer_html()
        return html_content

    def generate_summary_image_report(self, current_performance):
        """מייצר דוח סיכום המיועד לצילום מסך/שיתוף (summary.html)."""
        html_content = self._get_base_html("סיכום לשיתוף")

        portfolio_value = format_currency(current_performance['portfolio_value'])
        total_profit = format_currency(current_performance['total_profit'])
        total_return = format_percentage(current_performance['total_return'])
        date_str = datetime.strptime(current_performance['date'], '%Y-%m-%d').strftime('%d/%m/%Y')

        html_content += f"""
            <div class="summary-container">
                <div class="summary-header">סיכום ביצועי תיק {self.portfolio_name}</div>
                <p class="header-info">נכון לתאריך: {date_str}</p>
                <p class="header-info">השוואה לתאריך התחלה: {datetime.strptime(self.base_date, '%Y-%m-%d').strftime('%d/%m/%Y')}</p>

                <div class="summary-metric">
                    <div class="label">שווי תיק נוכחי:</div>
                    <div class="value">{portfolio_value}</div>
                </div>
                <div class="summary-metric">
                    <div class="label">סה"כ רווח/הפסד:</div>
                    <div class="value {performance_color_class(current_performance['total_profit'])}">{total_profit}</div>
                </div>
                <div class="summary-metric">
                    <div class="label">תשואה כוללת:</div>
                    <div class="value {performance_color_class(current_performance['total_return'])}">{total_return}</div>
                </div>

                <h2 style="margin-top: 40px; color: #007bff;">תשואה עודפת מול מדדי ייחוס</h2>
                <div class="comparison-grid" style="grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); max-width: 700px; margin: 20px auto;">
        """
        outperformance_data = current_performance.get('outperformance', {})
        for symbol, data in outperformance_data.items():
            html_content += f"""
                    <div class="comparison-item" style="padding: 15px;">
                        <h3>{symbol}</h3>
                        <p style="font-size: 1em;">תשואת מדד: <span class="{performance_color_class(data['benchmark_return'])}">{format_percentage(data['benchmark_return'])}</span></p>
                        <p style="font-size: 1.0em;">תשואת תיק: <span class="{performance_color_class(data['portfolio_return'])}">{format_percentage(data['portfolio_return'])}</span></p>
                        <p style="font-size: 1.4em; font-weight: bold;">תשואה עודפת: <span class="value {performance_color_class(data['outperformance'])}">{format_percentage(data['outperformance'])}</span></p>
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
        """
        html_content += self._get_footer_html()
        return html_content

    def generate_graphs_report(self, history_data):
        """מייצר דוח עם גרפים של ביצועים היסטוריים (graphs.html)."""
        html_content = self._get_base_html("גרפים", extra_head_content="<script src='https://cdn.plot.ly/plotly-latest.min.js'></script>")

        # prepare data for plotting
        dates = [datetime.strptime(rec['date'], '%Y-%m-%d') for rec in history_data]
        portfolio_returns = [rec['total_return'] for rec in history_data]
        spy_returns = [rec['benchmarks_returns'].get('SPY') for rec in history_data]
        qqq_returns = [rec['benchmarks_returns'].get('QQQ') for rec in history_data]
        tqqq_returns = [rec['benchmarks_returns'].get('TQQQ') for rec in history_data]

        # Create DataFrame for easier plotting
        df = pd.DataFrame({
            'Date': dates,
            'Portfolio Return': portfolio_returns,
            'SPY Return': spy_returns,
            'QQQ Return': qqq_returns,
            'TQQQ Return': tqqq_returns
        })
        df = df.sort_values('Date') # Ensure dates are sorted for plotting

        # Plot Portfolio Value
        fig_value = go.Figure()
        fig_value.add_trace(go.Scatter(x=df['Date'], y=[rec['portfolio_value'] for rec in history_data], mode='lines+markers', name='שווי תיק'))
        fig_value.update_layout(
            title_text='התפתחות שווי תיק לאורך זמן',
            title_x=0.5,
            xaxis_title='תאריך',
            yaxis_title='שווי תיק ($)',
            hovermode='x unified',
            height=600
        )
        plot_value_div = pio.to_html(fig_value, full_html=False, include_plotlyjs='cdn')

        # Plot Portfolio vs. Benchmarks (Returns)
        fig_returns = go.Figure()
        fig_returns.add_trace(go.Scatter(x=df['Date'], y=df['Portfolio Return'], mode='lines+markers', name=f'{self.portfolio_name} תשואה %'))
        if 'SPY Return' in df.columns:
            fig_returns.add_trace(go.Scatter(x=df['Date'], y=df['SPY Return'], mode='lines+markers', name='SPY תשואה %'))
        if 'QQQ Return' in df.columns:
            fig_returns.add_trace(go.Scatter(x=df['Date'], y=df['QQQ Return'], mode='lines+markers', name='QQQ תשואה %'))
        if 'TQQQ Return' in df.columns:
            fig_returns.add_trace(go.Scatter(x=df['Date'], y=df['TQQQ Return'], mode='lines+markers', name='TQQQ תשואה %'))
        
        fig_returns.update_layout(
            title_text='התפתחות ביצועי תיק ומדדים לאורך זמן',
            title_x=0.5,
            xaxis_title='תאריך',
            yaxis_title='ערך / תשואה (%)',
            hovermode='x unified',
            height=600
        )
        plot_returns_div = pio.to_html(fig_returns, full_html=False, include_plotlyjs='cdn')


        html_content += f"""
                <h1>גרפים היסטוריים - {self.portfolio_name}</h1>
                <p class="header-info">השוואה לתאריך התחלה: {datetime.strptime(self.base_date, '%Y-%m-%d').strftime('%d/%m/%Y')}</p>
                <p class="header-info">הצגה חזותית של ביצועי התיק לאורך זמן.</p>

                <div class="chart-container">
                    {plot_value_div}
                </div>

                <div class="chart-container">
                    {plot_returns_div}
                </div>

                <div class="links">
                    <a href="index.html">🏠 דף הבית</a>
                    <a href="history.html">📈 היסטוריית תיק</a>
                    <a href="summary.html">📸 סיכום לשיתוף</a>
                    <a href="graphs.html">📊 גרפים</a>
                </div>
        """
        html_content += self._get_footer_html()
        return html_content