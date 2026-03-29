#!/usr/bin/env python3
"""
Kirana Supplier CRM - Production Server
Entry point for production deployment
"""

import os
import sys
from app import app

if __name__ == '__main__':
    # Production settings
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'

    print("🚀 Starting Kirana Supplier CRM - Production Mode")
    print(f"📡 Port: {port}")
    print(f"🐛 Debug: {debug}")

    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        use_reloader=False  # Disable reloader in production
    )