#!/usr/bin/env python3
"""
FlowPrint.py - Automatic Email-to-Print Service with Web Interface

Monitors an IMAP mailbox and automatically prints HTML-formatted emails
with a specified subject prefix using Google Chrome.

Perfect for automated printing of Shopify orders, receipts, labels, and more.

License: GNU General Public License v3.0
Repository: https://github.com/NotDonaldTrump/FlowPrint
"""

import imaplib
import email
import time
import traceback
import os
import sys
import tempfile
import subprocess
import uuid
import threading
import re
import shutil
import json
import webbrowser
from datetime import datetime, timedelta
from email.header import decode_header
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit

# ==========================
# DEFAULT CONFIGURATION
# ==========================

DEFAULT_CONFIG = {
    "imap_host": "imap.gmail.com",
    "imap_port": 993,
    "imap_use_ssl": True,
    "imap_username": "",
    "imap_password": "",
    "mailbox": "Inbox",
    "poll_interval_seconds": 30,
    "subject_prefix": "[PRINT PACK]",
    "auto_print_enabled": True,
    "delete_email_after_print": False,
    "chrome_path": "",
    "chrome_print_wait_seconds": 8,
    "temp_file_cleanup_enabled": True,
    "temp_file_cleanup_hours": 6,
    "printed_uids_file": "printed_uids.txt",
    "log_file": "flowprint.log",
    "theme": "dark"
}

CONFIG_FILE = "flowprint_config.json"

# ==========================
# Configuration Manager
# ==========================

class ConfigManager:
    def __init__(self):
        self.config = self.load_config()
    
    def load_config(self):
        """Load configuration from file or create default."""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    loaded = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    config = DEFAULT_CONFIG.copy()
                    config.update(loaded)
                    return config
            except:
                return DEFAULT_CONFIG.copy()
        return DEFAULT_CONFIG.copy()
    
    def save_config(self, new_config):
        """Save configuration to file."""
        self.config.update(new_config)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=2)
        return True
    
    def get_config(self):
        """Get current configuration."""
        return self.config.copy()

# ==========================
# Logging Helper
# ==========================

def log_to_file(message, level="INFO"):
    """Write log entry to file with timestamp."""
    try:
        config = config_manager.get_config()
        log_file = config.get('log_file', 'flowprint.log')
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except:
        pass

# ==========================
# Global State
# ==========================

config_manager = ConfigManager()
daemon = None
daemon_thread = None

# Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'flowprint-secret-key-' + uuid.uuid4().hex
socketio = SocketIO(app, cors_allowed_origins="*")

# ==========================
# Email Helpers
# ==========================

def decode_str(s, enc):
    try:
        if enc:
            return s.decode(enc, errors="replace") if isinstance(s, (bytes, bytearray)) else str(s)
        else:
            return s.decode("utf-8", errors="replace") if isinstance(s, (bytes, bytearray)) else str(s)
    except:
        return s.decode("utf-8", errors="replace") if isinstance(s, (bytes, bytearray)) else str(s)

def get_subject(msg):
    raw_subject = msg.get("Subject", "")
    parts = decode_header(raw_subject)
    decoded = []
    for part, enc in parts:
        decoded.append(decode_str(part, enc))
    return "".join(decoded).strip()

def subject_matches_prefix(subject, prefix):
    return subject.strip().upper().startswith(prefix.strip().upper())

def get_best_body(msg):
    html_part = None
    text_part = None

    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_maintype() == "multipart":
                continue
            disp = str(part.get("Content-Disposition") or "").lower()
            if "attachment" in disp:
                continue
            ctype = part.get_content_type()
            charset = part.get_content_charset() or "utf-8"
            try:
                payload = part.get_payload(decode=True)
                if payload is None:
                    continue
                body = payload.decode(charset, errors="replace")
            except:
                continue
            if ctype == "text/html" and html_part is None:
                html_part = body
            elif ctype == "text/plain" and text_part is None:
                text_part = body
    else:
        ctype = msg.get_content_type()
        charset = msg.get_content_charset() or "utf-8"
        payload = msg.get_payload(decode=True)
        if payload is not None:
            body = payload.decode(charset, errors="replace")
            if ctype == "text/html":
                html_part = body
            elif ctype == "text/plain":
                text_part = body

    if html_part:
        return html_part
    if text_part:
        safe = text_part.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return f"<html><body><pre>{safe}</pre></body></html>"
    return "<html><body>(No body content)</body></html>"

# ==========================
# Chrome Printer
# ==========================

class ChromePrinter:
    def __init__(self):
        self.chrome_path = None
    
    def _resolve_chrome_path(self, custom_path=""):
        if custom_path and os.path.exists(custom_path):
            return custom_path
        
        candidates = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/usr/bin/google-chrome",
            "/usr/bin/chromium-browser",
        ]
        for c in candidates:
            if os.path.exists(c):
                return c
        
        raise FileNotFoundError("Could not find Chrome. Please specify path in settings.")

    def inject_print_script(self, html_content, auto_close=True):
        if auto_close:
            script = """
<script>
window.onload = function() {
    setTimeout(function() {
        window.print();
        window.close();
    }, 500);
};
</script>"""
        else:
            script = """
<script>
window.onload = function() {
    setTimeout(function() {
        window.print();
    }, 500);
};
</script>"""
        
        if re.search(r'</body>', html_content, re.IGNORECASE):
            html_content = re.sub(r'</body>', script + '</body>', html_content, flags=re.IGNORECASE)
        elif re.search(r'</html>', html_content, re.IGNORECASE):
            html_content = re.sub(r'</html>', script + '</html>', html_content, flags=re.IGNORECASE)
        else:
            html_content += script
        
        return html_content

    def print_html_file(self, html_path, auto_print=True, chrome_path="", wait_seconds=8):
        self.chrome_path = self._resolve_chrome_path(chrome_path)
        
        with open(html_path, "r", encoding="utf-8", errors="ignore") as f:
            html_content = f.read()
        
        modified_html = self.inject_print_script(html_content, auto_close=auto_print)
        
        temp_dir = tempfile.gettempdir()
        modified_name = f"flowprint_{uuid.uuid4().hex}.html"
        modified_path = os.path.join(temp_dir, modified_name)
        
        with open(modified_path, "w", encoding="utf-8", errors="ignore") as f:
            f.write(modified_html)
        
        user_data_dir = os.path.join(temp_dir, "flowprint_chrome_profile")
        os.makedirs(user_data_dir, exist_ok=True)

        if auto_print:
            cmd = [self.chrome_path, "--kiosk-printing", f"--user-data-dir={user_data_dir}", modified_path]
        else:
            cmd = [self.chrome_path, f"--user-data-dir={user_data_dir}", modified_path]

        if auto_print:
            try:
                proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(wait_seconds)
                try:
                    proc.terminate()
                except:
                    pass
            finally:
                try:
                    os.remove(modified_path)
                except:
                    pass
        else:
            try:
                subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception as e:
                try:
                    os.remove(modified_path)
                except:
                    pass
                raise

# ==========================
# Temp File Manager
# ==========================

class TempFileManager:
    def __init__(self):
        self.temp_dir = os.path.join(tempfile.gettempdir(), "flowprint_jobs")
        os.makedirs(self.temp_dir, exist_ok=True)
        self.tracked_files = {}
        self.last_cleanup = datetime.now()
        
    def create_temp_file(self, subject, html_content):
        safe_label = "".join(c for c in subject if c.isalnum() or c in ("-", "_", " "))[:40]
        filename = (safe_label or "FlowPrint") + f"_{uuid.uuid4().hex[:8]}.html"
        temp_path = os.path.join(self.temp_dir, filename)
        
        with open(temp_path, "w", encoding="utf-8", errors="ignore") as f:
            f.write(html_content)
        
        self.tracked_files[temp_path] = datetime.now()
        return temp_path
    
    def should_cleanup(self, cleanup_hours, cleanup_enabled):
        if not cleanup_enabled:
            return False
        elapsed = datetime.now() - self.last_cleanup
        return elapsed.total_seconds() >= (cleanup_hours * 3600)
    
    def cleanup_old_files(self, cleanup_hours):
        now = datetime.now()
        cutoff = now - timedelta(hours=cleanup_hours)
        
        files_to_remove = []
        for filepath, creation_time in list(self.tracked_files.items()):
            if creation_time < cutoff:
                files_to_remove.append(filepath)
        
        temp_dir = tempfile.gettempdir()
        try:
            for filename in os.listdir(temp_dir):
                if filename.startswith("flowprint_") and filename.endswith(".html"):
                    filepath = os.path.join(temp_dir, filename)
                    try:
                        file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                        if file_time < cutoff:
                            files_to_remove.append(filepath)
                    except:
                        pass
        except:
            pass
        
        for filepath in files_to_remove:
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
                if filepath in self.tracked_files:
                    del self.tracked_files[filepath]
            except:
                pass
        
        if files_to_remove:
            self.last_cleanup = now
            log_to_file(f"Cleaned up {len(files_to_remove)} old file(s)")
    
    def cleanup_all_files(self):
        for filepath in list(self.tracked_files.keys()):
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
            except:
                pass
        
        temp_dir = tempfile.gettempdir()
        try:
            for filename in os.listdir(temp_dir):
                if filename.startswith("flowprint_") and filename.endswith(".html"):
                    filepath = os.path.join(temp_dir, filename)
                    try:
                        os.remove(filepath)
                    except:
                        pass
        except:
            pass
        
        self.tracked_files.clear()

# ==========================
# IMAP Daemon
# ==========================

class ImapPrintDaemon:
    def __init__(self):
        self.conn = None
        self.chrome_printer = ChromePrinter()
        self.temp_manager = TempFileManager()
        self.printed_uids = set()
        self.running = False
        self.status = "Stopped"
        self.stats = {
            "last_check": "Never",
            "next_check": "Pending...",
            "messages_found": 0,
            "jobs_processed": 0,
            "jobs_pending": 0,
            "last_cleanup": "Never",
            "next_cleanup": "Calculating...",
            "recent_jobs": [],
            "errors": []
        }
        self._load_printed_uids()
        
    def _load_printed_uids(self):
        config = config_manager.get_config()
        uids_file = config.get('printed_uids_file', 'printed_uids.txt')
        if os.path.exists(uids_file):
            with open(uids_file, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    uid = line.strip()
                    if uid:
                        self.printed_uids.add(uid)

    def _save_printed_uid(self, uid):
        config = config_manager.get_config()
        uids_file = config.get('printed_uids_file', 'printed_uids.txt')
        self.printed_uids.add(uid)
        with open(uids_file, "a", encoding="utf-8", errors="ignore") as f:
            f.write(uid + "\n")

    def update_status(self, status):
        self.status = status
        self.emit_status_update()
        log_to_file(f"Status: {status}")

    def emit_status_update(self):
        """Emit status update to all connected clients."""
        socketio.emit('status_update', {
            'status': self.status,
            'stats': self.stats
        })

    def connect(self):
        config = config_manager.get_config()
        self.update_status("Connecting to mailbox...")
        
        try:
            if config['imap_use_ssl']:
                self.conn = imaplib.IMAP4_SSL(config['imap_host'], config['imap_port'])
            else:
                self.conn = imaplib.IMAP4(config['imap_host'], config['imap_port'])
            
            self.conn.login(config['imap_username'], config['imap_password'])
            self.conn.select(config['mailbox'])
            self.update_status("Connected ✓")
            log_to_file("Connected to mailbox successfully")
            return True
        except Exception as e:
            self.update_status(f"Connection failed: {str(e)}")
            self.add_error(f"Connection failed: {str(e)}")
            log_to_file(f"Connection failed: {str(e)}", "ERROR")
            return False

    def disconnect(self):
        if self.conn is not None:
            try:
                self.conn.close()
            except:
                pass
            try:
                self.conn.logout()
            except:
                pass
            self.conn = None

    def delete_email(self, uid_bytes):
        """Delete email from inbox after successful print."""
        try:
            uid = uid_bytes.decode("ascii", errors="ignore")
            self.conn.uid("store", uid_bytes, "+FLAGS", "\\Deleted")
            self.conn.expunge()
            log_to_file(f"Email UID {uid} deleted from inbox", "SUCCESS")
            return True
        except Exception as e:
            log_to_file(f"Failed to delete email UID: {str(e)}", "ERROR")
            return False

    def search_candidate_uids(self):
        config = config_manager.get_config()
        self.update_status("Searching for messages...")
        
        criteria = f'(SUBJECT "{config["subject_prefix"]}")'
        status, data = self.conn.uid("search", None, criteria)

        if status != "OK" or not data or not data[0]:
            return []
        
        return data[0].split()

    def add_job(self, subject, action, temp_file_path=None):
        timestamp = datetime.now().strftime("%H:%M:%S")
        job_entry = {
            "time": timestamp,
            "subject": subject[:50],
            "action": action,
            "temp_file": temp_file_path,
            "can_reprint": temp_file_path and os.path.exists(temp_file_path) if temp_file_path else False
        }
        self.stats['recent_jobs'].insert(0, job_entry)
        self.stats['recent_jobs'] = self.stats['recent_jobs'][:10]  # Keep last 10
        log_to_file(f"Job processed: {subject} - {action}", "SUCCESS")
        self.emit_status_update()

    def add_error(self, error_msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        error_entry = {
            "time": timestamp,
            "message": error_msg[:100]
        }
        self.stats['errors'].insert(0, error_entry)
        self.stats['errors'] = self.stats['errors'][:5]
        log_to_file(error_msg, "ERROR")
        self.emit_status_update()

    def process_message(self, uid_bytes):
        config = config_manager.get_config()
        uid = uid_bytes.decode("ascii", errors="ignore")
        
        if uid in self.printed_uids:
            return

        self.update_status(f"Processing message UID {uid}...")
        
        status, data = self.conn.uid("fetch", uid_bytes, "(RFC822)")
        if status != "OK" or not data or not data[0]:
            self.add_error(f"Failed to fetch UID {uid}")
            return

        raw = data[0][1]
        msg = email.message_from_bytes(raw)
        subject = get_subject(msg)

        if not subject_matches_prefix(subject, config['subject_prefix']):
            self._save_printed_uid(uid)
            return

        html_body = get_best_body(msg)
        temp_path = self.temp_manager.create_temp_file(subject, html_body)

        print_successful = False

        if config['auto_print_enabled']:
            try:
                self.chrome_printer.print_html_file(
                    temp_path, 
                    auto_print=True,
                    chrome_path=config['chrome_path'],
                    wait_seconds=config['chrome_print_wait_seconds']
                )
                self.add_job(subject, "Auto-printed ✓", temp_path)
                self.stats['jobs_processed'] += 1
                print_successful = True
            except Exception as e:
                error_msg = f"Print failed: {str(e)[:50]}"
                self.add_error(error_msg)
                print_successful = False
        else:
            try:
                self.chrome_printer.print_html_file(
                    temp_path, 
                    auto_print=False,
                    chrome_path=config['chrome_path'],
                    wait_seconds=config['chrome_print_wait_seconds']
                )
                self.add_job(subject, "Print dialog opened 🖨️", temp_path)
                self.stats['jobs_processed'] += 1
                print_successful = True
            except Exception as e:
                error_msg = f"Failed to open dialog: {str(e)[:50]}"
                self.add_error(error_msg)
                print_successful = False

        if print_successful and config['delete_email_after_print']:
            if self.delete_email(uid_bytes):
                log_to_file(f"Email '{subject}' printed and deleted", "SUCCESS")
            else:
                self.add_error(f"Print succeeded but failed to delete email")

        self.mark_seen(uid_bytes)
        self._save_printed_uid(uid)

    def mark_seen(self, uid_bytes):
        try:
            self.conn.uid("store", uid_bytes, "+FLAGS", "\\Seen")
        except:
            pass

    def run(self):
        """Main daemon loop."""
        self.running = True
        log_to_file("=" * 80)
        log_to_file("FlowPrint Service Started")
        
        config = config_manager.get_config()
        log_to_file(f"Mailbox: {config['imap_username']}")
        log_to_file(f"Folder: {config['mailbox']}")
        
        self.update_status("Starting...")
        
        while self.running:
            try:
                config = config_manager.get_config()
                
                # Cleanup check
                if self.temp_manager.should_cleanup(config['temp_file_cleanup_hours'], config.get('temp_file_cleanup_enabled', True)):
                    self.update_status("Cleaning up old temp files...")
                    self.temp_manager.cleanup_old_files(config['temp_file_cleanup_hours'])
                    self.stats['last_cleanup'] = datetime.now().strftime("%H:%M:%S")
                    next_cleanup = datetime.now() + timedelta(hours=config['temp_file_cleanup_hours'])
                    self.stats['next_cleanup'] = next_cleanup.strftime("%H:%M:%S")
                
                # Reconnect
                self.disconnect()
                if not self.connect():
                    time.sleep(10)
                    continue

                # Search for emails - set scanning status
                self.update_status("Scanning inbox...")
                uids = self.search_candidate_uids()
                self.stats['messages_found'] = len(uids)
                
                new_uids = [uid for uid in uids if uid.decode("ascii", errors="ignore") not in self.printed_uids]
                self.stats['jobs_pending'] = len(new_uids)
                
                if new_uids:
                    log_to_file(f"Found {len(new_uids)} new message(s) to process")
                
                self.update_status("Processing messages...")

                for uid_bytes in new_uids:
                    if not self.running:
                        break
                    try:
                        self.process_message(uid_bytes)
                    except Exception as e:
                        self.add_error(f"Error processing UID")

                self.stats['jobs_pending'] = 0
                self.stats['last_check'] = datetime.now().strftime("%H:%M:%S")
                next_time = datetime.now() + timedelta(seconds=config['poll_interval_seconds'])
                self.stats['next_check'] = next_time.strftime("%H:%M:%S")
                
                self.update_status("Idle - Waiting for next check")

            except imaplib.IMAP4.error as e:
                self.add_error(f"IMAP error")
                self.update_status("IMAP error - Reconnecting...")
                self.disconnect()
                time.sleep(10)
                continue
            except Exception as e:
                self.add_error(f"Unexpected error")
                self.update_status("Error - Retrying...")
                time.sleep(10)
                continue

            # Wait for next poll interval
            for _ in range(config['poll_interval_seconds']):
                if not self.running:
                    break
                time.sleep(1)
        
        log_to_file("Service stopped")
        self.update_status("Stopped")

    def stop(self):
        """Stop the daemon."""
        self.running = False
        self.disconnect()
        self.temp_manager.cleanup_all_files()
        log_to_file("Service stopped cleanly")

# ==========================
# Flask Routes
# ==========================

@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('index.html')

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration."""
    config = config_manager.get_config()
    # Don't send password to frontend
    safe_config = config.copy()
    safe_config['imap_password'] = '***' if config['imap_password'] else ''
    return jsonify(safe_config)

@app.route('/api/config', methods=['POST'])
def update_config():
    """Update configuration."""
    try:
        new_config = request.json
        
        # If password is unchanged (***), keep the existing one
        if new_config.get('imap_password') == '***':
            current_config = config_manager.get_config()
            new_config['imap_password'] = current_config['imap_password']
        
        config_manager.save_config(new_config)
        
        # Restart daemon if running
        global daemon
        if daemon and daemon.running:
            daemon.stop()
            time.sleep(1)
            start_daemon()
        
        return jsonify({"success": True, "message": "Configuration saved successfully"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current daemon status."""
    if daemon:
        return jsonify({
            "running": daemon.running,
            "status": daemon.status,
            "stats": daemon.stats
        })
    return jsonify({
        "running": False,
        "status": "Stopped",
        "stats": {}
    })

@app.route('/api/start', methods=['POST'])
def start_service():
    """Start the daemon."""
    try:
        start_daemon()
        return jsonify({"success": True, "message": "Service started"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/stop', methods=['POST'])
def stop_service():
    """Stop the daemon."""
    try:
        global daemon
        if daemon:
            daemon.stop()
        return jsonify({"success": True, "message": "Service stopped"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/test-connection', methods=['POST'])
def test_connection():
    """Test IMAP connection."""
    try:
        config = request.json
        
        if config['imap_use_ssl']:
            conn = imaplib.IMAP4_SSL(config['imap_host'], config['imap_port'])
        else:
            conn = imaplib.IMAP4(config['imap_host'], config['imap_port'])
        
        conn.login(config['imap_username'], config['imap_password'])
        conn.select(config['mailbox'])
        conn.close()
        conn.logout()
        
        return jsonify({"success": True, "message": "Connection successful!"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Get recent log entries."""
    try:
        config = config_manager.get_config()
        log_file = config.get('log_file', 'flowprint.log')
        
        if not os.path.exists(log_file):
            return jsonify({"logs": []})
        
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            # Return last 100 lines
            recent_lines = lines[-100:] if len(lines) > 100 else lines
            return jsonify({"logs": [line.strip() for line in recent_lines]})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/reprint', methods=['POST'])
def reprint_job():
    """Reprint a previous job."""
    try:
        data = request.json
        temp_file = data.get('temp_file')
        
        if not temp_file or not os.path.exists(temp_file):
            return jsonify({"success": False, "error": "Print file not found or has been cleaned up"}), 404
        
        config = config_manager.get_config()
        printer = ChromePrinter()
        
        printer.print_html_file(
            temp_file,
            auto_print=config['auto_print_enabled'],
            chrome_path=config['chrome_path'],
            wait_seconds=config['chrome_print_wait_seconds']
        )
        
        log_to_file(f"Reprinted job from {temp_file}", "SUCCESS")
        return jsonify({"success": True, "message": "Job reprinted successfully"})
    except Exception as e:
        log_to_file(f"Reprint failed: {str(e)}", "ERROR")
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/manual-check', methods=['POST'])
def manual_check():
    """Manually trigger an inbox check."""
    try:
        global daemon
        if not daemon or not daemon.running:
            return jsonify({"success": False, "error": "Service is not running"}), 400
        
        # Trigger an immediate check by setting next check to now
        daemon.stats['last_check'] = datetime.now().strftime("%H:%M:%S")
        daemon.stats['next_check'] = datetime.now().strftime("%H:%M:%S")
        
        log_to_file("Manual inbox check triggered", "INFO")
        return jsonify({"success": True, "message": "Inbox check triggered"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/clear-cache', methods=['POST'])
def clear_cache():
    """Manually clear temp file cache."""
    try:
        global daemon
        if daemon:
            daemon.temp_manager.cleanup_all_files()
            daemon.stats['last_cleanup'] = datetime.now().strftime("%H:%M:%S")
            
            # Update all jobs to mark them as non-reprintable
            for job in daemon.stats.get('recent_jobs', []):
                job['can_reprint'] = False
            
            daemon.emit_status_update()
        else:
            # If daemon doesn't exist, clean up manually
            temp_dir = os.path.join(tempfile.gettempdir(), "flowprint_jobs")
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                os.makedirs(temp_dir, exist_ok=True)
        
        log_to_file("Temp file cache cleared manually", "SUCCESS")
        return jsonify({"success": True, "message": "Cache cleared successfully"})
    except Exception as e:
        log_to_file(f"Cache clear failed: {str(e)}", "ERROR")
        return jsonify({"success": False, "error": str(e)}), 400

# ==========================
# WebSocket Events
# ==========================

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    print('Client connected')
    # Send current status
    if daemon:
        emit('status_update', {
            'status': daemon.status,
            'stats': daemon.stats
        })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    print('Client disconnected')

# ==========================
# Daemon Management
# ==========================

def start_daemon():
    """Start the daemon in a background thread."""
    global daemon, daemon_thread
    
    config = config_manager.get_config()
    
    # Validate configuration
    if not config['imap_username'] or not config['imap_password']:
        raise ValueError("Email credentials not configured")
    
    if daemon and daemon.running:
        return
    
    daemon = ImapPrintDaemon()
    daemon_thread = threading.Thread(target=daemon.run, daemon=True)
    daemon_thread.start()

def auto_start_daemon():
    """Auto-start daemon if credentials are configured."""
    config = config_manager.get_config()
    if config['imap_username'] and config['imap_password']:
        try:
            start_daemon()
            print("✓ Service auto-started")
        except Exception as e:
            print(f"⚠ Could not auto-start service: {e}")

# ==========================
# Main Entry Point
# ==========================

def open_browser():
    """Open the web browser to the dashboard."""
    time.sleep(1.5)  # Wait for server to start
    webbrowser.open('http://127.0.0.1:5000')

def main():
    import logging
    
    # Disable Flask/Werkzeug logging to console
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    
    print()
    print("=" * 80)
    print("  ███████╗██╗      ██████╗ ██╗    ██╗██████╗ ██████╗ ██╗███╗   ██╗████████╗")
    print("  ██╔════╝██║     ██╔═══██╗██║    ██║██╔══██╗██╔══██╗██║████╗  ██║╚══██╔══╝")
    print("  █████╗  ██║     ██║   ██║██║ █╗ ██║██████╔╝██████╔╝██║██╔██╗ ██║   ██║   ")
    print("  ██╔══╝  ██║     ██║   ██║██║███╗██║██╔═══╝ ██╔══██╗██║██║╚██╗██║   ██║   ")
    print("  ██║     ███████╗╚██████╔╝╚███╔███╔╝██║     ██║  ██║██║██║ ╚████║   ██║   ")
    print("  ╚═╝     ╚══════╝ ╚═════╝  ╚══╝╚══╝ ╚═╝     ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝   ╚═╝   ")
    print()
    print("  🖨️  Automatic Email-to-Print Service with Web Interface  🖨️")
    print("=" * 80)
    print()
    print("🌐 Starting web server...")
    print("📡 Dashboard: http://127.0.0.1:5000")
    print()
    print("✨ Opening dashboard in your browser...")
    print()
    
    # Auto-start daemon if configured
    auto_start_daemon()
    
    # Open browser
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    # Start Flask server with minimal logging
    try:
        socketio.run(app, host='127.0.0.1', port=5000, debug=False, use_reloader=False, log_output=False)
    except KeyboardInterrupt:
        print()
        print("🛑 Shutting down...")
        if daemon:
            daemon.stop()
        print("✓ FlowPrint stopped cleanly")
        print()

if __name__ == "__main__":
    main()