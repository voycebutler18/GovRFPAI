#!/bin/bash
# GovRFP AI Setup Script
echo "Setting up GovRFP AI Defense Contracting Platform..."
# Create project directory structure
mkdir -p templates static/css static/js static/images
mkdir -p logs uploads
# Create virtual environment
echo "Creating virtual environment..."
python -m venv venv
# Activate virtual environment
source venv/bin/activate
# Install requirements
echo "Installing Python dependencies..."
pip install -r requirements.txt
# Create templates directory and move HTML file
echo "Setting up templates..."
mv paste.txt templates/index.html
# Create basic static files structure
echo "Creating static files structure..."
mkdir -p static/css
mkdir -p static/js
mkdir -p static/images
# Create a basic CSS file (optional - styles are inline in HTML)
touch static/css/styles.css
# Create a basic JavaScript file (optional - JS is inline in HTML)  
touch static/js/app.js
# Copy environment template
cp .env.template .env
# Generate a secure secret key
echo "Generating secure secret key..."
RANDOM_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
sed -i "s/your-secret-key-here-generate-a-secure-one/$RANDOM_KEY/" .env
# Create logs directory
mkdir -p logs
touch logs/app.log
touch logs/audit.log
# Create startup script
cat > run.sh << 'EOF'
#!/bin/bash
source venv/bin/activate
export FLASK_APP=app.py
export FLASK_ENV=development
python app.py
EOF
chmod +x run.sh
# Create production startup script
cat > run_production.sh << 'EOF'
#!/bin/bash
source venv/bin/activate
export FLASK_ENV=production
gunicorn -w 4 -b 0.0.0.0:5000 app:app
EOF
chmod +x run_production.sh
# Create systemd service file template
cat > govrfp.service << 'EOF'
[Unit]
Description=GovRFP AI Defense Contracting Platform
After=network.target
[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/your/govrfp
Environment=PATH=/path/to/your/govrfp/venv/bin
ExecStart=/path/to/your/govrfp/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app
Restart=always
RestartSec=10
[Install]
WantedBy=multi-user.target
EOF
echo "Setup complete!"
echo ""
echo "To start the application:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Set environment variables: export FLASK_APP=app.py"
echo "3. Run the application: python app.py"
echo "   OR use the startup script: ./run.sh"
echo ""
echo "For production deployment:"
echo "1. Update the .env file with production settings"
echo "2. Use: ./run_production.sh"
echo "3. Or install as a systemd service using govrfp.service"
echo ""
echo "The application will be available at: http://localhost:5000"
echo ""
echo "Default authentication options:"
echo "- CAC/PIV Authentication (simulated)"
echo "- Secure Email Domain (simulated)"  
echo "- Demo Mode (for development)"
echo ""
echo "Security Notes:"
echo "- Change the SECRET_KEY in .env for production"
echo "- Enable SSL/TLS for production deployment"
echo "- Configure proper authentication for production"
echo "- Set up database for persistent storage"
echo "- Enable audit logging for compliance"
