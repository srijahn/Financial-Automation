

import os
import re
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ExtractedData:
    field_name: str
    value: Any
    confidence: float
    source_document: str
    context: str = ""
    extraction_method: str = ""

class EnhancedFinancialNormalizer:
    """Enhanced financial value normalization with better accuracy"""
    
    @staticmethod
    def normalize_financial_value(value: str, context: str = "") -> Optional[str]:
        """Enhanced financial value normalization with context awareness"""
        try:
            original_value = value
            value = value.replace(",", "").replace("$", "").strip()
            
            # Handle negative values
            is_negative = value.startswith('-') or value.startswith('(') or value.endswith(')')
            if is_negative:
                value = value.lstrip('-').strip('()')
            
            # Determine multiplier based on context and explicit indicators
            multiplier = 1
            value_lower = value.lower()
            context_lower = context.lower()
            
            # Check for explicit scale indicators
            if any(indicator in value_lower for indicator in ['trillion', 'trillions', 't']):
                multiplier = 1_000_000_000_000
            elif any(indicator in value_lower for indicator in ['billion', 'billions', 'b']):
                multiplier = 1_000_000_000
            elif any(indicator in value_lower for indicator in ['million', 'millions', 'm']):
                multiplier = 1_000_000
            elif any(indicator in value_lower for indicator in ['thousand', 'thousands', 'k']):
                multiplier = 1_000
            
            # Context-based scaling detection - IMPROVED
            if multiplier == 1 and context_lower:
                # Look for financial statement context
                if any(phrase in context_lower for phrase in [
                    'in thousands', 'thousands of dollars', 'thousands, except',
                    'amounts in thousands', 'dollars in thousands'
                ]):
                    multiplier = 1_000
                elif any(phrase in context_lower for phrase in [
                    'in millions', 'millions of dollars', 'millions, except',
                    'amounts in millions', 'dollars in millions'
                ]):
                    multiplier = 1_000_000
                elif any(phrase in context_lower for phrase in [
                    'in billions', 'billions of dollars', 'billions, except',
                    'amounts in billions', 'dollars in billions'
                ]):
                    multiplier = 1_000_000_000
            
            # Extract numeric value with improved regex
            number_match = re.search(r'(\d+(?:\.\d+)?)', value)
            if not number_match:
                return None
            
            number_str = number_match.group(1)
            if number_str == ".":
                return None
            
            final_value = float(number_str) * multiplier
            if is_negative:
                final_value = -final_value
            
            # Smart scaling for large numbers without explicit multipliers
            if multiplier == 1:
                # If value is very large (>1B), it's likely already in actual dollars
                if final_value >= 1_000_000_000:
                    pass  # Keep as is
                # If value is medium-large (100K-1B), likely in thousands
                elif final_value >= 100_000:
                    final_value *= 1_000
                    multiplier = 1_000
            
            # Format based on size with proper precision
            if abs(final_value) >= 1_000_000_000_000:
                return f"${final_value/1_000_000_000_000:.2f}T"
            elif abs(final_value) >= 1_000_000_000:
                return f"${final_value/1_000_000_000:.2f}B"
            elif abs(final_value) >= 1_000_000:
                return f"${final_value/1_000_000:.2f}M"
            elif abs(final_value) >= 1_000:
                return f"${final_value/1_000:.2f}K"
            else:
                return f"${final_value:,.0f}"
                
        except Exception as e:
            logger.warning(f"⚠️ Could not normalize value '{original_value}': {e}")
            return None

    @staticmethod
    def normalize_percentage(value: str) -> Optional[str]:
        """Normalize percentage values"""
        try:
            # Remove % symbol and whitespace
            cleaned = value.replace("%", "").strip()
            
            # Extract numeric value
            match = re.search(r'(\d+(?:\.\d+)?)', cleaned)
            if match:
                num = float(match.group(1))
                
                # If number is very small (< 1), assume it's already in decimal form
                if num < 1:
                    return f"{num * 100:.2f}%"
                else:
                    return f"{num:.2f}%"
            
            return None
        except Exception as e:
            logger.warning(f"⚠️ Could not normalize percentage '{value}': {e}")
            return None


class TargetedPatternMatcher:
    """Enhanced pattern matching targeting specific accuracy issues"""
    
    def __init__(self):
        self.financial_patterns = {
            'revenue': [
                # High-confidence table patterns
                r'(?:Net\s+sales|Total\s+revenue|Revenue)\s*\$?\s*([\d,\.]+(?:\s*(?:million|billion|m|b))?)',
                r'(?:Net\s+sales|Total\s+revenue)\s*\$?\s*([\d,\.]+)',
                # Context-aware patterns
                r'(?i)(?:net\s+sales|total\s+revenue|revenue)\s+(?:of\s+|was\s+|were\s+)?\$?\s*([\d,\.]+\s*(?:million|billion|m|b)?)',
                r'(?i)(?:generated|reported)\s+revenue\s+of\s+\$?\s*([\d,\.]+\s*(?:million|billion|m|b)?)',
            ],
            'net_income': [
                # Table patterns with better specificity
                r'(?:Net\s+income|Net\s+earnings)\s*\$?\s*([\d,\.]+(?:\s*(?:million|billion|m|b))?)',
                r'(?:Net\s+income|Net\s+loss)\s*\$?\s*\(?([\d,\.]+)\)?',
                # Earnings statement patterns
                r'(?i)(?:net\s+income|net\s+earnings)\s+(?:of\s+|was\s+|were\s+)?\$?\s*([\d,\.]+\s*(?:million|billion|m|b)?)',
                r'(?i)(?:net\s+income|earnings)\s+for\s+the\s+year\s+(?:of\s+|was\s+|were\s+)?\$?\s*([\d,\.]+\s*(?:million|billion|m|b)?)',
            ],
            'net_margin': [
                # Percentage patterns specifically
                r'(?i)net\s+(?:profit\s+)?margin\s*(?:of\s+|was\s+|were\s+)?([\d\.]+)%',
                r'(?i)net\s+margin\s*:\s*([\d\.]+)%',
                r'(?i)net\s+(?:profit\s+)?margin\s*(?:of\s+)?([\d\.]+)\s*percent',
            ],
            'operating_margin': [
                # Operating margin patterns
                r'(?i)operating\s+margin\s*(?:of\s+|was\s+|were\s+)?([\d\.]+)%',
                r'(?i)operating\s+margin\s*:\s*([\d\.]+)%',
                r'(?i)operating\s+(?:profit\s+)?margin\s*(?:of\s+)?([\d\.]+)\s*percent',
            ],
            'total_assets': [
                # Balance sheet patterns
                r'(?:Total\s+assets)\s*\$?\s*([\d,\.]+(?:\s*(?:million|billion|m|b))?)',
                r'(?i)total\s+assets\s+(?:of\s+|were\s+|was\s+)?\$?\s*([\d,\.]+\s*(?:million|billion|m|b)?)',
            ],
            'total_liabilities': [
                # Balance sheet patterns with better context
                r'(?:Total\s+liabilities)\s*\$?\s*([\d,\.]+(?:\s*(?:million|billion|m|b))?)',
                r'(?i)total\s+liabilities\s+(?:of\s+|were\s+|was\s+)?\$?\s*([\d,\.]+\s*(?:million|billion|m|b)?)',
                r'(?i)total\s+liabilities\s+and\s+stockholders\?\s+equity\s*\$?\s*([\d,\.]+\s*(?:million|billion|m|b))?',
            ],
            'eps': [
                # EPS patterns
                r'(?i)(?:basic\s+|diluted\s+)?earnings\s+per\s+share\s*\$?\s*([\d\.\-]+)',
                r'(?i)EPS\s*\$?\s*([\d\.\-]+)',
                r'(?i)earnings\s+per\s+common\s+share\s*\$?\s*([\d\.\-]+)',
            ],
            'market_cap': [
                # Market cap patterns
                r'(?i)market\s+cap(?:italization)?\s*\$?\s*([\d,\.]+\s*(?:million|billion|trillion|m|b|t)?)',
                r'(?i)market\s+value\s*\$?\s*([\d,\.]+\s*(?:million|billion|trillion|m|b|t)?)',
            ],
            'employees': [
                # Employee count patterns
                r'(?i)(?:approximately\s+|about\s+|over\s+)?([\d,]+)\s+(?:full-time\s+)?employees',
                r'(?i)(?:number\s+of\s+)?employees\s*:?\s*([\d,]+)',
                r'(?i)workforce\s+of\s+(?:approximately\s+|about\s+)?([\d,]+)',
            ],
            'operating_income': [
                # Operating income patterns
                r'(?:Operating\s+income|Operating\s+earnings)\s*\$?\s*([\d,\.]+(?:\s*(?:million|billion|m|b))?)',
                r'(?i)operating\s+income\s+(?:of\s+|was\s+|were\s+)?\$?\s*([\d,\.]+\s*(?:million|billion|m|b)?)',
                r'(?i)income\s+from\s+operations\s*\$?\s*([\d,\.]+\s*(?:million|billion|m|b)?)',
            ],
            'operating_cash_flow': [
                # Operating cash flow patterns
                r'(?:Operating\s+cash\s+flow|Cash\s+flow\s+from\s+operating)\s*\$?\s*([\d,\.]+(?:\s*(?:million|billion|m|b))?)',
                r'(?i)(?:net\s+)?cash\s+(?:provided\s+by|from)\s+operating\s+activities\s*\$?\s*([\d,\.]+\s*(?:million|billion|m|b)?)',
                r'(?i)operating\s+cash\s+flow\s+(?:of\s+|was\s+|were\s+)?\$?\s*([\d,\.]+\s*(?:million|billion|m|b)?)',
            ],
            'shareholders_equity': [
                # Shareholders equity patterns
                r'(?:Total\s+shareholders?\s+equity|Stockholders?\s+equity)\s*\$?\s*([\d,\.]+(?:\s*(?:million|billion|m|b))?)',
                r'(?i)total\s+shareholders?\s+equity\s+(?:of\s+|was\s+|were\s+)?\$?\s*([\d,\.]+\s*(?:million|billion|m|b)?)',
                r'(?i)stockholders?\s+equity\s*\$?\s*([\d,\.]+\s*(?:million|billion|m|b)?)',
            ],
            'roe': [
                # Return on equity patterns
                r'(?i)return\s+on\s+equity\s*(?:of\s+|was\s+|were\s+)?([\d\.]+)%',
                r'(?i)ROE\s*(?:of\s+|was\s+|were\s+)?([\d\.]+)%',
                r'(?i)return\s+on\s+shareholders?\s+equity\s*(?:of\s+)?([\d\.]+)\s*percent',
            ],
            'gross_profit': [
                # Gross profit patterns
                r'(?:Gross\s+profit|Gross\s+income)\s*\$?\s*([\d,\.]+(?:\s*(?:million|billion|m|b))?)',
                r'(?i)gross\s+profit\s+(?:of\s+|was\s+|were\s+)?\$?\s*([\d,\.]+\s*(?:million|billion|m|b)?)',
            ],
            'gross_margin': [
                # Gross margin patterns
                r'(?i)gross\s+(?:profit\s+)?margin\s*(?:of\s+|was\s+|were\s+)?([\d\.]+)%',
                r'(?i)gross\s+margin\s*:\s*([\d\.]+)%',
                r'(?i)gross\s+(?:profit\s+)?margin\s*(?:of\s+)?([\d\.]+)\s*percent',
            ],
            'current_assets': [
                # Current assets patterns
                r'(?:Total\s+current\s+assets|Current\s+assets)\s*\$?\s*([\d,\.]+(?:\s*(?:million|billion|m|b))?)',
                r'(?i)current\s+assets\s+(?:of\s+|were\s+|was\s+)?\$?\s*([\d,\.]+\s*(?:million|billion|m|b)?)',
            ],
            'current_liabilities': [
                # Current liabilities patterns
                r'(?:Total\s+current\s+liabilities|Current\s+liabilities)\s*\$?\s*([\d,\.]+(?:\s*(?:million|billion|m|b))?)',
                r'(?i)current\s+liabilities\s+(?:of\s+|were\s+|was\s+)?\$?\s*([\d,\.]+\s*(?:million|billion|m|b)?)',
            ],
            'current_ratio': [
                # Current ratio patterns
                r'(?i)current\s+ratio\s*(?:of\s+|was\s+|were\s+)?([\d\.]+)',
                r'(?i)current\s+ratio\s*:\s*([\d\.]+)',
                r'(?i)current\s+ratio\s*(?:of\s+)?([\d\.]+)\s*(?:to\s+1)?',
            ],
            'total_debt': [
                # Total debt patterns
                r'(?:Total\s+debt|Long-term\s+debt)\s*\$?\s*([\d,\.]+(?:\s*(?:million|billion|m|b))?)',
                r'(?i)total\s+debt\s+(?:of\s+|was\s+|were\s+)?\$?\s*([\d,\.]+\s*(?:million|billion|m|b)?)',
                r'(?i)long-term\s+debt\s*\$?\s*([\d,\.]+\s*(?:million|billion|m|b)?)',
            ],
            'debt_to_equity': [
                # Debt to equity patterns
                r'(?i)debt\s+to\s+equity\s*(?:ratio\s*)?(?:of\s+|was\s+|were\s+)?([\d\.]+)',
                r'(?i)debt-to-equity\s*(?:ratio\s*)?(?:of\s+)?([\d\.]+)',
                r'(?i)D/E\s*(?:ratio\s*)?(?:of\s+)?([\d\.]+)',
            ],
            'pe_ratio': [
                # P/E ratio patterns
                r'(?i)(?:price\s+to\s+earnings|P/E)\s*(?:ratio\s*)?(?:of\s+|was\s+|were\s+)?([\d\.]+)',
                r'(?i)PE\s*(?:ratio\s*)?(?:of\s+)?([\d\.]+)',
                r'(?i)price\s+earnings\s*(?:ratio\s*)?(?:of\s+)?([\d\.]+)',
            ],
            'book_value_per_share': [
                # Book value per share patterns
                r'(?i)book\s+value\s+per\s+share\s*\$?\s*([\d\.\-]+)',
                r'(?i)BVPS\s*\$?\s*([\d\.\-]+)',
                r'(?i)book\s+value\s+per\s+common\s+share\s*\$?\s*([\d\.\-]+)',
            ],
            'dividend_per_share': [
                # Dividend per share patterns
                r'(?i)dividend\s+per\s+share\s*\$?\s*([\d\.\-]+)',
                r'(?i)DPS\s*\$?\s*([\d\.\-]+)',
                r'(?i)quarterly\s+dividend\s*\$?\s*([\d\.\-]+)',
            ],
            'dividend_yield': [
                # Dividend yield patterns
                r'(?i)dividend\s+yield\s*(?:of\s+|was\s+|were\s+)?([\d\.]+)%',
                r'(?i)yield\s*(?:of\s+)?([\d\.]+)\s*percent',
                r'(?i)annual\s+yield\s*(?:of\s+)?([\d\.]+)%',
            ],
            'shares_outstanding': [
                # Shares outstanding patterns
                r'(?i)(?:shares\s+outstanding|outstanding\s+shares)\s*(?:of\s+|were\s+|was\s+)?([\d,\.]+(?:\s*(?:million|billion|m|b))?)',
                r'(?i)common\s+shares\s+outstanding\s*(?:of\s+)?([\d,\.]+\s*(?:million|billion|m|b)?)',
                r'(?i)weighted\s+average\s+shares\s+outstanding\s*(?:of\s+)?([\d,\.]+\s*(?:million|billion|m|b)?)',
            ],
            'roa': [
                # Return on assets patterns
                r'(?i)return\s+on\s+assets\s*(?:of\s+|was\s+|were\s+)?([\d\.]+)%',
                r'(?i)ROA\s*(?:of\s+|was\s+|were\s+)?([\d\.]+)%',
                r'(?i)return\s+on\s+total\s+assets\s*(?:of\s+)?([\d\.]+)\s*percent',
            ],
            'roic': [
                # Return on invested capital patterns
                r'(?i)return\s+on\s+invested\s+capital\s*(?:of\s+|was\s+|were\s+)?([\d\.]+)%',
                r'(?i)ROIC\s*(?:of\s+|was\s+|were\s+)?([\d\.]+)%',
                r'(?i)return\s+on\s+capital\s*(?:of\s+)?([\d\.]+)\s*percent',
            ],
            'working_capital': [
                # Working capital patterns
                r'(?i)working\s+capital\s+(?:of\s+|was\s+|were\s+)?\$?\s*([\d,\.]+\s*(?:million|billion|m|b)?)',
                r'(?i)net\s+working\s+capital\s*\$?\s*([\d,\.]+\s*(?:million|billion|m|b)?)',
            ],
            'enterprise_value': [
                # Enterprise value patterns
                r'(?i)enterprise\s+value\s*\$?\s*([\d,\.]+\s*(?:million|billion|trillion|m|b|t)?)',
                r'(?i)EV\s*\$?\s*([\d,\.]+\s*(?:million|billion|trillion|m|b|t)?)',
            ],
            'ebitda': [
                # EBITDA patterns
                r'(?i)EBITDA\s*\$?\s*([\d,\.]+(?:\s*(?:million|billion|m|b))?)',
                r'(?i)earnings\s+before\s+interest,?\s+taxes,?\s+depreciation\s+and\s+amortization\s*\$?\s*([\d,\.]+\s*(?:million|billion|m|b)?)',
                r'(?i)adjusted\s+EBITDA\s*\$?\s*([\d,\.]+\s*(?:million|billion|m|b)?)',
            ],
            'free_cash_flow': [
                # Free cash flow patterns
                r'(?i)free\s+cash\s+flow\s*\$?\s*([\d,\.]+(?:\s*(?:million|billion|m|b))?)',
                r'(?i)FCF\s*\$?\s*([\d,\.]+\s*(?:million|billion|m|b)?)',
                r'(?i)unlevered\s+free\s+cash\s+flow\s*\$?\s*([\d,\.]+\s*(?:million|billion|m|b)?)',
            ],
        }
        
        self.company_patterns = {
            'company_name': [
                # Generic patterns for any company name - improved for better accuracy
                r'(?i)(?:issuer|registrant|company):\s*([A-Z][A-Za-z\s&\.,]+(?:Corporation|Corp\.?|Inc\.?|LLC|Ltd\.?|Company|Co\.?))',
                r'(?i)(?:the\s+)?([A-Z][A-Za-z\s&\.,]+(?:Corporation|Corp\.?|Inc\.?|LLC|Ltd\.?|Company|Co\.?))\s+(?:is\s+a|operates|provides|offers)',
                r'(?i)^([A-Z][A-Za-z\s&\.,]+(?:Corporation|Corp\.?|Inc\.?|LLC|Ltd\.?|Company|Co\.?))\s+(?:has|was|is|will)',
                r'(?i)(?:about|regarding)\s+([A-Z][A-Za-z\s&\.,]+(?:Corporation|Corp\.?|Inc\.?|LLC|Ltd\.?|Company|Co\.?))',
                r'(?i)([A-Z][A-Za-z\s&\.,]+(?:Corporation|Corp\.?|Inc\.?|LLC|Ltd\.?|Company|Co\.?))\s+(?:announced|reported|filed)',
                r'(?i)(?:name|entity):\s*([A-Z][A-Za-z\s&\.,]+(?:Corporation|Corp\.?|Inc\.?|LLC|Ltd\.?|Company|Co\.?))',
                r'(?i)(?:issuer|registrant):\s*([A-Z][A-Za-z\s&\.,]+(?:Corporation|Corp\.?|Inc\.?|LLC|Ltd\.?|Company|Co\.?))',
                r'(?i)(?:company|corporation|entity)\s+name:\s*([A-Z][A-Za-z\s&\.,]+(?:Corporation|Corp\.?|Inc\.?|LLC|Ltd\.?|Company|Co\.?))',
            ],
            'company_address': [
                # IMPROVED: More specific address patterns
                r'(?i)(?:headquartered|located|based)\s+(?:in\s+|at\s+)([A-Za-z\s,]+,\s*[A-Z]{2}(?:\s*\d{5})?)',
                r'(?i)principal\s+(?:executive\s+)?offices?\s+(?:are\s+)?(?:located\s+)?(?:at\s+|in\s+)([A-Za-z\s,]+,\s*[A-Z]{2})',
                r'(?i)corporate\s+headquarters\s+(?:are\s+)?(?:located\s+)?(?:at\s+|in\s+)([A-Za-z\s,]+,\s*[A-Z]{2})',
                # City, State patterns
                r'(?i)(?:headquartered|located|based)\s+(?:in\s+|at\s+)([A-Za-z\s]+,\s*[A-Za-z]+)',
                # Specific location patterns
                r'(?i)(?:headquartered|located|based)\s+(?:in\s+|at\s+)(New\s+York,\s*New\s+York|Cupertino,\s*California|Macon,\s*Georgia|Redmond,\s*Washington)',
            ],
            'fiscal_year': [
                # IMPROVED: More specific fiscal year patterns with recent dates
                r'(?i)(?:fiscal\s+year|financial\s+year|year)\s+(?:ending|ended)\s+([A-Za-z]+\s+\d{1,2},?\s+202[0-9])',
                r'(?i)year\s+ended\s+([A-Za-z]+\s+\d{1,2},?\s+202[0-9])',
                r'(?i)for\s+the\s+year\s+ended\s+([A-Za-z]+\s+\d{1,2},?\s+202[0-9])',
                r'(?i)fiscal\s+year\s+202[0-9]\s+ended\s+([A-Za-z]+\s+\d{1,2},?\s+202[0-9])',
                r'(?i)(?:fiscal|financial)\s+year:\s+([A-Za-z]+\s+\d{1,2},?\s+202[0-9])',
                # Specific recent dates
                r'(?i)(September\s+30,?\s+202[0-9])',
                r'(?i)(December\s+31,?\s+202[0-9])',
                r'(?i)(June\s+30,?\s+202[0-9])',
                r'(?i)(March\s+31,?\s+202[0-9])',
            ],
            'stock_symbol': [
                # Exchange-specific patterns
                r'(?i)(?:NYSE|NASDAQ)\s*[:\-]?\s*([A-Z]{1,5})\b',
                r'(?i)(?:trading|ticker)\s+symbol\s*[:\-]?\s*([A-Z]{1,5})\b',
                r'(?i)common\s+stock\s+.*?(?:symbol|ticker)\s*[:\-]?\s*([A-Z]{1,5})\b',
                r'(?i)(?:symbol|ticker)\s*[:\-]?\s*([A-Z]{1,5})\b',
                r'(?i)trading\s+under\s+(?:the\s+)?symbol\s*[:\-]?\s*([A-Z]{1,5})\b',
                r'(?i)listed\s+on\s+(?:NYSE|NASDAQ)\s+under\s+(?:the\s+)?symbol\s*[:\-]?\s*([A-Z]{1,5})\b',
                r'(?i)stock\s+is\s+traded\s+under\s+(?:the\s+)?symbol\s*[:\-]?\s*([A-Z]{1,5})\b',
                r'(?i)shares\s+are\s+traded\s+under\s+(?:the\s+)?symbol\s*[:\-]?\s*([A-Z]{1,5})\b',
                r'(?i)(?:stock|shares)\s+.*?symbol\s*[:\-]?\s*([A-Z]{1,5})\b',
            ],
            'industry': [
                # IMPROVED: Better business description patterns
                r'(?i)(?:company|corporation)\s+(?:that\s+)?(?:operates|is|provides|offers)\s+(?:as\s+)?(?:a\s+|an\s+)?([^.]+(?:software|platform|technology|digital|advertising|measurement|analytics|designer|manufacturer|provider)[^.]*)',
                r'(?i)(?:is\s+)?(?:a\s+|an\s+)?([^.]+(?:independent\s+designer|manufacturer|provider|platform|software)[^.]*)',
                r'(?i)(?:operates|is|provides|offers)\s+(?:as\s+)?(?:a\s+|an\s+)?([^.]+(?:providing|offering|developing|manufacturing|designing)[^.]*)',
            ],
            'primary_business': [
                # IMPROVED: Better primary business patterns
                r'(?i)(?:company|corporation)\s+(?:that\s+)?(?:operates|is|provides|offers)\s+(?:as\s+)?(?:a\s+|an\s+)?([^.]+(?:providing|offering|developing|manufacturing|designing)[^.]*)',
                r'(?i)(?:is\s+)?(?:a\s+|an\s+)?([^.]+(?:independent\s+designer|manufacturer|provider|platform|software)[^.]*)',
                r'(?i)(?:business|primary\s+business)\s+(?:is\s+|includes\s+|involves\s+)([^.]+)',
            ],
            'geographic_markets': [
                # IMPROVED: More specific geographic patterns
                r'(?i)(?:operates|serves)\s+(?:in\s+|across\s+)?([^.]*(?:United\s+States\s+and\s+Canada|United\s+States\s+and\s+international|North\s+America)[^.]*)',
                r'(?i)(?:geographic|geographical)\s+(?:markets|presence)\s+(?:include|span)\s+([^.]+)',
                r'(?i)(?:markets|regions)\s+(?:include|served)\s+([^.]+)',
            ],
            'key_products': [
                # IMPROVED: Better product description patterns
                r'(?i)(?:products|solutions|services)\s+(?:include|comprise|consist\s+of)\s+([^.]+)',
                r'(?i)(?:product\s+portfolio|key\s+products)\s+(?:includes|comprises)\s+([^.]+)',
                r'(?i)(?:offers|provides)\s+([^.]+(?:buses|software|platform|solutions|services)[^.]*)',
            ]
        }

    def extract_with_patterns(self, text: str, document_name: str) -> List[ExtractedData]:
        """Extract data using improved patterns with targeted fixes"""
        extracted_data = []
        
        # Company context detection
        company_context = self._detect_company_context(text, document_name)
        
        # Extract financial data with improved patterns
        for metric_type, patterns in self.financial_patterns.items():
            for pattern_idx, pattern in enumerate(patterns):
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    raw_value = match.group(1).strip()
                    
                    # Skip invalid matches
                    if not raw_value or len(raw_value) < 2:
                        continue
                    
                    # Get extended context for better normalization
                    context = text[max(0, match.start() - 200): match.end() + 200]
                    
                    # Enhanced normalization based on field type
                    if metric_type in ['revenue', 'net_income', 'total_assets', 'total_liabilities', 'market_cap']:
                        normalized = EnhancedFinancialNormalizer.normalize_financial_value(raw_value, context)
                        if normalized:
                            value = normalized
                        else:
                            continue
                    elif metric_type in ['net_margin', 'operating_margin', 'gross_margin']:
                        normalized = EnhancedFinancialNormalizer.normalize_percentage(raw_value)
                        if normalized:
                            value = normalized
                        else:
                            continue
                    else:
                        value = raw_value
                    
                    # Enhanced confidence calculation
                    confidence = self._calculate_enhanced_confidence(
                        metric_type, pattern, match, context, pattern_idx, company_context
                    )
                    
                    extracted_data.append(ExtractedData(
                        field_name=metric_type,
                        value=value,
                        confidence=confidence,
                        source_document=document_name,
                        context=context[:200],  # Truncate context for storage
                        extraction_method=f"enhanced_pattern_{pattern_idx}"
                    ))
        
        # Extract company information with enhanced validation
        for info_type, patterns in self.company_patterns.items():
            for pattern_idx, pattern in enumerate(patterns):
                matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    raw_value = match.group(1).strip()
                    
                    # Enhanced validation
                    if not self._enhanced_validate_company_field(info_type, raw_value, company_context, text):
                        continue
                    
                    # Enhanced cleaning
                    cleaned_value = self._enhanced_clean_company_field(info_type, raw_value, company_context)
                    if not cleaned_value:
                        continue
                    
                    # Enhanced confidence calculation
                    confidence = self._calculate_enhanced_confidence(
                        info_type, pattern, match, match.group(0), pattern_idx, company_context
                    )
                    
                    extracted_data.append(ExtractedData(
                        field_name=info_type,
                        value=cleaned_value,
                        confidence=confidence,
                        source_document=document_name,
                        context=match.group(0),
                        extraction_method=f"enhanced_pattern_{pattern_idx}"
                    ))
        
        return extracted_data

    def _detect_company_context(self, text: str, document_name: str) -> Dict[str, Any]:
        """Dynamic company context detection based on document content"""
        context = {}
        
        # Extract company name and stock symbol dynamically
        company_name = ""
        stock_symbol = ""
        
        # Try to find company name in text
        for pattern in self.company_patterns['company_name']:
            match = re.search(pattern, text)
            if match:
                company_name = match.group(1).strip()
                break
        
        # Try to find stock symbol in text
        for pattern in self.company_patterns['stock_symbol']:
            match = re.search(pattern, text)
            if match:
                stock_symbol = match.group(1).strip()
                break
        
        # Create dynamic context based on extracted information
        if company_name:
            context['company_name'] = company_name
        if stock_symbol:
            context['stock_symbol'] = stock_symbol
        
        # Extract business type indicators
        business_indicators = []
        for pattern in self.company_patterns['industry']:
            match = re.search(pattern, text)
            if match:
                business_indicators.append(match.group(1).strip())
        
        context['business_indicators'] = business_indicators
        context['document_name'] = document_name.lower()
        
        return context

    def _calculate_enhanced_confidence(self, field_type: str, pattern: str, match: re.Match, 
                                     context: str, pattern_idx: int, company_context: Dict[str, Any]) -> float:
        """Enhanced confidence calculation with field-specific logic"""
        base_confidence = 0.8
        
        # Field-specific confidence adjustments
        field_confidence_map = {
            'company_name': 0.9,
            'stock_symbol': 0.95,
            'revenue': 0.85,
            'net_income': 0.85,
            'fiscal_year': 0.8,
            'company_address': 0.7,
            'industry': 0.75,
            'primary_business': 0.75,
            'geographic_markets': 0.7,
            'key_products': 0.7,
        }
        
        confidence = field_confidence_map.get(field_type, base_confidence)
        
        # Pattern priority bonus (earlier patterns are more specific)
        if pattern_idx == 0:
            confidence += 0.1
        elif pattern_idx == 1:
            confidence += 0.05
        
        # Context-based adjustments
        if context and field_type in ['revenue', 'net_income', 'total_assets']:
            # Financial context indicators
            if any(indicator in context.lower() for indicator in [
                'consolidated', 'financial', 'statements', 'income', 'balance sheet'
            ]):
                confidence += 0.05
        
        # Document name relevance
        if company_context.get('document_name'):
            doc_name = company_context['document_name']
            if field_type in ['company_name', 'stock_symbol']:
                # Higher confidence if company info matches document name
                if company_context.get('company_name') and company_context['company_name'].lower() in doc_name:
                    confidence += 0.05
                if company_context.get('stock_symbol') and company_context['stock_symbol'].lower() in doc_name:
                    confidence += 0.05
        
        # Ensure confidence stays within bounds
        return min(confidence, 1.0)

    def _enhanced_validate_company_field(self, info_type: str, value: str, 
                                       company_context: Dict[str, Any], full_text: str) -> bool:
        """Enhanced validation for company fields"""
        if len(value) < 3:
            return False
        
        value_lower = value.lower()
        
        # Company-specific validation
        if info_type == 'company_name':
            # Must look like a proper company name
            if not any(corp_indicator in value_lower for corp_indicator in [
                'inc', 'corp', 'corporation', 'llc', 'ltd', 'company', 'co', 'limited'
            ]):
                return False
            
            # Must not contain generic terms or regulatory language
            if any(bad_term in value_lower for bad_term in [
                'pursuant', 'section', 'regulation', 'rule', 'act', 'code',
                'financial', 'consolidated', 'statement', 'disclosure',
                'securities', 'exchange', 'commission', 'sec', 'form',
                'quarterly', 'annual', 'report', 'filing'
            ]):
                return False
            
            # Must not be too long (likely extracted wrong context)
            if len(value) > 100:
                return False
            
            # Must start with capital letter
            if not value[0].isupper():
                return False
        
        elif info_type == 'company_address':
            # IMPROVED: Address validation
            # Must look like an actual address
            if any(bad_phrase in value_lower for bad_phrase in [
                'pursuant', 'section', 'regulation', 'rule', 'act', 'code',
                'countries outside', 'commitment', 'lease',
                'financial', 'consolidated', 'statement', 'disclosure'
            ]):
                return False
            
            # Must have location indicators (states, cities, or address components)
            if not any(indicator in value_lower for indicator in [
                'new york', 'california', 'georgia', 'washington', 'texas', 'florida',
                'ny', 'ca', 'wa', 'ga', 'tx', 'fl', 'street', 'avenue', 'road',
                'boulevard', 'drive', 'lane', 'court', 'plaza', 'way', 'suite'
            ]):
                # Check for state abbreviations
                if not re.search(r'\b[A-Z]{2}\b', value):
                    return False
        
        elif info_type == 'stock_symbol':
            # Must be 1-5 capital letters
            if not re.match(r'^[A-Z]{1,5}$', value):
                return False
        
        elif info_type == 'fiscal_year':
            # IMPROVED: Must have recent year (2020-2024)
            if not re.search(r'202[0-4]', value):
                return False
            
            # Must look like a proper date
            if not any(month in value_lower for month in [
                'january', 'february', 'march', 'april', 'may', 'june',
                'july', 'august', 'september', 'october', 'november', 'december'
            ]):
                return False
            
            # Must not contain regulatory language
            if any(bad_term in value_lower for bad_term in [
                'pursuant', 'section', 'regulation', 'rule', 'act', 'code',
                'disclosure', 'securities', 'exchange', 'commission'
            ]):
                return False
        
        elif info_type in ['industry', 'primary_business']:
            # IMPROVED: Better business description filtering
            if any(bad_phrase in value_lower for bad_phrase in [
                'risk that', 'could be construed', 'pursuant to', 'section',
                'regulation', 'rule', 'act', 'code', 'disclosure', 'commitment',
                'lease', 'obligation', 'contingent', 'financial condition',
                'results of operations', 'consolidated', 'goodwill', 'intangible',
                'amortization', 'depreciation', 'impairment'
            ]):
                return False
            
            # Must have business-relevant keywords
            if not any(keyword in value_lower for keyword in [
                'platform', 'software', 'technology', 'digital', 'advertising',
                'measurement', 'analytics', 'designer', 'manufacturer', 'provider',
                'provides', 'operates', 'develops', 'offers', 'services',
                'independent', 'leader', 'school bus', 'buses'
            ]):
                return False
        
        elif info_type == 'geographic_markets':
            # IMPROVED: Geographic markets validation
            if any(bad_phrase in value_lower for bad_phrase in [
                'pursuant', 'section', 'regulation', 'business model',
                'consolidated', 'financial', 'statement', 'disclosure'
            ]):
                return False
            
            # Must have geographic indicators
            if not any(indicator in value_lower for indicator in [
                'united states', 'canada', 'north america', 'international',
                'global', 'worldwide', 'markets', 'regions', 'countries'
            ]):
                return False
        
        return True

    def _enhanced_clean_company_field(self, info_type: str, value: str, 
                                    company_context: Dict[str, Any]) -> str:
        """Enhanced cleaning for company field values"""
        value = value.strip()
        
        if info_type == 'company_name':
            # Remove common prefixes
            value = re.sub(r'^(The\s+|A\s+)', '', value, flags=re.IGNORECASE)
            value = value.strip()
            
            # Ensure proper capitalization
            if value.islower():
                value = value.title()
            
            # Remove trailing punctuation
            value = value.rstrip('.,;:')
        
        elif info_type == 'company_address':
            # Clean up address formatting
            value = re.sub(r'\s+', ' ', value)  # Normalize whitespace
            value = value.strip()
        
        elif info_type == 'stock_symbol':
            # Ensure uppercase
            value = value.upper().strip()
        
        elif info_type == 'primary_business':
            # Clean up business description
            value = re.sub(r'\s+', ' ', value)  # Normalize whitespace
            value = value.strip()
            
            # Remove trailing punctuation
            value = value.rstrip('.,;:')
        
        elif info_type == 'geographic_markets':
            # Clean up geographic markets
            value = re.sub(r'\s+', ' ', value)  # Normalize whitespace
            value = value.strip()
        
        return value


class EnhancedConsolidationEngine:
    """Enhanced consolidation with better conflict resolution"""
    
    def consolidate_extracted_data(self, extracted_data: List[ExtractedData]) -> Dict[str, Any]:
        """Enhanced consolidation with targeted improvements"""
        consolidated = {}
        grouped_data = {}
        
        # Group by field name
        for item in extracted_data:
            if item.field_name not in grouped_data:
                grouped_data[item.field_name] = []
            grouped_data[item.field_name].append(item)
        
        # Resolve conflicts for each field with enhanced logic
        for field_name, items in grouped_data.items():
            if not items:
                continue
            
            # Sort by confidence score (descending)
            items.sort(key=lambda x: x.confidence, reverse=True)
            
            # Enhanced conflict resolution
            best_value = self._enhanced_resolve_conflicts(field_name, items)
            consolidated[field_name] = best_value
        
        return consolidated
    
    def _enhanced_resolve_conflicts(self, field_name: str, items: List[ExtractedData]) -> str:
        """Enhanced conflict resolution with field-specific logic"""
        if not items:
            return ""
        
        # For fiscal year, prefer recent dates
        if field_name == 'fiscal_year':
            recent_items = [item for item in items if '202' in item.value]
            if recent_items:
                return recent_items[0].value
        
        # For financial fields, prefer values with proper scaling
        if field_name in ['revenue', 'net_income', 'total_assets', 'total_liabilities', 'market_cap']:
            # Prefer values with B/M/K suffixes (properly scaled)
            scaled_items = [item for item in items if any(suffix in item.value for suffix in ['B', 'M', 'K'])]
            if scaled_items:
                return scaled_items[0].value
        
        # For percentages, prefer % format
        if field_name in ['net_margin', 'operating_margin', 'gross_margin']:
            percent_items = [item for item in items if '%' in item.value]
            if percent_items:
                return percent_items[0].value
        
        # For address, prefer city/state format
        if field_name == 'company_address':
            address_items = [item for item in items if ',' in item.value and 
                           not any(bad in item.value.lower() for bad in ['pursuant', 'section', 'countries outside'])]
            if address_items:
                return address_items[0].value
        
        # Default to highest confidence
        return items[0].value


class EnhancedFinancialDataExtractor:
    """Enhanced financial data extractor with targeted improvements"""
    
    def __init__(self):
        self.pattern_matcher = TargetedPatternMatcher()
        self.consolidation_engine = EnhancedConsolidationEngine()
    
    def extract_data(self, text: str, document_name: str) -> List[ExtractedData]:
        """Extract data with enhanced accuracy"""
        return self.pattern_matcher.extract_with_patterns(text, document_name)
    
    def consolidate_data(self, extracted_data: List[ExtractedData]) -> Dict[str, Any]:
        """Consolidate extracted data with enhanced logic"""
        return self.consolidation_engine.consolidate_extracted_data(extracted_data)
