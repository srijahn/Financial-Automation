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
        """Generate opportunities analysis based on industry and company context"""
        opportunities = []
        
        # Industry-specific opportunities
        industry = self.info.get('industry', '').lower()
        sector = self.info.get('sector', '').lower()
        
        # Technology sector opportunities
        if 'technology' in sector or 'software' in industry:
            opportunities.extend([
                "Digital transformation driving increased demand for tech solutions",
                "Cloud adoption and subscription model growth",
                "AI and machine learning integration opportunities",
                "Expansion into emerging markets"
            ])
        
        # Transportation/Manufacturing opportunities
        elif 'transportation' in industry or 'manufacturing' in industry or 'industrial' in sector:
            opportunities.extend([
                "Infrastructure spending and government investment",
                "Electric vehicle transition creating new market opportunities",
                "Automation and efficiency improvements",
                "Supply chain optimization technologies"
            ])
        
        # Financial services opportunities
        elif 'financial' in sector or 'bank' in industry:
            opportunities.extend([
                "Digital banking and fintech innovation",
                "Interest rate environment changes",
                "Regulatory changes creating new market opportunities",
                "Cross-selling and customer acquisition strategies"
            ])
        
        # Healthcare opportunities
        elif 'healthcare' in sector or 'pharmaceutical' in industry:
            opportunities.extend([
                "Aging population driving healthcare demand",
                "Telehealth and digital health solutions",
                "Personalized medicine and genomics",
                "Healthcare technology integration"
            ])
        
        # Generic opportunities for all companies
        else:
            opportunities.extend([
                "Market expansion in emerging economies",
                "Digital transformation initiatives",
                "Strategic partnerships and alliances",
                "New product development and innovation"
            ])
        
        # Add growth-specific opportunities
        revenue_growth = self.info.get('revenueGrowth', 0)
        if revenue_growth > 0.1:
            opportunities.append("Strong growth momentum for market expansion")
        
        # Add cash-specific opportunities
        operating_cash_flow = self.get_operating_cash_flow()
        if operating_cash_flow > 0:
            opportunities.append("Strong cash generation enabling strategic investments")
        
        return "• " + "\n• ".join(opportunities[:5])  # Limit to top 5 opportunities
    
    def generate_threats_analysis(self) -> str:
        """Generate threats analysis based on industry and company context"""
        threats = []
        
        # Industry-specific threats
        industry = self.info.get('industry', '').lower()
        sector = self.info.get('sector', '').lower()
        
        # Technology sector threats
        if 'technology' in sector or 'software' in industry:
            threats.extend([
                "Rapid technological obsolescence and disruption",
                "Increased competition from tech giants",
                "Cybersecurity risks and data privacy regulations",
                "Talent acquisition and retention challenges"
            ])
        
        # Transportation/Manufacturing threats
        elif 'transportation' in industry or 'manufacturing' in industry or 'industrial' in sector:
            threats.extend([
                "Supply chain disruptions and material cost inflation",
                "Environmental regulations and compliance costs",
                "Global trade tensions and tariff impacts",
                "Economic cycles affecting capital expenditure"
            ])
        
        # Financial services threats
        elif 'financial' in sector or 'bank' in industry:
            threats.extend([
                "Interest rate volatility and credit risks",
                "Regulatory changes and compliance costs",
                "Fintech disruption and competition",
                "Economic downturns affecting loan quality"
            ])
        
        # Healthcare threats
        elif 'healthcare' in sector or 'pharmaceutical' in industry:
            threats.extend([
                "Regulatory approval risks and compliance costs",
                "Pricing pressure from government and insurers",
                "Patent expirations and generic competition",
                "Liability risks and litigation exposure"
            ])
        
        # Generic threats for all companies
        else:
            threats.extend([
                "Increased competition in the market",
                "Economic downturns and market volatility",
                "Regulatory changes and compliance costs",
                "Supply chain disruptions"
            ])
        
        # Add financial-specific threats
        debt_to_equity = self.get_debt_to_equity()
        if debt_to_equity > 1.0:
            threats.append("High debt levels increasing financial risk")
        
        current_ratio = self.get_current_ratio()
        if current_ratio < 1.2:
            threats.append("Liquidity constraints limiting operational flexibility")
        
        return "• " + "\n• ".join(threats[:5])  # Limit to top 5 threats
    
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
        """Get main competitors based on industry and sector"""
        industry = self.info.get('industry', '').lower()
        sector = self.info.get('sector', '').lower()
        
        # Industry-specific competitors
        if 'transportation' in industry or 'bus' in industry or 'construction machinery' in industry or 'farm' in industry:
            # Check if it's specifically BlueBird or similar bus companies
            business_summary = self.info.get('longBusinessSummary', '').lower()
            if 'school bus' in business_summary or 'bus' in business_summary:
                competitors = [
                    "Thomas Built Buses (Daimler)",
                    "IC Bus (Navistar)",
                    "Collins Bus Corporation",
                    "Carpenter Bus Sales",
                    "Trans Tech Bus"
                ]
            else:
                competitors = [
                    "Caterpillar Inc.",
                    "Deere & Company",
                    "CNH Industrial N.V.",
                    "AGCO Corporation",
                    "Komatsu Ltd."
                ]
            competitors = [
                "Thomas Built Buses (Daimler)",
                "IC Bus (Navistar)",
                "Collins Bus Corporation",
                "Carpenter Bus Sales",
                "Trans Tech Bus"
            ]
        elif 'technology' in sector or 'software' in industry:
            competitors = [
                "Microsoft Corporation",
                "Oracle Corporation",
                "Salesforce Inc.",
                "Adobe Inc.",
                "ServiceNow Inc."
            ]
        elif 'financial' in sector or 'bank' in industry:
            competitors = [
                "JPMorgan Chase & Co.",
                "Bank of America Corp.",
                "Wells Fargo & Company",
                "Citigroup Inc.",
                "Goldman Sachs Group Inc."
            ]
        elif 'healthcare' in sector or 'pharmaceutical' in industry:
            competitors = [
                "Johnson & Johnson",
                "Pfizer Inc.",
                "Merck & Co. Inc.",
                "Abbott Laboratories",
                "Bristol Myers Squibb"
            ]
        elif 'retail' in sector or 'consumer' in industry:
            competitors = [
                "Amazon.com Inc.",
                "Walmart Inc.",
                "Target Corporation",
                "Costco Wholesale Corp.",
                "Home Depot Inc."
            ]
        else:
            # Generic competitors based on market cap
            market_cap = self.info.get('marketCap', 0)
            if market_cap > 100e9:  # $100B+
                competitors = ["Major industry leaders and Fortune 500 companies"]
            elif market_cap > 10e9:  # $10B+
                competitors = ["Mid-to-large cap companies in similar sectors"]
            elif market_cap > 1e9:  # $1B+
                competitors = ["Mid-cap companies and emerging market players"]
            else:
                competitors = ["Small-cap companies and niche market players"]
        
        return "• " + "\n• ".join(competitors[:5])  # Limit to top 5
    
    def get_recent_acquisitions(self) -> str:
        """Get recent acquisitions analysis"""
        industry = self.info.get('industry', '').lower()
        sector = self.info.get('sector', '').lower()
        market_cap = self.info.get('marketCap', 0)
        
        acquisitions = []
        
        # Industry-specific acquisition trends
        if 'transportation' in industry or 'bus' in industry or 'construction machinery' in industry or 'farm' in industry:
            # Check if it's specifically BlueBird or similar bus companies
            business_summary = self.info.get('longBusinessSummary', '').lower()
            if 'school bus' in business_summary or 'bus' in business_summary:
                acquisitions.extend([
                    "Monitoring consolidation in school bus manufacturing sector",
                    "Potential acquisitions of electric vehicle technology companies",
                    "Strategic partnerships with charging infrastructure providers"
                ])
            else:
                acquisitions.extend([
                    "Equipment manufacturing consolidation opportunities",
                    "Technology acquisitions for autonomous vehicle capabilities",
                    "Service and parts distribution network expansion"
                ])
            acquisitions.extend([
                "Monitoring consolidation in school bus manufacturing sector",
                "Potential acquisitions of electric vehicle technology companies",
                "Strategic partnerships with charging infrastructure providers"
            ])
        elif 'technology' in sector:
            acquisitions.extend([
                "Active in AI and machine learning company acquisitions",
                "Cloud infrastructure and SaaS platform acquisitions",
                "Cybersecurity and data analytics company targets"
            ])
        elif 'financial' in sector:
            acquisitions.extend([
                "Fintech startup acquisitions for digital transformation",
                "Wealth management and advisory firm acquisitions",
                "Payment processing and blockchain technology investments"
            ])
        else:
            acquisitions.extend([
                "Strategic acquisitions to expand market presence",
                "Technology acquisitions for digital transformation",
                "Vertical integration opportunities being evaluated"
            ])
        
        # Add market cap specific context
        if market_cap > 10e9:
            acquisitions.append("Well-positioned for strategic acquisitions with strong balance sheet")
        elif market_cap > 1e9:
            acquisitions.append("Selective acquisition strategy focused on core competencies")
        else:
            acquisitions.append("Potential acquisition target for larger industry players")
        
        return "• " + "\n• ".join(acquisitions[:3])
    
    def get_product_launches(self) -> str:
        """Get product launches analysis"""
        industry = self.info.get('industry', '').lower()
        sector = self.info.get('sector', '').lower()
        
        launches = []
        
        # Industry-specific product launches
        if 'transportation' in industry or 'bus' in industry or 'construction machinery' in industry or 'farm' in industry:
            # Check if it's specifically BlueBird or similar bus companies
            business_summary = self.info.get('longBusinessSummary', '').lower()
            if 'school bus' in business_summary or 'bus' in business_summary:
                launches.extend([
                    "Electric school bus models with advanced safety features",
                    "Connected vehicle technologies and fleet management systems",
                    "Alternative fuel propulsion systems (CNG, propane, hydrogen)"
                ])
            else:
                launches.extend([
                    "Advanced construction and agricultural equipment",
                    "Autonomous and semi-autonomous vehicle technologies",
                    "Sustainable and electric-powered machinery"
                ])
            launches.extend([
                "Electric school bus models with advanced safety features",
                "Connected vehicle technologies and fleet management systems",
                "Alternative fuel propulsion systems (CNG, propane, hydrogen)"
            ])
        elif 'technology' in sector:
            launches.extend([
                "Cloud-based software solutions and platform updates",
                "AI-powered analytics and automation tools",
                "Mobile applications and user experience enhancements"
            ])
        elif 'financial' in sector:
            launches.extend([
                "Digital banking platforms and mobile payment solutions",
                "Robo-advisory and wealth management tools",
                "Blockchain and cryptocurrency services"
            ])
        elif 'healthcare' in sector:
            launches.extend([
                "Telemedicine and digital health platforms",
                "Personalized medicine and genomic testing services",
                "Medical device innovations and drug pipeline updates"
            ])
        else:
            launches.extend([
                "New product lines targeting emerging market segments",
                "Technology-enhanced service offerings",
                "Sustainability-focused product innovations"
            ])
        
        # Add innovation context
        rd_expenses = self.info.get('totalRevenue', 0) * 0.05  # Estimate 5% of revenue
        if rd_expenses > 0:
            launches.append(f"Continued R&D investment driving innovation pipeline")
        
        return "• " + "\n• ".join(launches[:3])
    
    def get_strategic_initiatives(self) -> str:
        """Get strategic initiatives analysis"""
        industry = self.info.get('industry', '').lower()
        sector = self.info.get('sector', '').lower()
        
        initiatives = []
        
        # Industry-specific strategic initiatives
        if 'transportation' in industry or 'bus' in industry or 'construction machinery' in industry or 'farm' in industry:
            # Check if it's specifically BlueBird or similar bus companies
            business_summary = self.info.get('longBusinessSummary', '').lower()
            if 'school bus' in business_summary or 'bus' in business_summary:
                initiatives.extend([
                    "Transition to electric and alternative fuel vehicles",
                    "Expansion of aftermarket parts and service revenue",
                    "Digital transformation of manufacturing processes"
                ])
            else:
                initiatives.extend([
                    "Precision agriculture and smart farming technologies",
                    "Electrification of construction and agricultural equipment",
                    "Autonomous vehicle development and deployment"
                ])
            initiatives.extend([
                "Transition to electric and alternative fuel vehicles",
                "Expansion of aftermarket parts and service revenue",
                "Digital transformation of manufacturing processes"
            ])
        elif 'technology' in sector:
            initiatives.extend([
                "Cloud-first strategy and SaaS transformation",
                "AI and machine learning integration across products",
                "International market expansion and localization"
            ])
        elif 'financial' in sector:
            initiatives.extend([
                "Digital transformation and branch optimization",
                "ESG investing and sustainable finance initiatives",
                "Regulatory compliance and risk management enhancement"
            ])
        else:
            initiatives.extend([
                "Operational efficiency and cost optimization programs",
                "Sustainability and environmental responsibility initiatives",
                "Customer experience enhancement and digitization"
            ])
        
        # Add financial health context
        operating_margin = self.get_operating_margin()
        if operating_margin > 0.15:
            initiatives.append("Strong margins enabling strategic reinvestment")
        elif operating_margin > 0.05:
            initiatives.append("Focus on margin improvement and operational efficiency")
        else:
            initiatives.append("Restructuring initiatives to improve profitability")
        
        return "• " + "\n• ".join(initiatives[:3])
    
    def get_regulatory_changes(self) -> str:
        """Get regulatory changes analysis"""
        industry = self.info.get('industry', '').lower()
        sector = self.info.get('sector', '').lower()
        
        regulatory = []
        
        # Industry-specific regulatory changes
        if 'transportation' in industry or 'bus' in industry or 'construction machinery' in industry or 'farm' in industry:
            # Check if it's specifically BlueBird or similar bus companies
            business_summary = self.info.get('longBusinessSummary', '').lower()
            if 'school bus' in business_summary or 'bus' in business_summary:
                regulatory.extend([
                    "EPA emissions standards driving electric vehicle adoption",
                    "DOT safety regulations for school transportation",
                    "State-level incentives for clean energy vehicles"
                ])
            else:
                regulatory.extend([
                    "EPA emissions standards for heavy machinery",
                    "OSHA safety regulations for construction equipment",
                    "Agricultural equipment efficiency standards"
                ])
            regulatory.extend([
                "EPA emissions standards driving electric vehicle adoption",
                "DOT safety regulations for school transportation",
                "State-level incentives for clean energy vehicles"
            ])
        elif 'technology' in sector:
            regulatory.extend([
                "Data privacy regulations (GDPR, CCPA) compliance",
                "AI governance and algorithmic transparency requirements",
                "Cybersecurity standards and reporting mandates"
            ])
        elif 'financial' in sector:
            regulatory.extend([
                "Basel III capital requirements and stress testing",
                "Consumer protection and fair lending regulations",
                "Anti-money laundering and KYC compliance"
            ])
        elif 'healthcare' in sector:
            regulatory.extend([
                "FDA approval processes and drug pricing regulations",
                "HIPAA compliance and patient data protection",
                "Telehealth regulations and reimbursement policies"
            ])
        else:
            regulatory.extend([
                "Environmental regulations and sustainability reporting",
                "Labor regulations and workplace safety standards",
                "Tax policy changes and international trade regulations"
            ])
        
        return "• " + "\n• ".join(regulatory[:3])
    
    def get_market_developments(self) -> str:
        """Get market developments analysis"""
        industry = self.info.get('industry', '').lower()
        sector = self.info.get('sector', '').lower()
        
        developments = []
        
        # Industry-specific market developments
        if 'transportation' in industry or 'bus' in industry or 'construction machinery' in industry or 'farm' in industry:
            # Check if it's specifically BlueBird or similar bus companies
            business_summary = self.info.get('longBusinessSummary', '').lower()
            if 'school bus' in business_summary or 'bus' in business_summary:
                developments.extend([
                    "Growing demand for electric school buses driven by environmental concerns",
                    "Infrastructure spending bills supporting transportation modernization",
                    "Supply chain challenges affecting vehicle production timelines"
                ])
            else:
                developments.extend([
                    "Infrastructure spending driving construction equipment demand",
                    "Precision agriculture trends boosting smart farming equipment",
                    "Labor shortages driving automation adoption"
                ])
            developments.extend([
                "Growing demand for electric school buses driven by environmental concerns",
                "Infrastructure spending bills supporting transportation modernization",
                "Supply chain challenges affecting vehicle production timelines"
            ])
        elif 'technology' in sector:
            developments.extend([
                "Accelerated digital transformation post-pandemic",
                "Cloud computing market expansion and competition",
                "AI and automation driving productivity gains"
            ])
        elif 'financial' in sector:
            developments.extend([
                "Interest rate environment affecting lending margins",
                "Fintech disruption and digital banking adoption",
                "Regulatory changes impacting capital requirements"
            ])
        else:
            developments.extend([
                "Economic uncertainty affecting consumer spending patterns",
                "Supply chain disruptions and inflation pressures",
                "Sustainability trends driving business model changes"
            ])
        
        # Add market cap context
        market_cap = self.info.get('marketCap', 0)
        if market_cap > 10e9:
            developments.append("Market leader well-positioned for industry trends")
        elif market_cap > 1e9:
            developments.append("Mid-cap company adapting to market changes")
        else:
            developments.append("Small-cap company seeking growth opportunities")
        
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
        """Get price target based on valuation analysis"""
        current_price = self.info.get('currentPrice', 0)
        if current_price == 0:
            return "N/A"
        
        # Try to get analyst target first
        analyst_target = self.info.get('targetMeanPrice', 0)
        if analyst_target and analyst_target > 0:
            upside = ((analyst_target - current_price) / current_price) * 100
            return f"${analyst_target:.2f} (Analyst consensus, {upside:+.1f}% upside)"
        
        # Calculate based on industry multiples
        pe_ratio = self.get_pe_ratio()
        eps = self.get_eps()
        
        if pe_ratio > 0 and eps > 0:
            # Use industry average P/E (assuming 15x for conservative estimate)
            industry_pe = 15
            fair_value = eps * industry_pe
            upside = ((fair_value - current_price) / current_price) * 100
            return f"${fair_value:.2f} (Fair value estimate, {upside:+.1f}% upside)"
        
        # Fallback to simple growth-based target
        revenue_growth = self.info.get('revenueGrowth', 0)
        if revenue_growth > 0:
            growth_multiple = min(1.2, 1 + revenue_growth)  # Cap at 20% upside
            target_price = current_price * growth_multiple
            upside = ((target_price - current_price) / current_price) * 100
            return f"${target_price:.2f} (Growth-based estimate, {upside:+.1f}% upside)"
        
        return f"${current_price * 1.05:.2f} (Conservative estimate, +5% upside)"
    
    def get_investment_horizon(self) -> str:
        """Get investment horizon based on company characteristics"""
        market_cap = self.info.get('marketCap', 0)
        revenue_growth = self.info.get('revenueGrowth', 0)
        industry = self.info.get('industry', '').lower()
        
        # Technology companies - shorter horizon due to rapid changes
        if 'technology' in industry or 'software' in industry:
            return "6-12 months (Technology sector volatility)"
        
        # Large cap stable companies - longer horizon
        elif market_cap > 50e9:
            return "18-24 months (Large cap stability)"
        
        # High growth companies - medium horizon
        elif revenue_growth > 0.15:
            return "12-18 months (High growth trajectory)"
        
        # Cyclical industries - shorter horizon
        elif any(sector in industry for sector in ['transportation', 'manufacturing', 'industrial']):
            return "12-15 months (Cyclical sector considerations)"
        
        # Default medium-term horizon
        else:
            return "12-18 months (Standard investment horizon)"
    
    def generate_risk_assessment(self) -> str:
        """Generate comprehensive risk assessment"""
        risk_factors = []
        
        # Market risk
        beta = self.info.get('beta', 1.0)
        if beta > 1.3:
            risk_factors.append("High market volatility (Beta > 1.3)")
        elif beta < 0.7:
            risk_factors.append("Low market correlation (Beta < 0.7)")
        
        # Financial risk
        debt_to_equity = self.get_debt_to_equity()
        if debt_to_equity > 2.0:
            risk_factors.append("Very high financial leverage")
        elif debt_to_equity > 1.0:
            risk_factors.append("Elevated debt levels")
        
        # Liquidity risk
        current_ratio = self.get_current_ratio()
        if current_ratio < 1.0:
            risk_factors.append("Liquidity constraints")
        elif current_ratio < 1.2:
            risk_factors.append("Tight liquidity position")
        
        # Profitability risk
        net_margin = self.get_net_margin()
        if net_margin < 0:
            risk_factors.append("Negative profitability")
        elif net_margin < 0.05:
            risk_factors.append("Low profit margins")
        
        # Growth risk
        revenue_growth = self.info.get('revenueGrowth', 0)
        if revenue_growth < -0.10:
            risk_factors.append("Significant revenue decline")
        elif revenue_growth < 0:
            risk_factors.append("Revenue contraction")
        
        # Industry-specific risks
        industry = self.info.get('industry', '').lower()
        if 'technology' in industry:
            risk_factors.append("Technology disruption risk")
        elif 'transportation' in industry:
            risk_factors.append("Regulatory and environmental risks")
        elif 'financial' in industry:
            risk_factors.append("Interest rate and credit risks")
        
        # Market cap risk
        market_cap = self.info.get('marketCap', 0)
        if market_cap < 1e9:
            risk_factors.append("Small-cap volatility and liquidity risk")
        
        # Default if no specific risks identified
        if not risk_factors:
            risk_factors.append("Moderate risk profile within industry norms")
        
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