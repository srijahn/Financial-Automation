"""
Main Application - Command line interface for document automation
"""

import argparse
import logging
from automation_engine import EnhancedAutomationEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Enhanced command line interface"""
    parser = argparse.ArgumentParser(description="Enhanced Document Automation with DOCX Support")
    parser.add_argument("--source", "-s", required=True, help="Source folder")
    parser.add_argument("--template", "-t", required=True, help="Template file (DOCX or TXT)")
    parser.add_argument("--output", "-o", required=True, help="Output folder")
    
    args = parser.parse_args()
    
    engine = EnhancedAutomationEngine()
    
    try:
        report = engine.process_documents(args.source, args.template, args.output)
        
        print(f"\n✅ Processing completed!")
        
        # Display output files
        if report['output_files']:
            print(f"📄 Output Files:")
            for output_file in report['output_files']:
                print(f"   • {output_file}")
        
        print(f"📊 Fields: {report['fields_populated']}/{report['total_template_fields']}")
        
        if report['unpopulated_fields']:
            print(f"\n⚠️  Unpopulated: {', '.join(report['unpopulated_fields'][:10])}")
            if len(report['unpopulated_fields']) > 10:
                print(f"    ... and {len(report['unpopulated_fields']) - 10} more")
        
        # Show some key populated fields
        print(f"\n📋 Key Fields Populated:")
        key_fields = ['company_name', 'revenue', 'net_income', 'total_assets', 'stock_symbol']
        for field in key_fields:
            if field in report['mapped_data'] and report['mapped_data'][field]:
                print(f"   • {field}: {report['mapped_data'][field]}")
        
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()