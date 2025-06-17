# -*- coding: utf-8 -*-
"""
סגנונות CSS מודרניים וחיים
"""

from .colors import Colors

class ModernStyles:
    """מחלקה ליצירת CSS מודרני"""
    
    @staticmethod
    def get_all_styles():
        """מחזיר את כל הסגנונות המודרניים"""
        return f"""
        <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            background: {Colors.PRIMARY_BG};
            color: {Colors.TEXT_PRIMARY};
            line-height: 1.6;
            direction: rtl;
            min-height: 100vh;
        }}
        
        .container {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}
        
        .header {{
            background: {Colors.SECONDARY_BG};
            border-radius: 20px;
            padding: 40px;
            margin-bottom: 30px;
            text-align: center;
            border: 2px solid {Colors.CARD_BORDER};
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
        }}
        
        .header h1 {{
            font-size: 3.5rem;
            font-weight: 900;
            margin-bottom: 16px;
            background: linear-gradient(135deg, {Colors.TEXT_PRIMARY} 0%, {Colors.ACCENT_BLUE} 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .header-subtitle {{
            font-size: 1.3rem;
            color: {Colors.TEXT_SECONDARY};
            margin-bottom: 8px;
            font-weight: 600;
        }}
        
        .header-date {{
            font-size: 1.5rem;
            color: {Colors.ACCENT_ORANGE};
            font-weight: 700;
            margin-bottom: 24px;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
        }}
        
        .nav-links {{
            display: flex;
            justify-content: center;
            gap: 16px;
            margin-top: 24px;
        }}
        
        .nav-links a {{
            padding: 14px 28px;
            background: {Colors.CARD_BG};
            border: 2px solid {Colors.CARD_BORDER};
            border-radius: 50px;
            color: {Colors.TEXT_PRIMARY};
            text-decoration: none;
            font-weight: 700;
            font-size: 1.1rem;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
        }}
        
        .nav-links a:hover {{
            background: {Colors.CARD_HOVER};
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.3);
        }}
        
        .nav-links a.current {{
            background: {Colors.GRADIENT_BUTTON};
            border-color: {Colors.ACCENT_BLUE};
            box-shadow: 0 8px 25px rgba(59,130,246,0.4);
        }}
        
        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
            margin-bottom: 40px;
        }}
        
        .summary-card {{
            background: {Colors.CARD_BG};
            backdrop-filter: blur(20px);
            border: 2px solid {Colors.CARD_BORDER};
            border-radius: 20px;
            padding: 35px;
            transition: all 0.4s ease;
            position: relative;
            overflow: hidden;
        }}
        
        .summary-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 5px;
            background: {Colors.GRADIENT_BUTTON};
            transform: scaleX(0);
            transform-origin: left;
            transition: transform 0.4s ease;
        }}
        
        .summary-card:hover {{
            transform: translateY(-8px) scale(1.02);
            background: {Colors.CARD_HOVER};
            border-color: {Colors.ACCENT_BLUE};
            box-shadow: 0 25px 50px rgba(0,0,0,0.3);
        }}
        
        .summary-card:hover::before {{ transform: scaleX(1); }}
        
        .summary-card h3 {{
            font-size: 1.3rem;
            color: {Colors.TEXT_SECONDARY};
            margin-bottom: 20px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .summary-card .value {{
            font-size: 3rem;
            font-weight: 900;
            margin-bottom: 12px;
            direction: ltr;
            text-align: center;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .summary-card .profit {{
            font-size: 1.6rem;
            font-weight: 800;
            direction: ltr;
            text-align: center;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
        }}
        
        .comparison-table, .portfolio-table {{
            width: 100%;
            border-collapse: collapse;
            background: {Colors.CARD_BG};
            border-radius: 20px;
            overflow: hidden;
            margin-bottom: 40px;
            border: 2px solid {Colors.CARD_BORDER};
            box-shadow: 0 15px 35px rgba(0,0,0,0.2);
        }}
        
        .comparison-table th, .portfolio-table th {{
            background: {Colors.GRADIENT_BUTTON};
            color: {Colors.TEXT_PRIMARY};
            padding: 25px;
            text-align: center;
            font-weight: 800;
            font-size: 1.2rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
        }}
        
        .comparison-table td, .portfolio-table td {{
            padding: 20px;
            text-align: center;
            border-bottom: 1px solid {Colors.CARD_BORDER};
            font-size: 1.1rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }}
        
        .comparison-table tr:hover, .portfolio-table tr:hover {{
            background: {Colors.CARD_HOVER};
            transform: scale(1.01);
        }}
        
        .stock-symbol {{
            font-weight: 900;
            font-size: 1.4rem;
            color: {Colors.TEXT_PRIMARY};
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
        }}
        
        .number-cell {{
            direction: ltr;
            text-align: center;
            font-weight: 700;
            font-size: 1.15rem;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        }}
        
        .portfolio-row {{
            background: linear-gradient(135deg, rgba(59,130,246,0.2) 0%, rgba(29,78,216,0.2) 100%) !important;
            border: 2px solid {Colors.ACCENT_BLUE} !important;
            box-shadow: 0 8px 25px rgba(59,130,246,0.3) !important;
        }}
        
        .portfolio-row .stock-symbol {{ color: {Colors.ACCENT_BLUE}; font-size: 1.5rem; }}
        
        .best-performer {{
            background: linear-gradient(135deg, rgba(34,197,94,0.2) 0%, rgba(22,163,74,0.2) 100%) !important;
            border-left: 5px solid {Colors.PROFIT_GREEN} !important;
        }}
        
        .worst-performer {{
            background: linear-gradient(135deg, rgba(239,68,68,0.2) 0%, rgba(220,38,38,0.2) 100%) !important;
            border-left: 5px solid {Colors.LOSS_RED} !important;
        }}
        
        .positive {{ color: {Colors.PROFIT_GREEN} !important; }}
        .negative {{ color: {Colors.LOSS_RED} !important; }}
        
        .section-title {{
            font-size: 2.5rem;
            color: {Colors.TEXT_PRIMARY};
            text-align: center;
            margin-bottom: 30px;
            font-weight: 800;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        @media (max-width: 768px) {{
            .container {{ padding: 16px; }}
            .header h1 {{ font-size: 2.5rem; }}
            .summary-cards {{ grid-template-columns: 1fr; gap: 16px; }}
            .nav-links {{ flex-direction: column; align-items: center; }}
            .comparison-table, .portfolio-table {{ font-size: 0.9rem; }}
            .comparison-table th, .portfolio-table th,
            .comparison-table td, .portfolio-table td {{ padding: 12px 8px; }}
        }}
        </style>
        """