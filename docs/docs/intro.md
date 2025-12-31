---
sidebar_position: 1
---

# Getting Started

Welcome to **Word to PDF Agent** - your intelligent solution for converting Microsoft Word documents to PDF format with ease and precision.

## What is Word to PDF Agent?

Word to PDF Agent is an AI-powered document conversion tool that transforms `.docx` files into high-quality PDF documents. Built with Python, it offers both a simple command-line interface and a powerful Python API for seamless integration into your workflows.

### Why Choose Word to PDF Agent?

- 🚀 **Fast**: Convert documents in seconds
- 🎯 **Accurate**: Preserves formatting and layout
- 🤖 **Intelligent**: AI-powered processing for complex documents
- 🔧 **Flexible**: CLI and Python API interfaces
- 📦 **Lightweight**: Minimal dependencies

---

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/VectorSystems/word-to-pdf-agent.git
cd word-to-pdf-agent

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Your First Conversion

Convert a Word document to PDF with a single command:

```bash
python main.py input.docx --output-file output.pdf
```

That's it! Your PDF is ready.

---

## What's Next?

Explore the documentation to learn more:

- **[Product Information](./product-info.md)** - Detailed features and capabilities
- **[Installation](./installation.md)** - Complete installation guide
- **[Usage Guide](./usage.md)** - Learn all the ways to use the tool
- **[API Reference](./product-info.md#api-reference)** - Programmatic usage

---

## Example Use Cases

### Command-Line Conversion
```bash
python main.py report.docx --output-file report.pdf
```

### Python API
```python
from app import WordToPDFConverter

converter = WordToPDFConverter()
converter.convert("document.docx", "document.pdf")
```

### Batch Processing
```python
converter.batch_convert(
    ["doc1.docx", "doc2.docx", "doc3.docx"],
    output_dir="pdfs/"
)
```

---

## Need Help?

- 📖 Check the [Usage Guide](./usage.md) for detailed examples
- 🐛 Report issues on [GitHub](https://github.com/VectorSystems/word-to-pdf-agent/issues)
- 💡 See [Product Info](./product-info.md) for advanced features

Happy converting! 🎉
