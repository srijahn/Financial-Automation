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
        data['roe'] = self.format_percentage(self.get_roe())
        
        # Key Financial Metrics
        data['gross_margin'] = self.format_percentage(self.get_gross_margin())
        data['operating_margin'] = self.format_percentage(self.get_operating_margin())
        data['net_margin'] = self.format_percentage(self.get_net_margin())
        data['current_ratio'] = self.format_ratio(self.get_current_ratio())
        data['debt_to_equity'] = self.format_ratio(self.get_debt_to_equity())
        data['eps'] = self.format_currency_simple(self.get_eps())
        data['pe_ratio'] = self.format_ratio(self.get_pe_ratio())
        data['book_value_per_share'] = self.format_currency_simple(self.get_book_value_per_share())
        
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
    
    def get_roe(self) -> float:
        """Get return on equity with fallback calculation"""
        # Try from info first
        roe = self.info.get('returnOnEquity', 0)
        if roe and roe != 0:
            return roe
        
        # Calculate manually: Net Income / Shareholders Equity
        net_income = self.get_net_income()
        shareholders_equity = self.get_shareholders_equity()
        
        if shareholders_equity and shareholders_equity != 0:
            return net_income / shareholders_equity
        
        return 0
    
    def get_gross_margin(self) -> float:
        """Get gross margin with fallback calculation"""
        # Try from info first
        gross_margin = self.info.get('grossMargins', 0)
        if gross_margin and gross_margin != 0:
            return gross_margin
        
        # Calculate manually from financials
        if not self.financials.empty:
            try:
                revenue = self.financials.loc['Total Revenue'].iloc[0] if 'Total Revenue' in self.financials.index else 0
                cost_of_revenue = self.financials.loc['Cost Of Revenue'].iloc[0] if 'Cost Of Revenue' in self.financials.index else 0
                
                if revenue and revenue != 0:
                    return (revenue - cost_of_revenue) / revenue
            except:
                pass
        
        return 0
    
    def get_operating_margin(self) -> float:
        """Get operating margin with fallback calculation"""
        # Try from info first
        operating_margin = self.info.get('operatingMargins', 0)
        if operating_margin and operating_margin != 0:
            return operating_margin
        
        # Calculate manually from financials
        if not self.financials.empty:
            try:
                revenue = self.financials.loc['Total Revenue'].iloc[0] if 'Total Revenue' in self.financials.index else 0
                operating_income = self.financials.loc['Operating Income'].iloc[0] if 'Operating Income' in self.financials.index else 0
                
                if revenue and revenue != 0:
                    return operating_income / revenue
            except:
                pass
        
        return 0
    
    def get_net_margin(self) -> float:
        """Get net margin with fallback calculation"""
        # Try from info first
        net_margin = self.info.get('profitMargins', 0)
        if net_margin and net_margin != 0:
            return net_margin
        
        # Calculate manually: Net Income / Revenue
        net_income = self.get_net_income()
        revenue = self.info.get('totalRevenue', 0)
        
        if revenue and revenue != 0:
            return net_income / revenue
        
        return 0
    
    def get_current_ratio(self) -> float:
        """Get current ratio with fallback calculation"""
        # Try from info first
        current_ratio = self.info.get('currentRatio', 0)
        if current_ratio and current_ratio != 0:
            return current_ratio
        
        # Calculate manually from balance sheet
        if not self.balance_sheet.empty:
            try:
                current_assets = self.balance_sheet.loc['Total Current Assets'].iloc[0] if 'Total Current Assets' in self.balance_sheet.index else 0
                current_liabilities = self.balance_sheet.loc['Total Current Liabilities'].iloc[0] if 'Total Current Liabilities' in self.balance_sheet.index else 0
                
                if current_liabilities and current_liabilities != 0:
                    return current_assets / current_liabilities
            except:
                pass
        
        return 0
    
    def get_debt_to_equity(self) -> float:
        """Get debt-to-equity ratio with fallback calculation"""
        # Try from info first
        debt_to_equity = self.info.get('debtToEquity', 0)
        if debt_to_equity and debt_to_equity != 0:
            return debt_to_equity / 100  # Convert from percentage
        
        # Calculate manually from balance sheet
        if not self.balance_sheet.empty:
            try:
                total_debt = self.balance_sheet.loc['Total Debt'].iloc[0] if 'Total Debt' in self.balance_sheet.index else 0
                if total_debt == 0:
                    # Try long-term debt
                    total_debt = self.balance_sheet.loc['Long Term Debt'].iloc[0] if 'Long Term Debt' in self.balance_sheet.index else 0
                
                shareholders_equity = self.get_shareholders_equity()
                
                if shareholders_equity and shareholders_equity != 0:
                    return total_debt / shareholders_equity
            except:
                pass
        
        return 0
    
    def get_eps(self) -> float:
        """Get earnings per share"""
        eps = self.info.get('trailingEps', 0)
        if eps and eps != 0:
            return eps
        
        # Calculate manually: Net Income / Shares Outstanding
        net_income = self.get_net_income()
        shares_outstanding = self.info.get('sharesOutstanding', 0)
        
        if shares_outstanding and shares_outstanding != 0:
            return net_income / shares_outstanding
        
        return 0
    
    def get_pe_ratio(self) -> float:
        """Get price-to-earnings ratio"""
        pe_ratio = self.info.get('trailingPE', 0)
        if pe_ratio and pe_ratio != 0:
            return pe_ratio
        
        # Calculate manually: Current Price / EPS
        current_price = self.info.get('currentPrice', 0)
        eps = self.get_eps()
        
        if eps and eps != 0:
            return current_price / eps
        
        return 0
    
    def get_book_value_per_share(self) -> float:
        """Get book value per share"""
        book_value = self.info.get('bookValue', 0)
        if book_value and book_value != 0:
            return book_value
        
        # Calculate manually: Shareholders Equity / Shares Outstanding
        shareholders_equity = self.get_shareholders_equity()
        shares_outstanding = self.info.get('sharesOutstanding', 0)
        
        if shares_outstanding and shares_outstanding != 0:
            return shareholders_equity / shares_outstanding
        
        return 0
    
    def generate_strengths_analysis(self) -> str:
        """Generate strengths analysis based on actual financial data"""
        strengths = []
        
        # Profitability analysis
        net_margin = self.get_net_margin()
        if net_margin > 0.1:
            strengths.append(f"Strong profit margins of {self.format_percentage(net_margin)}")
        elif net_margin > 0.05:
            strengths.append(f"Decent profit margins of {self.format_percentage(net_margin)}")
        
        # Return on equity analysis
        roe = self.get_roe()
        if roe > 0.15:
            strengths.append(f"High return on equity of {self.format_percentage(roe)}")
        elif roe > 0.10:
            strengths.append(f"Solid return on equity of {self.format_percentage(roe)}")
        
        # Liquidity analysis
        current_ratio = self.get_current_ratio()
        if current_ratio > 2.0:
            strengths.append(f"Excellent liquidity with current ratio of {self.format_ratio(current_ratio)}")
        elif current_ratio > 1.5:
            strengths.append(f"Strong liquidity with current ratio of {self.format_ratio(current_ratio)}")
        elif current_ratio > 1.2:
            strengths.append(f"Good liquidity with current ratio of {self.format_ratio(current_ratio)}")
        
        # Revenue growth analysis
        revenue_growth = self.info.get('revenueGrowth', 0)
        if revenue_growth > 0.15:
            strengths.append(f"Strong revenue growth of {self.format_percentage(revenue_growth)}")
        elif revenue_growth > 0.05:
            strengths.append(f"Positive revenue growth of {self.format_percentage(revenue_growth)}")
        
        # Operating margin analysis
        operating_margin = self.get_operating_margin()
        if operating_margin > 0.15:
            strengths.append(f"Strong operating efficiency with {self.format_percentage(operating_margin)} operating margin")
        elif operating_margin > 0.10:
            strengths.append(f"Good operating efficiency with {self.format_percentage(operating_margin)} operating margin")
        
        # Cash flow analysis
        operating_cash_flow = self.get_operating_cash_flow()
        if operating_cash_flow > 0:
            strengths.append(f"Positive operating cash flow of {self.format_currency(operating_cash_flow)}")
        
        # Market position
        market_cap = self.info.get('marketCap', 0)
        if market_cap > 10e9:  # $10B+
            strengths.append("Large market capitalization indicating market leadership")
        elif market_cap > 1e9:  # $1B+
            strengths.append("Mid-cap company with established market presence")
        
        return "• " + "\n• ".join(strengths) if strengths else "• Positive aspects being evaluated based on available data"
    
    def generate_weaknesses_analysis(self) -> str:
        """Generate weaknesses analysis based on actual financial data"""
        weaknesses = []
        
        # Profitability concerns
        net_margin = self.get_net_margin()
        if net_margin < 0:
            weaknesses.append(f"Negative profit margins of {self.format_percentage(net_margin)}")
        elif net_margin < 0.05:
            weaknesses.append(f"Low profit margins of {self.format_percentage(net_margin)}")
        
        # Leverage concerns
        debt_to_equity = self.get_debt_to_equity()
        if debt_to_equity > 2.0:
            weaknesses.append(f"Very high debt-to-equity ratio of {self.format_ratio(debt_to_equity)}")
        elif debt_to_equity > 1.0:
            weaknesses.append(f"High debt-to-equity ratio of {self.format_ratio(debt_to_equity)}")
        
        # Liquidity concerns
        current_ratio = self.get_current_ratio()
        if current_ratio < 1.0:
            weaknesses.append(f"Low liquidity with current ratio of {self.format_ratio(current_ratio)}")
        elif current_ratio < 1.2:
            weaknesses.append(f"Tight liquidity with current ratio of {self.format_ratio(current_ratio)}")
        
        # Growth concerns
        revenue_growth = self.info.get('revenueGrowth', 0)
        if revenue_growth < -0.05:
            weaknesses.append(f"Significant revenue decline of {self.format_percentage(revenue_growth)}")
        elif revenue_growth < 0:
            weaknesses.append(f"Declining revenue growth of {self.format_percentage(revenue_growth)}")
        
        # Return concerns
        roe = self.get_roe()
        if roe < 0:
            weaknesses.append(f"Negative return on equity of {self.format_percentage(roe)}")
        elif roe < 0.05:
            weaknesses.append(f"Low return on equity of {self.format_percentage(roe)}")
        
        # Valuation concerns
        pe_ratio = self.get_pe_ratio()
        if pe_ratio > 30:
            weaknesses.append(f"High valuation with P/E ratio of {self.format_ratio(pe_ratio)}")
        elif pe_ratio < 0:
            weaknesses.append("Negative earnings affecting valuation metrics")
        
        return "• " + "\n• ".join(weaknesses) if weaknesses else "• Areas for improvement being evaluated based on available data"
    
    def generate_opportunities_analysis(self) -> str:
        """Generate opportunities analysis based on actual company data and business context"""
        opportunities = []
        
        # Extract from business summary for real opportunities
        business_summary = self.info.get('longBusinessSummary', '').lower()
        
        # Data-driven opportunities based on financial metrics
        revenue_growth = self.info.get('revenueGrowth', 0)
        if revenue_growth > 0.15:
            opportunities.append(f"Strong revenue growth of {self.format_percentage(revenue_growth)} indicates market expansion potential")
        elif revenue_growth > 0.05:
            opportunities.append(f"Positive revenue growth of {self.format_percentage(revenue_growth)} suggests stable market demand")
        
        # Cash flow opportunities
        operating_cash_flow = self.get_operating_cash_flow()
        free_cash_flow = self.info.get('freeCashflow', 0)
        if operating_cash_flow > 0 and free_cash_flow > 0:
            opportunities.append(f"Strong cash generation of {self.format_currency(operating_cash_flow)} enables strategic investments and acquisitions")
        
        # Market position opportunities
        market_cap = self.info.get('marketCap', 0)
        if market_cap > 10e9:
            opportunities.append("Large market capitalization provides resources for global expansion and strategic initiatives")
        elif market_cap < 1e9:
            opportunities.append("Small-cap positioning offers potential for significant growth and acquisition opportunities")
        
        # Profitability improvement opportunities
        gross_margin = self.get_gross_margin()
        operating_margin = self.get_operating_margin()
        if gross_margin > operating_margin + 0.1:
            opportunities.append("High gross margins indicate potential for operational efficiency improvements")
        
        # Extract industry-specific opportunities from business description
        if 'electric' in business_summary or 'clean energy' in business_summary:
            opportunities.append("Electric vehicle transition and clean energy mandates creating new market opportunities")
        
        if 'infrastructure' in business_summary or 'government' in business_summary:
            opportunities.append("Infrastructure spending and government investment programs driving demand")
        
        if 'technology' in business_summary or 'digital' in business_summary:
            opportunities.append("Digital transformation initiatives across industries creating growth opportunities")
        
        if 'international' in business_summary or 'global' in business_summary:
            opportunities.append("International market expansion opportunities in emerging economies")
        
        # R&D and innovation opportunities
        if self.info.get('totalRevenue', 0) > 1e9:  # Large companies likely have R&D
            opportunities.append("Innovation capabilities and R&D investment enabling new product development")
        
        # Acquisition opportunities based on balance sheet strength
        current_ratio = self.get_current_ratio()
        debt_to_equity = self.get_debt_to_equity()
        if current_ratio > 1.5 and debt_to_equity < 0.5:
            opportunities.append("Strong balance sheet positioning for strategic acquisitions and partnerships")
        
        # Market efficiency opportunities
        if operating_margin < 0.10 and gross_margin > 0.20:
            opportunities.append("Operational efficiency improvements could significantly enhance profitability")
        
        # Generic fallback if no specific opportunities identified
        if not opportunities:
            opportunities.extend([
                "Market expansion in core business segments",
                "Operational efficiency and cost optimization initiatives",
                "Strategic partnerships and technology integration"
            ])
        
        return "• " + "\n• ".join(opportunities[:5])  # Limit to top 5 opportunities
    
    def generate_threats_analysis(self) -> str:
        """Generate threats analysis based on actual company data and financial vulnerabilities"""
        threats = []
        
        # Extract from business summary for real threats
        business_summary = self.info.get('longBusinessSummary', '').lower()
        
        # Financial-specific threats based on actual metrics
        debt_to_equity = self.get_debt_to_equity()
        if debt_to_equity > 2.0:
            threats.append(f"Very high debt-to-equity ratio of {self.format_ratio(debt_to_equity)} increases financial risk and interest rate sensitivity")
        elif debt_to_equity > 1.0:
            threats.append(f"Elevated debt levels of {self.format_ratio(debt_to_equity)} debt-to-equity ratio pose refinancing risks")
        
        # Liquidity threats
        current_ratio = self.get_current_ratio()
        if current_ratio < 1.0:
            threats.append(f"Poor liquidity position with {self.format_ratio(current_ratio)} current ratio limits operational flexibility")
        elif current_ratio < 1.2:
            threats.append(f"Tight liquidity with {self.format_ratio(current_ratio)} current ratio could constrain growth investments")
        
        # Profitability threats
        net_margin = self.get_net_margin()
        operating_margin = self.get_operating_margin()
        if net_margin < 0:
            threats.append(f"Negative profit margins of {self.format_percentage(net_margin)} indicate operational challenges")
        elif net_margin < 0.05:
            threats.append(f"Low profit margins of {self.format_percentage(net_margin)} vulnerable to cost inflation and competition")
        
        # Revenue growth threats
        revenue_growth = self.info.get('revenueGrowth', 0)
        if revenue_growth < -0.10:
            threats.append(f"Significant revenue decline of {self.format_percentage(revenue_growth)} indicates market share loss")
        elif revenue_growth < 0:
            threats.append(f"Revenue contraction of {self.format_percentage(revenue_growth)} suggests competitive pressures")
        
        # Market concentration threats
        market_cap = self.info.get('marketCap', 0)
        if market_cap < 500e6:  # Small cap
            threats.append("Small market capitalization increases volatility and limits access to capital markets")
        
        # Extract industry-specific threats from business description
        if 'regulation' in business_summary or 'compliance' in business_summary:
            threats.append("Regulatory compliance costs and changing regulations pose operational risks")
        
        if 'seasonal' in business_summary or 'cyclical' in business_summary:
            threats.append("Seasonal or cyclical business patterns create revenue volatility and cash flow challenges")
        
        if 'competition' in business_summary or 'competitive' in business_summary:
            threats.append("Intense competitive environment pressures pricing and market share")
        
        if 'supply chain' in business_summary or 'manufacturing' in business_summary:
            threats.append("Supply chain disruptions and material cost inflation impact production and margins")
        
        # Technology disruption threats
        if 'traditional' in business_summary or 'established' in business_summary:
            threats.append("Technology disruption and changing consumer preferences threaten traditional business models")
        
        # Interest rate sensitivity
        if debt_to_equity > 0.5:
            threats.append("Interest rate increases could significantly impact borrowing costs and profitability")
        
        # Beta-based market risk
        beta = self.info.get('beta', 1.0)
        if beta > 1.5:
            threats.append(f"High market volatility with beta of {beta:.2f} amplifies market downturns")
        
        # Generic fallback if no specific threats identified
        if not threats:
            threats.extend([
                "Economic downturns and market volatility affecting business operations",
                "Competitive pressures and market share challenges",
                "Regulatory changes and compliance requirements"
            ])
        
        return "• " + "\n• ".join(threats[:5])  # Limit to top 5 threats
    
    def get_geographic_markets(self) -> str:
        """Get geographic markets based on actual business context"""
        business_summary = self.info.get('longBusinessSummary', '').lower()
        
        # Extract geographic information from business summary
        geographic_indicators = []
        
        # Check for specific geographic mentions
        if 'united states' in business_summary or 'north america' in business_summary:
            geographic_indicators.append("United States and North America")
        
        if 'international' in business_summary or 'global' in business_summary:
            geographic_indicators.append("International markets")
        
        if 'europe' in business_summary or 'european' in business_summary:
            geographic_indicators.append("European markets")
        
        if 'asia' in business_summary or 'asian' in business_summary:
            geographic_indicators.append("Asian markets")
        
        if 'emerging markets' in business_summary or 'developing' in business_summary:
            geographic_indicators.append("Emerging markets")
        
        if 'worldwide' in business_summary or 'globally' in business_summary:
            geographic_indicators.append("Global operations")
        
        # Fallback to country information if available
        if not geographic_indicators:
            country = self.info.get('country', '')
            if country:
                geographic_indicators.append(f"{country} and regional markets")
            else:
                geographic_indicators.append("Regional and domestic markets")
        
        return ", ".join(geographic_indicators) if geographic_indicators else "Domestic and regional markets"
    
    def get_key_products(self) -> str:
        """Get key products/services based on actual business description"""
        business_summary = self.info.get('longBusinessSummary', '')
        
        if business_summary:
            # Extract the most relevant parts of the business summary
            # Focus on the first 300 characters for key products/services
            key_products = business_summary[:300]
            
            # Clean up the text and add ellipsis
            if len(business_summary) > 300:
                key_products += "..."
            
            return key_products
        
        # Fallback based on industry if no business summary
        industry = self.info.get('industry', '').lower()
        if 'software' in industry:
            return "Software solutions and technology platforms"
        elif 'financial' in industry:
            return "Financial services and banking products"
        elif 'healthcare' in industry:
            return "Healthcare products and medical services"
        elif 'transportation' in industry:
            return "Transportation equipment and related services"
        elif 'retail' in industry:
            return "Consumer products and retail services"
        else:
            return "Diversified product and service portfolio"
    
    def get_competitors(self) -> str:
        """Get main competitors based on actual business context and industry analysis"""
        business_summary = self.info.get('longBusinessSummary', '').lower()
        industry = self.info.get('industry', '').lower()
        sector = self.info.get('sector', '').lower()
        
        competitors = []
        
        # Extract competitors from business summary keywords
        if 'school bus' in business_summary or 'student transportation' in business_summary:
            competitors.extend([
                "Thomas Built Buses (Daimler)",
                "IC Bus (Navistar International)",
                "Collins Bus Corporation",
                "Carpenter Bus Sales",
                "Trans Tech Bus"
            ])
        elif 'construction' in business_summary and 'equipment' in business_summary:
            competitors.extend([
                "Caterpillar Inc.",
                "Deere & Company",
                "Komatsu Ltd.",
                "Volvo Construction Equipment",
                "Liebherr Group"
            ])
        elif 'agricultural' in business_summary or 'farming' in business_summary:
            competitors.extend([
                "Deere & Company",
                "CNH Industrial N.V.",
                "AGCO Corporation",
                "Kubota Corporation",
                "Mahindra & Mahindra"
            ])
        elif 'software' in business_summary or 'cloud' in business_summary:
            competitors.extend([
                "Microsoft Corporation",
                "Oracle Corporation",
                "Salesforce Inc.",
                "Adobe Inc.",
                "ServiceNow Inc."
            ])
        elif 'financial services' in business_summary or 'banking' in business_summary:
            competitors.extend([
                "JPMorgan Chase & Co.",
                "Bank of America Corp.",
                "Wells Fargo & Company",
                "Citigroup Inc.",
                "Goldman Sachs Group Inc."
            ])
        elif 'healthcare' in business_summary or 'pharmaceutical' in business_summary:
            competitors.extend([
                "Johnson & Johnson",
                "Pfizer Inc.",
                "Merck & Co. Inc.",
                "Abbott Laboratories",
                "Bristol Myers Squibb"
            ])
        elif 'retail' in business_summary or 'consumer' in business_summary:
            competitors.extend([
                "Amazon.com Inc.",
                "Walmart Inc.",
                "Target Corporation",
                "Costco Wholesale Corp.",
                "Home Depot Inc."
            ])
        elif 'energy' in business_summary or 'oil' in business_summary:
            competitors.extend([
                "ExxonMobil Corporation",
                "Chevron Corporation",
                "ConocoPhillips",
                "Shell plc",
                "BP plc"
            ])
        elif 'transportation' in business_summary or 'logistics' in business_summary:
            competitors.extend([
                "FedEx Corporation",
                "United Parcel Service Inc.",
                "DHL Group",
                "XPO Logistics Inc.",
                "C.H. Robinson Worldwide"
            ])
        
        # If no specific competitors found, use industry-based approach
        if not competitors:
            # Technology sector
            if 'technology' in sector or 'software' in industry:
                competitors.extend([
                    "Major technology companies in similar segments",
                    "Cloud computing and SaaS providers",
                    "Enterprise software competitors"
                ])
            # Industrial sector
            elif 'industrial' in sector or 'manufacturing' in industry:
                competitors.extend([
                    "Industrial equipment manufacturers",
                    "Heavy machinery competitors",
                    "Automation and manufacturing companies"
                ])
            # Financial sector
            elif 'financial' in sector:
                competitors.extend([
                    "Regional and national banks",
                    "Financial services companies",
                    "Investment and wealth management firms"
                ])
            # Fallback based on market cap
            else:
                market_cap = self.info.get('marketCap', 0)
                if market_cap > 100e9:
                    competitors.append("Fortune 100 companies in similar industries")
                elif market_cap > 10e9:
                    competitors.append("Large-cap companies in the same sector")
                elif market_cap > 1e9:
                    competitors.append("Mid-cap companies and industry specialists")
                else:
                    competitors.append("Small-cap companies and niche market players")
        
        return "• " + "\n• ".join(competitors[:5])  # Limit to top 5
    
    def get_recent_acquisitions(self) -> str:
        """Get recent acquisitions analysis based on actual business context and financial capacity"""
        business_summary = self.info.get('longBusinessSummary', '').lower()
        
        acquisitions = []
        
        # Analyze financial capacity for acquisitions
        operating_cash_flow = self.get_operating_cash_flow()
        current_ratio = self.get_current_ratio()
        debt_to_equity = self.get_debt_to_equity()
        
        # Strong balance sheet = acquisition potential
        if current_ratio > 1.5 and debt_to_equity < 0.5 and operating_cash_flow > 0:
            acquisitions.append("Strong balance sheet positioning for strategic acquisitions and market consolidation")
        elif current_ratio > 1.2 and debt_to_equity < 1.0:
            acquisitions.append("Moderate acquisition capacity with selective strategic opportunities")
        else:
            acquisitions.append("Limited acquisition capacity due to financial constraints")
        
        # Business-specific acquisition opportunities
        if 'school bus' in business_summary or 'student transportation' in business_summary:
            acquisitions.extend([
                "Electric vehicle technology companies and charging infrastructure providers",
                "Regional school bus operators and service companies",
                "Transportation management software and fleet optimization companies"
            ])
        elif 'construction' in business_summary and 'equipment' in business_summary:
            acquisitions.extend([
                "Construction equipment rental and service companies",
                "Autonomous vehicle and construction robotics companies",
                "Equipment telematics and IoT technology providers"
            ])
        elif 'software' in business_summary or 'technology' in business_summary:
            acquisitions.extend([
                "AI and machine learning startups for product enhancement",
                "Cloud infrastructure and security companies",
                "Vertical-specific software solutions and platforms"
            ])
        elif 'financial' in business_summary or 'banking' in business_summary:
            acquisitions.extend([
                "Fintech startups and digital payment companies",
                "Wealth management and advisory firms",
                "RegTech and compliance technology providers"
            ])
        elif 'healthcare' in business_summary or 'pharmaceutical' in business_summary:
            acquisitions.extend([
                "Biotech companies and drug development pipelines",
                "Medical device and diagnostic companies",
                "Digital health and telemedicine platforms"
            ])
        
        # Market cap based acquisition strategy
        market_cap = self.info.get('marketCap', 0)
        if market_cap > 50e9:
            acquisitions.append("Large-scale transformational acquisitions and international expansion")
        elif market_cap > 5e9:
            acquisitions.append("Strategic bolt-on acquisitions and technology integration")
        elif market_cap < 1e9:
            acquisitions.append("Potential acquisition target for larger industry players")
        
        # Revenue growth impact
        revenue_growth = self.info.get('revenueGrowth', 0)
        if revenue_growth > 0.15:
            acquisitions.append("Strong organic growth reducing need for acquisitive growth")
        elif revenue_growth < 0:
            acquisitions.append("Acquisitions may be considered to drive growth and market share")
        
        return "• " + "\n• ".join(acquisitions[:3])
    
    def get_product_launches(self) -> str:
        """Get product launches analysis based on actual business context and R&D investment"""
        business_summary = self.info.get('longBusinessSummary', '').lower()
        
        launches = []
        
        # Analyze R&D capacity and innovation potential
        revenue = self.info.get('totalRevenue', 0)
        market_cap = self.info.get('marketCap', 0)
        
        # Business-specific product launches based on actual context
        if 'school bus' in business_summary or 'student transportation' in business_summary:
            launches.extend([
                "Electric school bus models with advanced safety features",
                "Connected vehicle technologies and fleet management systems",
                "Alternative fuel propulsion systems development"
            ])
        elif 'construction' in business_summary and 'equipment' in business_summary:
            launches.extend([
                "Advanced construction equipment with IoT integration",
                "Autonomous and semi-autonomous machinery development",
                "Sustainable and electric-powered equipment lines"
            ])
        elif 'software' in business_summary or 'cloud' in business_summary:
            launches.extend([
                "Cloud-based platform enhancements and new modules",
                "AI-powered analytics and automation features",
                "Mobile and web application updates"
            ])
        elif 'financial' in business_summary or 'banking' in business_summary:
            launches.extend([
                "Digital banking platform improvements",
                "Mobile payment and fintech solutions",
                "Regulatory compliance and risk management tools"
            ])
        elif 'healthcare' in business_summary or 'pharmaceutical' in business_summary:
            launches.extend([
                "Digital health and telemedicine solutions",
                "Medical device innovations and upgrades",
                "Pharmaceutical pipeline developments"
            ])
        elif 'retail' in business_summary or 'consumer' in business_summary:
            launches.extend([
                "E-commerce platform enhancements",
                "Customer experience and personalization tools",
                "Omnichannel retail solutions"
            ])
        elif 'energy' in business_summary or 'renewable' in business_summary:
            launches.extend([
                "Renewable energy technology solutions",
                "Energy efficiency and storage systems",
                "Smart grid and infrastructure products"
            ])
        
        # Add innovation context based on company size and financial capacity
        if revenue > 10e9:  # Large companies
            launches.append("Large-scale R&D investment enabling comprehensive product portfolio expansion")
        elif revenue > 1e9:  # Mid-size companies
            launches.append("Focused innovation strategy targeting core market segments")
        else:  # Small companies
            launches.append("Niche product development and targeted market solutions")
        
        # Add growth-based innovation context
        revenue_growth = self.info.get('revenueGrowth', 0)
        if revenue_growth > 0.15:
            launches.append("Strong growth momentum funding accelerated product development")
        elif revenue_growth < 0:
            launches.append("Focus on cost-effective product improvements and market retention")
        
        # Generic fallback if no specific launches identified
        if not launches:
            launches.extend([
                "New product development aligned with market trends",
                "Technology integration and feature enhancements",
                "Market-driven innovation and customer solutions"
            ])
        
        return "• " + "\n• ".join(launches[:3])
    
    def get_strategic_initiatives(self) -> str:
        """Get strategic initiatives analysis based on actual business context and financial position"""
        business_summary = self.info.get('longBusinessSummary', '').lower()
        
        initiatives = []
        
        # Analyze financial capacity for strategic initiatives
        operating_margin = self.get_operating_margin()
        operating_cash_flow = self.get_operating_cash_flow()
        revenue_growth = self.info.get('revenueGrowth', 0)
        
        # Business-specific strategic initiatives
        if 'school bus' in business_summary or 'student transportation' in business_summary:
            initiatives.extend([
                "Transition to electric and alternative fuel vehicles",
                "Expansion of aftermarket parts and service revenue",
                "Digital transformation of manufacturing processes"
            ])
        elif 'construction' in business_summary and 'equipment' in business_summary:
            initiatives.extend([
                "Equipment automation and IoT integration",
                "Service and maintenance revenue expansion",
                "Sustainable equipment development programs"
            ])
        elif 'software' in business_summary or 'cloud' in business_summary:
            initiatives.extend([
                "Cloud-first strategy and platform consolidation",
                "AI and machine learning integration across products",
                "International market expansion and localization"
            ])
        elif 'financial' in business_summary or 'banking' in business_summary:
            initiatives.extend([
                "Digital transformation and operational efficiency",
                "Risk management and regulatory compliance enhancement",
                "Customer experience and service automation"
            ])
        elif 'healthcare' in business_summary or 'pharmaceutical' in business_summary:
            initiatives.extend([
                "Digital health and telemedicine platform development",
                "Research and development pipeline expansion",
                "Regulatory compliance and quality assurance programs"
            ])
        elif 'retail' in business_summary or 'consumer' in business_summary:
            initiatives.extend([
                "Omnichannel customer experience enhancement",
                "Supply chain optimization and automation",
                "E-commerce platform development and expansion"
            ])
        elif 'energy' in business_summary or 'renewable' in business_summary:
            initiatives.extend([
                "Renewable energy technology development",
                "Energy efficiency and sustainability programs",
                "Smart grid and infrastructure modernization"
            ])
        
        # Add financial health context for strategic capacity
        if operating_margin > 0.15 and operating_cash_flow > 0:
            initiatives.append("Strong financial position enabling aggressive strategic investments")
        elif operating_margin > 0.05 and operating_cash_flow > 0:
            initiatives.append("Moderate financial capacity supporting selective strategic initiatives")
        else:
            initiatives.append("Focus on operational efficiency and cost optimization programs")
        
        # Add growth-based strategic context
        if revenue_growth > 0.15:
            initiatives.append("High growth momentum driving expansion and market penetration strategies")
        elif revenue_growth < 0:
            initiatives.append("Turnaround and restructuring initiatives to restore growth")
        
        # Generic fallback if no specific initiatives identified
        if not initiatives:
            initiatives.extend([
                "Operational excellence and process optimization",
                "Market expansion and customer acquisition strategies",
                "Technology integration and digital transformation"
            ])
        
        return "• " + "\n• ".join(initiatives[:3])
    
    def get_regulatory_changes(self) -> str:
        """Get regulatory changes analysis based on actual business context and industry exposure"""
        business_summary = self.info.get('longBusinessSummary', '').lower()
        
        regulatory = []
        
        # Business-specific regulatory changes
        if 'school bus' in business_summary or 'student transportation' in business_summary:
            regulatory.extend([
                "EPA emissions standards driving electric vehicle adoption",
                "DOT safety regulations for school transportation",
                "State-level incentives for clean energy vehicles"
            ])
        elif 'construction' in business_summary and 'equipment' in business_summary:
            regulatory.extend([
                "EPA emissions standards for heavy machinery",
                "OSHA safety regulations for construction equipment",
                "Environmental compliance and equipment efficiency standards"
            ])
        elif 'software' in business_summary or 'cloud' in business_summary:
            regulatory.extend([
                "Data privacy regulations (GDPR, CCPA) compliance requirements",
                "AI governance and algorithmic transparency standards",
                "Cybersecurity reporting and breach notification mandates"
            ])
        elif 'financial' in business_summary or 'banking' in business_summary:
            regulatory.extend([
                "Capital requirements and stress testing regulations",
                "Consumer protection and fair lending compliance",
                "Anti-money laundering and KYC regulatory updates"
            ])
        elif 'healthcare' in business_summary or 'pharmaceutical' in business_summary:
            regulatory.extend([
                "FDA approval processes and drug pricing regulations",
                "Patient data protection and HIPAA compliance",
                "Telehealth regulations and reimbursement policy changes"
            ])
        elif 'energy' in business_summary or 'oil' in business_summary:
            regulatory.extend([
                "Environmental regulations and carbon emission standards",
                "Energy efficiency and renewable energy mandates",
                "Safety and environmental compliance requirements"
            ])
        elif 'retail' in business_summary or 'consumer' in business_summary:
            regulatory.extend([
                "Consumer protection and product safety regulations",
                "Data privacy and e-commerce compliance requirements",
                "Labor regulations and workplace safety standards"
            ])
        
        # Add international regulatory context if applicable
        if 'international' in business_summary or 'global' in business_summary:
            regulatory.append("International regulatory harmonization and cross-border compliance requirements")
        
        # Add general regulatory context based on company size
        market_cap = self.info.get('marketCap', 0)
        if market_cap > 50e9:  # Large companies
            regulatory.append("Enhanced regulatory scrutiny and reporting requirements for large corporations")
        elif market_cap < 1e9:  # Small companies
            regulatory.append("Regulatory compliance costs creating proportionally higher burden")
        
        # Generic fallback if no specific regulatory changes identified
        if not regulatory:
            regulatory.extend([
                "Environmental regulations and sustainability reporting requirements",
                "Tax policy changes and compliance obligations",
                "Industry-specific regulatory updates and standards"
            ])
        
        return "• " + "\n• ".join(regulatory[:3])
    
    def get_market_developments(self) -> str:
        """Get market developments analysis based on actual business context and financial performance"""
        business_summary = self.info.get('longBusinessSummary', '').lower()
        
        developments = []
        
        # Analyze market position and financial metrics
        market_cap = self.info.get('marketCap', 0)
        revenue_growth = self.info.get('revenueGrowth', 0)
        operating_margin = self.get_operating_margin()
        
        # Business-specific market developments
        if 'school bus' in business_summary or 'student transportation' in business_summary:
            developments.extend([
                "Growing demand for electric school buses driven by environmental mandates",
                "Infrastructure spending supporting transportation modernization",
                "Supply chain challenges affecting vehicle production and delivery"
            ])
        elif 'construction' in business_summary and 'equipment' in business_summary:
            developments.extend([
                "Infrastructure spending driving construction equipment demand",
                "Labor shortages accelerating equipment automation adoption",
                "Supply chain disruptions affecting manufacturing and pricing"
            ])
        elif 'software' in business_summary or 'cloud' in business_summary:
            developments.extend([
                "Accelerated digital transformation increasing software demand",
                "Cloud computing market expansion and competitive pressures",
                "AI integration driving productivity and automation trends"
            ])
        elif 'financial' in business_summary or 'banking' in business_summary:
            developments.extend([
                "Interest rate environment affecting lending margins and profitability",
                "Fintech disruption accelerating digital banking adoption",
                "Regulatory changes impacting capital requirements and operations"
            ])
        elif 'healthcare' in business_summary or 'pharmaceutical' in business_summary:
            developments.extend([
                "Aging population driving healthcare demand and spending",
                "Regulatory approval processes affecting drug development timelines",
                "Digital health adoption accelerating post-pandemic transformation"
            ])
        elif 'energy' in business_summary or 'oil' in business_summary:
            developments.extend([
                "Energy transition policies affecting traditional energy markets",
                "Renewable energy investment driving market transformation",
                "Geopolitical factors impacting energy supply and pricing"
            ])
        elif 'retail' in business_summary or 'consumer' in business_summary:
            developments.extend([
                "E-commerce growth transforming retail landscape",
                "Consumer spending patterns shifting post-pandemic",
                "Supply chain disruptions affecting inventory and pricing"
            ])
        
        # Add market position context based on performance
        if market_cap > 50e9 and revenue_growth > 0.10:
            developments.append("Market leadership position enabling advantageous response to industry trends")
        elif market_cap > 5e9 and operating_margin > 0.10:
            developments.append("Strong market position and profitability supporting strategic adaptation")
        elif market_cap < 1e9:
            developments.append("Small-cap positioning requiring agile response to market changes")
        
        # Add financial performance context
        if revenue_growth > 0.15:
            developments.append("Strong growth momentum outpacing industry trends")
        elif revenue_growth < -0.05:
            developments.append("Revenue challenges requiring strategic repositioning")
        
        # Generic fallback if no specific developments identified
        if not developments:
            developments.extend([
                "Economic uncertainty affecting business investment and consumer spending",
                "Technology disruption creating new market opportunities and challenges",
                "Sustainability trends driving business model evolution"
            ])
        
        return "• " + "\n• ".join(developments[:3])
    
    def generate_overall_rating(self) -> str:
        """Generate overall investment rating based on comprehensive analysis"""
        score = 0
        factors = []
        
        # Profitability factors
        net_margin = self.get_net_margin()
        if net_margin > 0.15:
            score += 2
            factors.append("Strong profitability")
        elif net_margin > 0.05:
            score += 1
            factors.append("Decent profitability")
        elif net_margin < 0:
            score -= 1
            factors.append("Negative profitability")
        
        # Growth factors
        revenue_growth = self.info.get('revenueGrowth', 0)
        if revenue_growth > 0.15:
            score += 2
            factors.append("Strong growth")
        elif revenue_growth > 0.05:
            score += 1
            factors.append("Moderate growth")
        elif revenue_growth < 0:
            score -= 1
            factors.append("Declining revenue")
        
        # Financial health factors
        current_ratio = self.get_current_ratio()
        if current_ratio > 1.5:
            score += 1
            factors.append("Strong liquidity")
        elif current_ratio < 1.0:
            score -= 1
            factors.append("Liquidity concerns")
        
        # Leverage factors
        debt_to_equity = self.get_debt_to_equity()
        if debt_to_equity < 0.5:
            score += 1
            factors.append("Conservative leverage")
        elif debt_to_equity > 2.0:
            score -= 1
            factors.append("High leverage")
        
        # Valuation factors
        pe_ratio = self.get_pe_ratio()
        if 10 <= pe_ratio <= 20:
            score += 1
            factors.append("Reasonable valuation")
        elif pe_ratio > 30:
            score -= 1
            factors.append("High valuation")
        
        # Return factors
        roe = self.get_roe()
        if roe > 0.15:
            score += 1
            factors.append("Strong returns")
        elif roe < 0:
            score -= 1
            factors.append("Poor returns")
        
        # Determine rating
        if score >= 4:
            rating = "STRONG BUY"
        elif score >= 2:
            rating = "BUY"
        elif score >= 0:
            rating = "HOLD"
        elif score >= -2:
            rating = "WEAK HOLD"
        else:
            rating = "SELL"
        
        return f"{rating} (Score: {score}/6)"
    
    def get_price_target(self) -> str:
        """Get price target based on valuation analysis and company fundamentals"""
        current_price = self.info.get('currentPrice', 0)
        if current_price == 0:
            return "N/A - Current price not available"
        
        # Try to get analyst target first
        analyst_target = self.info.get('targetMeanPrice', 0)
        if analyst_target and analyst_target > 0:
            upside = ((analyst_target - current_price) / current_price) * 100
            return f"${analyst_target:.2f} (Analyst consensus, {upside:+.1f}% upside)"
        
        # Calculate based on financial metrics and growth
        pe_ratio = self.get_pe_ratio()
        eps = self.get_eps()
        revenue_growth = self.info.get('revenueGrowth', 0)
        
        if pe_ratio > 0 and eps > 0:
            # Adjust P/E based on growth rate
            if revenue_growth > 0.15:
                target_pe = min(25, pe_ratio * 1.1)  # Growth premium
            elif revenue_growth > 0.05:
                target_pe = min(20, pe_ratio)  # Maintain current
            else:
                target_pe = max(10, pe_ratio * 0.9)  # Discount for low growth
            
            fair_value = eps * target_pe
            upside = ((fair_value - current_price) / current_price) * 100
            return f"${fair_value:.2f} (Fundamental analysis, {upside:+.1f}% upside)"
        
        # Fallback to growth-based target
        if revenue_growth > 0.10:
            growth_multiple = min(1.25, 1 + (revenue_growth * 0.5))  # Cap at 25% upside
            target_price = current_price * growth_multiple
            upside = ((target_price - current_price) / current_price) * 100
            return f"${target_price:.2f} (Growth-based estimate, {upside:+.1f}% upside)"
        elif revenue_growth > 0:
            target_price = current_price * 1.10  # Conservative 10% upside
            return f"${target_price:.2f} (Conservative estimate, +10% upside)"
        else:
            target_price = current_price * 0.95  # Slight discount for declining growth
            return f"${target_price:.2f} (Risk-adjusted estimate, -5% downside)"
    
    def get_investment_horizon(self) -> str:
        """Get investment horizon based on company characteristics and market dynamics"""
        market_cap = self.info.get('marketCap', 0)
        revenue_growth = self.info.get('revenueGrowth', 0)
        business_summary = self.info.get('longBusinessSummary', '').lower()
        beta = self.info.get('beta', 1.0)
        
        # Technology companies - shorter horizon due to rapid changes
        if 'technology' in business_summary or 'software' in business_summary:
            if revenue_growth > 0.20:
                return "6-12 months (High-growth tech with rapid market changes)"
            else:
                return "9-15 months (Mature tech with steady innovation cycles)"
        
        # Financial services - medium horizon based on regulatory cycles
        elif 'financial' in business_summary or 'banking' in business_summary:
            if market_cap > 50e9:
                return "18-24 months (Large financial institution stability)"
            else:
                return "12-18 months (Regional financial services)"
        
        # Healthcare - longer horizon due to regulatory approvals
        elif 'healthcare' in business_summary or 'pharmaceutical' in business_summary:
            return "24-36 months (Healthcare regulatory and development cycles)"
        
        # Industrial/Manufacturing - cyclical considerations
        elif 'construction' in business_summary or 'manufacturing' in business_summary:
            if revenue_growth > 0.15:
                return "12-18 months (Strong growth in cyclical industry)"
            else:
                return "18-24 months (Cyclical industry considerations)"
        
        # Large cap stable companies - longer horizon
        elif market_cap > 50e9:
            return "18-24 months (Large cap stability and market leadership)"
        
        # High volatility companies - shorter horizon
        elif beta > 1.5:
            return "6-12 months (High volatility requiring active management)"
        
        # High growth companies - medium horizon
        elif revenue_growth > 0.15:
            return "12-18 months (High growth trajectory with execution risk)"
        
        # Small cap companies - shorter horizon due to volatility
        elif market_cap < 1e9:
            return "9-15 months (Small cap volatility and liquidity considerations)"
        
        # Default medium-term horizon
        else:
            return "12-18 months (Standard investment horizon for stable operations)"
    
    def generate_risk_assessment(self) -> str:
        """Generate comprehensive risk assessment based on actual business context and financial metrics"""
        risk_factors = []
        business_summary = self.info.get('longBusinessSummary', '').lower()
        
        # Market risk based on actual beta
        beta = self.info.get('beta', 1.0)
        if beta > 1.5:
            risk_factors.append(f"Very high market volatility with beta of {beta:.2f} amplifying market movements")
        elif beta > 1.3:
            risk_factors.append(f"High market volatility with beta of {beta:.2f} above market average")
        elif beta < 0.7:
            risk_factors.append(f"Low market correlation with beta of {beta:.2f} indicating unique risk factors")
        
        # Financial leverage risk based on actual metrics
        debt_to_equity = self.get_debt_to_equity()
        if debt_to_equity > 2.0:
            risk_factors.append(f"Very high financial leverage with {self.format_ratio(debt_to_equity)} debt-to-equity ratio")
        elif debt_to_equity > 1.0:
            risk_factors.append(f"Elevated debt levels with {self.format_ratio(debt_to_equity)} debt-to-equity ratio")
        
        # Liquidity risk based on actual current ratio
        current_ratio = self.get_current_ratio()
        if current_ratio < 1.0:
            risk_factors.append(f"Liquidity constraints with {self.format_ratio(current_ratio)} current ratio below 1.0")
        elif current_ratio < 1.2:
            risk_factors.append(f"Tight liquidity position with {self.format_ratio(current_ratio)} current ratio")
        
        # Profitability risk based on actual margins
        net_margin = self.get_net_margin()
        if net_margin < 0:
            risk_factors.append(f"Negative profitability with {self.format_percentage(net_margin)} net margin")
        elif net_margin < 0.05:
            risk_factors.append(f"Low profit margins of {self.format_percentage(net_margin)} vulnerable to cost pressures")
        
        # Growth risk based on actual revenue trends
        revenue_growth = self.info.get('revenueGrowth', 0)
        if revenue_growth < -0.10:
            risk_factors.append(f"Significant revenue decline of {self.format_percentage(revenue_growth)} indicating market challenges")
        elif revenue_growth < 0:
            risk_factors.append(f"Revenue contraction of {self.format_percentage(revenue_growth)} suggesting competitive pressures")
        
        # Business-specific risks based on actual business context
        if 'cyclical' in business_summary or 'seasonal' in business_summary:
            risk_factors.append("Cyclical or seasonal business patterns creating revenue volatility")
        
        if 'regulation' in business_summary or 'compliance' in business_summary:
            risk_factors.append("Regulatory compliance risks and changing regulatory environment")
        
        if 'supply chain' in business_summary or 'manufacturing' in business_summary:
            risk_factors.append("Supply chain disruptions and manufacturing cost inflation risks")
        
        if 'competition' in business_summary or 'competitive' in business_summary:
            risk_factors.append("Intense competitive environment pressuring margins and market share")
        
        if 'technology' in business_summary or 'digital' in business_summary:
            risk_factors.append("Technology disruption and rapid innovation cycle risks")
        
        if 'international' in business_summary or 'global' in business_summary:
            risk_factors.append("Foreign exchange and international market risks")
        
        # Market cap based risk assessment
        market_cap = self.info.get('marketCap', 0)
        if market_cap < 500e6:  # Small cap
            risk_factors.append("Small-cap volatility and limited liquidity increasing investment risk")
        elif market_cap < 1e9:  # Small to mid cap
            risk_factors.append("Mid-cap volatility and market access constraints")
        
        # Interest rate sensitivity for high debt companies
        if debt_to_equity > 0.5:
            risk_factors.append("Interest rate sensitivity due to debt levels affecting borrowing costs")
        
        # Concentration risk for small companies
        if market_cap < 2e9:
            risk_factors.append("Business concentration risk and limited diversification")
        
        # Default moderate risk if no specific risks identified
        if not risk_factors:
            risk_factors.append("Moderate risk profile within industry norms and market conditions")
        
        return "• " + "\n• ".join(risk_factors[:5])  # Limit to top 5 risks
    
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
    
    def format_currency_simple(self, value) -> str:
        """Format simple currency values (for EPS, book value)"""
        if pd.isna(value) or value == 0:
            return "N/A"
        return f"${value:.2f}"
    
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