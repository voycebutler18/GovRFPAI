from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime, timedelta
import secrets
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)  # Generate a secure secret key
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)  # Session timeout

# In-memory storage (replace with database in production)
users = {}
rfp_documents = {}
templates = {}
audit_logs = []
chat_history = {}

# Security levels and compliance standards
SECURITY_LEVELS = {
    'cui': 'CUI (Controlled Unclassified Information)',
    'confidential': 'Confidential',
    'secret': 'Secret',
    'topsecret': 'Top Secret'
}

ACQUISITION_TYPES = {
    'far': 'FAR-Based Contract',
    'ota': 'Other Transaction Authority',
    'cso': 'Commercial Solutions Opening',
    'sbir': 'Small Business Innovation Research'
}

COMPLIANCE_STANDARDS = {
    'nist800171': 'NIST 800-171 (CUI Protection)',
    'cmmc': 'CMMC (Cybersecurity Maturity Model)',
    'fisma': 'FISMA (Federal Information Security)',
    'dfars': 'DFARS (Defense Federal Acquisition)'
}

# Initialize default templates
def initialize_templates():
    """Initialize default RFP templates"""
    default_templates = {
        'cyber': {
            'name': 'Advanced Cybersecurity Platform',
            'title': 'Advanced Cybersecurity Platform',
            'objective': 'Develop and implement a comprehensive cybersecurity platform capable of real-time threat detection, automated incident response, and continuous security monitoring for critical DoD networks. The solution must integrate with existing security infrastructure and provide scalable protection against emerging cyber threats.',
            'acquisition_type': 'far',
            'security_level': 'secret',
            'contract_value': 'major',
            'compliance': ['nist800171', 'cmmc', 'fisma', 'dfars']
        },
        'medical': {
            'name': 'Medical Device Development Platform',
            'title': 'Medical Device Development Platform',
            'objective': 'Design and develop innovative medical devices for military healthcare applications, including portable diagnostic equipment, telemedicine solutions, and battlefield medical support systems. The platform must meet FDA regulatory requirements and military specifications.',
            'acquisition_type': 'ota',
            'security_level': 'cui',
            'contract_value': 'simplified',
            'compliance': ['nist800171', 'fisma']
        },
        'aerospace': {
            'name': 'Next-Generation Aerospace System',
            'title': 'Next-Generation Aerospace System',
            'objective': 'Research, develop, and prototype advanced aerospace technologies including propulsion systems, avionics, and flight control systems. The solution must demonstrate improved performance, reliability, and maintainability over existing systems.',
            'acquisition_type': 'ota',
            'security_level': 'secret',
            'contract_value': 'major',
            'compliance': ['nist800171', 'cmmc', 'fisma', 'dfars']
        },
        'research': {
            'name': 'Advanced Research and Development Initiative',
            'title': 'Advanced Research and Development Initiative',
            'objective': 'Conduct cutting-edge research in emerging technologies with potential military applications. Focus areas include artificial intelligence, quantum computing, advanced materials, and biotechnology. Deliverables include research reports, prototypes, and technology demonstrations.',
            'acquisition_type': 'sbir',
            'security_level': 'cui',
            'contract_value': 'small',
            'compliance': ['nist800171', 'fisma']
        }
    }
    
    for template_id, template_data in default_templates.items():
        templates[template_id] = template_data

# Authentication decorator
def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def log_audit_event(user_id, action, details):
    """Log audit events for compliance tracking"""
    audit_logs.append({
        'timestamp': datetime.now().isoformat(),
        'user_id': user_id,
        'action': action,
        'details': details,
        'ip_address': request.remote_addr
    })

@app.route('/')
def index():
    """Main application route"""
    return render_template('index.html')

@app.route('/api/auth/cac', methods=['POST'])
def authenticate_cac():
    """Simulate CAC authentication"""
    # In production, this would integrate with actual CAC/PIV systems
    user_id = str(uuid.uuid4())
    user_data = {
        'id': user_id,
        'name': 'John Smith',
        'email': 'john.smith@defense.gov',
        'role': 'Contracting Officer',
        'clearance': 'Secret',
        'auth_method': 'CAC'
    }
    
    users[user_id] = user_data
    session['user_id'] = user_id
    session.permanent = True
    
    log_audit_event(user_id, 'CAC_AUTH', 'User authenticated via CAC')
    
    return jsonify({
        'success': True,
        'user': user_data,
        'message': 'Successfully authenticated via CAC'
    })

@app.route('/api/auth/email', methods=['POST'])
def authenticate_email():
    """Simulate secure email authentication"""
    user_id = str(uuid.uuid4())
    user_data = {
        'id': user_id,
        'name': 'Jane Doe',
        'email': 'jane.doe@army.mil',
        'role': 'Contracting Specialist',
        'clearance': 'Confidential',
        'auth_method': 'Email'
    }
    
    users[user_id] = user_data
    session['user_id'] = user_id
    session.permanent = True
    
    log_audit_event(user_id, 'EMAIL_AUTH', 'User authenticated via secure email')
    
    return jsonify({
        'success': True,
        'user': user_data,
        'message': 'Successfully authenticated via secure email'
    })

@app.route('/api/auth/demo', methods=['POST'])
def authenticate_demo():
    """Demo authentication for development"""
    user_id = str(uuid.uuid4())
    user_data = {
        'id': user_id,
        'name': 'Demo User',
        'email': 'demo@defense.gov',
        'role': 'Contracting Officer',
        'clearance': 'Demo',
        'auth_method': 'Demo'
    }
    
    users[user_id] = user_data
    session['user_id'] = user_id
    session.permanent = True
    
    log_audit_event(user_id, 'DEMO_AUTH', 'Demo mode activated')
    
    return jsonify({
        'success': True,
        'user': user_data,
        'message': 'Demo mode activated'
    })

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout user and clear session"""
    if 'user_id' in session:
        log_audit_event(session['user_id'], 'LOGOUT', 'User logged out')
        session.clear()
    
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@app.route('/api/rfp/generate', methods=['POST'])
@login_required
def generate_rfp():
    """Generate RFP using AI simulation"""
    data = request.json
    user_id = session['user_id']
    
    # Validate required fields
    required_fields = ['project_title', 'mission_objective', 'acquisition_type', 'security_level']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Generate RFP document
    rfp_id = str(uuid.uuid4())
    rfp_number = f"RFP-{datetime.now().year}-{len(rfp_documents) + 1:03d}"
    
    rfp_document = {
        'id': rfp_id,
        'number': rfp_number,
        'title': data['project_title'],
        'objective': data['mission_objective'],
        'acquisition_type': data['acquisition_type'],
        'security_level': data['security_level'],
        'contract_value': data.get('contract_value', 'simplified'),
        'compliance_requirements': data.get('compliance_requirements', []),
        'status': 'draft',
        'created_by': user_id,
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
        'content': generate_rfp_content(data)
    }
    
    rfp_documents[rfp_id] = rfp_document
    
    log_audit_event(user_id, 'RFP_GENERATED', f'RFP generated: {data["project_title"]}')
    
    return jsonify({
        'success': True,
        'rfp_id': rfp_id,
        'rfp_number': rfp_number,
        'content': rfp_document['content'],
        'message': 'RFP generated successfully'
    })

def generate_rfp_content(data):
    """Generate RFP content based on input data"""
    acq_type_name = ACQUISITION_TYPES.get(data['acquisition_type'], 'Standard Contract')
    security_name = SECURITY_LEVELS.get(data['security_level'], 'Standard')
    
    # Generate compliance requirements text
    compliance_text = ""
    if data.get('compliance_requirements'):
        compliance_items = [COMPLIANCE_STANDARDS.get(req, req) for req in data['compliance_requirements']]
        compliance_text = "\n".join([f"<li>{item}</li>" for item in compliance_items])
    
    content = f"""
    <div class="rfp-section">
        <h3>1. INTRODUCTION</h3>
        <p>The Department of Defense hereby solicits proposals for {data['project_title']}. This acquisition will be conducted under {acq_type_name} authority with {security_name} security classification requirements.</p>
    </div>
    
    <div class="rfp-section">
        <h3>2. SCOPE OF WORK</h3>
        <p>{data['mission_objective']}</p>
        <p>The contractor shall provide all necessary personnel, equipment, facilities, and services to accomplish the stated objectives in compliance with all applicable federal regulations and security requirements.</p>
    </div>
    
    <div class="rfp-section">
        <h3>3. TECHNICAL REQUIREMENTS</h3>
        <p>All deliverables must meet the following technical specifications:</p>
        <ul style="margin-left: 20px;">
            <li>Compliance with relevant DoD and federal standards</li>
            <li>Integration with existing government systems</li>
            <li>Scalability for future requirements</li>
            <li>Comprehensive documentation and training materials</li>
        </ul>
    </div>
    
    <div class="rfp-section">
        <h3>4. SECURITY REQUIREMENTS</h3>
        <p>This contract requires {security_name} security clearance. The following security standards apply:</p>
        <ul style="margin-left: 20px;">
            {compliance_text}
        </ul>
    </div>
    
    <div class="rfp-section">
        <h3>5. EVALUATION CRITERIA</h3>
        <p>Proposals will be evaluated based on the following criteria:</p>
        <ul style="margin-left: 20px;">
            <li>Technical Approach (40%)</li>
            <li>Management Approach (25%)</li>
            <li>Past Performance (20%)</li>
            <li>Cost/Price (15%)</li>
        </ul>
    </div>
    
    <div class="rfp-section">
        <h3>6. SUBMISSION REQUIREMENTS</h3>
        <p>Proposals must be submitted electronically through the designated secure portal no later than [INSERT DATE]. Late submissions will not be considered.</p>
    </div>
    
    <div class="rfp-section">
        <h3>7. CONTRACT INFORMATION</h3>
        <p>Contract Type: {acq_type_name}<br>
        Estimated Value: {data.get('contract_value', 'TBD')}<br>
        Period of Performance: [INSERT PERIOD]<br>
        Place of Performance: [INSERT LOCATION]</p>
    </div>
    """
    
    return content

@app.route('/api/templates', methods=['GET'])
@login_required
def get_templates():
    """Get available RFP templates"""
    return jsonify({'templates': templates})

@app.route('/api/templates/<template_id>', methods=['GET'])
@login_required
def get_template(template_id):
    """Get specific template by ID"""
    template = templates.get(template_id)
    if not template:
        return jsonify({'error': 'Template not found'}), 404
    
    log_audit_event(session['user_id'], 'TEMPLATE_ACCESSED', f'Template accessed: {template_id}')
    
    return jsonify({'template': template})

@app.route('/api/templates', methods=['POST'])
@login_required
def save_template():
    """Save new template"""
    data = request.json
    user_id = session['user_id']
    
    template_id = str(uuid.uuid4())
    template_data = {
        'id': template_id,
        'name': data['name'],
        'title': data['title'],
        'objective': data['objective'],
        'acquisition_type': data['acquisition_type'],
        'security_level': data['security_level'],
        'contract_value': data.get('contract_value', 'simplified'),
        'compliance': data.get('compliance', []),
        'created_by': user_id,
        'created_at': datetime.now().isoformat()
    }
    
    templates[template_id] = template_data
    
    log_audit_event(user_id, 'TEMPLATE_SAVED', f'Template saved: {data["name"]}')
    
    return jsonify({
        'success': True,
        'template_id': template_id,
        'message': 'Template saved successfully'
    })

@app.route('/api/rfp/<rfp_id>', methods=['GET'])
@login_required
def get_rfp(rfp_id):
    """Get RFP document by ID"""
    rfp = rfp_documents.get(rfp_id)
    if not rfp:
        return jsonify({'error': 'RFP not found'}), 404
    
    # Check if user has access to this RFP
    if rfp['created_by'] != session['user_id']:
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify({'rfp': rfp})

@app.route('/api/rfp', methods=['GET'])
@login_required
def get_user_rfps():
    """Get all RFPs created by current user"""
    user_id = session['user_id']
    user_rfps = [rfp for rfp in rfp_documents.values() if rfp['created_by'] == user_id]
    
    return jsonify({'rfps': user_rfps})

@app.route('/api/chat', methods=['POST'])
@login_required
def chat_with_ai():
    """Handle chat messages with AI assistant"""
    data = request.json
    user_id = session['user_id']
    message = data.get('message', '').strip()
    
    if not message:
        return jsonify({'error': 'Message cannot be empty'}), 400
    
    # Initialize chat history for user if not exists
    if user_id not in chat_history:
        chat_history[user_id] = []
    
    # Add user message to history
    chat_history[user_id].append({
        'type': 'user',
        'message': message,
        'timestamp': datetime.now().isoformat()
    })
    
    # Generate AI response
    ai_response = generate_ai_response(message)
    
    # Add AI response to history
    chat_history[user_id].append({
        'type': 'ai',
        'message': ai_response,
        'timestamp': datetime.now().isoformat()
    })
    
    log_audit_event(user_id, 'CHAT_MESSAGE', f'User chat: {message[:50]}...')
    
    return jsonify({
        'success': True,
        'response': ai_response,
        'chat_history': chat_history[user_id]
    })

def generate_ai_response(message):
    """Generate AI response based on message content"""
    message_lower = message.lower()
    
    responses = {
        'far': 'The Federal Acquisition Regulation (FAR) governs most federal procurement. Key requirements include competitive bidding, evaluation criteria, and specific contract clauses. Would you like me to explain any specific FAR part?',
        'ota': 'Other Transaction Authority allows for more flexible contracting outside traditional FAR requirements. OTAs are great for research and development or prototype projects. They can include IP arrangements not possible under FAR.',
        'cmmc': 'CMMC (Cybersecurity Maturity Model Certification) is mandatory for DoD contractors handling CUI. There are five maturity levels, with most contracts requiring Level 3. Implementation includes 130+ security controls.',
        'nist': 'NIST 800-171 provides security requirements for protecting Controlled Unclassified Information (CUI) in non-federal systems. It includes 14 control families with 110 security requirements.',
        'security': 'Security requirements depend on classification level. CUI requires NIST 800-171, while classified contracts need additional controls. Always include appropriate security clauses in your RFP.',
        'evaluation': 'Evaluation criteria should be clearly defined and weighted. Common factors include technical approach, management approach, past performance, and cost. Make sure criteria align with your actual needs.',
        'dfars': 'DFARS (Defense Federal Acquisition Regulation Supplement) contains DoD-specific procurement requirements. Key areas include cybersecurity, supply chain security, and contractor business systems.',
        'fisma': 'FISMA requires federal agencies to develop, document, and implement information security programs. For contractors, this means implementing appropriate security controls and conducting regular assessments.'
    }
    
    # Check for keywords in message
    for keyword, response in responses.items():
        if keyword in message_lower:
            return response
    
    # Default response
    return 'I can help with FAR regulations, security requirements, evaluation criteria, contract types, and more. What specific aspect of RFP development would you like to discuss?'

@app.route('/api/compliance/check', methods=['POST'])
@login_required
def check_compliance():
    """Check RFP compliance with regulations"""
    data = request.json
    rfp_id = data.get('rfp_id')
    
    if not rfp_id or rfp_id not in rfp_documents:
        return jsonify({'error': 'RFP not found'}), 404
    
    rfp = rfp_documents[rfp_id]
    
    # Simulate compliance checking
    compliance_results = {
        'far_compliance': True,
        'security_clauses': True,
        'evaluation_criteria': True,
        'cmmc_requirements': False,  # Simulate a warning
        'overall_score': 85,
        'warnings': ['CMMC requirements need review'],
        'recommendations': [
            'Review CMMC certification requirements',
            'Ensure all security controls are properly documented',
            'Verify evaluation weights sum to 100%'
        ]
    }
    
    log_audit_event(session['user_id'], 'COMPLIANCE_CHECK', f'Compliance check for RFP: {rfp_id}')
    
    return jsonify({
        'success': True,
        'compliance_results': compliance_results
    })

@app.route('/api/audit', methods=['GET'])
@login_required
def get_audit_logs():
    """Get audit logs for current user"""
    user_id = session['user_id']
    user_logs = [log for log in audit_logs if log['user_id'] == user_id]
    
    # Sort by timestamp, most recent first
    user_logs.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return jsonify({'audit_logs': user_logs})

@app.route('/api/dashboard', methods=['GET'])
@login_required
def get_dashboard_data():
    """Get dashboard data for current user"""
    user_id = session['user_id']
    
    # Get user's RFPs
    user_rfps = [rfp for rfp in rfp_documents.values() if rfp['created_by'] == user_id]
    
    # Get recent activity
    recent_logs = [log for log in audit_logs if log['user_id'] == user_id][-5:]
    
    # Generate statistics
    stats = {
        'total_rfps': len(user_rfps),
        'draft_rfps': len([rfp for rfp in user_rfps if rfp['status'] == 'draft']),
        'approved_rfps': len([rfp for rfp in user_rfps if rfp['status'] == 'approved']),
        'templates_used': len(set([rfp.get('template_id') for rfp in user_rfps if rfp.get('template_id')])),
        'recent_activity': recent_logs
    }
    
    return jsonify({
        'success': True,
        'stats': stats,
        'recent_rfps': user_rfps[-5:]  # Last 5 RFPs
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Initialize templates on startup
    initialize_templates()
    
    # Run the application
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    app.run(host='0.0.0.0', port=port, debug=debug)
