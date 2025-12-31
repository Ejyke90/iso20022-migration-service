# Word to PDF Converter - Complete Fix Guide

## Overview
This guide provides fixes for converting `.docx`, `.doc`, and `.dcx` files to PDF format.

## Backend Fixes

### 1. Update `requirements.txt`

```txt
Flask==3.0.0
Flask-CORS==4.0.0
python-docx==1.1.0
pypandoc==1.12
python-magic==0.4.27
LibreOffice-converter==0.1.0
# For .doc files
pywin32==306; sys_platform == 'win32'
comtypes==1.2.0; sys_platform == 'win32'
# Alternative cross-platform
unoconv==0.9.0
```

### 2. Create/Update `converter.py`

```python
import os
import subprocess
import platform
from pathlib import Path
from docx import Document
import tempfile
import shutil

class DocumentConverter:
    def __init__(self):
        self.supported_formats = ['.docx', '.doc', '.dcx']
        
    def convert_to_pdf(self, input_path, output_path=None):
        """
        Convert Word documents to PDF
        Supports: .docx, .doc, .dcx
        """
        input_path = Path(input_path)
        
        if not input_path.exists():
            raise FileNotFoundError(f"File not found: {input_path}")
        
        if input_path.suffix.lower() not in self.supported_formats:
            raise ValueError(f"Unsupported format: {input_path.suffix}")
        
        if output_path is None:
            output_path = input_path.with_suffix('.pdf')
        else:
            output_path = Path(output_path)
        
        # Convert based on file type
        if input_path.suffix.lower() == '.docx':
            return self._convert_docx_to_pdf(input_path, output_path)
        elif input_path.suffix.lower() in ['.doc', '.dcx']:
            return self._convert_legacy_to_pdf(input_path, output_path)
    
    def _convert_docx_to_pdf(self, input_path, output_path):
        """Convert .docx using LibreOffice or pandoc"""
        try:
            # Method 1: LibreOffice (recommended)
            return self._convert_with_libreoffice(input_path, output_path)
        except Exception as e:
            print(f"LibreOffice conversion failed: {e}")
            try:
                # Method 2: Pandoc fallback
                return self._convert_with_pandoc(input_path, output_path)
            except Exception as e2:
                print(f"Pandoc conversion failed: {e2}")
                raise Exception("All conversion methods failed")
    
    def _convert_legacy_to_pdf(self, input_path, output_path):
        """Convert .doc and .dcx files"""
        # First convert to .docx, then to PDF
        temp_docx = input_path.with_suffix('.docx')
        
        try:
            # Convert legacy format to .docx
            if platform.system() == 'Windows':
                self._convert_with_word_com(input_path, temp_docx)
            else:
                self._convert_with_libreoffice(input_path, temp_docx, 'docx')
            
            # Then convert .docx to PDF
            result = self._convert_docx_to_pdf(temp_docx, output_path)
            
            # Cleanup temp file
            if temp_docx.exists() and temp_docx != input_path:
                temp_docx.unlink()
            
            return result
        except Exception as e:
            # Cleanup on error
            if temp_docx.exists() and temp_docx != input_path:
                temp_docx.unlink()
            raise e
    
    def _convert_with_libreoffice(self, input_path, output_path, format='pdf'):
        """Convert using LibreOffice command line"""
        output_dir = output_path.parent
        
        cmd = [
            'libreoffice',
            '--headless',
            '--convert-to', format,
            '--outdir', str(output_dir),
            str(input_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            raise Exception(f"LibreOffice conversion failed: {result.stderr}")
        
        # LibreOffice creates file with same name but different extension
        expected_output = output_dir / f"{input_path.stem}.{format}"
        if expected_output != output_path and expected_output.exists():
            shutil.move(str(expected_output), str(output_path))
        
        return str(output_path)
    
    def _convert_with_pandoc(self, input_path, output_path):
        """Convert using pandoc"""
        cmd = [
            'pandoc',
            str(input_path),
            '-o', str(output_path),
            '--pdf-engine=xelatex'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            raise Exception(f"Pandoc conversion failed: {result.stderr}")
        
        return str(output_path)
    
    def _convert_with_word_com(self, input_path, output_path):
        """Convert using Windows COM (requires Microsoft Word)"""
        if platform.system() != 'Windows':
            raise Exception("COM automation only works on Windows")
        
        import win32com.client
        
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        
        try:
            doc = word.Documents.Open(str(input_path.absolute()))
            
            # wdFormatPDF = 17, wdFormatDocumentDefault = 16
            if output_path.suffix.lower() == '.pdf':
                doc.SaveAs(str(output_path.absolute()), FileFormat=17)
            else:
                doc.SaveAs(str(output_path.absolute()), FileFormat=16)
            
            doc.Close()
        finally:
            word.Quit()
        
        return str(output_path)
    
    def validate_file(self, file_path):
        """Validate if file can be converted"""
        path = Path(file_path)
        
        if not path.exists():
            return False, "File does not exist"
        
        if path.suffix.lower() not in self.supported_formats:
            return False, f"Unsupported format: {path.suffix}"
        
        if path.stat().st_size == 0:
            return False, "File is empty"
        
        if path.stat().st_size > 50 * 1024 * 1024:  # 50MB limit
            return False, "File too large (max 50MB)"
        
        return True, "Valid"


# Utility function for the API
def convert_file(input_file, output_file=None):
    converter = DocumentConverter()
    return converter.convert_to_pdf(input_file, output_file)
```

### 3. Update `app.py` (Flask Backend)

```python
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from pathlib import Path
from converter import DocumentConverter
import tempfile
import shutil

app = Flask(__name__)

# Configure CORS
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "https://*.vercel.app"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Configuration
UPLOAD_FOLDER = Path(tempfile.gettempdir()) / 'word-to-pdf-uploads'
UPLOAD_FOLDER.mkdir(exist_ok=True)
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

ALLOWED_EXTENSIONS = {'.docx', '.doc', '.dcx'}

def allowed_file(filename):
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'supported_formats': ['.docx', '.doc', '.dcx']
    })

@app.route('/api/convert', methods=['POST', 'OPTIONS'])
def convert_document():
    if request.method == 'OPTIONS':
        return '', 204
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({
            'error': f'Unsupported file type. Supported: {", ".join(ALLOWED_EXTENSIONS)}'
        }), 400
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        input_path = UPLOAD_FOLDER / filename
        file.save(str(input_path))
        
        # Convert to PDF
        converter = DocumentConverter()
        output_path = input_path.with_suffix('.pdf')
        
        # Validate file
        valid, message = converter.validate_file(input_path)
        if not valid:
            input_path.unlink()
            return jsonify({'error': message}), 400
        
        # Perform conversion
        result_path = converter.convert_to_pdf(str(input_path), str(output_path))
        
        # Send file
        response = send_file(
            result_path,
            as_attachment=True,
            download_name=f"{Path(filename).stem}.pdf",
            mimetype='application/pdf'
        )
        
        # Cleanup after sending (using after_request would be better)
        @response.call_on_close
        def cleanup():
            try:
                if input_path.exists():
                    input_path.unlink()
                if output_path.exists():
                    output_path.unlink()
            except:
                pass
        
        return response
        
    except Exception as e:
        # Cleanup on error
        try:
            if input_path.exists():
                input_path.unlink()
            if output_path.exists():
                output_path.unlink()
        except:
            pass
        
        return jsonify({'error': str(e)}), 500

@app.route('/api/validate', methods=['POST'])
def validate_file():
    """Validate file before conversion"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if not allowed_file(file.filename):
        return jsonify({
            'valid': False,
            'message': f'Unsupported file type. Supported: {", ".join(ALLOWED_EXTENSIONS)}'
        })
    
    # Check file size
    file.seek(0, 2)  # Seek to end
    size = file.tell()
    file.seek(0)  # Reset
    
    if size > MAX_FILE_SIZE:
        return jsonify({
            'valid': False,
            'message': 'File too large (max 50MB)'
        })
    
    return jsonify({
        'valid': True,
        'message': 'File is valid',
        'size': size,
        'filename': file.filename
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

## Frontend Fixes

### 4. Update Frontend Component (React/Next.js)

```typescript
// components/FileConverter.tsx
import React, { useState } from 'react';

interface ConversionState {
  status: 'idle' | 'uploading' | 'converting' | 'success' | 'error';
  message: string;
  progress: number;
}

export default function FileConverter() {
  const [file, setFile] = useState<File | null>(null);
  const [state, setState] = useState<ConversionState>({
    status: 'idle',
    message: '',
    progress: 0
  });

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      
      // Validate file extension
      const validExtensions = ['.docx', '.doc', '.dcx'];
      const fileExt = selectedFile.name.substring(selectedFile.name.lastIndexOf('.')).toLowerCase();
      
      if (!validExtensions.includes(fileExt)) {
        setState({
          status: 'error',
          message: `Invalid file type. Supported: ${validExtensions.join(', ')}`,
          progress: 0
        });
        return;
      }
      
      // Validate file size (50MB max)
      if (selectedFile.size > 50 * 1024 * 1024) {
        setState({
          status: 'error',
          message: 'File too large. Maximum size is 50MB',
          progress: 0
        });
        return;
      }
      
      setFile(selectedFile);
      setState({
        status: 'idle',
        message: `Selected: ${selectedFile.name}`,
        progress: 0
      });
    }
  };

  const handleConvert = async () => {
    if (!file) {
      setState({
        status: 'error',
        message: 'Please select a file first',
        progress: 0
      });
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      setState({ status: 'uploading', message: 'Uploading file...', progress: 30 });

      const response = await fetch(`${API_URL}/api/convert`, {
        method: 'POST',
        body: formData,
      });

      setState({ status: 'converting', message: 'Converting to PDF...', progress: 60 });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Conversion failed');
      }

      // Download the PDF
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = file.name.replace(/\.(docx?|dcx)$/i, '.pdf');
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      setState({
        status: 'success',
        message: 'PDF downloaded successfully!',
        progress: 100
      });

      // Reset after 3 seconds
      setTimeout(() => {
        setFile(null);
        setState({ status: 'idle', message: '', progress: 0 });
      }, 3000);

    } catch (error) {
      setState({
        status: 'error',
        message: error instanceof Error ? error.message : 'Conversion failed',
        progress: 0
      });
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg p-8">
        <h1 className="text-3xl font-bold text-center mb-8 text-gray-800">
          Word to PDF Converter
        </h1>

        <div className="space-y-6">
          {/* File Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Word Document (.docx, .doc, .dcx)
            </label>
            <input
              type="file"
              accept=".doc,.docx,.dcx"
              onChange={handleFileChange}
              className="block w-full text-sm text-gray-500
                file:mr-4 file:py-2 file:px-4
                file:rounded-md file:border-0
                file:text-sm file:font-semibold
                file:bg-blue-50 file:text-blue-700
                hover:file:bg-blue-100
                cursor-pointer"
            />
          </div>

          {/* Convert Button */}
          <button
            onClick={handleConvert}
            disabled={!file || state.status === 'uploading' || state.status === 'converting'}
            className="w-full py-3 px-4 bg-blue-600 text-white font-semibold rounded-lg
              hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed
              transition duration-200"
          >
            {state.status === 'uploading' || state.status === 'converting'
              ? 'Converting...'
              : 'Convert to PDF'}
          </button>

          {/* Progress Bar */}
          {(state.status === 'uploading' || state.status === 'converting') && (
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${state.progress}%` }}
              />
            </div>
          )}

          {/* Status Message */}
          {state.message && (
            <div className={`p-4 rounded-lg ${
              state.status === 'error' 
                ? 'bg-red-50 text-red-700 border border-red-200'
                : state.status === 'success'
                ? 'bg-green-50 text-green-700 border border-green-200'
                : 'bg-blue-50 text-blue-700 border border-blue-200'
            }`}>
              {state.message}
            </div>
          )}
        </div>

        {/* Info Section */}
        <div className="mt-8 p-4 bg-gray-50 rounded-lg">
          <h3 className="font-semibold text-gray-800 mb-2">Supported Formats:</h3>
          <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
            <li>.docx - Microsoft Word 2007+</li>
            <li>.doc - Microsoft Word 97-2003</li>
            <li>.dcx - Multi-page PCX image (if applicable)</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
```

## Deployment Notes

### For Production (Railway/Render/Heroku):

1. **Install LibreOffice** in your buildpack/Dockerfile:
```dockerfile
# Add to Dockerfile
RUN apt-get update && apt-get install -y \
    libreoffice \
    libreoffice-writer \
    && rm -rf /var/lib/apt/lists/*
```

2. **Environment Variables**:
```env
FLASK_ENV=production
MAX_FILE_SIZE=52428800
ALLOWED_ORIGINS=https://your-frontend.vercel.app
```

3. **For Windows deployment**, ensure Microsoft Word is installed for COM automation.

## Testing

Test all three formats:
```bash
curl -F "file=@test.docx" http://localhost:5000/api/convert --output test.pdf
curl -F "file=@test.doc" http://localhost:5000/api/convert --output test.pdf
curl -F "file=@test.dcx" http://localhost:5000/api/convert --output test.pdf
```

## Troubleshooting

1. **LibreOffice not found**: Install with `apt-get install libreoffice` (Linux) or download from libreoffice.org
2. **COM errors on Windows**: Ensure Microsoft Word is installed
3. **CORS errors**: Check `ALLOWED_ORIGINS` in backend configuration
4. **Large files failing**: Increase `MAX_CONTENT_LENGTH` in Flask config

This solution provides robust conversion with multiple fallback methods!