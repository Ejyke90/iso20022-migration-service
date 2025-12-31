#!/bin/bash

# Ensure we are in the right directory
cd "$(dirname "$0")"

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Virtual environment not found. Please run installation first."
    exit 1
fi

# Run the Streamlit app
echo "🚀 Starting Word-to-PDF Agent UI..."
echo "Press Ctrl+C to stop."
streamlit run app.py
