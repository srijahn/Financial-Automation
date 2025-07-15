# Using the main application
python main.py --source BlueBird_files --template case_study_document_template.docx --output BlueBird_output

# Running the demo
python demo_display.py

# Using individual modules (example)
python -c "from data_extraction import EnhancedDocumentExtractor; extractor = EnhancedDocumentExtractor(); print(extractor.supported_formats)"