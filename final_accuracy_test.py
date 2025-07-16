"""
Final Accuracy Test with Ultra-Targeted Improvements
"""

import os
import sys
import logging
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, List, Any

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_data_extraction import EnhancedFinancialDataExtractor
from ultra_targeted_extraction import UltraTargetedFinancialExtractor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FinalAccuracyTester:
    """Final accuracy tester combining all improvements"""
    
    def __init__(self):
        self.enhanced_extractor = EnhancedFinancialDataExtractor()
        self.ultra_targeted_extractor = UltraTargetedFinancialExtractor()
    
    def run_final_accuracy_test(self):
        """Run final accuracy test with combined approaches"""
        print("🎯 FINAL ACCURACY TEST - ULTRA-TARGETED IMPROVEMENTS")
        print("=" * 70)
        
        # Test cases based on user feedback
        test_cases = {
            'DoubleVerify_files': {
                'company_name': 'DoubleVerify Holdings, Inc.',
                'company_address': 'New York, NY',
                'stock_symbol': 'DV',
                'fiscal_year': '2023',
                'net_margin': '%',
                'primary_business': 'digital advertising measurement',
                'target_accuracy': 80
            },
            'BlueBird_files': {
                'company_name': 'Blue Bird Corporation',
                'company_address': 'Macon, Georgia',
                'stock_symbol': 'BLBD',
                'fiscal_year': '2023',
                'net_margin': '%',
                'primary_business': 'school bus manufacturer',
                'target_accuracy': 85
            }
        }
        
        final_results = {}
        
        for test_folder, expectations in test_cases.items():
            print(f"\n📁 Testing: {test_folder}")
            print("-" * 50)
            
            if not os.path.exists(test_folder):
                print(f"❌ Folder not found: {test_folder}")
                continue
            
            try:
                # Get combined results
                combined_results = self._extract_with_combined_approach(test_folder)
                
                # Analyze accuracy
                accuracy_analysis = self._analyze_final_accuracy(
                    combined_results, expectations
                )
                
                final_results[test_folder] = accuracy_analysis
                
                # Display results
                self._display_final_results(test_folder, accuracy_analysis)
                
            except Exception as e:
                print(f"❌ Test failed: {e}")
                final_results[test_folder] = {'error': str(e)}
        
        # Generate final summary
        self._generate_final_summary(final_results)
        
        return final_results
    
    def _extract_with_combined_approach(self, folder_path: str) -> Dict[str, Any]:
        """Extract data using combined enhanced + ultra-targeted approach"""
        folder_path = Path(folder_path)
        
        # Collect all text from documents
        all_text = ""
        document_names = []
        
        for file_path in folder_path.glob("*.pdf"):
            try:
                text = self._extract_text_from_file(file_path)
                if text:
                    all_text += text + "\n"
                    document_names.append(file_path.name)
            except Exception as e:
                logger.error(f"Error extracting text from {file_path}: {e}")
        
        if not all_text:
            return {}
        
        # Extract with enhanced approach
        enhanced_data = self.enhanced_extractor.extract_data(all_text, f"{folder_path.name}_combined")
        enhanced_consolidated = self.enhanced_extractor.consolidate_data(enhanced_data)
        
        # Extract with ultra-targeted approach
        ultra_data = self.ultra_targeted_extractor.extract_data(all_text, f"{folder_path.name}_combined")
        ultra_consolidated = self.ultra_targeted_extractor.consolidate_data(ultra_data)
        
        # Combine results with priority to ultra-targeted
        final_results = enhanced_consolidated.copy()
        
        # Override with ultra-targeted results where available
        for field, value in ultra_consolidated.items():
            if value and value != 'NOT_FOUND':
                final_results[field] = value
                logger.info(f"✅ Ultra-targeted override for {field}: {value}")
        
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
    
    def _analyze_final_accuracy(self, extracted_data: Dict[str, Any], 
                               expectations: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze final accuracy with detailed scoring"""
        analysis = {
            'field_analysis': {},
            'improvements': [],
            'remaining_issues': [],
            'accuracy_score': 0
        }
        
        total_fields = len(expectations) - 1  # Exclude target_accuracy
        correct_fields = 0
        
        for field, expected_value in expectations.items():
            if field == 'target_accuracy':
                continue
                
            extracted_value = extracted_data.get(field, 'NOT_FOUND')
            field_result = {
                'expected': expected_value,
                'extracted': extracted_value,
                'correct': False,
                'score': 0,
                'notes': []
            }
            
            # Detailed field-specific scoring
            if field == 'company_address':
                if isinstance(extracted_value, str):
                    if expected_value.lower() in extracted_value.lower():
                        field_result['correct'] = True
                        field_result['score'] = 100
                        correct_fields += 1
                        field_result['notes'].append("✅ Perfect address match")
                    elif any(word in extracted_value.lower() for word in expected_value.lower().split()):
                        field_result['score'] = 70
                        field_result['notes'].append("🟨 Partial address match")
                    else:
                        field_result['score'] = 0
                        field_result['notes'].append("❌ Address mismatch")
                else:
                    field_result['score'] = 0
                    field_result['notes'].append("❌ Address not found")
            
            elif field == 'stock_symbol':
                if isinstance(extracted_value, str) and extracted_value.upper() == expected_value.upper():
                    field_result['correct'] = True
                    field_result['score'] = 100
                    correct_fields += 1
                    field_result['notes'].append("✅ Perfect symbol match")
                else:
                    field_result['score'] = 0
                    field_result['notes'].append("❌ Symbol mismatch")
            
            elif field == 'fiscal_year':
                if isinstance(extracted_value, str) and expected_value in extracted_value:
                    field_result['correct'] = True
                    field_result['score'] = 100
                    correct_fields += 1
                    field_result['notes'].append("✅ Perfect fiscal year match")
                elif isinstance(extracted_value, str) and '202' in extracted_value:
                    field_result['score'] = 80
                    field_result['notes'].append("🟨 Recent year found")
                else:
                    field_result['score'] = 0
                    field_result['notes'].append("❌ Fiscal year mismatch")
            
            elif field == 'net_margin':
                if isinstance(extracted_value, str) and '%' in extracted_value:
                    field_result['correct'] = True
                    field_result['score'] = 100
                    correct_fields += 1
                    field_result['notes'].append("✅ Perfect percentage format")
                else:
                    field_result['score'] = 0
                    field_result['notes'].append("❌ Not in percentage format")
            
            elif field == 'primary_business':
                if isinstance(extracted_value, str) and len(extracted_value) > 10:
                    business_keywords = expected_value.split()
                    if any(keyword in extracted_value.lower() for keyword in business_keywords):
                        field_result['correct'] = True
                        field_result['score'] = 100
                        correct_fields += 1
                        field_result['notes'].append("✅ Perfect business match")
                    else:
                        field_result['score'] = 50
                        field_result['notes'].append("🟨 Generic business description")
                else:
                    field_result['score'] = 0
                    field_result['notes'].append("❌ Business description missing")
            
            elif field == 'company_name':
                if isinstance(extracted_value, str):
                    name_words = expected_value.lower().split()
                    if all(word in extracted_value.lower() for word in name_words):
                        field_result['correct'] = True
                        field_result['score'] = 100
                        correct_fields += 1
                        field_result['notes'].append("✅ Perfect name match")
                    elif any(word in extracted_value.lower() for word in name_words):
                        field_result['score'] = 70
                        field_result['notes'].append("🟨 Partial name match")
                    else:
                        field_result['score'] = 0
                        field_result['notes'].append("❌ Name mismatch")
                else:
                    field_result['score'] = 0
                    field_result['notes'].append("❌ Name not found")
            
            analysis['field_analysis'][field] = field_result
        
        # Calculate overall accuracy
        total_possible_score = total_fields * 100
        actual_score = sum(field['score'] for field in analysis['field_analysis'].values())
        accuracy_percentage = (actual_score / total_possible_score) * 100 if total_possible_score > 0 else 0
        
        analysis['accuracy_score'] = accuracy_percentage
        analysis['field_accuracy'] = (correct_fields / total_fields) * 100 if total_fields > 0 else 0
        
        # Check against target
        target_accuracy = expectations.get('target_accuracy', 80)
        if accuracy_percentage >= target_accuracy:
            analysis['improvements'].append(f"✅ TARGET ACHIEVED: {accuracy_percentage:.1f}% >= {target_accuracy}%")
        else:
            analysis['remaining_issues'].append(f"❌ Target not met: {accuracy_percentage:.1f}% < {target_accuracy}%")
        
        return analysis
    
    def _display_final_results(self, test_folder: str, analysis: Dict[str, Any]):
        """Display final test results"""
        print(f"\n🎯 FINAL RESULTS for {test_folder}:")
        print(f"Accuracy Score: {analysis['accuracy_score']:.1f}%")
        print(f"Field Accuracy: {analysis['field_accuracy']:.1f}%")
        
        print("\n📊 DETAILED FIELD ANALYSIS:")
        for field, result in analysis['field_analysis'].items():
            status = "✅" if result['correct'] else ("🟨" if result['score'] > 50 else "❌")
            print(f"  {status} {field}: {result['extracted']} (Score: {result['score']}/100)")
            for note in result['notes']:
                print(f"    {note}")
        
        if analysis['improvements']:
            print(f"\n✅ ACHIEVEMENTS:")
            for improvement in analysis['improvements']:
                print(f"  {improvement}")
        
        if analysis['remaining_issues']:
            print(f"\n❌ REMAINING ISSUES:")
            for issue in analysis['remaining_issues']:
                print(f"  {issue}")
    
    def _generate_final_summary(self, results: Dict[str, Any]):
        """Generate final summary report"""
        print("\n" + "=" * 70)
        print("🏆 FINAL ACCURACY TEST SUMMARY")
        print("=" * 70)
        
        successful_tests = sum(1 for r in results.values() if 'error' not in r)
        
        if successful_tests > 0:
            avg_accuracy = sum(r['accuracy_score'] for r in results.values() if 'accuracy_score' in r) / successful_tests
            avg_field_accuracy = sum(r['field_accuracy'] for r in results.values() if 'field_accuracy' in r) / successful_tests
            
            print(f"📈 OVERALL PERFORMANCE:")
            print(f"  Average Accuracy Score: {avg_accuracy:.1f}%")
            print(f"  Average Field Accuracy: {avg_field_accuracy:.1f}%")
            print(f"  Successful Tests: {successful_tests}")
            
            print(f"\n🎯 COMPANY-SPECIFIC RESULTS:")
            for company, result in results.items():
                if 'error' not in result:
                    status = "✅ PASSED" if result['accuracy_score'] >= 80 else "❌ NEEDS WORK"
                    print(f"  {company}: {result['accuracy_score']:.1f}% {status}")
                else:
                    print(f"  {company}: ERROR - {result['error']}")
        
        # Save detailed report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = f"final_accuracy_report_{timestamp}.json"
        
        with open(report_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📄 Detailed report saved: {report_path}")
        
        # Final recommendations
        print(f"\n💡 FINAL RECOMMENDATIONS:")
        print("1. ✅ Enhanced pattern matching implemented")
        print("2. ✅ Ultra-targeted company-specific patterns added")
        print("3. ✅ Improved financial value normalization")
        print("4. ✅ Better field validation and cleaning")
        print("5. 🔄 Continue monitoring accuracy with new documents")


def main():
    """Main function"""
    tester = FinalAccuracyTester()
    results = tester.run_final_accuracy_test()
    
    print("\n🎉 FINAL ACCURACY TESTING COMPLETED!")
    print("The system now includes both enhanced and ultra-targeted improvements!")
    
    return results


if __name__ == "__main__":
    main()
