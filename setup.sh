#!/bin/bash
# GovRFP AI Setup Script - Fixed Version
echo "Setting up GovRFP AI Defense Contracting Platform..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
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

# Create requirements.txt if it doesn't exist
if [ ! -f "requirements.txt" ]; then
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
fi

# Install requirements
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create improved Flask app structure
echo "Setting up Flask application..."
cat > app.py << 'EOF'
#!/usr/bin/env python3
import os
import sys
from flask import Flask
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler

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
    
    # Import and register routes
    from routes import main_bp
    app.register_blueprint(main_bp)
    
    return app

# Create the app instance
app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
EOF

# Create routes module
echo "Creating routes module..."
cat > routes.py << 'EOF'
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
import os
import logging

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Main dashboard route"""
    return render_template('index.html')

@main_bp.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'GovRFP AI'})

@main_bp.route('/api/analyze', methods=['POST'])
def analyze_rfp():
    """RFP analysis endpoint"""
    try:
        data = request.get_json()
        # Add your RFP analysis logic here
        return jsonify({
            'status': 'success',
            'analysis': 'RFP analysis would go here',
            'recommendations': []
        })
    except Exception as e:
        logging.error(f"Error in RFP analysis: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Analysis failed'}), 500

@main_bp.route('/upload', methods=['POST'])
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
            filepath = os.path.join('uploads', filename)
            file.save(filepath)
            return jsonify({'status': 'success', 'filename': filename})
    
    except Exception as e:
        logging.error(f"Upload error: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Upload failed'}), 500

def secure_filename(filename):
    """Secure filename helper"""
    import re
    filename = re.sub(r'[^a-zA-Z0-9._-]', '', filename)
    return filename[:100]  # Limit length
EOF

# Create basic HTML template
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
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background: #1e3a8a; color: white; padding: 20px; text-align: center; }
        .main-content { background: white; margin: 20px 0; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .btn { background: #3b82f6; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        .btn:hover { background: #2563eb; }
        .status { margin: 20px 0; padding: 15px; border-radius: 5px; }
        .status.success { background: #d1fae5; color: #065f46; }
        .status.error { background: #fee2e2; color: #991b1b; }
    </style>
</head>
<body>
    <div class="header">
        <h1>GovRFP AI Defense Contracting Platform</h1>
        <p>Secure Government Contract Analysis & Management</p>
    </div>
    
    <div class="container">
        <div class="main-content">
            <h2>System Status</h2>
            <div id="status" class="status">Checking system status...</div>
            
            <h2>RFP Analysis</h2>
            <button class="btn" onclick="testAnalysis()">Test RFP Analysis</button>
            
            <h2>File Upload</h2>
            <input type="file" id="fileInput" accept=".pdf,.doc,.docx">
            <button class="btn" onclick="uploadFile()">Upload Document</button>
        </div>
    </div>

    <script>
        // Check system health
        fetch('/api/health')
            .then(response => response.json())
            .then(data => {
                document.getElementById('status').innerHTML = 
                    `<div class="status success">✓ System Online - ${data.service}</div>`;
            })
            .catch(error => {
                document.getElementById('status').innerHTML = 
                    `<div class="status error">✗ System Error: ${error.message}</div>`;
            });

        function testAnalysis() {
            fetch('/api/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ test: 'data' })
            })
            .then(response => response.json())
            .then(data => alert('Analysis Status: ' + data.status))
            .catch(error => alert('Error: ' + error.message));
        }

        function uploadFile() {
            const fileInput = document.getElementById('fileInput');
            const file = fileInput.files[0];
            if (!file) {
                alert('Please select a file');
                return;
            }

            const formData = new FormData();
            formData.append('file', file);

            fetch('/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    alert('File uploaded successfully: ' + data.filename);
                } else {
                    alert('Upload failed: ' + data.message);
                }
            })
            .catch(error => alert('Upload error: ' + error.message));
        }
    </script>
</body>
</html>
EOF

# Create environment file
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

# Create startup scripts
echo "Creating startup scripts..."
cat > run.sh << 'EOF'
#!/bin/bash
set -e

# Activate virtual environment
source venv/bin/activate

# Load environment variables
export $(cat .env | xargs)

# Run the application
python3 app.py
EOF

cat > run_production.sh << 'EOF'
#!/bin/bash
set -e

# Activate virtual environment
source venv/bin/activate

# Load environment variables
export $(cat .env | xargs)
export FLASK_DEBUG=False

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 --keep-alive 2 app:app
EOF

# Make scripts executable
chmod +x run.sh
chmod +x run_production.sh

# Create systemd service file
cat > govrfp.service << 'EOF'
[Unit]
Description=GovRFP AI Defense Contracting Platform
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/your/govrfp
Environment=PATH=/path/to/your/govrfp/venv/bin
EnvironmentFile=/path/to/your/govrfp/.env
ExecStart=/path/to/your/govrfp/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app
Restart=always
RestartSec=10
StandardOutput=syslog
StandardError=syslog
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

echo "✓ Setup complete!"
echo ""
echo "To start the application:"
echo "1. ./run.sh                    (Development mode)"
echo "2. ./run_production.sh         (Production mode)"
echo ""
echo "The application will be available at: http://localhost:5000"
echo ""
echo "Troubleshooting tips:"
echo "- Check logs in logs/app.log"
echo "- Verify virtual environment: source venv/bin/activate"
echo "- Test with: curl http://localhost:5000/api/health"
echo "- For permission issues: chmod +x run.sh"
echo ""
echo "Security reminders:"
echo "- Update SECRET_KEY in .env for production"
echo "- Enable HTTPS for production deployment"
echo "- Configure proper authentication"
echo "- Set up database backups"
echo "- Enable audit logging"
