---
sidebar_position: 4
---

# Usage Guide

Learn how to use the Word to PDF Agent effectively for your document conversion needs.

---

## Quick Start

The simplest way to convert a document:

```bash
python main.py input.docx output.pdf
```

That's it! Your Word document will be converted to PDF.

---

## Command-Line Usage

### Basic Syntax

```bash
python main.py [OPTIONS] <input_file> <output_file>
```

### Examples

#### Simple Conversion
```bash
python main.py report.docx report.pdf
```

#### With Relative Paths
```bash
python main.py documents/report.docx output/report.pdf
```

#### With Absolute Paths
```bash
python main.py /Users/username/Documents/report.docx /Users/username/Desktop/report.pdf
```

### Advanced Options

#### High Quality Output
```bash
python main.py --quality high document.docx document.pdf
```

#### Enable Compression
```bash
python main.py --compress large-file.docx compressed-output.pdf
```

#### Verbose Logging
```bash
python main.py --verbose document.docx output.pdf
```

#### Combine Multiple Options
```bash
python main.py --quality high --compress --verbose report.docx report.pdf
```

---

## Python API Usage

### Basic Conversion

```python
from app import WordToPDFConverter

# Create converter instance
converter = WordToPDFConverter()

# Convert a document
converter.convert("input.docx", "output.pdf")
```

### With Error Handling

```python
from app import WordToPDFConverter

converter = WordToPDFConverter()

try:
    success = converter.convert("input.docx", "output.pdf")
    if success:
        print("✓ Conversion successful!")
    else:
        print("✗ Conversion failed")
except FileNotFoundError:
    print("✗ Input file not found")
except PermissionError:
    print("✗ Permission denied - check file access")
except Exception as e:
    print(f"✗ Error: {e}")
```

### Custom Configuration

```python
from app import WordToPDFConverter

# Configure converter
config = {
    'quality': 'high',
    'compression': True,
    'preserve_hyperlinks': True
}

converter = WordToPDFConverter(config)
converter.convert("input.docx", "output.pdf")
```

---

## Batch Processing

### Process Multiple Files

#### Using Python API

```python
from app import WordToPDFConverter
import os

converter = WordToPDFConverter()

# List of files to convert
files = ["doc1.docx", "doc2.docx", "doc3.docx"]

# Convert each file
for file in files:
    output = file.replace(".docx", ".pdf")
    converter.convert(file, output)
    print(f"Converted: {file} → {output}")
```

#### Process Directory

```python
from app import WordToPDFConverter
import os

converter = WordToPDFConverter()

input_dir = "documents/"
output_dir = "pdfs/"

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Process all .docx files
for filename in os.listdir(input_dir):
    if filename.endswith(".docx"):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename.replace(".docx", ".pdf"))
        
        try:
            converter.convert(input_path, output_path)
            print(f"✓ {filename}")
        except Exception as e:
            print(f"✗ {filename}: {e}")
```

#### Using Batch Convert Method

```python
from app import WordToPDFConverter

converter = WordToPDFConverter()

# Batch convert with results
results = converter.batch_convert(
    input_files=["doc1.docx", "doc2.docx", "doc3.docx"],
    output_dir="output/"
)

print(f"Successfully converted: {results['success']}/{results['total']}")
print(f"Failed: {results['failed']}")
```

### Shell Script for Batch Processing

Create a file `batch_convert.sh`:

```bash
#!/bin/bash

# Convert all .docx files in current directory
for file in *.docx; do
    if [ -f "$file" ]; then
        output="${file%.docx}.pdf"
        echo "Converting: $file → $output"
        python main.py "$file" "$output"
    fi
done

echo "Batch conversion complete!"
```

Make it executable and run:

```bash
chmod +x batch_convert.sh
./batch_convert.sh
```

---

## Integration Examples {#examples}

### 1. Automated Report Generation

```python
from app import WordToPDFConverter
from datetime import datetime

def generate_monthly_report():
    # Generate report in Word (your existing logic)
    report_name = f"report_{datetime.now().strftime('%Y-%m')}.docx"
    create_word_report(report_name)  # Your function
    
    # Convert to PDF
    converter = WordToPDFConverter()
    pdf_name = report_name.replace(".docx", ".pdf")
    converter.convert(report_name, pdf_name)
    
    # Send via email
    send_email_with_attachment(pdf_name)
    
    return pdf_name

# Run monthly
monthly_pdf = generate_monthly_report()
print(f"Report generated: {monthly_pdf}")
```

### 2. Web Application Integration

```python
from flask import Flask, request, send_file
from app import WordToPDFConverter
import os

app = Flask(__name__)
converter = WordToPDFConverter()

@app.route('/convert', methods=['POST'])
def convert_document():
    # Get uploaded file
    file = request.files['document']
    
    # Save temporarily
    input_path = f"temp/{file.filename}"
    file.save(input_path)
    
    # Convert
    output_path = input_path.replace(".docx", ".pdf")
    converter.convert(input_path, output_path)
    
    # Send PDF back
    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
```

### 3. CI/CD Pipeline Integration

```yaml
# .github/workflows/convert-docs.yml
name: Convert Documentation

on:
  push:
    paths:
      - 'docs/*.docx'

jobs:
  convert:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Convert documents
        run: |
          python main.py docs/manual.docx docs/manual.pdf
      
      - name: Upload PDFs
        uses: actions/upload-artifact@v2
        with:
          name: pdfs
          path: docs/*.pdf
```

### 4. Scheduled Conversion Task

```python
import schedule
import time
from app import WordToPDFConverter
import os

converter = WordToPDFConverter()

def convert_daily_reports():
    """Convert all reports from the last 24 hours"""
    reports_dir = "daily_reports/"
    output_dir = "pdf_archive/"
    
    for file in os.listdir(reports_dir):
        if file.endswith(".docx"):
            input_path = os.path.join(reports_dir, file)
            output_path = os.path.join(output_dir, file.replace(".docx", ".pdf"))
            
            try:
                converter.convert(input_path, output_path)
                print(f"Archived: {file}")
            except Exception as e:
                print(f"Error with {file}: {e}")

# Schedule daily at 6 PM
schedule.every().day.at("18:00").do(convert_daily_reports)

# Run scheduler
while True:
    schedule.run_pending()
    time.sleep(60)
```

---

## Best Practices

### 1. **Use Virtual Environments**
Always use a virtual environment to avoid dependency conflicts:
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

### 2. **Handle Errors Gracefully**
Always wrap conversions in try-except blocks:
```python
try:
    converter.convert(input_file, output_file)
except Exception as e:
    logging.error(f"Conversion failed: {e}")
    # Handle error appropriately
```

### 3. **Validate Input Files**
Check files before conversion:
```python
import os

def safe_convert(input_file, output_file):
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    if not input_file.endswith('.docx'):
        raise ValueError("Input must be a .docx file")
    
    converter.convert(input_file, output_file)
```

### 4. **Clean Up Temporary Files**
```python
import os

try:
    converter.convert("temp.docx", "output.pdf")
finally:
    if os.path.exists("temp.docx"):
        os.remove("temp.docx")
```

### 5. **Use Logging**
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"Converting {input_file}")
converter.convert(input_file, output_file)
logger.info(f"Conversion complete: {output_file}")
```

---

## Tips & Tricks

### Preserve Document Quality
```bash
python main.py --quality high document.docx document.pdf
```

### Reduce File Size
```bash
python main.py --compress large-document.docx compressed.pdf
```

### Process Files with Spaces in Names
```bash
python main.py "My Document.docx" "My Document.pdf"
```

### Convert and Open Automatically (macOS)
```bash
python main.py document.docx document.pdf && open document.pdf
```

### Convert and Open Automatically (Windows)
```bash
python main.py document.docx document.pdf && start document.pdf
```

---

## Performance Optimization

### For Large Documents
- Use compression: `--compress`
- Process during off-peak hours
- Ensure sufficient system memory

### For Batch Processing
- Process files in parallel (advanced):
```python
from concurrent.futures import ThreadPoolExecutor
from app import WordToPDFConverter

def convert_file(file_pair):
    input_file, output_file = file_pair
    converter = WordToPDFConverter()
    converter.convert(input_file, output_file)

files_to_convert = [
    ("doc1.docx", "doc1.pdf"),
    ("doc2.docx", "doc2.pdf"),
    ("doc3.docx", "doc3.pdf"),
]

with ThreadPoolExecutor(max_workers=4) as executor:
    executor.map(convert_file, files_to_convert)
```

---

## Next Steps

- Explore the [API Reference](./product-info.md#api-reference) for advanced usage
- Check out [Product Information](./product-info.md) for detailed features
- Report issues or request features on [GitHub](https://github.com/VectorSystems/word-to-pdf-agent/issues)
