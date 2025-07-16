"""
Enhanced Financial Automation System - Main Runner
=================================================

This is the main entry point for the enhanced financial automation system
with ultra-targeted accuracy improvements.

Usage:
    python run_enhanced_system.py --company [company_folder] --template [template_path] --output [output_folder]
    python run_enhanced_system.py --demo  # Run demo with all companies
    python run_enhanced_system.py --test  # Run accuracy test

Examples:
    python run_enhanced_system.py --company DoubleVerify_files
    python run_enhanced_system.py --company BlueBird_files
    python run_enhanced_system.py --demo
    python run_enhanced_system.py --test
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_automation_engine import EnhancedAutomationEngine
from enhanced_data_extraction import EnhancedFinancialDataExtractor
from ultra_targeted_extraction import UltraTargetedFinancialExtractor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedFinancialAutomationRunner:
    """Main runner for the enhanced financial automation system"""
    
    def __init__(self):
        self.engine = EnhancedAutomationEngine(debug=True)
        self.enhanced_extractor = EnhancedFinancialDataExtractor()
        self.ultra_targeted_extractor = UltraTargetedFinancialExtractor()
    
    def run_company_processing(self, company_folder: str, template_path: str = None, output_folder: str = None):
        """Run enhanced processing for a specific company"""
        print(f"🚀 Enhanced Financial Automation System")
        print(f"📁 Processing: {company_folder}")
        print("=" * 60)
        
        # Set default paths
        if not template_path:
            template_path = "case_study_document_template.docx"
        if not output_folder:
            output_folder = f"{company_folder}_enhanced_output"
        
        # Process with enhanced system
        result = self.engine.process_documents(
            folder_path=company_folder,
            output_folder=output_folder,
            template_path=template_path
        )
        
        if result['success']:
            print(f"✅ Processing completed successfully!")
            print(f"📊 Overall accuracy: {result['accuracy_metrics']['overall_accuracy']:.1f}%")
            print(f"📁 Outputs saved to: {output_folder}")
            print(f"📄 Report saved to: {result['report_path']}")
            
            # Show extracted data summary
            print(f"\n📋 Extracted Data Summary:")
            for field, value in result['consolidated_data'].items():
                print(f"  {field}: {value}")
        else:
            print(f"❌ Processing failed: {result['error']}")
        
        return result
    
    def run_demo(self):
        """Run demo with all available companies"""
        print("🎯 ENHANCED FINANCIAL AUTOMATION DEMO")
        print("=" * 60)
        
        # Available companies
        companies = ['DoubleVerify_files', 'BlueBird_files', 'Apple_files', 'Microsoft_files']
        
        demo_results = {}
        
        for company in companies:
            if os.path.exists(company):
                print(f"\n📁 Processing {company}...")
                result = self.run_company_processing(company)
                demo_results[company] = result
            else:
                print(f"⚠️ Skipping {company} - folder not found")
        
        # Demo summary
        print(f"\n🎯 DEMO SUMMARY")
        print("=" * 40)
        
        successful = sum(1 for r in demo_results.values() if r.get('success', False))
        total = len(demo_results)
        
        print(f"Total companies processed: {total}")
        print(f"Successful: {successful}")
        print(f"Failed: {total - successful}")
        
        if successful > 0:
            avg_accuracy = sum(r['accuracy_metrics']['overall_accuracy'] 
                             for r in demo_results.values() 
                             if r.get('success', False)) / successful
            print(f"Average accuracy: {avg_accuracy:.1f}%")
            
            print(f"\n📈 Company Results:")
            for company, result in demo_results.items():
                if result.get('success', False):
                    accuracy = result['accuracy_metrics']['overall_accuracy']
                    print(f"  {company}: {accuracy:.1f}%")
        
        return demo_results
    
    def run_accuracy_test(self):
        """Run accuracy test with combined enhanced + ultra-targeted approach"""
        print("🧪 ENHANCED ACCURACY TEST")
        print("=" * 60)
        
        # Test companies
        test_companies = {
            'DoubleVerify_files': {
                'target_accuracy': 70,
                'expected_fields': ['company_name', 'company_address', 'stock_symbol', 'fiscal_year']
            },
            'BlueBird_files': {
                'target_accuracy': 75,
                'expected_fields': ['company_name', 'company_address', 'stock_symbol', 'fiscal_year']
            }
        }
        
        test_results = {}
        
        for company, config in test_companies.items():
            if not os.path.exists(company):
                print(f"⚠️ Skipping {company} - folder not found")
                continue
            
            print(f"\n📁 Testing {company}...")
            
            # Get combined results
            combined_data = self._get_combined_extraction_results(company)
            
            # Calculate accuracy
            accuracy = self._calculate_test_accuracy(combined_data, config['expected_fields'])
            target = config['target_accuracy']
            
            test_results[company] = {
                'accuracy': accuracy,
                'target': target,
                'passed': accuracy >= target,
                'extracted_data': combined_data
            }
            
            # Display results
            status = "✅ PASSED" if accuracy >= target else "❌ FAILED"
            print(f"  Accuracy: {accuracy:.1f}% (Target: {target}%) {status}")
        
        # Test summary
        print(f"\n🎯 ACCURACY TEST SUMMARY")
        print("=" * 40)
        
        total_tests = len(test_results)
        passed_tests = sum(1 for r in test_results.values() if r['passed'])
        
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        
        if test_results:
            avg_accuracy = sum(r['accuracy'] for r in test_results.values()) / len(test_results)
            print(f"Average accuracy: {avg_accuracy:.1f}%")
        
        return test_results
    
    def _get_combined_extraction_results(self, company_folder: str) -> Dict[str, Any]:
        """Get combined enhanced + ultra-targeted extraction results"""
        folder_path = Path(company_folder)
        
        # Collect all text
        all_text = ""
        for file_path in folder_path.glob("*.pdf"):
            try:
                text = self._extract_text_from_file(file_path)
                if text:
                    all_text += text + "\n"
            except Exception as e:
                logger.error(f"Error extracting text from {file_path}: {e}")
        
        if not all_text:
            return {}
        
        # Enhanced extraction
        enhanced_data = self.enhanced_extractor.extract_data(all_text, f"{company_folder}_combined")
        enhanced_consolidated = self.enhanced_extractor.consolidate_data(enhanced_data)
        
        # Ultra-targeted extraction
        ultra_data = self.ultra_targeted_extractor.extract_data(all_text, f"{company_folder}_combined")
        ultra_consolidated = self.ultra_targeted_extractor.consolidate_data(ultra_data)
        
        # Combine with priority to ultra-targeted
        final_results = enhanced_consolidated.copy()
        for field, value in ultra_consolidated.items():
            if value and value != 'NOT_FOUND':
                final_results[field] = value
        
        return final_results
    
    def _extract_text_from_file(self, file_path: Path) -> str:
        """Extract text from PDF file"""
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
    
    def _calculate_test_accuracy(self, extracted_data: Dict[str, Any], expected_fields: List[str]) -> float:
        """Calculate accuracy score for testing"""
        if not expected_fields:
            return 0.0
        
        filled_fields = 0
        for field in expected_fields:
            if field in extracted_data and extracted_data[field] and extracted_data[field] != 'NOT_FOUND':
                filled_fields += 1
        
        return (filled_fields / len(expected_fields)) * 100


def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(
        description='Enhanced Financial Automation System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument('--company', '-c', help='Company folder to process')
    parser.add_argument('--template', '-t', help='Template file path', default='case_study_document_template.docx')
    parser.add_argument('--output', '-o', help='Output folder path')
    parser.add_argument('--demo', action='store_true', help='Run demo with all companies')
    parser.add_argument('--test', action='store_true', help='Run accuracy test')
    
    args = parser.parse_args()
    
    runner = EnhancedFinancialAutomationRunner()
    
    if args.demo:
        runner.run_demo()
    elif args.test:
        runner.run_accuracy_test()
    elif args.company:
        runner.run_company_processing(args.company, args.template, args.output)
    else:
        parser.print_help()
        print("\n🎯 Quick Start:")
        print("  python run_enhanced_system.py --demo")
        print("  python run_enhanced_system.py --test")
        print("  python run_enhanced_system.py --company DoubleVerify_files")


if __name__ == "__main__":
    main()
