#!/usr/bin/env python3
"""
Kirana Supplier CRM - Development Server Manager
Starts and manages both HTTP (frontend) and Flask (backend) servers
with hot reload, logging, and developer utilities
"""

import os
import sys
import subprocess
import signal
import time
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)8s | %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DevServer:
    def __init__(self):
        self.http_process = None
        self.flask_process = None
        self.running = True
        
    def start_http_server(self):
        """Start Python HTTP server on port 8000"""
        logger.info("🌐 Starting HTTP Server on port 8000...")
        try:
            self.http_process = subprocess.Popen(
                ['python3', '-m', 'http.server', '8000'],
                cwd=os.getcwd(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1
            )
            logger.info("✅ HTTP Server started (PID: {})".format(self.http_process.pid))
        except Exception as e:
            logger.error(f"❌ Failed to start HTTP Server: {e}")
            return False
        return True
    
    def start_flask_server(self):
        """Start Flask development server on port 5000"""
        logger.info("🔧 Starting Flask Backend on port 5000...")
        try:
            self.flask_process = subprocess.Popen(
                ['python3', 'app.py'],
                cwd=os.getcwd(),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            logger.info("✅ Flask Server started (PID: {})".format(self.flask_process.pid))
        except Exception as e:
            logger.error(f"❌ Failed to start Flask Server: {e}")
            return False
        return True
    
    def log_server_output(self, process, name):
        """Log output from server processes"""
        try:
            for line in process.stdout:
                if line.strip():
                    logger.info(f"[{name}] {line.strip()}")
        except:
            pass
    
    def start(self):
        """Start all servers"""
        logger.info("=" * 70)
        logger.info("🚀 KIRANA SUPPLIER CRM - FULL DEVELOPER MODE")
        logger.info("=" * 70)
        
        # Start servers
        if not self.start_http_server():
            return False
        time.sleep(1)
        
        if not self.start_flask_server():
            self.stop()
            return False
        
        # Print access information
        logger.info("=" * 70)
        logger.info("📱 ACCESS POINTS:")
        logger.info("  • Frontend:  http://localhost:8000")
        logger.info("  • Backend:   http://localhost:5000")
        logger.info("  • Health:    http://localhost:5000/health")
        logger.info("  • Debug:     http://localhost:5000/api/debug/logs")
        logger.info("=" * 70)
        logger.info("🛠️  DEVELOPER FEATURES:")
        logger.info("  • Hot Reload: Enabled (Flask --reload)")
        logger.info("  • Debug Mode: ACTIVE")
        logger.info("  • Request Logging: ENABLED")
        logger.info("  • Database Debug: /api/debug/db-reset")
        logger.info("=" * 70)
        logger.info("⚡ Press Ctrl+C to stop all servers")
        logger.info("=" * 70)
        
        return True
    
    def stop(self):
        """Stop all servers gracefully"""
        logger.info("\n🛑 Stopping servers...")
        
        if self.http_process:
            try:
                self.http_process.terminate()
                self.http_process.wait(timeout=5)
                logger.info("✅ HTTP Server stopped")
            except:
                self.http_process.kill()
                logger.info("⚠️  HTTP Server force-stopped")
        
        if self.flask_process:
            try:
                self.flask_process.terminate()
                self.flask_process.wait(timeout=5)
                logger.info("✅ Flask Server stopped")
            except:
                self.flask_process.kill()
                logger.info("⚠️  Flask Server force-stopped")
        
        self.running = False
    
    def monitor(self):
        """Monitor running processes"""
        while self.running:
            try:
                # Check if processes are still alive
                if self.http_process and self.http_process.poll() is not None:
                    logger.warning("⚠️  HTTP Server crashed, restarting...")
                    self.start_http_server()
                
                if self.flask_process and self.flask_process.poll() is not None:
                    logger.warning("⚠️  Flask Server crashed, restarting...")
                    self.start_flask_server()
                
                time.sleep(2)
            except KeyboardInterrupt:
                break
    
    def run(self):
        """Run development server"""
        if not self.start():
            return 1
        
        try:
            self.monitor()
        except KeyboardInterrupt:
            logger.info("\n📩 Received interrupt signal")
        finally:
            self.stop()
        
        return 0

def main():
    dev_server = DevServer()
    
    def signal_handler(sig, frame):
        dev_server.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    exit_code = dev_server.run()
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
