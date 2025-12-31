from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from converter import WordToPDFConverter

app = Flask(__name__)

# CORS configuration - allows localhost and Vercel deployments
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:3000",
            "http://localhost:3001", 
            "http://localhost:3002",
            "https://*.vercel.app",
            "https://vercel.app"
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'docx'}

# Create folders if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Word to PDF API is running'})

@app.route('/api/convert', methods=['POST'])
def convert_document():
    """
    Convert uploaded Word document to PDF
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check if file type is allowed
        if not allowed_file(file.filename):
            return jsonify({'error': 'Only .docx files are allowed'}), 400
        
        # Secure the filename
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save uploaded file
        file.save(input_path)
        
        # Generate output filename
        output_filename = filename.rsplit('.', 1)[0] + '.pdf'
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
        # Convert using the Word to PDF converter
        converter = WordToPDFConverter()
        success = converter.convert(input_path, output_path)
        
        if not success:
            # Clean up input file
            if os.path.exists(input_path):
                os.remove(input_path)
            return jsonify({'error': 'Conversion failed'}), 500
        
        # Clean up input file after successful conversion
        if os.path.exists(input_path):
            os.remove(input_path)
        
        return jsonify({
            'success': True,
            'message': 'Conversion successful',
            'filename': output_filename,
            'download_url': f'/api/download/{output_filename}'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    """
    Download converted PDF file
    """
    try:
        # Secure the filename
        filename = secure_filename(filename)
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Send file and clean up after
        response = send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
        # Schedule file deletion after download
        @response.call_on_close
        def cleanup():
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Error cleaning up file: {e}")
        
        return response
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cleanup', methods=['POST'])
def cleanup_files():
    """
    Clean up old files (optional endpoint for maintenance)
    """
    try:
        import time
        current_time = time.time()
        cleanup_count = 0
        
        # Clean up files older than 1 hour
        for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER]:
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                if os.path.isfile(file_path):
                    file_age = current_time - os.path.getmtime(file_path)
                    if file_age > 3600:  # 1 hour
                        os.remove(file_path)
                        cleanup_count += 1
        
        return jsonify({
            'success': True,
            'message': f'Cleaned up {cleanup_count} old files'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Word to PDF API Server")
    print("📍 Running on http://localhost:5000")
    print("📝 API Endpoints:")
    print("   - POST /api/convert - Convert Word to PDF")
    print("   - GET  /api/download/<filename> - Download PDF")
    print("   - GET  /api/health - Health check")
    app.run(debug=True, port=5000)
