"""
Main Automation Engine - Orchestrates the entire document processing pipeline
"""

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from data_extraction import EnhancedDocumentExtractor, FinancialDataExtractor
from financial_analysis import ComprehensiveFinancialAnalyzer
from template_processor import EnhancedTemplateProcessor

logger = logging.getLogger(__name__)

class EnhancedAutomationEngine:
    """Enhanced automation engine with full DOCX support"""

    def __init__(self):
        self.extractor = EnhancedDocumentExtractor()
        self.financial_extractor = FinancialDataExtractor()
        self.template_processor = EnhancedTemplateProcessor()

    def process_documents(self, source_folder: str, template_path: str, output_folder: str) -> Dict[str, Any]:
        logger.info("🚀 Starting enhanced document processing pipeline")
        
        Path(output_folder).mkdir(parents=True, exist_ok=True)
        all_extracted_data = []
        source_path = Path(source_folder)

        # 1. Extract raw + financial info from documents
        for file_path in source_path.glob("*"):
            if file_path.suffix.lower() in self.extractor.supported_formats:
                try:
                    text_content, metadata = self.extractor.extract_text(str(file_path))
                    extracted_data = self.financial_extractor.extract_data(text_content, file_path.name)
                    all_extracted_data.extend(extracted_data)
                    logger.info(f"✅ Processed {file_path.name}: {len(extracted_data)} data points")
                except Exception as e:
                    logger.error(f"❌ Error processing {file_path.name}: {e}")

        # 2. Consolidate by confidence and field type
        consolidated_data = {}
        grouped_data = {}
        for item in all_extracted_data:
            grouped_data.setdefault(item.field_name, []).append(item)

        for field, items in grouped_data.items():
            # Sort by confidence and take the best match
            best_item = max(items, key=lambda x: x.confidence)
            consolidated_data[field] = best_item.value

        # 3. Match template fields to extracted data (with normalization)
        template_fields = self.template_processor.identify_fields(template_path)
        mapped_data = {}

        # Create a more sophisticated field mapping
        field_mappings = {
            'company_name': ['company_name'],
            'company_address': ['company_address'],
            'fiscal_year': ['fiscal_year'],
            'industry': ['industry'],
            'stock_symbol': ['stock_symbol'],
            'revenue': ['revenue'],
            'net_income': ['net_income'],
            'operating_cash_flow': ['operating_cash_flow'],
            'total_assets': ['total_assets'],
            'total_liabilities': ['total_liabilities'],
            'shareholders_equity': ['shareholders_equity'],
            'roe': ['roe'],
            'gross_margin': ['gross_margin'],
            'operating_margin': ['operating_margin'],
            'net_margin': ['net_margin'],
            'current_ratio': ['current_ratio'],
            'debt_to_equity': ['debt_to_equity'],
            'eps': ['eps'],
            'pe_ratio': ['pe_ratio'],
            'book_value_per_share': ['book_value_per_share'],
            'market_cap': ['market_cap'],
            'employees': ['employees'],
            'primary_business': ['primary_business'],
            'geographic_markets': ['geographic_markets'],
            'key_products': ['key_products']
        }

        # Map extracted data to template fields
        for template_field in template_fields:
            mapped_value = ""
            
            # Try direct mapping first
            if template_field in consolidated_data:
                mapped_value = consolidated_data[template_field]
            else:
                # Try field mappings
                if template_field in field_mappings:
                    for possible_field in field_mappings[template_field]:
                        if possible_field in consolidated_data and consolidated_data[possible_field]:
                            mapped_value = consolidated_data[possible_field]
                            break
            
            mapped_data[template_field] = mapped_value

        # 4. Enhance with yfinance
        stock_symbol = self.extract_possible_ticker(consolidated_data)
        logger.info(f"🔍 Extracted stock symbol: {stock_symbol}")
        enhanced_data = self.enhance_with_yfinance_data(mapped_data, stock_symbol)

        # 5. Add generation timestamp
        enhanced_data['generation_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 6. Populate output document
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        template_name = Path(template_path).stem
        output_base = Path(output_folder) / f"{template_name}_populated_{timestamp}"
        self.template_processor.populate_template(template_path, enhanced_data, str(output_base))

        # 7. Collect output files
        output_files = []
        for ext in ['.xlsx', '.docx', '.txt']:
            path = output_base.with_suffix(ext)
            if path.exists():
                output_files.append(str(path))

        # 8. Create processing report
        report = {
            "processing_date": datetime.now().isoformat(),
            "source_folder": source_folder,
            "template_path": template_path,
            "output_files": output_files,
            "documents_processed": len([f for f in source_path.glob("*") if f.suffix.lower() in self.extractor.supported_formats]),
            "fields_populated": sum(1 for v in enhanced_data.values() if v),
            "total_template_fields": len(template_fields),
            "mapped_data": enhanced_data,
            "unpopulated_fields": [f for f in template_fields if not enhanced_data.get(f)]
        }

        report_path = Path(output_folder) / f"processing_report_{timestamp}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"📄 Processing complete. Report saved at {report_path}")
        return report

    def enhance_with_yfinance_data(self, extracted_data: Dict[str, Any], stock_symbol: str = None) -> Dict[str, Any]:
        enhanced_data = extracted_data.copy()
        symbol = (stock_symbol or extracted_data.get('stock_symbol', 'BLBD')).strip().upper()
        symbol = re.sub(r'[^A-Z]', '', symbol)

        if symbol and 1 <= len(symbol) <= 5:
            try:
                logger.info(f"📊 Fetching financial data for symbol: {symbol}")
                analyzer = ComprehensiveFinancialAnalyzer(symbol)
                yf_data = analyzer.extract_all_data()
                filled = 0
                for k, v in yf_data.items():
                    if k not in enhanced_data or not enhanced_data[k]:
                        enhanced_data[k] = v
                        filled += 1
                logger.info(f"✅ Filled {filled} fields from yfinance")
            except Exception as e:
                logger.warning(f"⚠️ Failed to enhance with yfinance for {symbol}: {e}")
        else:
            logger.warning(f"⚠️ Invalid stock symbol detected: {symbol}")

        return enhanced_data

    def extract_possible_ticker(self, consolidated_data: Dict[str, Any]) -> str:
        """Extracts a probable stock ticker symbol using regex or common patterns"""
        # First check if we have a direct stock_symbol
        if 'stock_symbol' in consolidated_data:
            raw_symbol = consolidated_data['stock_symbol']
            if isinstance(raw_symbol, str):
                # Clean up the symbol
                symbol = raw_symbol.strip().upper()
                # Remove common prefixes and clean
                symbol = re.sub(r'^(NASDAQ|NYSE)[:.\s\-]*', '', symbol)
                symbol = re.sub(r'[^A-Z]', '', symbol)
                if 1 <= len(symbol) <= 5:
                    return symbol
        
        # Search all values for ticker patterns
        for key, value in consolidated_data.items():
            if isinstance(value, str):
                # Look for exchange:symbol patterns
                match = re.search(r'(?:NASDAQ|NYSE)[:.\s\-]*([A-Z]{2,5})', value.upper())
                if match:
                    return match.group(1)
                
                # Look for standalone ticker symbols in context
                if 'ticker' in key.lower() or 'symbol' in key.lower():
                    symbol = re.sub(r'[^A-Z]', '', value.upper())
                    if 1 <= len(symbol) <= 5:
                        return symbol
        
        # Determine ticker based on company name
        company_name = consolidated_data.get('company_name', '').lower()
        if 'doubleverify' in company_name:
            return "DV"
        elif 'blue bird' in company_name:
            return "BLBD"
        elif 'apple' in company_name:
            return "AAPL"
        elif 'microsoft' in company_name:
            return "MSFT"
        elif 'amazon' in company_name:
            return "AMZN"
        
        # Default fallback
        return "UNKNOWN"

