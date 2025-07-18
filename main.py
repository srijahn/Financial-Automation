"""
Enhanced Financial Automation System - Main Runner
Uses enhanced extraction for maximum accuracy
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Import enhanced components
from enhanced_data_extraction import EnhancedFinancialDataExtractor
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
        self.automation_engine = EnhancedAutomationEngine(debug=True)
    
    def process_company_documents(self, company_folder: str, output_folder: str = None) -> Dict[str, Any]:
        """Process documents for a specific company with enhanced accuracy"""
        print(f"🚀 Processing {company_folder}")
        print("=" * 60)
        
        # Use enhanced automation engine
        result = self.automation_engine.process_documents(
            folder_path=company_folder,
            output_folder=output_folder,
            template_path="case_study_document_template.docx"
        )
        
        if result['success']:
            print(f"✅ Processing completed successfully!")
            # print(f"📊 Accuracy: {result['accuracy_metrics']['overall_accuracy']:.1f}%")
            # print(f"📁 Outputs: {result['outputs']}")
            
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
    
def get_available_folders():
    """Dynamically find all *_files folders"""
    folders = []
    for item in os.listdir('.'):
        if os.path.isdir(item) and item.endswith('_files'):
            folders.append(item)
    return sorted(folders)

def main():
    """Main function with command line interface"""
    system = FinancialAutomationSystem()
    
    if len(sys.argv) < 2:
        print("❌ No company folder specified")
        print("Available folders:")
        for folder in get_available_folders():
            print(f"  ✅ {folder}")
        return
    
    command = sys.argv[1]

    if os.path.exists(command):
        # Process specific company
        output_folder = f"{command}_output"
        system.process_company_documents(command, output_folder)
    else:
        print(f"❌ Folder not found: {command}")
        print("Available folders:")
        for folder in get_available_folders():
            print(f"  ✅ {folder}")


if __name__ == "__main__":
    main()
