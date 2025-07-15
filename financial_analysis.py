"""
Financial Analysis Module - Handles yfinance data and financial calculations
"""

import re
import logging
from datetime import datetime
from typing import Dict, Any
import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)

class ComprehensiveFinancialAnalyzer:
    """Comprehensive financial analyzer using yfinance"""
    
    def __init__(self, ticker):
        self.ticker = ticker.upper()
        self.stock = yf.Ticker(ticker)
        self.info = self.stock.info
        self.financials = self.stock.financials
        self.balance_sheet = self.stock.balance_sheet
        self.cash_flow = self.stock.cashflow
        
    def extract_all_data(self) -> Dict[str, Any]:
        """Extract all required financial data"""
        data = {}
        
        # Company Information
        data['company_name'] = self.info.get('longName', 'N/A')
        data['company_address'] = self.get_company_address()
        data['fiscal_year'] = self.get_fiscal_year()
        data['industry'] = self.info.get('industry', 'N/A')
        data['stock_symbol'] = self.ticker
        
        # Financial Performance
        data['revenue'] = self.format_currency(self.info.get('totalRevenue', 0))
        data['net_income'] = self.format_currency(self.get_net_income())
        data['operating_cash_flow'] = self.format_currency(self.get_operating_cash_flow())
        data['total_assets'] = self.format_currency(self.get_total_assets())
        data['total_liabilities'] = self.format_currency(self.get_total_liabilities())
        data['shareholders_equity'] = self.format_currency(self.get_shareholders_equity())
        data['roe'] = self.format_percentage(self.info.get('returnOnEquity', 0))
        
        # Key Financial Metrics
        data['gross_margin'] = self.format_percentage(self.info.get('grossMargins', 0))
        data['operating_margin'] = self.format_percentage(self.info.get('operatingMargins', 0))
        data['net_margin'] = self.format_percentage(self.info.get('profitMargins', 0))
        data['current_ratio'] = self.format_ratio(self.info.get('currentRatio', 0))
        data['debt_to_equity'] = self.format_ratio(self.info.get('debtToEquity', 0))
        data['eps'] = f"${self.info.get('trailingEps', 0):.2f}"
        data['pe_ratio'] = self.format_ratio(self.info.get('trailingPE', 0))
        data['book_value_per_share'] = f"${self.info.get('bookValue', 0):.2f}"
        
        # Financial Analysis (SWOT)
        data['strengths_analysis'] = self.generate_strengths_analysis()
        data['weaknesses_analysis'] = self.generate_weaknesses_analysis()
        data['opportunities_analysis'] = self.generate_opportunities_analysis()
        data['threats_analysis'] = self.generate_threats_analysis()
        
        # Business Context
        data['market_cap'] = self.format_currency(self.info.get('marketCap', 0))
        data['employees'] = f"{self.info.get('fullTimeEmployees', 0):,}"
        data['primary_business'] = self.info.get('longBusinessSummary', 'N/A')[:500] + '...'
        data['geographic_markets'] = self.get_geographic_markets()
        data['key_products'] = self.get_key_products()
        data['competitors'] = self.get_competitors()
        
        # Recent Developments
        data['acquisitions'] = self.get_recent_acquisitions()
        data['product_launches'] = self.get_product_launches()
        data['strategic_initiatives'] = self.get_strategic_initiatives()
        data['regulatory_changes'] = self.get_regulatory_changes()
        data['market_developments'] = self.get_market_developments()
        
        # Investment Recommendation
        data['overall_rating'] = self.generate_overall_rating()
        data['price_target'] = self.get_price_target()
        data['investment_horizon'] = self.get_investment_horizon()
        data['risk_assessment'] = self.generate_risk_assessment()
        
        return data
    
    def get_company_address(self) -> str:
        """Get company address"""
        address_parts = []
        if self.info.get('address1'):
            address_parts.append(self.info.get('address1'))
        if self.info.get('city'):
            address_parts.append(self.info.get('city'))
        if self.info.get('state'):
            address_parts.append(self.info.get('state'))
        if self.info.get('zip'):
            address_parts.append(self.info.get('zip'))
        if self.info.get('country'):
            address_parts.append(self.info.get('country'))
        
        return ', '.join(address_parts) if address_parts else 'N/A'
    
    def get_fiscal_year(self) -> str:
        """Get fiscal year"""
        if not self.financials.empty:
            return str(self.financials.columns[0].year)
        return str(datetime.now().year)
    
    def get_net_income(self) -> float:
        """Get net income from financials"""
        if not self.financials.empty and 'Net Income' in self.financials.index:
            return self.financials.loc['Net Income'].iloc[0]
        return self.info.get('netIncomeToCommon', 0)
    
    def get_operating_cash_flow(self) -> float:
        """Get operating cash flow"""
        if not self.cash_flow.empty and 'Operating Cash Flow' in self.cash_flow.index:
            return self.cash_flow.loc['Operating Cash Flow'].iloc[0]
        return self.info.get('operatingCashflow', 0)
    
    def get_total_assets(self) -> float:
        """Get total assets"""
        if not self.balance_sheet.empty and 'Total Assets' in self.balance_sheet.index:
            return self.balance_sheet.loc['Total Assets'].iloc[0]
        return 0
    
    def get_total_liabilities(self) -> float:
        """Get total liabilities"""
        if not self.balance_sheet.empty and 'Total Liab' in self.balance_sheet.index:
            return self.balance_sheet.loc['Total Liab'].iloc[0]
        return 0
    
    def get_shareholders_equity(self) -> float:
        """Get shareholders equity"""
        if not self.balance_sheet.empty and 'Total Stockholder Equity' in self.balance_sheet.index:
            return self.balance_sheet.loc['Total Stockholder Equity'].iloc[0]
        return 0
    
    def generate_strengths_analysis(self) -> str:
        """Generate strengths analysis"""
        strengths = []
        
        if self.info.get('profitMargins', 0) > 0.1:
            strengths.append(f"Strong profit margins of {self.format_percentage(self.info.get('profitMargins', 0))}")
        
        if self.info.get('returnOnEquity', 0) > 0.15:
            strengths.append(f"High return on equity of {self.format_percentage(self.info.get('returnOnEquity', 0))}")
        
        if self.info.get('currentRatio', 0) > 1.2:
            strengths.append(f"Strong liquidity with current ratio of {self.format_ratio(self.info.get('currentRatio', 0))}")
        
        if self.info.get('revenueGrowth', 0) > 0.05:
            strengths.append(f"Positive revenue growth of {self.format_percentage(self.info.get('revenueGrowth', 0))}")
        
        return "• " + "\n• ".join(strengths) if strengths else "Analysis pending"
    
    def generate_weaknesses_analysis(self) -> str:
        """Generate weaknesses analysis"""
        weaknesses = []
        
        if self.info.get('profitMargins', 0) < 0.05:
            weaknesses.append(f"Low profit margins of {self.format_percentage(self.info.get('profitMargins', 0))}")
        
        if self.info.get('debtToEquity', 0) > 1.0:
            weaknesses.append(f"High debt-to-equity ratio of {self.format_ratio(self.info.get('debtToEquity', 0))}")
        
        if self.info.get('currentRatio', 0) < 1.0:
            weaknesses.append(f"Low liquidity with current ratio of {self.format_ratio(self.info.get('currentRatio', 0))}")
        
        if self.info.get('revenueGrowth', 0) < 0:
            weaknesses.append(f"Declining revenue growth of {self.format_percentage(self.info.get('revenueGrowth', 0))}")
        
        return "• " + "\n• ".join(weaknesses) if weaknesses else "Analysis pending"
    
    def generate_opportunities_analysis(self) -> str:
        """Generate opportunities analysis"""
        opportunities = [
            "Market expansion in emerging economies",
            "Digital transformation initiatives",
            "Strategic partnerships and alliances",
            "New product development and innovation",
            "Cost optimization and operational efficiency"
        ]
        return "• " + "\n• ".join(opportunities)
    
    def generate_threats_analysis(self) -> str:
        """Generate threats analysis"""
        threats = [
            "Increased competition in the market",
            "Economic downturns and market volatility",
            "Regulatory changes and compliance costs",
            "Supply chain disruptions",
            "Technological disruption and obsolescence"
        ]
        return "• " + "\n• ".join(threats)
    
    def get_geographic_markets(self) -> str:
        """Get geographic markets"""
        return self.info.get('country', 'Global') + " and international markets"
    
    def get_key_products(self) -> str:
        """Get key products/services"""
        business_summary = self.info.get('longBusinessSummary', '')
        if business_summary:
            return business_summary[:200] + "..."
        return "Diversified product portfolio"
    
    def get_competitors(self) -> str:
        """Get main competitors"""
        industry = self.info.get('industry', '')
        return f"Key competitors in {industry} sector"
    
    def get_recent_acquisitions(self) -> str:
        """Get recent acquisitions"""
        return "Recent acquisition activity being monitored"
    
    def get_product_launches(self) -> str:
        """Get product launches"""
        return "New product launches and service offerings"
    
    def get_strategic_initiatives(self) -> str:
        """Get strategic initiatives"""
        return "Digital transformation and market expansion initiatives"
    
    def get_regulatory_changes(self) -> str:
        """Get regulatory changes"""
        return "Monitoring regulatory developments in key markets"
    
    def get_market_developments(self) -> str:
        """Get market developments"""
        return "Market trends and competitive landscape analysis"
    
    def generate_overall_rating(self) -> str:
        """Generate overall investment rating"""
        score = 0
        
        if self.info.get('profitMargins', 0) > 0.1:
            score += 1
        if self.info.get('returnOnEquity', 0) > 0.15:
            score += 1
        if self.info.get('currentRatio', 0) > 1.2:
            score += 1
        if self.info.get('revenueGrowth', 0) > 0.05:
            score += 1
        if self.info.get('trailingPE', 0) < 20:
            score += 1
        
        if score >= 4:
            return "BUY"
        elif score >= 2:
            return "HOLD"
        else:
            return "SELL"
    
    def get_price_target(self) -> str:
        """Get price target"""
        current_price = self.info.get('currentPrice', 0)
        target_price = self.info.get('targetMeanPrice', current_price * 1.1)
        return f"${target_price:.2f}"
    
    def get_investment_horizon(self) -> str:
        """Get investment horizon"""
        return "12-18 months"
    
    def generate_risk_assessment(self) -> str:
        """Generate risk assessment"""
        risk_factors = []
        
        if self.info.get('beta', 1) > 1.2:
            risk_factors.append("High market volatility")
        
        if self.info.get('debtToEquity', 0) > 1.0:
            risk_factors.append("High financial leverage")
        
        if not risk_factors:
            risk_factors.append("Moderate risk profile")
        
        return "• " + "\n• ".join(risk_factors)
    
    def format_currency(self, value) -> str:
        """Format currency values"""
        if pd.isna(value) or value == 0:
            return "N/A"
        
        if abs(value) >= 1e12:
            return f"${value/1e12:.2f}T"
        elif abs(value) >= 1e9:
            return f"${value/1e9:.2f}B"
        elif abs(value) >= 1e6:
            return f"${value/1e6:.2f}M"
        else:
            return f"${value:,.0f}"
    
    def format_percentage(self, value) -> str:
        """Format percentage values"""
        if pd.isna(value) or value == 0:
            return "N/A"
        return f"{value*100:.2f}%"
    
    def format_ratio(self, value) -> str:
        """Format ratio values"""
        if pd.isna(value) or value == 0:
            return "N/A"
        return f"{value:.2f}"