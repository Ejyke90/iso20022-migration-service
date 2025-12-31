# Word to PDF AI Agent

This repository contains an AI agent designed to receive Microsoft Word documents (`.docx`) and convert them into PDF files.

## Features

- **Automated Conversion**: Watch a folder or accept files for instant conversion.
- **AI Processing** (Future): Analyze content before conversion (e.g., summarization, formatting checks).

## Prerequisites

- Python 3.8+
- Microsoft Word (for macOS/Windows) installed for `docx2pdf` to work natively.

## Installation

1. Clone the repository (or if you just created this locally):
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the agent:

```bash
python main.py --input path/to/document.docx --output path/to/output.pdf
```
