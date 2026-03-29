# Kirana Supplier CRM - Full Stack Demo

A simple, shop-owner friendly **Supplier & Payment Management System** for small retailers (kirana wala) with AI assistant bot.

🎯 **Built with:** Python (Flask) + SQLite + Vanilla JS | 📱 **UI:** Simple Black & White Design | 🤖 **Bot:** Hinglish Language Support

---

## 🚀 Quick Start - Developer Mode

### 1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 2. **Start Both Servers** (Recommended)
```bash
python3 dev-server.py
```
This starts:
- ✅ **Frontend:** http://localhost:8000 (HTML/CSS/JS)
- ✅ **Backend:** http://localhost:5000 (Flask API)
- ✅ **Hot Reload:** Enabled (changes refresh automatically)
- ✅ **Debug Mode:** ACTIVE (detailed error messages)

**Output:**
```
🚀 KIRANA SUPPLIER CRM - FULL DEVELOPER MODE
❯ Frontend:  http://localhost:8000
❯ Backend:   http://localhost:5000
❯ Health:    http://localhost:5000/health
❯ Debug:     http://localhost:5000/api/debug/logs

🛠️  DEVELOPER FEATURES:
❯ Hot Reload: Enabled
❯ Debug Mode: ACTIVE
❯ Request Logging: ENABLED
```

---

## � Deployment Options

### **Docker (Recommended)**
```bash
# Build and run with Docker Compose
make docker-run

# Or manually:
docker-compose up --build
```

### **Heroku**
```bash
# Deploy to Heroku
heroku create your-app-name
git push heroku main
```

### **Local Production**
```bash
# Install dependencies
pip install -r requirements.txt

# Run production server
python3 run.py
```

### **Makefile Commands**
```bash
make help        # Show all available commands
make install     # Install dependencies
make dev         # Run development server
make run         # Run production server
make build       # Build Docker image
make docker-run  # Run with Docker Compose
make clean       # Clean up generated files
make test        # Run health checks
make db-reset    # Reset database
make logs        # Show dev server logs
```

---

## 📁 Complete Project Structure

```
├── index.html              # Main UI (kirana dashboard)
├── app.py                  # Flask backend with API endpoints
├── dev-server.py           # Development server manager (hot reload)
├── run.py                  # Production entry point
├── api-client.js           # Frontend API wrapper
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker container config
├── docker-compose.yml      # Docker Compose setup
├── Procfile                # Heroku deployment
├── runtime.txt             # Python version for Heroku
├── Makefile                # Build automation
├── .env                    # Environment configuration
├── .env.example            # Environment template
├── .gitignore              # Git ignore rules
├── .dockerignore           # Docker ignore rules
├── kirana.db              # SQLite database (auto-created)
├── README.md               # This file
└── LICENSE                 # MIT License
```

---

## 🔌 API Endpoints

### **Health Check**
```bash
GET /health
→ {"status": "healthy", "mode": "development"}
```

### **Front Desk Form**
```bash
POST /api/frontdesk
{"name": "Rajesh", "phone": "9876543210", "issue": "bill pending", "notes": "urgent"}
→ {"success": true, "id": 1, "message": "Front desk request #1 submitted"}
```

### **AI Bot Query**
```bash
POST /api/bot
{"query": "rajesh ka bill kitna hai"}
→ {"reply": "Rajesh & Sons ka udhaar ₹45200 hai, due date 2026-04-06 hai."}
```

### **Get All Suppliers**
```bash
GET /api/suppliers
→ [{"id": 1, "name": "Suman Traders", "outstanding": 28500, ...}]
```

### **Record Payment**
```bash
POST /api/payments
{"supplier_id": 1, "amount": 5000, "method": "cash", "reference": "payment123"}
→ {"success": true, "message": "Payment of ₹5000 recorded"}
```

### **Dashboard Stats**
```bash
GET /api/dashboard
→ {"total_outstanding": 176500, "due_this_week": 80500, "total_suppliers": 5, "total_payments": 0}
```

### **Debug Utils** (Dev Mode Only)
```bash
GET  /api/debug/logs              # Get current logs
POST /api/debug/db-reset          # Reset DB to initial state
```

---

## 🛠️ Developer Mode Features

### **🔄 Hot Reload**
- Flask auto-reloader watches for file changes
- No manual restart needed
- Just save and refresh browser

### **📊 Request/Response Logging**
- **Format:** `📨 POST /api/bot` → `✅ Response: 200`
- **Data Logging:** Complete JSON payloads logged to console
- **Timestamps:** All requests timestamped
- **Error Tracking:** Failed requests logged with `❌` marker

### **🐛 Debug Mode**
- Full stack traces on errors
- Detailed error messages
- Interactive Flask debugger

### **⚙️ Environment Configuration** (`.env` file)
```env
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=True
LOG_LEVEL=DEBUG
ENABLE_REQUEST_LOGGING=True
```

### **🔀 CORS Enabled**
- Frontend (8000) ↔ Backend (5000) communication
- Automatic request/response handling

---

## 📊 Database Schema

### **suppliers** table
```sql
id, name, description, outstanding, due_date, contact_phone, created_at
```
**Sample Data:** 5 suppliers with outstanding amounts

### **front_desk** table
```sql
id, name, phone, issue, notes, status, created_at
```

### **payments** table
```sql
id, supplier_id, amount, payment_method, reference, created_at
```

---

## 💡 Features

### **For Shop Owners (Simple UI)**
- ✅ Black & white interface (easy on eyes)
- ✅ Simple Hinglish language (राजेश, उधार, आदि)
- ✅ Track supplier bills easily
- ✅ Record payments with one click

### **For Developers (Professional Stack)**
- ✅ RESTful API architecture
- ✅ SQL database with 3 normalized tables
- ✅ Hot reload development environment
- ✅ Request/response logging
- ✅ Debug mode with stack traces
- ✅ Environment-based configuration
- ✅ CORS support
- ✅ Error handling middleware

---

## 🤖 AI Bot Examples

**Query:** "rajesh ka bill kitna hai"  
**Response:** "Rajesh & Sons ka udhaar ₹45200.0 hai, due date 2026-04-06 hai."

**Query:** "total baki kitna hai"  
**Response:** "Total 5 suppliers se baki ₹176500 hai. Sabko payment kro."

**Query:** "jaldi kisko payment deni hai"  
**Response:** "Sabse jaldi due: Kumar Wholesale (2026-03-30), Rajesh & Sons (2026-04-06)..."

---

## 🚀 Running Individual Servers

### **Frontend Only** (No backend)
```bash
python3 -m http.server 8000
```

### **Backend Only** (Dev mode)
```bash
python3 app.py
```

### **Backend Only** (Production)
```bash
python3 app.py  # Set FLASK_ENV=production in .env
```

---

## 🔧 Troubleshooting

### **Port Already in Use**
```bash
# Kill existing process on port 5000 or 8000
lsof -i :5000 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

### **Database Errors**
```bash
# Reset database to initial state
curl -X POST http://localhost:5000/api/debug/db-reset
```

### **CORS Issues**
- Ensure backend is running on 5000
- Check `.env` has CORS settings
- Verify `Flask-CORS` is installed

---

## 📦 Deployment Checklist

- [ ] Update `.env` to `FLASK_ENV=production`
- [ ] Set `DEBUG=False` in app.py
- [ ] Use production WSGI server (Gunicorn, uWSGI)
- [ ] Setup SSL/TLS certificates
- [ ] Configure database backups
- [ ] Enable logging to files

---

## 📝 License
Demo project for Kirana Store CRM system

## 👨‍💻 Author
Built with ❤️ for small retailers
