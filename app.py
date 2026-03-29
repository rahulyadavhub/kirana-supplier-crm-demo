#!/usr/bin/env python3
"""
Kirana Supplier CRM - Full Stack Backend (Flask + Developer Mode)
Features: CORS, Hot Reload, Logging, Debug Mode, Request Monitoring
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime, timedelta
import json
import os
import sqlite3
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='.', static_url_path='')

# Enable CORS for development (frontend on 8000, backend on 5000)
CORS(app, resources={r"/api/*": {"origins": "*"}})

DB_FILE = 'kirana.db'
DEV_MODE = True

# ==================== REQUEST/RESPONSE LOGGING ====================
@app.before_request
def log_request():
    """Log incoming requests"""
    if DEV_MODE:
        logger.info(f"📨 {request.method} {request.path}")
        if request.is_json:
            logger.debug(f"📤 Payload: {request.json}")

@app.after_request
def log_response(response):
    """Log outgoing responses"""
    if DEV_MODE:
        logger.info(f"✅ Response: {response.status_code}")
        if response.content_type == 'application/json':
            try:
                logger.debug(f"📥 Response data: {response.get_json()}")
            except:
                pass
    return response

# ==================== ERROR HANDLERS ====================
@app.errorhandler(404)
def not_found(error):
    logger.error(f"❌ 404 Not Found: {request.path}")
    return jsonify({'error': 'Endpoint not found', 'path': request.path}), 404

@app.errorhandler(500)
def server_error(error):
    logger.error(f"❌ 500 Server Error: {str(error)}")
    return jsonify({'error': 'Server error', 'details': str(error)}), 500

def init_db():
    """Initialize SQLite database with tables"""
    if os.path.exists(DB_FILE):
        logger.info(f"📁 Database {DB_FILE} already exists")
        return
    
    logger.info(f"🔧 Creating database {DB_FILE}...")
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Front desk requests table
    c.execute('''CREATE TABLE front_desk (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        issue TEXT NOT NULL,
        notes TEXT,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    logger.debug("✓ Created front_desk table")
    
    # Suppliers table
    c.execute('''CREATE TABLE suppliers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT,
        outstanding REAL DEFAULT 0,
        due_date TEXT,
        contact_phone TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    logger.debug("✓ Created suppliers table")
    
    # Payments table
    c.execute('''CREATE TABLE payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        supplier_id INTEGER,
        amount REAL NOT NULL,
        payment_method TEXT,
        reference TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(supplier_id) REFERENCES suppliers(id)
    )''')
    logger.debug("✓ Created payments table")
    
    # Insert sample suppliers
    suppliers = [
        ('Suman Traders', 'Snacks & Biscuits', 28500, '2026-04-01', '9876543210'),
        ('Rajesh & Sons', 'Milk & Dairy', 45200, '2026-04-06', '9876543211'),
        ('Delhi Spice Co.', 'Spices', 12800, '2026-04-15', '9876543212'),
        ('Kumar Wholesale', 'Oils & Ghee', 52000, '2026-03-30', '9876543213'),
        ('Priya Distributors', 'Drinks & Juices', 38000, '2026-04-08', '9876543214'),
    ]
    
    for name, desc, outstanding, due_date, phone in suppliers:
        c.execute('INSERT INTO suppliers (name, description, outstanding, due_date, contact_phone) VALUES (?, ?, ?, ?, ?)',
                  (name, desc, outstanding, due_date, phone))
        logger.debug(f"✓ Inserted supplier: {name}")
    
    conn.commit()
    conn.close()
    logger.info(f"✅ Database initialized with 5 sample suppliers")

# ===================== ROUTES =====================

@app.route('/')
def index():
    """Serve main HTML file"""
    logger.info("📄 Serving index.html")
    return send_from_directory('.', 'index.html')

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for dev monitoring"""
    return jsonify({'status': 'healthy', 'mode': 'development' if DEV_MODE else 'production', 'timestamp': datetime.now().isoformat()}), 200

# ==================== FRONT DESK API ====================

@app.route('/api/frontdesk', methods=['POST'])
def submit_frontdesk():
    """Handle front desk form submission"""
    try:
        data = request.json
        name = data.get('name', '').strip()
        phone = data.get('phone', '').strip()
        issue = data.get('issue', '').strip()
        notes = data.get('notes', '').strip()
        
        logger.info(f"📝 Front desk request from {name} ({phone}): {issue}")
        
        if not name or not phone or not issue:
            logger.warning("⚠️ Missing required fields in front desk request")
            return jsonify({'error': 'Name, Phone, and Issue are required'}), 400
        
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('INSERT INTO front_desk (name, phone, issue, notes) VALUES (?, ?, ?, ?)',
                  (name, phone, issue, notes))
        conn.commit()
        request_id = c.lastrowid
        conn.close()
        
        logger.info(f"✅ Front desk request saved (ID: {request_id})")
        return jsonify({'success': True, 'message': f'Front desk request #{request_id} submitted', 'id': request_id}), 201
    except Exception as e:
        logger.error(f"❌ Front desk error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/frontdesk/history', methods=['GET'])
def frontdesk_history():
    """Get front desk request history"""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('SELECT id, name, phone, issue, status, created_at FROM front_desk ORDER BY created_at DESC LIMIT 10')
        rows = c.fetchall()
        conn.close()
        
        history = [{'id': r[0], 'name': r[1], 'phone': r[2], 'issue': r[3], 'status': r[4], 'created_at': r[5]} for r in rows]
        logger.info(f"📋 Front desk history retrieved ({len(history)} entries)")
        return jsonify(history), 200
    except Exception as e:
        logger.error(f"❌ Front desk history error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ==================== AI BOT API ====================

@app.route('/api/bot', methods=['POST'])
def bot_reply():
    """Handle AI bot queries with smart responses from database"""
    try:
        data = request.json
        query = data.get('query', '').lower().strip()
        
        logger.info(f"🤖 Bot query: {query}")
        
        if not query:
            return jsonify({'reply': 'Kuch likho bhaiya!'}), 400
        
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        
        reply = None
        
        # Smart query matching
        if 'rajesh' in query:
            c.execute('SELECT outstanding, due_date FROM suppliers WHERE name LIKE ?', ('%Rajesh%',))
            row = c.fetchone()
            if row:
                reply = f"Rajesh & Sons ka udhaar ₹{row[0]} hai, due date {row[1]} hai."
            else:
                reply = "Rajesh & Sons ka info nahi mila."
        
        elif 'suman' in query:
            c.execute('SELECT outstanding, due_date FROM suppliers WHERE name LIKE ?', ('%Suman%',))
            row = c.fetchone()
            if row:
                reply = f"Suman Traders ka udhaar ₹{row[0]} hai, due date {row[1]} hai."
            else:
                reply = "Suman Traders ka info nahi mila."
        
        elif 'baki' in query or 'outstanding' in query or 'total' in query:
            c.execute('SELECT SUM(outstanding) FROM suppliers')
            total = c.fetchone()[0] or 0
            c.execute('SELECT COUNT(*) FROM suppliers')
            count = c.fetchone()[0]
            reply = f"Total {count} suppliers se baki ₹{total} hai. Sabko payment kro."
        
        elif 'payment' in query or 'bhugtan' in query:
            reply = "Payment karne ke liye 'Record Payment' button dabao. Supplier select karo, amount bharo, method select karo."
        
        elif 'supplier' in query:
            c.execute('SELECT name, outstanding FROM suppliers')
            rows = c.fetchall()
            if rows:
                supplier_list = ', '.join([f"{r[0]} (₹{r[1]})" for r in rows[:3]])
                reply = f"Top suppliers: {supplier_list}. Sab ka detail dashboard mein hai."
            else:
                reply = "Koi supplier nahi mila."
        
        elif 'due' in query or 'jaldi' in query or 'kab' in query or 'deadline' in query:
            c.execute('SELECT name, outstanding, due_date FROM suppliers ORDER BY due_date LIMIT 3')
            rows = c.fetchall()
            if rows:
                due_list = ', '.join([f"{r[0]} (₹{r[1]} due {r[2]})" for r in rows])
                reply = f"Dhyan se: jaldi due wale suppliers: {due_list}."
            else:
                reply = "Abhi sab clear hai, koi urgent due nahi." 

        elif 'kya' in query or 'kaise' in query or 'help' in query:
            reply = "Poocho simple: 'Rajesh ka bill kitna', 'Suman ka due kab', 'total baki kitna', 'payment record kaise kare'."

        else:
            reply = "Maaf karo bhaiya, samajhne me thoda dikkat hua. Seedha likho: 'rajesh due', 'total baki', 'kisne payment ki'."

        conn.close()

        logger.info(f"🤖 Bot reply: {reply}")
        return jsonify({'reply': reply}), 200
    
    except Exception as e:
        logger.error(f"❌ Bot error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ==================== SUPPLIER API ====================

@app.route('/api/suppliers', methods=['GET'])
def get_suppliers():
    """Get all suppliers with current outstanding"""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('SELECT id, name, description, outstanding, due_date, contact_phone FROM suppliers')
        rows = c.fetchall()
        conn.close()
        
        suppliers = [{'id': r[0], 'name': r[1], 'description': r[2], 'outstanding': r[3], 'due_date': r[4], 'phone': r[5]} for r in rows]
        logger.info(f"📦 Suppliers list retrieved ({len(suppliers)} suppliers)")
        return jsonify(suppliers), 200
    except Exception as e:
        logger.error(f"❌ Suppliers error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/suppliers/<int:supplier_id>', methods=['GET'])
def get_supplier(supplier_id):
    """Get single supplier details"""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('SELECT id, name, description, outstanding, due_date, contact_phone FROM suppliers WHERE id = ?', (supplier_id,))
        row = c.fetchone()
        
        if not row:
            conn.close()
            logger.warning(f"⚠️ Supplier {supplier_id} not found")
            return jsonify({'error': 'Supplier not found'}), 404
        
        supplier = {'id': row[0], 'name': row[1], 'description': row[2], 'outstanding': row[3], 'due_date': row[4], 'phone': row[5]}
        
        # Get payment history
        c.execute('SELECT amount, payment_method, reference, created_at FROM payments WHERE supplier_id = ? ORDER BY created_at DESC LIMIT 5', (supplier_id,))
        payments = [{'amount': p[0], 'method': p[1], 'ref': p[2], 'date': p[3]} for p in c.fetchall()]
        supplier['payments'] = payments
        
        conn.close()
        logger.info(f"📦 Supplier details retrieved: {supplier['name']}")
        return jsonify(supplier), 200
    except Exception as e:
        logger.error(f"❌ Supplier details error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ==================== PAYMENT API ====================

@app.route('/api/payments', methods=['POST'])
def record_payment():
    """Record a payment"""
    try:
        data = request.json
        supplier_id = data.get('supplier_id')
        amount = data.get('amount', 0)
        method = data.get('method', 'unknown')
        reference = data.get('reference', '')
        
        logger.info(f"💳 Payment record: Supplier {supplier_id}, Amount ₹{amount}, Method {method}")
        
        if not supplier_id or amount <= 0:
            logger.warning("⚠️ Invalid payment data")
            return jsonify({'error': 'Invalid supplier or amount'}), 400
        
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        
        # Record payment
        c.execute('INSERT INTO payments (supplier_id, amount, payment_method, reference) VALUES (?, ?, ?, ?)',
                  (supplier_id, amount, method, reference))
        
        # Update supplier outstanding
        c.execute('UPDATE suppliers SET outstanding = outstanding - ? WHERE id = ?', (amount, supplier_id))
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Payment recorded: ₹{amount}")
        return jsonify({'success': True, 'message': f'Payment of ₹{amount} recorded'}), 201
    except Exception as e:
        logger.error(f"❌ Payment error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ==================== DASHBOARD API ====================

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    """Get dashboard stats"""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        
        # Total suppliers
        c.execute('SELECT COUNT(*) FROM suppliers')
        total_suppliers = c.fetchone()[0]
        
        # Total outstanding
        c.execute('SELECT SUM(outstanding) FROM suppliers')
        total_outstanding = c.fetchone()[0] or 0
        
        # Due this week
        today = datetime.now()
        week_end = today + timedelta(days=7)
        c.execute('SELECT SUM(outstanding) FROM suppliers WHERE due_date BETWEEN ? AND ?',
                  (today.strftime('%Y-%m-%d'), week_end.strftime('%Y-%m-%d')))
        due_week = c.fetchone()[0] or 0
        
        # Total payments (count)
        c.execute('SELECT COUNT(*) FROM payments')
        total_payments = c.fetchone()[0]
        
        conn.close()
        
        stats = {
            'total_suppliers': total_suppliers,
            'total_outstanding': total_outstanding,
            'due_this_week': due_week,
            'total_payments': total_payments,
            'timestamp': datetime.now().isoformat()
        }
        logger.info(f"📊 Dashboard stats: {stats}")
        return jsonify(stats), 200
    except Exception as e:
        logger.error(f"❌ Dashboard error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ==================== DEVELOPMENT UTILITIES ====================

@app.route('/api/debug/logs', methods=['GET'])
def get_logs():
    """Get recent debug logs (dev mode only)"""
    if not DEV_MODE:
        return jsonify({'error': 'Not available in production'}), 403
    return jsonify({'message': 'Check terminal for logs'}), 200

@app.route('/api/debug/db-reset', methods=['POST'])
def reset_database():
    """Reset database to initial state (dev mode only)"""
    if not DEV_MODE:
        return jsonify({'error': 'Not available in production'}), 403
    
    try:
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
            logger.warning("🔄 Database reset")
        init_db()
        return jsonify({'message': 'Database reset to initial state'}), 200
    except Exception as e:
        logger.error(f"❌ Reset error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_db()
    logger.info("=" * 60)
    logger.info("🚀 KIRANA SUPPLIER CRM - DEVELOPER MODE ACTIVE")
    logger.info("=" * 60)
    logger.info("✅ Database initialized")
    logger.info("🔗 Frontend: http://localhost:8000")
    logger.info("🔗 Backend API: http://localhost:5000")
    logger.info("🔗 Health Check: http://localhost:5000/health")
    logger.info("📊 Debug: http://localhost:5000/api/debug/logs")
    logger.info("=" * 60)
    
    app.run(debug=True, port=5000, use_reloader=True, host='0.0.0.0')


def init_db():
    """Initialize SQLite database with tables"""
    if os.path.exists(DB_FILE):
        return
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Front desk requests table
    c.execute('''CREATE TABLE front_desk (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        issue TEXT NOT NULL,
        notes TEXT,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Suppliers table
    c.execute('''CREATE TABLE suppliers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT,
        outstanding REAL DEFAULT 0,
        due_date TEXT,
        contact_phone TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Payments table
    c.execute('''CREATE TABLE payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        supplier_id INTEGER,
        amount REAL NOT NULL,
        payment_method TEXT,
        reference TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(supplier_id) REFERENCES suppliers(id)
    )''')
    
    # Insert sample suppliers
    suppliers = [
        ('Suman Traders', 'Snacks & Biscuits', 28500, '2026-04-01', '9876543210'),
        ('Rajesh & Sons', 'Milk & Dairy', 45200, '2026-04-06', '9876543211'),
        ('Delhi Spice Co.', 'Spices', 12800, '2026-04-15', '9876543212'),
        ('Kumar Wholesale', 'Oils & Ghee', 52000, '2026-03-30', '9876543213'),
        ('Priya Distributors', 'Drinks & Juices', 38000, '2026-04-08', '9876543214'),
    ]
    
    for name, desc, outstanding, due_date, phone in suppliers:
        c.execute('INSERT INTO suppliers (name, description, outstanding, due_date, contact_phone) VALUES (?, ?, ?, ?, ?)',
                  (name, desc, outstanding, due_date, phone))
    
    conn.commit()
    conn.close()

# ===================== ROUTES =====================

@app.route('/')
def index():
    """Serve main HTML file"""
    return send_from_directory('.', 'index.html')

# ==================== FRONT DESK API ====================

@app.route('/api/frontdesk', methods=['POST'])
def submit_frontdesk():
    """Handle front desk form submission"""
    try:
        data = request.json
        name = data.get('name', '').strip()
        phone = data.get('phone', '').strip()
        issue = data.get('issue', '').strip()
        notes = data.get('notes', '').strip()
        
        if not name or not phone or not issue:
            return jsonify({'error': 'Name, Phone, and Issue are required'}), 400
        
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('INSERT INTO front_desk (name, phone, issue, notes) VALUES (?, ?, ?, ?)',
                  (name, phone, issue, notes))
        conn.commit()
        request_id = c.lastrowid
        conn.close()
        
        return jsonify({'success': True, 'message': f'Front desk request #{request_id} submitted', 'id': request_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/frontdesk/history', methods=['GET'])
def frontdesk_history():
    """Get front desk request history"""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('SELECT id, name, phone, issue, status, created_at FROM front_desk ORDER BY created_at DESC LIMIT 10')
        rows = c.fetchall()
        conn.close()
        
        history = [{'id': r[0], 'name': r[1], 'phone': r[2], 'issue': r[3], 'status': r[4], 'created_at': r[5]} for r in rows]
        return jsonify(history), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== AI BOT API ====================

@app.route('/api/bot', methods=['POST'])
def bot_reply():
    """Handle AI bot queries"""
    try:
        data = request.json
        query = data.get('query', '').lower().strip()
        
        if not query:
            return jsonify({'reply': 'Kuch likho bhaiya!'}), 400
        
        # Smart replies based on query
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        
        if 'rajesh' in query:
            c.execute('SELECT outstanding, due_date FROM suppliers WHERE name LIKE ?', ('%Rajesh%',))
            row = c.fetchone()
            if row:
                reply = f"Rajesh & Sons ka udhaar ₹{row[0]} hai, due date {row[1]} hai."
            else:
                reply = "Rajesh & Sons ka info nahi mila."
        
        elif 'suman' in query:
            c.execute('SELECT outstanding, due_date FROM suppliers WHERE name LIKE ?', ('%Suman%',))
            row = c.fetchone()
            if row:
                reply = f"Suman Traders ka udhaar ₹{row[0]} hai, due date {row[1]} hai."
            else:
                reply = "Suman Traders ka info nahi mila."
        
        elif 'baki' in query or 'outstanding' in query or 'total' in query:
            c.execute('SELECT SUM(outstanding) FROM suppliers')
            total = c.fetchone()[0] or 0
            reply = f"Total baki ₹{total} hai. Suppliers ko payment karo."
        
        elif 'payment' in query or 'bhugtan' in query:
            reply = "Payment karne ke liye 'Record Payment' button dabao. Supplier, amount, aur method select karo."
        
        elif 'supplier' in query:
            c.execute('SELECT name, outstanding FROM suppliers')
            rows = c.fetchall()
            if rows:
                supplier_list = ', '.join([f"{r[0]} (₹{r[1]})" for r in rows[:3]])
                reply = f"Top suppliers: {supplier_list}. Sab ka info dashboard mein hai."
            else:
                reply = "Koi supplier nahi mila."
        
        else:
            reply = "Maaf karo, samajh nahi aaya. Pooch: Rajesh ka bill? Suman due? Ya total baki kitna?"
        
        conn.close()
        return jsonify({'reply': reply}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== SUPPLIER API ====================

@app.route('/api/suppliers', methods=['GET'])
def get_suppliers():
    """Get all suppliers with current outstanding"""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('SELECT id, name, description, outstanding, due_date, contact_phone FROM suppliers')
        rows = c.fetchall()
        conn.close()
        
        suppliers = [{'id': r[0], 'name': r[1], 'description': r[2], 'outstanding': r[3], 'due_date': r[4], 'phone': r[5]} for r in rows]
        return jsonify(suppliers), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/suppliers/<int:supplier_id>', methods=['GET'])
def get_supplier(supplier_id):
    """Get single supplier details"""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('SELECT id, name, description, outstanding, due_date, contact_phone FROM suppliers WHERE id = ?', (supplier_id,))
        row = c.fetchone()
        
        if not row:
            conn.close()
            return jsonify({'error': 'Supplier not found'}), 404
        
        supplier = {'id': row[0], 'name': row[1], 'description': row[2], 'outstanding': row[3], 'due_date': row[4], 'phone': row[5]}
        
        # Get payment history
        c.execute('SELECT amount, payment_method, reference, created_at FROM payments WHERE supplier_id = ? ORDER BY created_at DESC LIMIT 5', (supplier_id,))
        payments = [{'amount': p[0], 'method': p[1], 'ref': p[2], 'date': p[3]} for p in c.fetchall()]
        supplier['payments'] = payments
        
        conn.close()
        return jsonify(supplier), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== PAYMENT API ====================

@app.route('/api/payments', methods=['POST'])
def record_payment():
    """Record a payment"""
    try:
        data = request.json
        supplier_id = data.get('supplier_id')
        amount = data.get('amount', 0)
        method = data.get('method', 'unknown')
        reference = data.get('reference', '')
        
        if not supplier_id or amount <= 0:
            return jsonify({'error': 'Invalid supplier or amount'}), 400
        
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        
        # Record payment
        c.execute('INSERT INTO payments (supplier_id, amount, payment_method, reference) VALUES (?, ?, ?, ?)',
                  (supplier_id, amount, method, reference))
        
        # Update supplier outstanding
        c.execute('UPDATE suppliers SET outstanding = outstanding - ? WHERE id = ?', (amount, supplier_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': f'Payment of ₹{amount} recorded'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== DASHBOARD API ====================

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    """Get dashboard stats"""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        
        # Total suppliers
        c.execute('SELECT COUNT(*) FROM suppliers')
        total_suppliers = c.fetchone()[0]
        
        # Total outstanding
        c.execute('SELECT SUM(outstanding) FROM suppliers')
        total_outstanding = c.fetchone()[0] or 0
        
        # Due this week
        today = datetime.now()
        week_end = today + timedelta(days=7)
        c.execute('SELECT SUM(outstanding) FROM suppliers WHERE due_date BETWEEN ? AND ?',
                  (today.strftime('%Y-%m-%d'), week_end.strftime('%Y-%m-%d')))
        due_week = c.fetchone()[0] or 0
        
        # Total payments (count)
        c.execute('SELECT COUNT(*) FROM payments')
        total_payments = c.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'total_suppliers': total_suppliers,
            'total_outstanding': total_outstanding,
            'due_this_week': due_week,
            'total_payments': total_payments
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_db()
    print("✅ Database initialized")
    print("🚀 Flask server running on http://localhost:5000")
    app.run(debug=True, port=5000, use_reloader=False)
