def generate_history_report(self, history_data):
        """יוצר דוח היסטוריה מלא"""
        if not history_data:
            return self._generate_empty_history_report()
        
        sorted_history = sorted(history_data, key=lambda x: x['timestamp'])
        
        html = f"""<!DOCTYPE html>
<html dir="rtl" lang="he">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>היסטוריית {self.portfolio_name}</title>
    {self._get_css_styles()}
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><span class="emoji">📈</span>היסטוריית התיק<span class="emoji">📊</span></h1>
            <div class="subtitle">מעקב ביצועים לאורך זמן</div>
            <div class="nav-links">
                <a href="index.html">דוח נוכחי</a>
                <a href="history.html">היסטוריה</a>
                <a href="summary.html">תמונת סיכום</a>
            </div>
        </div>
        
        <div class="section">"""
        
        if len(sorted_history) >= 2:
            latest = sorted_history[-1]
            first = sorted_history[0]
            
            total_growth = latest['portfolio_value'] - first['portfolio_value']
            total_return_change = latest['total_return'] - first['total_return']
            
            html += f"""
                <div class="stats-grid">
                    <div class="stat-card">
                        <h3>💰 צמיחה כוללת</h3>
                        <div class="value {performance_color_class(total_growth)}">{format_currency(total_growth)}</div>
                    </div>
                    <div class="stat-card">
                        <h3>📈 שינוי תשואה</h3>
                        <div class="value {performance_color_class(total_return_change)}">{format_percentage(total_return_change)}</div>
                    </div>
                    <div class="stat-card">
                        <h3>📊 רשומות</h3>
                        <div class="value">{len(sorted_history)}</div>
                    </div>
                    <div class="stat-card">
                        <h3>⏰ תקופת מעקב</h3>
                        <div class="value">{latest['days_invested']} ימים</div>
                    </div>
                </div>"""
        
        html += """
            <h2 class="section-title">היסטוריית ביצועים מפורטת</h2>
            <table class="history-table">
                <thead>
                    <tr>
                        <th>📅 תאריך</th>
                        <th>💎 ערך התיק</th>
                        <th>📊 רווח/הפסד</th>
                        <th>📈 % תשואה</th>
                        <th>🇺🇸 מול S&P 500</th>
                        <th>🚀 מול NASDAQ</th>
                        <th>📊 שינוי יומי</th>
                    </tr>
                </thead>
                <tbody>"""
        
        for i, record in enumerate(sorted_history):
            if i > 0:
                prev_value = sorted_history[i-1]['portfolio_value']
                daily_change = record['portfolio_value'] - prev_value
                daily_change_percent = (daily_change / prev_value) * 100 if prev_value > 0 else 0
                change_class = performance_color_class(daily_change)
                change_text = f"{format_currency(daily_change)} ({daily_change_percent:+.1f}%)"
            else:
                change_class = "neutral"
                change_text = "נקודת התחלה"
            
            spy_outperf = record['outperformance'].get('SPY', 0)
            qqq_outperf = record['outperformance'].get('QQQ', 0)
            
            html += f"""
                    <tr>
                        <td><strong>{record['date']}</strong></td>
                        <td class="number-cell">{format_currency(record['portfolio_value'])}</td>
                        <td class="number-cell {performance_color_class(record['total_profit'])}">{format_currency(record['total_profit'])}</td>
                        <td class="number-cell {performance_color_class(record['total_return'])}">{format_percentage(record['total_return'])}</td>
                        <td class="number-cell {performance_color_class(spy_outperf)}">{format_percentage(spy_outperf)}</td>
                        <td class="number-cell {performance_color_class(qqq_outperf)}">{format_percentage(qqq_outperf)}</td>
                        <td class="number-cell {change_class}">{change_text}</td>
                    </tr>"""
        
        html += f"""
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p><span class="emoji">🤖</span>דוח היסטוריה נוצר אוטומטית<span class="emoji">📈</span></p>
            <p>עודכן: {safe_strftime(datetime.now(), '%d/%m/%Y %H:%M')}</p>
        </div>
    </div>
</body>
</html>"""
        
        return html

    def generate_summary_image_report(self, performance_data):
        """יוצר דוח מקוצר לשיתוף כתמונה"""
        portfolio = performance_data['portfolio_summary']
        benchmarks = performance_data['benchmarks']
        outperformance = performance_data['outperformance']
        
        html = f"""<!DOCTYPE html>
<html dir="rtl" lang="he">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>סיכום {self.portfolio_name}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            padding: 30px;
            direction: rtl;
            color: #1a202c;
            width: 800px;
            height: 600px;
            overflow: hidden;
        }}
        
        .summary-container {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-radius: 25px;
            padding: 40px;
            box-shadow: 0 25px 50px rgba(0,0,0,0.15);
            border: 1px solid rgba(255, 255, 255, 0.3);
            height: 100%;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            font-weight: 800;
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }}
        
        .header .date {{
            font-size: 1.1em;
            color: #4a5568;
            font-weight: 600;
        }}
        
        .main-stats {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-box {{
            background: rgba(255, 255, 255, 0.9);
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }}
        
        .stat-box.profit {{
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(16, 185, 129, 0.05) 100%);
            border: 2px solid rgba(16, 185, 129, 0.3);
        }}
        
        .stat-box.loss {{
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(239, 68, 68, 0.05) 100%);
            border: 2px solid rgba(239, 68, 68, 0.3);
        }}
        
        .stat-box h3 {{
            font-size: 1em;
            color: #4a5568;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .stat-box .value {{
            font-size: 2em;
            font-weight: 800;
            direction: ltr;
        }}
        
        .performance-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }}
        
        .performance-item {{
            background: rgba(255, 255, 255, 0.8);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            font-size: 0.9em;
        }}
        
        .performance-item .name {{
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 5px;
        }}
        
        .performance-item .result {{
            font-weight: 700;
            font-size: 1.1em;
        }}
        
        .positive {{ color: #10b981; }}
        .negative {{ color: #ef4444; }}
        .neutral {{ color: #6b7280; }}
        
        .footer {{
            text-align: center;
            color: #4a5568;
            font-size: 0.9em;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="summary-container">
        <div class="header">
            <h1>🚀 {self.portfolio_name} 📊</h1>
            <div class="date">📅 {performance_data['hebrew_date']}</div>
        </div>
        
        <div class="main-stats">
            <div class="stat-box">
                <h3>💎 ערך נוכחי</h3>
                <div class="value">{format_currency(portfolio['current_value'])}</div>
            </div>
            <div class="stat-box {'profit' if portfolio['total_profit'] >= 0 else 'loss'}">
                <h3>📈 רווח/הפסד</h3>
                <div class="value {performance_color_class(portfolio['total_profit'])}">{format_currency(portfolio['total_profit'])}</div>
                <div class="{performance_color_class(portfolio['total_return'])}" style="font-size: 1.2em; font-weight: 700; margin-top: 5px;">
                    {format_percentage(portfolio['total_return'])}
                </div>
            </div>
        </div>
        
        <h3 style="text-align: center; margin-bottom: 15px; color: #2d3748;">🏆 ביצועים מול השוק</h3>
        <div class="performance-grid">"""
        
        benchmark_names = {"SPY": "S&P 500", "QQQ": "NASDAQ", "TQQQ": "NASDAQ 3x"}
        
        for symbol, data in benchmarks.items():
            outperf_data = outperformance[symbol]
            outperf_value = outperf_data['outperformance']
            name = benchmark_names.get(symbol, symbol)
            status = "מנצח" if outperf_value > 0 else "מפסיד"
            
            html += f"""
            <div class="performance-item">
                <div class="name">{name}</div>
                <div class="result {performance_color_class(outperf_value)}">
                    {status} {abs(outperf_value):.1f}%
                </div>
            </div>"""
        
        html += f"""
        </div>
        
        <div class="footer">
            🤖 דוח אוטומטי • ⏰ {portfolio['days_invested']} ימים מההשקעה
        </div>
    </div>
</body>
</html>"""
        
        return html

    def _generate_empty_history_report(self):
        """יוצר דוח היסטוריה ריק"""
        return f"""<!DOCTYPE html>
<html dir="rtl" lang="he">
<head>
    <meta charset="UTF-8">
    <title>היסטוריית {self.portfolio_name}</title>
    {self._get_css_styles()}
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><span class="emoji">📈</span>היסטוריית התיק<span class="emoji">📊</span></h1>
            <div class="subtitle">מעקב ביצועים לאורך זמן</div>
        </div>
        <div class="section">
            <h2 class="section-title">אין נתוני היסטוריה עדיין</h2>
            <p style="text-align: center; font-size: 1.5em; padding: 40px;">
                📊 ההיסטוריה תתצבר עם הזמן
            </p>
        </div>
    </div>
</body>
</html>"""