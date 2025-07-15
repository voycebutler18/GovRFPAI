#!/bin/bash
# GovRFP AI Setup Script - Fixed Version with Error Resolution
echo "Setting up GovRFP AI Defense Contracting Platform..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Clean up existing installation if it exists
if [ -d "venv" ]; then
    echo "Removing existing virtual environment..."
    rm -rf venv
fi

# Create project directory structure
echo "Creating directory structure..."
mkdir -p templates static/css static/js static/images
mkdir -p logs uploads data
mkdir -p config

# Create virtual environment with explicit Python 3
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip first
echo "Upgrading pip..."
pip install --upgrade pip

# Create requirements.txt with compatible versions
echo "Creating requirements.txt..."
cat > requirements.txt << 'EOF'
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-Login==0.6.2
Flask-WTF==1.1.1
WTForms==3.0.1
Werkzeug==2.3.7
gunicorn==21.2.0
python-dotenv==1.0.0
cryptography==41.0.4
requests==2.31.0
Jinja2==3.1.2
itsdangerous==2.1.2
click==8.1.7
markupsafe==2.1.3
blinker==1.6.2
EOF

# Install requirements
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create fixed Flask app structure
echo "Setting up Flask application..."
cat > app.py << 'EOF'
#!/usr/bin/env python3
import os
import sys
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler
import re

# Load environment variables
load_dotenv()

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.config['TESTING'] = False
    
    # Database configuration (SQLite for now)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///govrfp.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # File upload configuration
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    app.config['UPLOAD_FOLDER'] = 'uploads'
    
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Setup logging
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('GovRFP AI startup')
    
    # Define routes directly in app to avoid blueprint conflicts
    @app.route('/')
    def index():
        """Main dashboard route"""
        return render_template('index.html')

    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        return jsonify({'status': 'healthy', 'service': 'GovRFP AI'})

    @app.route('/api/analyze', methods=['POST'])
    def analyze_rfp():
        """RFP analysis endpoint"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'status': 'error', 'message': 'No data provided'}), 400
            
            # Add your RFP analysis logic here
            return jsonify({
                'status': 'success',
                'analysis': 'RFP analysis completed successfully',
                'recommendations': ['Review technical requirements', 'Check compliance standards']
            })
        except Exception as e:
            app.logger.error(f"Error in RFP analysis: {str(e)}")
            return jsonify({'status': 'error', 'message': 'Analysis failed'}), 500

    @app.route('/api/upload', methods=['POST'])
    def upload_file():
        """File upload endpoint"""
        try:
            if 'file' not in request.files:
                return jsonify({'status': 'error', 'message': 'No file provided'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'status': 'error', 'message': 'No file selected'}), 400
            
            if file:
                filename = secure_filename(file.filename)
                # Additional security: limit filename length and sanitize
                filename = re.sub(r'[^a-zA-Z0-9._-]', '', filename)[:100]
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                return jsonify({'status': 'success', 'filename': filename})
        
        except Exception as e:
            app.logger.error(f"Upload error: {str(e)}")
            return jsonify({'status': 'error', 'message': 'Upload failed'}), 500

    @app.errorhandler(413)
    def too_large(e):
        return jsonify({'status': 'error', 'message': 'File too large'}), 413

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'status': 'error', 'message': 'Endpoint not found'}), 404

    @app.errorhandler(500)
    def internal_error(e):
        app.logger.error(f"Internal server error: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500
    
    return app

# Create the app instance
app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    host = os.getenv('HOST', '0.0.0.0')
    app.run(host=host, port=port, debug=debug)
EOF

# Create improved HTML template
echo "Creating HTML template..."
cat > templates/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GovRFP AI - Defense Contracting Platform</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { 
            background: rgba(30, 58, 138, 0.9); 
            color: white; 
            padding: 30px; 
            text-align: center; 
            border-radius: 10px;
            margin-bottom: 20px;
            backdrop-filter: blur(10px);
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.2em; opacity: 0.9; }
        .main-content { 
            background: rgba(255, 255, 255, 0.95); 
            margin: 20px 0; 
            padding: 30px; 
            border-radius: 15px; 
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
        }
        .section { margin: 30px 0; }
        .section h2 { 
            color: #1e3a8a; 
            margin-bottom: 15px; 
            font-size: 1.5em;
            border-bottom: 2px solid #3b82f6;
            padding-bottom: 5px;
        }
        .btn { 
            background: linear-gradient(45deg, #3b82f6, #1d4ed8); 
            color: white; 
            padding: 12px 24px; 
            border: none; 
            border-radius: 8px; 
            cursor: pointer; 
            font-size: 1em;
            transition: all 0.3s ease;
            margin: 5px;
        }
        .btn:hover { 
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
        }
        .status { 
            margin: 20px 0; 
            padding: 15px; 
            border-radius: 8px; 
            font-weight: 500;
        }
        .status.success { 
            background: linear-gradient(45deg, #d1fae5, #a7f3d0); 
            color: #065f46; 
            border-left: 4px solid #10b981;
        }
        .status.error { 
            background: linear-gradient(45deg, #fee2e2, #fecaca); 
            color: #991b1b; 
            border-left: 4px solid #ef4444;
        }
        .status.loading { 
            background: linear-gradient(45deg, #dbeafe, #bfdbfe); 
            color: #1e40af; 
            border-left: 4px solid #3b82f6;
        }
        .file-input { 
            margin: 10px 0; 
            padding: 10px; 
            border: 2px dashed #3b82f6; 
            border-radius: 8px;
            background: rgba(59, 130, 246, 0.1);
        }
        .grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
            gap: 20px; 
            margin: 20px 0;
        }
        .card { 
            background: rgba(255, 255, 255, 0.8); 
            padding: 20px; 
            border-radius: 10px; 
            border: 1px solid rgba(59, 130, 246, 0.2);
        }
        .spinner { 
            border: 2px solid #f3f3f3; 
            border-top: 2px solid #3b82f6; 
            border-radius: 50%; 
            width: 20px; 
            height: 20px; 
            animation: spin 1s linear infinite; 
            display: inline-block;
            margin-right: 10px;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ GovRFP AI</h1>
            <p>Defense Contracting Platform - Secure Government Contract Analysis & Management</p>
        </div>
        
        <div class="main-content">
            <div class="section">
                <h2>System Status</h2>
                <div id="status" class="status loading">
                    <div class="spinner"></div>Checking system status...
                </div>
            </div>
            
            <div class="grid">
                <div class="card">
                    <h2>🔍 RFP Analysis</h2>
                    <p>Advanced AI-powered analysis of government RFPs and contracts.</p>
                    <button class="btn" onclick="testAnalysis()">Test Analysis Engine</button>
                </div>
                
                <div class="card">
                    <h2>📁 Document Upload</h2>
                    <p>Secure document processing and analysis.</p>
                    <div class="file-input">
                        <input type="file" id="fileInput" accept=".pdf,.doc,.docx,.txt">
                    </div>
                    <button class="btn" onclick="uploadFile()">Upload Document</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Check system health on page load
        window.addEventListener('load', function() {
            fetch('/health')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('status').innerHTML = 
                        `<div class="status success">✅ System Online - ${data.service}</div>`;
                })
                .catch(error => {
                    document.getElementById('status').innerHTML = 
                        `<div class="status error">❌ System Error: ${error.message}</div>`;
                });
        });

        function testAnalysis() {
            const btn = event.target;
            btn.disabled = true;
            btn.innerHTML = '<div class="spinner"></div>Analyzing...';
            
            fetch('/api/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    test: 'data',
                    rfp_type: 'defense_contract',
                    timestamp: new Date().toISOString()
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    alert('✅ Analysis Status: ' + data.status + '\n\nAnalysis: ' + data.analysis);
                } else {
                    alert('❌ Analysis failed: ' + data.message);
                }
            })
            .catch(error => {
                alert('❌ Error: ' + error.message);
            })
            .finally(() => {
                btn.disabled = false;
                btn.innerHTML = 'Test Analysis Engine';
            });
        }

        function uploadFile() {
            const fileInput = document.getElementById('fileInput');
            const file = fileInput.files[0];
            
            if (!file) {
                alert('Please select a file first');
                return;
            }

            const btn = event.target;
            btn.disabled = true;
            btn.innerHTML = '<div class="spinner"></div>Uploading...';

            const formData = new FormData();
            formData.append('file', file);

            fetch('/api/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    alert('✅ File uploaded successfully: ' + data.filename);
                    fileInput.value = ''; // Clear input
                } else {
                    alert('❌ Upload failed: ' + data.message);
                }
            })
            .catch(error => {
                alert('❌ Upload error: ' + error.message);
            })
            .finally(() => {
                btn.disabled = false;
                btn.innerHTML = 'Upload Document';
            });
        }
    </script>
</body>
</html>
EOF

# Create environment file with better security
echo "Creating environment file..."
cat > .env << 'EOF'
# Flask Configuration
FLASK_APP=app.py
FLASK_DEBUG=False
SECRET_KEY=your-secret-key-here-generate-a-secure-one

# Database
DATABASE_URL=sqlite:///govrfp.db

# Server
PORT=5000
HOST=0.0.0.0

# Security
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=uploads

# Logging
LOG_LEVEL=INFO
EOF

# Generate secure secret key
echo "Generating secure secret key..."
RANDOM_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
sed -i "s/your-secret-key-here-generate-a-secure-one/$RANDOM_KEY/" .env

# Create improved startup scripts
echo "Creating startup scripts..."
cat > run.sh << 'EOF'
#!/bin/bash
set -e

echo "Starting GovRFP AI in development mode..."

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "Virtual environment not found. Run setup script first."
    exit 1
fi

# Load environment variables
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "Environment file not found."
    exit 1
fi

# Set debug mode for development
export FLASK_DEBUG=True

# Create necessary directories
mkdir -p logs uploads

# Run the application
echo "Starting server at http://localhost:${PORT:-5000}"
python3 app.py
EOF

cat > run_production.sh << 'EOF'
#!/bin/bash
set -e

echo "Starting GovRFP AI in production mode..."

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "Virtual environment not found. Run setup script first."
    exit 1
fi

# Load environment variables
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "Environment file not found."
    exit 1
fi

# Ensure production settings
export FLASK_DEBUG=False

# Create necessary directories
mkdir -p logs uploads

# Run with Gunicorn
echo "Starting production server with Gunicorn..."
gunicorn -w 4 -b ${HOST:-0.0.0.0}:${PORT:-5000} --timeout 120 --keep-alive 2 --max-requests 1000 --preload app:app
EOF

# Make scripts executable
chmod +x run.sh
chmod +x run_production.sh

# Create a test script
cat > test_app.sh << 'EOF'
#!/bin/bash
echo "Testing GovRFP AI endpoints..."

# Test health endpoint
echo "Testing health endpoint..."
curl -s http://localhost:5000/health | python3 -m json.tool

echo -e "\n\nTesting analyze endpoint..."
curl -s -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"test": "data", "rfp_type": "defense_contract"}' | python3 -m json.tool

echo -e "\n\nDone!"
EOF

chmod +x test_app.sh

# Create Docker support
cat > Dockerfile << 'EOF'
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs uploads

# Expose port
EXPOSE 5000

# Run the application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
EOF

cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  govrfp-ai:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_DEBUG=False
    volumes:
      - ./logs:/app/logs
      - ./uploads:/app/uploads
    restart: unless-stopped
EOF

# Create systemd service file
cat > govrfp.service << 'EOF'
[Unit]
Description=GovRFP AI Defense Contracting Platform
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/govrfp
Environment=PATH=/opt/govrfp/venv/bin
EnvironmentFile=/opt/govrfp/.env
ExecStart=/opt/govrfp/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=govrfp

[Install]
WantedBy=multi-user.target
EOF

# Create log rotation config
cat > logrotate.conf << 'EOF'
logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
}
EOF

# Create a simple health check script
cat > health_check.py << 'EOF'
#!/usr/bin/env python3
import requests
import sys
import json

def check_health():
    try:
        response = requests.get('http://localhost:5000/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Service is healthy: {data['service']}")
            return True
        else:
            print(f"❌ Service returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: {e}")
        return False

if __name__ == "__main__":
    if check_health():
        sys.exit(0)
    else:
        sys.exit(1)
EOF

chmod +x health_check.py

echo "✅ Setup complete!"
echo ""
echo "🚀 To start the application:"
echo "   Development:  ./run.sh"
echo "   Production:   ./run_production.sh"
echo "   Docker:       docker-compose up -d"
echo ""
echo "🔗 Access URLs:"
echo "   Main App:     http://localhost:5000"
echo "   Health Check: http://localhost:5000/health"
echo ""
echo "🧪 Testing:"
echo "   Run tests:    ./test_app.sh"
echo "   Health check: python3 health_check.py"
echo ""
echo "📋 Key fixes applied:"
echo "   ✅ Removed blueprint conflicts"
echo "   ✅ Fixed endpoint routing issues"
echo "   ✅ Added proper error handling"
echo "   ✅ Improved security measures"
echo "   ✅ Enhanced UI/UX"
echo "   ✅ Added Docker support"
echo "   ✅ Created health monitoring"
echo ""
echo "⚠️  Security reminders:"
echo "   - Update SECRET_KEY in .env for production"
echo "   - Enable HTTPS for production deployment"
echo "   - Configure proper authentication"
echo "   - Set up database backups"
echo "   - Enable audit logging"
echo "   - Review file upload restrictions"
