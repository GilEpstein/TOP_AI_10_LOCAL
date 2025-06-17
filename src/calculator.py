#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
חישובי ביצועים לתיק TOP AI 10 מול מדדי השוק
"""

from datetime import datetime
import config
from utils import load_json, save_json, days_since_investment, get_hebrew_date

class PerformanceCalculator:
    """מחלקה לחישוב ביצועי התיק והמדדים"""
    
    def __init__(self):
        self.base_prices = config.BASE_PRICES
        self.investment_per_stock = config.INVESTMENT_PER_STOCK
        self.ai_stocks = config.AI_STOCKS
        self.benchmarks = config.BENCHMARKS
    
    def calculate_stock_performance(self, symbol, current_price):
        """מחשב ביצועים למניה בודדת"""
        if symbol not in self.base_prices:
            return None
        
        base_price = self.base_prices[symbol]
        
        # חישוב כמות מניות שנקנו ב-100$
        quantity = self.investment_per_stock / base_price
        
        # ערך נוכחי
        current_value = quantity * current_price
        
        # רווח/הפסד
        profit_loss = current_value - self.investment_per_stock
        return_percent = (profit_loss / self.investment_per_stock) * 100
        
        return {
            'symbol': symbol,
            'base_price': round(base_price, 2),
            'current_price': round(current_price, 2),
            'quantity': round(quantity, 4),
            'investment': self.investment_per_stock,
            'current_value': round(current_value, 2),
            'profit_loss': round(profit_loss, 2),
            'return_percent': round(return_percent, 2),
            'price_change_percent': round(((current_price - base_price) / base_price) * 100, 2)
        }
    
    def calculate_benchmark_performance(self, symbol, current_price):
        """מחשב ביצועי מדד השוואה"""
        if symbol not in self.base_prices:
            return None
        
        base_price = self.base_prices[symbol]
        
        # חישוב כמות שנקנתה ב-100$
        quantity = self.investment_per_stock / base_price
        
        # ערך נוכחי
        current_value = quantity * current_price
        
        # רווח/הפסד
        profit_loss = current_value - self.investment_per_stock
        return_percent = (profit_loss / self.investment_per_stock) * 100
        
        return {
            'symbol': symbol,
            'base_price': round(base_price, 2),
            'current_price': round(current_price, 2),
            'investment': self.investment_per_stock,
            'current_value': round(current_value, 2),
            'profit_loss': round(profit_loss, 2),
            'return_percent': round(return_percent, 2)
        }
    
    def calculate_portfolio_summary(self, stocks_performance):
        """מחשב סיכום כללי של התיק"""
        total_investment = len(self.ai_stocks) * self.investment_per_stock
        total_current_value = sum(stock['current_value'] for stock in stocks_performance.values())
        total_profit_loss = total_current_value - total_investment
        total_return_percent = (total_profit_loss / total_investment) * 100
        
        # מציאת המניה הטובה והגרועה ביותר
        best_stock = max(stocks_performance.values(), key=lambda x: x['return_percent'])
        worst_stock = min(stocks_performance.values(), key=lambda x: x['return_percent'])
        
        return {
            'original_investment': total_investment,
            'current_value': round(total_current_value, 2),
            'total_profit': round(total_profit_loss, 2),
            'total_return': round(total_return_percent, 2),
            'days_invested': days_since_investment(),
            'best_performer': {
                'symbol': best_stock['symbol'],
                'return': best_stock['return_percent']
            },
            'worst_performer': {
                'symbol': worst_stock['symbol'],
                'return': worst_stock['return_percent']
            },
            'stocks_count': len(stocks_performance)
        }
    
    def calculate_outperformance(self, portfolio_return, benchmarks_performance):
        """מחשב עליונות התיק על המדדים"""
        outperformance = {}
        
        for symbol, benchmark_data in benchmarks_performance.items():
            benchmark_return = benchmark_data['return_percent']
            outperf = portfolio_return - benchmark_return
            
            outperformance[symbol] = {
                'benchmark_return': benchmark_return,
                'portfolio_return': portfolio_return,
                'outperformance': round(outperf, 2),
                'is_outperforming': outperf > 0
            }
        
        return outperformance
    
    def calculate_all_performance(self, current_prices):
        """מחשב את כל הביצועים - תיק ומדדים"""
        print("🧮 מחשב ביצועי מניות...")
        
        # חישוב ביצועי מניות התיק
        stocks_performance = {}
        for symbol in self.ai_stocks:
            if symbol in current_prices:
                perf = self.calculate_stock_performance(symbol, current_prices[symbol]['current_price'])
                if perf:
                    stocks_performance[symbol] = perf
            else:
                print(f"⚠️ חסר מחיר נוכחי עבור {symbol}")
        
        print("🧮 מחשב ביצועי מדדים...")
        
        # חישוב ביצועי מדדי השוק
        benchmarks_performance = {}
        for symbol in self.benchmarks:
            if symbol in current_prices:
                perf = self.calculate_benchmark_performance(symbol, current_prices[symbol]['current_price'])
                if perf:
                    benchmarks_performance[symbol] = perf
            else:
                print(f"⚠️ חסר מחיר נוכחי עבור מדד {symbol}")
        
        # סיכום התיק
        portfolio_summary = self.calculate_portfolio_summary(stocks_performance)
        
        # חישוב עליונות על המדדים
        outperformance = self.calculate_outperformance(
            portfolio_summary['total_return'], 
            benchmarks_performance
        )
        
        # נתונים כלליים
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'hebrew_date': get_hebrew_date(),
            'base_date': config.BASE_DATE,
            'days_since_investment': days_since_investment(),
            'portfolio_summary': portfolio_summary,
            'stocks_performance': stocks_performance,
            'benchmarks': benchmarks_performance,
            'outperformance': outperformance,
            'market_data': {
                'symbols_analyzed': len(stocks_performance) + len(benchmarks_performance),
                'successful_ai_stocks': len(stocks_performance),
                'successful_benchmarks': len(benchmarks_performance)
            }
        }
        
        print(f"✅ חושבו ביצועים עבור {len(stocks_performance)} מניות ו-{len(benchmarks_performance)} מדדים")
        
        return report_data
    
    def update_history(self, performance_data):
        """מעדכן את קובץ ההיסטוריה"""
        history_file = "data/portfolio_history.json"
        
        # טעינת היסטוריה קיימת
        history = load_json(history_file) or []
        
        # יצירת רשומה חדשה
        new_record = {
            'date': performance_data['hebrew_date'],
            'timestamp': performance_data['timestamp'],
            'portfolio_value': performance_data['portfolio_summary']['current_value'],
            'original_investment': performance_data['portfolio_summary']['original_investment'],
            'total_profit': performance_data['portfolio_summary']['total_profit'],
            'total_return': performance_data['portfolio_summary']['total_return'],
            'days_invested': performance_data['days_since_investment'],
            'benchmarks_returns': {
                symbol: data['return_percent'] 
                for symbol, data in performance_data['benchmarks'].items()
            },
            'outperformance': {
                symbol: data['outperformance'] 
                for symbol, data in performance_data['outperformance'].items()
            }
        }
        
        # בדיקה אם כבר יש רשומה לתאריך הזה (עדכון יומי)
        today_date = datetime.now().strftime("%Y-%m-%d")
        updated_existing = False
        
        for i, record in enumerate(history):
            record_date = record['timestamp'][:10]  # לוקח רק את החלק של התאריך
            if record_date == today_date:
                history[i] = new_record
                updated_existing = True
                print("🔄 עודכנה רשומה קיימת בהיסטוריה")
                break
        
        if not updated_existing:
            history.append(new_record)
            print("➕ נוספה רשומה חדשה להיסטוריה")
        
        # שמירת ההיסטוריה המעודכנת
        save_json(history, history_file)
        
        return history
    
    def get_performance_trends(self, history_data, days=30):
        """מחשב מגמות ביצועים לתקופה האחרונה"""
        if len(history_data) < 2:
            return None
        
        # מיון לפי תאריך
        sorted_history = sorted(history_data, key=lambda x: x['timestamp'])
        
        # לוקח רק את הרשומות האחרונות
        recent_data = sorted_history[-days:] if len(sorted_history) > days else sorted_history
        
        if len(recent_data) < 2:
            return None
        
        first_record = recent_data[0]
        last_record = recent_data[-1]
        
        value_change = last_record['portfolio_value'] - first_record['portfolio_value']
        return_change = last_record['total_return'] - first_record['total_return']
        
        return {
            'period_days': len(recent_data),
            'value_change': round(value_change, 2),
            'return_change': round(return_change, 2),
            'trend_direction': 'עלייה' if value_change > 0 else 'ירידה',
            'avg_daily_change': round(value_change / len(recent_data), 2)
        }