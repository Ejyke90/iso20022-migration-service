# Word to PDF Web Application

A modern, full-stack web application for converting Word documents to PDF with a beautiful UI.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- npm

### 1. Start the Backend API

```bash
# Install Python dependencies
pip install -r api/requirements.txt

# Start Flask server
python api/server.py
```

The API will run on `http://localhost:5000`

### 2. Start the Frontend

```bash
# Navigate to web app directory
cd web-app

# Install dependencies
npm install

# Start development server
npm run dev
```

The web app will run on `http://localhost:3000`

## 📁 Project Structure

```
word-to-pdf-agent/
├── api/
│   ├── server.py          # Flask API server
│   ├── requirements.txt   # Python dependencies
│   ├── uploads/          # Temporary upload folder
│   └── outputs/          # Temporary output folder
├── web-app/
│   ├── app/
│   │   ├── page.tsx      # Main landing page
│   │   ├── globals.css   # Global styles
│   │   └── layout.tsx    # Root layout
│   ├── package.json      # Node dependencies
│   └── next.config.js    # Next.js configuration
├── app.py                # Word to PDF converter
└── main.py               # CLI interface
```

## 🎨 Features

### Frontend
- ✨ Modern, gradient UI with glassmorphism effects
- 📤 Drag & drop file upload
- ⚡ Real-time conversion status
- 📥 Automatic PDF download
- 📱 Fully responsive design
- 🎯 Vector Systems branding

### Backend
- 🔒 Secure file handling
- 🗑️ Automatic file cleanup
- ⚠️ Error handling
- 🌐 CORS enabled for frontend
- 📊 Health check endpoint

## 🔧 API Endpoints

### `POST /api/convert`
Upload and convert a Word document to PDF

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: `file` (Word document)

**Response:**
```json
{
  "success": true,
  "message": "Conversion successful",
  "filename": "document.pdf",
  "download_url": "/api/download/document.pdf"
}
```

### `GET /api/download/<filename>`
Download the converted PDF file

**Response:**
- Content-Type: `application/pdf`
- File automatically deleted after download

### `GET /api/health`
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "message": "Word to PDF API is running"
}
```

## 🎯 Usage

1. Open `http://localhost:3000` in your browser
2. Drag and drop a `.docx` file or click to browse
3. Click "Convert to PDF"
4. Wait for conversion (usually 2-5 seconds)
5. Click "Download PDF" to get your file

## 🛠️ Development

### Backend Development

```bash
# Run with auto-reload
python api/server.py
```

### Frontend Development

```bash
cd web-app
npm run dev
```

Hot reload is enabled for both frontend and backend during development.

## 📦 Production Build

### Frontend

```bash
cd web-app
npm run build
npm start
```

### Backend

For production, use a WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 api.server:app
```

## 🚢 Deployment Options

### Option 1: Vercel (Frontend) + Railway (Backend)
- Deploy Next.js app to Vercel
- Deploy Flask API to Railway
- Update API URL in frontend

### Option 2: Docker
Create `Dockerfile` for both frontend and backend, then use Docker Compose

### Option 3: Traditional Hosting
- Frontend: Any static hosting (Netlify, Vercel, etc.)
- Backend: Any Python hosting (Heroku, Railway, DigitalOcean, etc.)

## 🔒 Security Notes

- Files are automatically deleted after download
- Maximum file size: 16MB
- Only `.docx` files are accepted
- CORS is configured for localhost (update for production)

## 🎨 Customization

### Change Colors

Edit `web-app/app/globals.css` and `web-app/app/page.tsx` to customize the color scheme.

### Change Branding

Update the header and footer in `web-app/app/page.tsx` with your branding.

## 📝 License

MIT License - see LICENSE file for details

## 🤝 Support

For issues or questions, please open an issue on GitHub.

---

Built with ❤️ by Vector Systems
