// Full Stack API Functions for Frontend

// ==================== NOTIFICATION ====================
function showNotification(message, type = 'info') {
    const notif = document.createElement('div');
    notif.className = `notification ${type}`;
    notif.textContent = message;
    document.body.appendChild(notif);
    
    setTimeout(() => {
        notif.remove();
    }, 3000);
}

// ==================== AI BOT (with Flask API) ====================
function aiBotSend() {
    const inputEl = document.getElementById('aiBotInput');
    const text = inputEl.value.trim();
    if (!text) return;

    const msgContainer = document.getElementById('aiBotMessages');
    const userMsg = document.createElement('div');
    userMsg.className = 'ai-bot-message user';
    userMsg.textContent = 'You: ' + text;
    msgContainer.appendChild(userMsg);

    // Call Flask API
    fetch('http://localhost:5000/api/bot', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: text })
    })
    .then(res => res.json())
    .then(data => {
        const botMsg = document.createElement('div');
        botMsg.className = 'ai-bot-message bot';
        botMsg.textContent = 'Bot: ' + (data.reply || 'Kuch galti ho gayi.');
        msgContainer.appendChild(botMsg);
        msgContainer.scrollTop = msgContainer.scrollHeight;
    })
    .catch(err => {
        const errorMsg = document.createElement('div');
        errorMsg.className = 'ai-bot-message bot';
        errorMsg.textContent = 'Bot: Flask server se connect nahi ho raha. Ensure app.py is running on port 5000.';
        msgContainer.appendChild(errorMsg);
        msgContainer.scrollTop = msgContainer.scrollHeight;
        console.error('Bot API error:', err);
    });

    inputEl.value = '';
}

// ==================== FRONT DESK (with Flask API) ====================
function frontDeskSubmit() {
    const name = document.getElementById('fdName').value.trim();
    const phone = document.getElementById('fdPhone').value.trim();
    const issue = document.getElementById('fdIssue').value.trim();
    const notes = document.getElementById('fdNotes').value.trim();

    if (!name || !phone || !issue) {
        alert('Kripya Name, Phone aur Issue sab bharien');
        return;
    }

    // Call Flask API
    fetch('http://localhost:5000/api/frontdesk', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, phone, issue, notes })
    })
    .then(res => res.json())
    .then(data => {
        showNotification(`📥 ${data.message || 'Request submitted'}`, 'success');
        document.getElementById('fdName').value = '';
        document.getElementById('fdPhone').value = '';
        document.getElementById('fdIssue').value = '';
        document.getElementById('fdNotes').value = '';
    })
    .catch(err => {
        showNotification('Request mein error: Flask server check karein.', 'error');
        console.error('Front desk API error:', err);
    });
}

// ==================== GET SUPPLIERS ====================
function loadSuppliers() {
    fetch('http://localhost:5000/api/suppliers')
    .then(res => res.json())
    .then(suppliers => {
        console.log('Suppliers loaded:', suppliers);
        // Update UI with suppliers
    })
    .catch(err => console.error('Suppliers API error:', err));
}

// ==================== RECORD PAYMENT ====================
function recordPayment(supplierId, amount, method, reference) {
    fetch('http://localhost:5000/api/payments', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ supplier_id: supplierId, amount, method, reference })
    })
    .then(res => res.json())
    .then(data => {
        showNotification(data.message, 'success');
    })
    .catch(err => {
        showNotification('Payment recording failed', 'error');
        console.error('Payment API error:', err);
    });
}

// ==================== GET DASHBOARD STATS ====================
function loadDashboardStats() {
    fetch('http://localhost:5000/api/dashboard')
    .then(res => res.json())
    .then(data => {
        console.log('Dashboard stats:', data);
        // Update dashboard UI with real data from database
        // Example: update stat boxes with data.total_outstanding, data.total_suppliers, etc.
    })
    .catch(err => console.error('Dashboard API error:', err));
}

// Load on page ready
document.addEventListener('DOMContentLoaded', function() {
    loadSuppliers();
    loadDashboardStats();
    
    // Set today's date as default
    const today = new Date().toISOString().split('T')[0];
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        if (!input.value) input.value = today;
    });
});
