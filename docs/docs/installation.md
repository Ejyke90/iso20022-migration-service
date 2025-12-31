---
sidebar_position: 3
---

# Installation

This guide will walk you through installing and setting up the Word to PDF Agent on your system.

## Prerequisites

Before installing, ensure you have:

- **Python 3.8 or higher** installed on your system
- **pip** package manager (usually comes with Python)
- **Git** (optional, for cloning the repository)

### Verify Python Installation

```bash
python --version
# or
python3 --version
```

You should see output like `Python 3.8.x` or higher.

---

## Installation Methods

### Method 1: Clone from GitHub (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/VectorSystems/word-to-pdf-agent.git
   cd word-to-pdf-agent
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   
   **On macOS/Linux:**
   ```bash
   source venv/bin/activate
   ```
   
   **On Windows:**
   ```bash
   venv\Scripts\activate
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Method 2: Download ZIP

1. Download the ZIP file from the [GitHub repository](https://github.com/VectorSystems/word-to-pdf-agent)
2. Extract the ZIP file to your desired location
3. Follow steps 2-4 from Method 1

---

## Verify Installation

Test that everything is working correctly:

```bash
python main.py --help
```

You should see the help message with usage instructions.

### Run a Test Conversion

A test document is included in the repository:

```bash
python main.py test_doc.docx --output-file test_output.pdf
```

If successful, you'll see a confirmation message and `test_output.pdf` will be created.

---

## Dependencies

The following Python packages are required:

- `python-docx` - For reading Word documents
- `reportlab` or similar PDF library - For generating PDFs

These are automatically installed when you run `pip install -r requirements.txt`.

---

## Troubleshooting

### Common Issues

**Issue: `python: command not found`**
- Try using `python3` instead of `python`
- Ensure Python is added to your system PATH

**Issue: `pip: command not found`**
- Try using `pip3` instead of `pip`
- Install pip: `python -m ensurepip --upgrade`

**Issue: Permission denied errors**
- Use `sudo` on macOS/Linux (not recommended for virtual environments)
- Run terminal as Administrator on Windows
- Better: Use a virtual environment to avoid permission issues

**Issue: Module not found errors**
- Ensure you've activated the virtual environment
- Reinstall dependencies: `pip install -r requirements.txt`

---

## Next Steps

Now that you have the Word to PDF Agent installed, check out:

- [Usage Guide](./usage.md) - Learn how to use the tool
- [Product Information](./product-info.md) - Detailed feature documentation
- [API Reference](./product-info.md#api-reference) - Programmatic usage

---

## Updating

To update to the latest version:

```bash
cd word-to-pdf-agent
git pull origin main
pip install -r requirements.txt --upgrade
```
