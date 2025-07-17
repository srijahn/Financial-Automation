"""
Enhanced Automation Engine with Targeted Accuracy Improvements
"""

import os
import re
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json
import traceback

from enhanced_data_extraction import EnhancedFinancialDataExtractor
from template_processor import EnhancedTemplateProcessor
from financial_analysis import ComprehensiveFinancialAnalyzer

logger = logging.getLogger(__name__)

class EnhancedAutomationEngine:
    """Enhanced automation engine with targeted accuracy improvements"""
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.extractor = EnhancedFinancialDataExtractor()
        self.template_processor = EnhancedTemplateProcessor()
        self.financial_analyzer = None  # Will be initialized with ticker
        self.processing_stats = {
            'total_documents': 0,
            'successful_extractions': 0,
            'failed_extractions': 0,
            'accuracy_score': 0.0,
            'processing_time': 0,
            'extraction_details': []
        }
    
    def process_documents(self, folder_path: str, output_folder: str = None, 
                         template_path: str = None) -> Dict[str, Any]:
        """Enhanced document processing with targeted improvements"""
        start_time = datetime.now()
        
        try:
            logger.info(f"🚀 Starting enhanced document processing for: {folder_path}")
            
            # Setup paths
            folder_path = Path(folder_path)
            if not folder_path.exists():
                raise FileNotFoundError(f"Folder not found: {folder_path}")
            
            output_folder = Path(output_folder) if output_folder else folder_path.parent / f"{folder_path.name}_enhanced_output"
            output_folder.mkdir(exist_ok=True)
            
            template_path = Path(template_path) if template_path else folder_path.parent / "case_study_document_template.docx"
            
            # Initialize processing stats
            self.processing_stats['total_documents'] = 0
            self.processing_stats['successful_extractions'] = 0
            self.processing_stats['failed_extractions'] = 0
            self.processing_stats['extraction_details'] = []
            
            # Process documents
            all_extracted_data = []
            processed_files = []
            
            for file_path in folder_path.glob("*.pdf"):
                try:
                    logger.info(f"📄 Processing: {file_path.name}")
                    self.processing_stats['total_documents'] += 1
                    
                    # Extract text
                    text = self._extract_text_from_file(file_path)
                    if not text:
                        logger.warning(f"⚠️ No text extracted from {file_path.name}")
                        self.processing_stats['failed_extractions'] += 1
                        continue
                    
                    # Extract data with enhanced accuracy
                    extracted_data = self.extractor.extract_data(text, file_path.name)
                    all_extracted_data.extend(extracted_data)
                    
                    processed_files.append(file_path.name)
                    self.processing_stats['successful_extractions'] += 1
                    
                    # Log extraction details
                    self.processing_stats['extraction_details'].append({
                        'file': file_path.name,
                        'extractions': len(extracted_data),
                        'avg_confidence': sum(item.confidence for item in extracted_data) / len(extracted_data) if extracted_data else 0
                    })
                    
                except Exception as e:
                    logger.error(f"❌ Error processing {file_path.name}: {e}")
                    self.processing_stats['failed_extractions'] += 1
                    if self.debug:
                        traceback.print_exc()
            
            # Consolidate data with enhanced logic
            consolidated_data = self.extractor.consolidate_data(all_extracted_data)
            
            # Enhanced yfinance integration
            enhanced_data = self._enhanced_yfinance_integration(consolidated_data)
            
            # Enhanced validation and improvement
            validated_data = self._enhanced_validate_and_improve_data(enhanced_data)
            
            # Generate outputs
            outputs = self._generate_enhanced_outputs(validated_data, output_folder, template_path)
            
            # Calculate enhanced accuracy metrics
            accuracy_metrics = self._calculate_enhanced_accuracy_metrics(validated_data, all_extracted_data)
            
            # Finalize processing stats
            processing_time = (datetime.now() - start_time).total_seconds()
            self.processing_stats['processing_time'] = processing_time
            self.processing_stats['accuracy_score'] = accuracy_metrics['overall_accuracy']
            
            # Generate processing report
            report = self._generate_enhanced_processing_report(
                validated_data, outputs, accuracy_metrics, processed_files
            )
            
            # Save processing report
            report_path = output_folder / f"enhanced_processing_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"✅ Enhanced processing completed in {processing_time:.2f}s")
            logger.info(f"📊 Overall accuracy: {accuracy_metrics['overall_accuracy']:.1f}%")
            logger.info(f"📁 Outputs saved to: {output_folder}")
            
            return {
                'success': True,
                'consolidated_data': validated_data,
                'accuracy_metrics': accuracy_metrics,
                'processing_stats': self.processing_stats,
                'outputs': outputs,
                'report_path': str(report_path)
            }
            
        except Exception as e:
            logger.error(f"❌ Critical error in enhanced document processing: {e}")
            if self.debug:
                traceback.print_exc()
            return {
                'success': False,
                'error': str(e),
                'processing_stats': self.processing_stats
            }
    
    def _extract_text_from_file(self, file_path: Path) -> str:
        """Enhanced text extraction"""
        try:
            import pdfplumber
            
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}")
            return ""
    
    def _enhanced_yfinance_integration(self, consolidated_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced yfinance integration with better validation"""
        try:
            # Get stock symbol with enhanced validation
            stock_symbol = consolidated_data.get('stock_symbol', '').upper()
            
            if not stock_symbol:
                logger.warning("⚠️ No stock symbol found for yfinance integration")
                return consolidated_data
            
            # Validate stock symbol format (1-5 capital letters)
            if not re.match(r'^[A-Z]{1,5}$', stock_symbol):
                logger.warning(f"⚠️ Invalid stock symbol format: {stock_symbol}")
                return consolidated_data
            
            # Use the extracted symbol directly
            final_symbol = stock_symbol
            
            # Initialize financial analyzer with ticker
            self.financial_analyzer = ComprehensiveFinancialAnalyzer(final_symbol)
            
            # Get yfinance data
            yfinance_data = self.financial_analyzer.extract_all_data()
            
            if yfinance_data:
                logger.info(f"📈 yfinance data retrieved for {final_symbol}")
                
                # Enhanced data integration with comprehensive yfinance data
                enhanced_data = consolidated_data.copy()
                
                # Fill missing data with yfinance data - comprehensive integration
                yfinance_fields = [
                    'market_cap', 'employees', 'operating_cash_flow', 'shareholders_equity',
                    'roe', 'gross_margin', 'operating_margin', 'net_margin', 'current_ratio',
                    'debt_to_equity', 'eps', 'pe_ratio', 'book_value_per_share',
                    'competitors', 'acquisitions', 'product_launches', 'strategic_initiatives',
                    'regulatory_changes', 'market_developments', 'overall_rating',
                    'price_target', 'investment_horizon', 'risk_assessment',
                    'strengths_analysis', 'weaknesses_analysis', 'opportunities_analysis',
                    'threats_analysis'
                ]
                
                for field in yfinance_fields:
                    if not enhanced_data.get(field) and yfinance_data.get(field):
                        enhanced_data[field] = yfinance_data[field]
                
                # Always use yfinance financial metrics if available (they're more accurate)
                financial_metrics = [
                    'operating_cash_flow', 'shareholders_equity', 'roe', 'gross_margin',
                    'operating_margin', 'net_margin', 'current_ratio', 'debt_to_equity',
                    'eps', 'pe_ratio', 'book_value_per_share'
                ]
                
                for metric in financial_metrics:
                    if yfinance_data.get(metric) and yfinance_data[metric] != 'N/A':
                        enhanced_data[metric] = yfinance_data[metric]
                
                # Always use yfinance analysis sections (they're more comprehensive)
                analysis_sections = [
                    'competitors', 'acquisitions', 'product_launches', 'strategic_initiatives',
                    'regulatory_changes', 'market_developments', 'overall_rating',
                    'price_target', 'investment_horizon', 'risk_assessment',
                    'strengths_analysis', 'weaknesses_analysis', 'opportunities_analysis',
                    'threats_analysis'
                ]
                
                for section in analysis_sections:
                    if yfinance_data.get(section):
                        enhanced_data[section] = yfinance_data[section]
                
                # Validate financial data consistency
                if yfinance_data.get('revenue') and enhanced_data.get('revenue'):
                    # Compare extracted vs yfinance revenue (basic validation)
                    extracted_revenue = self._parse_financial_value(enhanced_data['revenue'])
                    yfinance_revenue = self._parse_financial_value(yfinance_data['revenue'])
                    
                    if extracted_revenue and yfinance_revenue:
                        ratio = extracted_revenue / yfinance_revenue
                        if 0.8 <= ratio <= 1.2:  # Within 20% range
                            logger.info(f"✅ Revenue validation passed (ratio: {ratio:.2f})")
                        else:
                            logger.warning(f"⚠️ Revenue validation failed (ratio: {ratio:.2f})")
                
                return enhanced_data
            else:
                logger.warning(f"⚠️ No yfinance data retrieved for {final_symbol}")
                return consolidated_data
                
        except Exception as e:
            logger.error(f"❌ Error in enhanced yfinance integration: {e}")
            return consolidated_data
    
    def _enhanced_validate_and_improve_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced validation and improvement of extracted data"""
        validated_data = data.copy()
        
        # Enhanced validation rules
        validation_rules = {
            'company_name': self._validate_company_name,
            'company_address': self._validate_company_address,
            'fiscal_year': self._validate_fiscal_year,
            'revenue': self._validate_financial_value,
            'net_income': self._validate_financial_value,
            'total_assets': self._validate_financial_value,
            'total_liabilities': self._validate_financial_value,
            'net_margin': self._validate_percentage,
            'operating_margin': self._validate_percentage,
            'stock_symbol': self._validate_stock_symbol,
            'primary_business': self._validate_business_description,
            'geographic_markets': self._validate_geographic_markets
        }
        
        # Apply validation rules
        for field, validator in validation_rules.items():
            if field in validated_data:
                try:
                    validated_value = validator(validated_data[field])
                    if validated_value is not None:
                        validated_data[field] = validated_value
                    else:
                        logger.warning(f"⚠️ Validation failed for {field}: {validated_data[field]}")
                        # Keep original value with warning
                except Exception as e:
                    logger.error(f"❌ Validation error for {field}: {e}")
        
        return validated_data
    
    def _validate_company_name(self, value: str) -> str:
        """Enhanced company name validation"""
        if not value or len(value) < 3:
            return None
        
        # Clean up common issues
        value = value.strip()
        value = re.sub(r'\s+', ' ', value)
        
        # Ensure proper capitalization
        if value.islower():
            value = value.title()
        
        return value
    
    def _validate_company_address(self, value: str) -> str:
        """Enhanced company address validation"""
        if not value or len(value) < 5:
            return None
        
        # Must look like a real address
        if any(bad_phrase in value.lower() for bad_phrase in [
            'pursuant', 'section', 'regulation', 'countries outside'
        ]):
            return None
        
        # Must have location indicators (states, countries, or address structure)
        if not any(indicator in value.lower() for indicator in [
            'new york', 'california', 'georgia', 'washington', 'texas', 'florida',
            'illinois', 'pennsylvania', 'ohio', 'michigan', 'virginia', 'massachusetts',
            'united states', 'usa', 'us', 'america', 'canada', 'street', 'avenue',
            'road', 'boulevard', 'drive', 'lane', 'court', 'plaza', 'way'
        ]):
            # Check for state abbreviations
            if not re.search(r'\b[A-Z]{2}\b', value):
                return None
        
        return value.strip()
    
    def _validate_fiscal_year(self, value: str) -> str:
        """Enhanced fiscal year validation"""
        if not value:
            return None
        
        # Must contain recent year
        if not re.search(r'202[0-4]', value):
            return None
        
        return value.strip()
    
    def _validate_financial_value(self, value: str) -> str:
        """Enhanced financial value validation"""
        if not value:
            return None
        
        # Must contain dollar sign and scaling
        if '$' not in value:
            return None
        
        # Must have proper scaling (B, M, K)
        if not any(suffix in value for suffix in ['B', 'M', 'K']):
            return None
        
        return value.strip()
    
    def _validate_percentage(self, value: str) -> str:
        """Enhanced percentage validation"""
        if not value:
            return None
        
        # Must contain % symbol
        if '%' not in value:
            return None
        
        return value.strip()
    
    def _validate_stock_symbol(self, value: str) -> str:
        """Enhanced stock symbol validation"""
        if not value:
            return None
        
        # Must be 1-5 capital letters
        if not re.match(r'^[A-Z]{1,5}$', value):
            return None
        
        return value.strip()
    
    def _validate_business_description(self, value: str) -> str:
        """Enhanced business description validation"""
        if not value or len(value) < 10:
            return None
        
        # Must not contain bad phrases
        if any(bad_phrase in value.lower() for bad_phrase in [
            'risk that', 'pursuant to', 'section', 'regulation', 'disclosure'
        ]):
            return None
        
        return value.strip()
    
    def _validate_geographic_markets(self, value: str) -> str:
        """Enhanced geographic markets validation"""
        if not value:
            return None
        
        # Must contain geographic indicators
        if not any(indicator in value.lower() for indicator in [
            'united states', 'canada', 'north america', 'international', 'global',
            'worldwide', 'domestic', 'foreign', 'overseas', 'europe', 'asia',
            'africa', 'australia', 'south america', 'latin america', 'pacific',
            'region', 'country', 'countries', 'market', 'markets', 'territory'
        ]):
            return None
        
        return value.strip()
    
    def _parse_financial_value(self, value: str) -> Optional[float]:
        """Parse financial value to float for comparison"""
        if not value:
            return None
        
        try:
            # Extract number and multiplier
            clean_value = value.replace('$', '').replace(',', '')
            
            multiplier = 1
            if 'T' in clean_value:
                multiplier = 1_000_000_000_000
                clean_value = clean_value.replace('T', '')
            elif 'B' in clean_value:
                multiplier = 1_000_000_000
                clean_value = clean_value.replace('B', '')
            elif 'M' in clean_value:
                multiplier = 1_000_000
                clean_value = clean_value.replace('M', '')
            elif 'K' in clean_value:
                multiplier = 1_000
                clean_value = clean_value.replace('K', '')
            
            return float(clean_value) * multiplier
            
        except Exception:
            return None
    
    def _calculate_enhanced_accuracy_metrics(self, validated_data: Dict[str, Any], 
                                          all_extracted_data: List) -> Dict[str, Any]:
        """Calculate enhanced accuracy metrics"""
        try:
            # Field completeness
            expected_fields = [
                'company_name', 'company_address', 'stock_symbol', 'fiscal_year',
                'revenue', 'net_income', 'total_assets', 'total_liabilities',
                'net_margin', 'operating_margin', 'primary_business', 'geographic_markets'
            ]
            
            filled_fields = sum(1 for field in expected_fields if validated_data.get(field))
            completeness_score = (filled_fields / len(expected_fields)) * 100
            
            # Data quality score based on validation
            quality_score = 0
            for field in expected_fields:
                if field in validated_data:
                    value = validated_data[field]
                    if value and len(str(value)) > 3:
                        quality_score += 1
            
            quality_score = (quality_score / len(expected_fields)) * 100
            
            # Confidence score
            if all_extracted_data:
                avg_confidence = sum(item.confidence for item in all_extracted_data) / len(all_extracted_data)
                confidence_score = avg_confidence * 100
            else:
                confidence_score = 0
            
            # Overall accuracy (weighted average)
            overall_accuracy = (completeness_score * 0.4 + quality_score * 0.4 + confidence_score * 0.2)
            
            return {
                'overall_accuracy': overall_accuracy,
                'completeness_score': completeness_score,
                'quality_score': quality_score,
                'confidence_score': confidence_score,
                'filled_fields': filled_fields,
                'total_fields': len(expected_fields)
            }
            
        except Exception as e:
            logger.error(f"❌ Error calculating accuracy metrics: {e}")
            return {
                'overall_accuracy': 0,
                'completeness_score': 0,
                'quality_score': 0,
                'confidence_score': 0,
                'filled_fields': 0,
                'total_fields': len(expected_fields)
            }
    
    def _generate_enhanced_outputs(self, validated_data: Dict[str, Any], 
                                 output_folder: Path, template_path: Path) -> Dict[str, str]:
        """Generate enhanced outputs"""
        outputs = {}
        
        try:
            # Generate populated document
            if template_path.exists():
                doc_output = self.template_processor.populate_template(
                    str(template_path), validated_data, str(output_folder)
                )
                outputs['document'] = doc_output
            
            # Generate Excel report
            excel_path = output_folder / f"enhanced_financial_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            self._generate_enhanced_excel_report(validated_data, excel_path)
            outputs['excel'] = str(excel_path)
            
            return outputs
            
        except Exception as e:
            logger.error(f"❌ Error generating enhanced outputs: {e}")
            return outputs
    
    def _generate_enhanced_excel_report(self, data: Dict[str, Any], excel_path: Path):
        """Generate enhanced Excel report"""
        try:
            import pandas as pd
            
            # Create DataFrame
            df_data = []
            for field, value in data.items():
                df_data.append({
                    'Field': field.replace('_', ' ').title(),
                    'Value': value,
                    'Type': type(value).__name__
                })
            
            df = pd.DataFrame(df_data)
            
            # Save to Excel
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Financial Data', index=False)
                
                # Format the worksheet
                worksheet = writer.sheets['Financial Data']
                for column in worksheet.columns:
                    max_length = 0
                    column = [cell for cell in column]
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = (max_length + 2)
                    worksheet.column_dimensions[column[0].column_letter].width = adjusted_width
                    
        except Exception as e:
            logger.error(f"❌ Error generating Excel report: {e}")
    
    def _generate_enhanced_processing_report(self, validated_data: Dict[str, Any], 
                                           outputs: Dict[str, str], 
                                           accuracy_metrics: Dict[str, Any],
                                           processed_files: List[str]) -> Dict[str, Any]:
        """Generate enhanced processing report"""
        return {
            'timestamp': datetime.now().isoformat(),
            'processing_stats': self.processing_stats,
            'accuracy_metrics': accuracy_metrics,
            'processed_files': processed_files,
            'extracted_data': validated_data,
            'outputs': outputs,
            'enhancement_details': {
                'pattern_matching': 'Enhanced with context-aware validation',
                'financial_normalization': 'Improved scaling detection and formatting',
                'consolidation': 'Smart conflict resolution with field-specific logic',
                'validation': 'Comprehensive field-level validation rules',
                'yfinance_integration': 'Enhanced with data consistency checks'
            }
        }
