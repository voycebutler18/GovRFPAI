from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime, timedelta
from functools import wraps
from openai import OpenAI
import secrets
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import openai

# Initialize OpenAI client
client = None
try:
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    if openai_api_key:
        client = OpenAI(api_key=openai_api_key)
        print("OpenAI client initialized successfully")
    else:
        print("Warning: OPENAI_API_KEY environment variable not set")
except Exception as e:
    print(f"Failed to initialize OpenAI client: {e}")

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)

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

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required', 'redirect': '/login'}), 401
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

# ===== MAIN ROUTES =====
@app.route('/')
def home():
    """Landing page - home.html"""
    return render_template('home.html')

@app.route('/signup')
def signup_page():
    """Signup page"""
    return render_template('signup.html')

@app.route('/login')
def login_page():
    """Email authentication page"""
    return render_template('login.html')

@app.route('/app')
def main_app():
    """Main RFP application"""
    return render_template('index.html')

# ===== AUTHENTICATION ROUTES =====
@app.route('/api/auth/verify', methods=['POST'])
def verify_session():
    """Verify frontend authentication and create Flask session"""
    try:
        data = request.json
        email = data.get('email')
        name = data.get('name', 'Unknown User')
        auth_method = data.get('authMethod', 'unknown')
        role = data.get('role', 'User')
        
        if not email:
            return jsonify({'error': 'Email required'}), 400
        
        # Create user session for Flask
        user_id = str(uuid.uuid4())
        user_data = {
            'id': user_id,
            'name': name,
            'email': email,
            'role': role,
            'clearance': 'Demo' if auth_method == 'demo' else 'Secret',
            'auth_method': auth_method
        }
        
        users[user_id] = user_data
        session['user_id'] = user_id
        session.permanent = True
        
        log_audit_event(user_id, 'SESSION_CREATED', f'Session created for {email}')
        
        return jsonify({
            'success': True,
            'user': user_data,
            'message': 'Session verified'
        })
        
    except Exception as e:
        print(f"Session verification error: {e}")
        return jsonify({'error': 'Session verification failed'}), 500

@app.route('/api/auth/status', methods=['GET'])
def check_auth_status():
    """Check if user is authenticated"""
    if 'user_id' in session and session['user_id'] in users:
        user_data = users[session['user_id']]
        return jsonify({
            'authenticated': True,
            'user': user_data
        })
    else:
        return jsonify({
            'authenticated': False
        })

@app.route('/api/auth/cac', methods=['POST'])
def authenticate_cac():
    """Simulate CAC authentication"""
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

# ===== RFP GENERATION ROUTES =====
@app.route('/api/rfp/generate', methods=['POST'])
@login_required
def generate_rfp():
    """API endpoint to generate an RFP document using OpenAI API"""
    print("=== RFP Generation Endpoint Called ===")
    
    if not client:
        print("ERROR: OpenAI client not configured")
        return jsonify({'error': 'OpenAI client is not configured. Please check your API key environment variable.'}), 500

    try:
        data = request.json
        print(f"Received data: {data}")
        user_id = session['user_id']
        print(f"User ID: {user_id}")

        required_fields = ['project_title', 'mission_objective', 'acquisition_type', 'security_level']
        if not all(field in data for field in required_fields):
            missing_fields = [field for field in required_fields if field not in data]
            print(f"Missing fields: {missing_fields}")
            return jsonify({'error': f'Missing required fields: {missing_fields}'}), 400

        print("=== Calling OpenAI generation function ===")
        generated_content = generate_rfp_content_with_openai(data)
        print("=== OpenAI generation completed ===")

        rfp_id = str(uuid.uuid4())
        rfp_document = {
            'id': rfp_id,
            'number': f"RFP-{datetime.now().year}-{len(rfp_documents) + 1:03d}",
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
            'content': generated_content
        }
        rfp_documents[rfp_id] = rfp_document
        
        log_audit_event(user_id, 'RFP_GENERATED', f'Generated RFP: {data["project_title"]}')
        
        print(f"=== RFP Created Successfully - ID: {rfp_id} ===")
        
        return jsonify({
            'success': True,
            'rfp_id': rfp_id,
            'rfp_number': rfp_document['number'],
            'content': rfp_document['content'],
            'message': 'RFP generated successfully using OpenAI'
        })
        
    except Exception as e:
        print(f"=== GENERAL ERROR in generate_rfp ===: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

def generate_rfp_content_with_openai(data):
    """Generate comprehensive RFP content using OpenAI API"""
    print(f"=== OpenAI Generation Started ===")
    print(f"Input data: {data}")
    
    if not client:
        error_msg = "OpenAI client is not initialized"
        print(f"ERROR: {error_msg}")
        return f"<h3>Error: {error_msg}</h3><p>Please check your API key configuration.</p>"
    
    acq_type_name = ACQUISITION_TYPES.get(data['acquisition_type'], 'Standard Contract')
    security_name = SECURITY_LEVELS.get(data['security_level'], 'Standard')
    
    compliance_text = "None specified."
    if data.get('compliance_requirements'):
        items = [COMPLIANCE_STANDARDS.get(req, req) for req in data['compliance_requirements']]
        compliance_text = "\n".join([f"- {item}" for item in items])

    # Enhanced prompt for complete, detailed RFP
    prompt = f"""
    You are a senior Department of Defense contracting officer. Generate a COMPLETE, comprehensive Request for Proposal (RFP) document that meets DoD standards. This must be a full, detailed document - not a summary.

    PROJECT DETAILS:
    - Title: {data['project_title']}
    - Acquisition: {acq_type_name}
    - Classification: {security_name}
    - Objective: {data['mission_objective']}
    - Compliance: {compliance_text}

    Generate a COMPLETE RFP with ALL sections fully detailed. Each section must be comprehensive and professional:

    1. INTRODUCTION (2-3 paragraphs)
    - Background and purpose
    - Acquisition authority and justification
    - Program overview and strategic importance

    2. SCOPE OF WORK (4-5 paragraphs)
    - Detailed requirements breakdown
    - Performance objectives and metrics
    - Deliverables and milestones
    - Technical specifications

    3. TECHNICAL REQUIREMENTS (5-6 paragraphs)
    - Detailed technical specifications
    - Performance standards and benchmarks
    - Integration requirements
    - Testing and validation criteria
    - Quality assurance standards

    4. SECURITY REQUIREMENTS (3-4 paragraphs)
    - Security clearance requirements
    - Compliance framework details
    - Data protection and handling
    - Facility security requirements

    5. EVALUATION CRITERIA (4-5 paragraphs)
    - Technical approach evaluation (40%)
    - Past performance assessment (25%)
    - Management approach (20%)
    - Cost evaluation (15%)
    - Detailed scoring methodology

    6. SUBMISSION REQUIREMENTS (3-4 paragraphs)
    - Proposal format and structure
    - Required documentation
    - Submission process and deadlines
    - Mandatory proposal elements

    7. CONTRACT INFORMATION (3-4 paragraphs)
    - Contract type and structure
    - Period of performance
    - Payment terms and schedule
    - Key contract clauses

    8. INSTRUCTIONS TO OFFERORS (3-4 paragraphs)
    - Pre-proposal conference details
    - Question and answer process
    - Proposal preparation guidelines
    - Contact information

    9. STATEMENT OF WORK DETAILS (4-5 paragraphs)
    - Phase-by-phase work breakdown
    - Specific tasks and subtasks
    - Government-furnished equipment/information
    - Contractor responsibilities

    10. TERMS AND CONDITIONS (3-4 paragraphs)
    - Standard FAR clauses
    - DFARS provisions
    - Special contract requirements
    - Intellectual property considerations

    IMPORTANT: Generate the COMPLETE document with ALL sections fully written out. Do not use placeholders or summaries. Each section must be detailed and comprehensive. Format as clean HTML using <h3> for section headers and <p> for paragraphs. Use <ul><li> for lists. Make this a complete 3000+ word professional RFP document.
    """

    try:
        print("=== Calling OpenAI API for Complete RFP ===")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a senior DoD contracting officer who generates comprehensive, complete RFP documents. Always provide full, detailed content - never summaries or placeholders."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4000,  # Increased token limit for longer content
            temperature=0.3   # Lower temperature for more consistent, professional output
        )
        print("=== OpenAI API Call Successful ===")
        result = response.choices[0].message.content
        print(f"Generated content length: {len(result)} characters")
        return result
    except Exception as e:
        error_msg = f"OpenAI API Call Failed: {str(e)}"
        print(f"=== ERROR ===: {error_msg}")
        return f"<h3>Error: AI Content Generation Failed</h3><p>The connection to the OpenAI service failed. Please check the server logs for details.</p><p><strong>Error Details:</strong> {e}</p>"
                {"role": "system", "content": "You are a professional DoD contracting officer assistant that generates comprehensive RFP documents."},
                {"role": "user", "content": prompt}
            ]
        )
        print("=== OpenAI API Call Successful ===")
        result = response.choices[0].message.content
        print(f"Generated content length: {len(result)} characters")
        return result
    except Exception as e:
        error_msg = f"OpenAI API Call Failed: {str(e)}"
        print(f"=== ERROR ===: {error_msg}")
        return f"<h3>Error: AI Content Generation Failed</h3><p>The connection to the OpenAI service failed. Please check the server logs for details.</p><p><strong>Error Details:</strong> {e}</p>"

# ===== TEMPLATE ROUTES =====
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

# ===== OTHER API ROUTES =====
@app.route('/api/rfp/<rfp_id>', methods=['GET'])
@login_required
def get_rfp(rfp_id):
    """Get RFP document by ID"""
    rfp = rfp_documents.get(rfp_id)
    if not rfp:
        return jsonify({'error': 'RFP not found'}), 404
    
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
    
    if user_id not in chat_history:
        chat_history[user_id] = []
    
    chat_history[user_id].append({
        'type': 'user',
        'message': message,
        'timestamp': datetime.now().isoformat()
    })
    
    ai_response = generate_ai_response(message)
    
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
    
    for keyword, response in responses.items():
        if keyword in message_lower:
            return response
    
    return 'I can help with FAR regulations, security requirements, evaluation criteria, contract types, and more. What specific aspect of RFP development would you like to discuss?'

@app.route('/api/compliance/check', methods=['POST'])
@login_required
def check_compliance():
    """Check RFP compliance with regulations"""
    data = request.json
    rfp_id = data.get('rfp_id')
    
    if not rfp_id or rfp_id not in rfp_documents:
        return jsonify({'error': 'RFP not found'}), 404
    
    compliance_results = {
        'far_compliance': True,
        'security_clauses': True,
        'evaluation_criteria': True,
        'cmmc_requirements': False,
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
    user_logs.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return jsonify({'audit_logs': user_logs})

@app.route('/api/dashboard', methods=['GET'])
@login_required
def get_dashboard_data():
    """Get dashboard data for current user"""
    user_id = session['user_id']
    user_rfps = [rfp for rfp in rfp_documents.values() if rfp['created_by'] == user_id]
    recent_logs = [log for log in audit_logs if log['user_id'] == user_id][-5:]
    
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
        'recent_rfps': user_rfps[-5:]
    })

# ===== ERROR HANDLERS =====
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    initialize_templates()
    
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    app.run(host='0.0.0.0', port=port, debug=debug)
