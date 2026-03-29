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
    // Safe API base: if same origin in future, use relative path
    const apiBase = window.location.hostname === 'localhost' ? 'http://localhost:5000' : '';

    fetch(`${apiBase}/api/bot`, {
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
        
        const container = document.getElementById('supplierListContainer');
        container.innerHTML = ''; // Clear existing content
        
        if (suppliers.length === 0) {
            container.innerHTML = '<div class="empty-state"><div class="empty-state-icon">📦</div><p>No suppliers found</p></div>';
            return;
        }
        
        suppliers.forEach(supplier => {
            const item = document.createElement('div');
            item.className = 'supplier-item';
            
            // Calculate status based on due date
            const today = new Date();
            const dueDate = new Date(supplier.due_date);
            const daysDiff = Math.ceil((dueDate - today) / (1000 * 60 * 60 * 24));
            
            let statusText = '';
            let statusClass = '';
            if (supplier.outstanding <= 0) {
                statusText = 'Settled';
                statusClass = 'status-ok';
            } else if (daysDiff < 0) {
                statusText = 'OVERDUE';
                statusClass = 'status-due';
            } else if (daysDiff <= 7) {
                statusText = `Due in ${daysDiff} days`;
                statusClass = 'status-due';
            } else {
                statusText = `Due in ${daysDiff} days`;
                statusClass = 'status-partial';
            }
            
            item.innerHTML = `
                <div>
                    <div class="supplier-name">${supplier.name}</div>
                    <div class="supplier-contact">${supplier.description}</div>
                </div>
                <div class="balance pending">₹${supplier.outstanding.toLocaleString()}</div>
                <div>${supplier.description}</div>
                <div><span class="status-badge ${statusClass}">${statusText}</span></div>
                <div><button class="action-btn btn-primary" onclick="viewSupplierDetails(${supplier.id})">View</button></div>
            `;
            
            container.appendChild(item);
        });
    })
    .catch(err => {
        console.error('Suppliers API error:', err);
        const container = document.getElementById('supplierListContainer');
        container.innerHTML = '<div class="empty-state"><div class="empty-state-icon">❌</div><p>Error loading suppliers</p></div>';
    });
}

// ==================== VIEW SUPPLIER DETAILS ====================
function viewSupplierDetails(supplierId) {
    fetch(`http://localhost:5000/api/suppliers/${supplierId}`)
    .then(res => res.json())
    .then(supplier => {
        console.log('Supplier details:', supplier);
        
        // Update supplier portal view
        switchView('supplier');
        
        // Update supplier info
        document.querySelector('#supplier-view h2').textContent = `📦 Supplier: ${supplier.name}`;
        document.querySelector('#supplier-view p').textContent = `${supplier.description} | Contact: ${supplier.phone}`;
        
        // Update stats
        document.getElementById('supplierOutstanding').textContent = '₹' + supplier.outstanding.toLocaleString();
        document.getElementById('supplierDueDate').textContent = supplier.due_date;
        
        // Update payment history
        const paymentList = document.getElementById('supplierPaymentHistory');
        paymentList.innerHTML = '';
        
        if (supplier.payments && supplier.payments.length > 0) {
            supplier.payments.forEach(payment => {
                const paymentItem = document.createElement('tr');
                paymentItem.innerHTML = `
                    <td>${payment.date}</td>
                    <td>₹${payment.amount.toLocaleString()}</td>
                    <td>${payment.method}</td>
                    <td>${payment.ref || 'N/A'}</td>
                `;
                paymentList.appendChild(paymentItem);
            });
        } else {
            paymentList.innerHTML = '<tr><td colspan="4" style="text-align: center;">No payments recorded</td></tr>';
        }
        
        showNotification(`Loaded details for ${supplier.name}`, 'info');
    })
    .catch(err => {
        console.error('Supplier details error:', err);
        showNotification('Error loading supplier details', 'error');
    });
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
        loadSuppliers(); // Refresh supplier list
        loadDashboardStats(); // Refresh dashboard
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
        document.getElementById('totalSuppliers').textContent = data.total_suppliers;
        document.getElementById('totalOutstanding').textContent = '₹' + data.total_outstanding.toLocaleString();
        document.getElementById('dueThisWeek').textContent = '₹' + data.due_this_week.toLocaleString();
        document.getElementById('totalPayments').textContent = data.total_payments;
    })
    .catch(err => {
        console.error('Dashboard API error:', err);
        // Fallback values
        document.getElementById('totalSuppliers').textContent = 'Error';
        document.getElementById('totalOutstanding').textContent = 'Error';
        document.getElementById('dueThisWeek').textContent = 'Error';
        document.getElementById('totalPayments').textContent = 'Error';
    });
}

// ==================== FORM HANDLERS ====================

function handleAddInvoice(e) {
    e.preventDefault();
    // For now, just show notification (invoice management not implemented yet)
    const supplier = document.getElementById('supplierSelect').value;
    const amount = document.getElementById('invoiceAmount').value;
    closeModal('addInvoiceModal');
    showNotification(`✅ Invoice added for ${supplier} (₹${amount})`, 'success');
    e.target.reset();
}

function handleRecordPayment(e) {
    e.preventDefault();
    
    // Get form values
    const supplierSelect = document.getElementById('paymentSupplier');
    const supplierName = supplierSelect.value;
    const amount = parseFloat(document.getElementById('paymentAmount').value);
    const method = document.getElementById('paymentMethod').value;
    const reference = document.getElementById('paymentRef').value;
    
    if (!supplierName || !amount || !method) {
        showNotification('Please fill all required fields', 'error');
        return;
    }
    
    // Find supplier ID from name
    fetch('http://localhost:5000/api/suppliers')
    .then(res => res.json())
    .then(suppliers => {
        const supplier = suppliers.find(s => s.name === supplierName);
        if (!supplier) {
            showNotification('Supplier not found', 'error');
            return;
        }
        
        // Record payment
        recordPayment(supplier.id, amount, method, reference);
        closeModal('recordPaymentModal');
        e.target.reset();
    })
    .catch(err => {
        console.error('Payment supplier lookup error:', err);
        showNotification('Error processing payment', 'error');
    });
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
