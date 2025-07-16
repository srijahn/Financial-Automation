"""
Enhanced Financial Automation System - Main Runner
Combines enhanced and ultra-targeted extraction for maximum accuracy
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Import enhanced components
from enhanced_data_extraction import EnhancedFinancialDataExtractor
from ultra_targeted_extraction import UltraTargetedFinancialExtractor
from enhanced_automation_engine import EnhancedAutomationEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FinancialAutomationSystem:
    """Main financial automation system with enhanced accuracy"""
    
    def __init__(self):
        self.enhanced_extractor = EnhancedFinancialDataExtractor()
        self.ultra_targeted_extractor = UltraTargetedFinancialExtractor()
        self.automation_engine = EnhancedAutomationEngine(debug=True)
    
    def process_company_documents(self, company_folder: str, output_folder: str = None) -> Dict[str, Any]:
        """Process documents for a specific company with enhanced accuracy"""
        print(f"🚀 Processing {company_folder} with Enhanced Accuracy System")
        print("=" * 60)
        
        # Use enhanced automation engine
        result = self.automation_engine.process_documents(
            folder_path=company_folder,
            output_folder=output_folder,
            template_path="case_study_document_template.docx"
        )
        
        if result['success']:
            print(f"✅ Processing completed successfully!")
            print(f"📊 Accuracy: {result['accuracy_metrics']['overall_accuracy']:.1f}%")
            print(f"📁 Outputs: {result['outputs']}")
            
            # Display key extracted data
            self._display_extracted_data(result['consolidated_data'])
            
        else:
            print(f"❌ Processing failed: {result['error']}")
        
        return result
    
    def _display_extracted_data(self, data: Dict[str, Any]):
        """Display key extracted data"""
        print("\n📋 KEY EXTRACTED DATA:")
        print("-" * 30)
        
        key_fields = [
            'company_name', 'company_address', 'stock_symbol', 'fiscal_year',
            'revenue', 'net_income', 'net_margin', 'primary_business'
        ]
        
        for field in key_fields:
            value = data.get(field, 'NOT_FOUND')
            if value and value != 'NOT_FOUND':
                print(f"  {field.replace('_', ' ').title()}: {value}")
            else:
                print(f"  {field.replace('_', ' ').title()}: ❌ Not found")
    
    def run_accuracy_test(self):
        """Run accuracy test on all companies"""
        print("🧪 RUNNING ACCURACY TEST ON ALL COMPANIES")
        print("=" * 60)
        
        test_folders = ['DoubleVerify_files', 'BlueBird_files', 'Apple_files', 'Microsoft_files']
        results = {}
        
        for folder in test_folders:
            if os.path.exists(folder):
                print(f"\n📁 Testing: {folder}")
                result = self.process_company_documents(folder)
                results[folder] = result
            else:
                print(f"❌ Folder not found: {folder}")
        
        # Summary
        print("\n🎯 ACCURACY TEST SUMMARY")
        print("=" * 40)
        
        successful_tests = sum(1 for r in results.values() if r.get('success', False))
        total_tests = len(results)
        
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        
        if successful_tests > 0:
            avg_accuracy = sum(r['accuracy_metrics']['overall_accuracy'] for r in results.values() if r.get('success', False)) / successful_tests
            print(f"Average Accuracy: {avg_accuracy:.1f}%")
            
            print("\n📈 Company Results:")
            for company, result in results.items():
                if result.get('success', False):
                    accuracy = result['accuracy_metrics']['overall_accuracy']
                    status = "✅ GOOD" if accuracy >= 75 else "⚠️ NEEDS WORK"
                    print(f"  {company}: {accuracy:.1f}% {status}")
        
        return results


def main():
    """Main function with command line interface"""
    system = FinancialAutomationSystem()
    
    if len(sys.argv) < 2:
        print("🔧 FINANCIAL AUTOMATION SYSTEM - ENHANCED ACCURACY")
        print("=" * 60)
        print("Usage:")
        print("  python main.py <company_folder>     - Process specific company")
        print("  python main.py --test               - Run accuracy test on all companies")
        print("  python main.py --help               - Show this help")
        print()
        print("Examples:")
        print("  python main.py DoubleVerify_files")
        print("  python main.py BlueBird_files")
        print("  python main.py --test")
        return
    
    command = sys.argv[1]
    
    if command == '--test':
        system.run_accuracy_test()
    elif command == '--help':
        main()
    elif os.path.exists(command):
        # Process specific company
        output_folder = f"{command}_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        system.process_company_documents(command, output_folder)
    else:
        print(f"❌ Folder not found: {command}")
        print("Available folders:")
        for folder in ['DoubleVerify_files', 'BlueBird_files', 'Apple_files', 'Microsoft_files']:
            if os.path.exists(folder):
                print(f"  ✅ {folder}")
            else:
                print(f"  ❌ {folder} (not found)")


if __name__ == "__main__":
    main()
