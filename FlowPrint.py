#!/usr/bin/env python3
"""
FlowPrint.py - Automatic Email-to-Print Service

Monitors an IMAP mailbox and automatically prints HTML-formatted emails
with a specified subject prefix using Google Chrome.

Perfect for automated printing of Shopify orders, receipts, labels, and more.

License: GNU General Public License v3.0
Repository: https://github.com/yourusername/flowprint
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
from datetime import datetime, timedelta
from email.header import decode_header

# Try to import colorama for colored console output
try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False
    print("Note: Install colorama for colored output: pip install colorama")

# ==========================
# CONFIGURATION
# ==========================

# Email Server Settings
IMAP_HOST = "imap.gmail.com"              # Your IMAP server hostname
IMAP_PORT = 993                            # IMAP port (usually 993 for SSL)
IMAP_USE_SSL = True                        # Use SSL encryption (recommended)
IMAP_USERNAME = "your-email@example.com"   # Your email address
IMAP_PASSWORD = "your-app-password"        # Your email password or app-specific password

# Email Monitoring Settings
MAILBOX = "Inbox"                          # Mailbox folder to monitor
POLL_INTERVAL_SECONDS = 30                 # How often to check for new emails (seconds)
SUBJECT_PREFIX = "[PRINT PACK]"            # Only print emails with subjects starting with this

# Printing Settings
AUTO_PRINT_ENABLED = True                  # True = auto-print, False = open print dialog
CHROME_PATH = ""                           # Leave blank for auto-detection, or specify path to chrome.exe
CHROME_PRINT_WAIT_SECONDS = 8              # How long to wait for Chrome to print before closing

# File Management
PRINTED_UIDS_FILE = "printed_uids.txt"     # File to track processed emails (prevents duplicates)
TEMP_FILE_CLEANUP_HOURS = 6                # Clean up temp files older than this many hours

# Email Management (USE WITH CAUTION!)
# When enabled, emails will be PERMANENTLY DELETED from inbox after successful print
# If print fails, email is NOT deleted and remains in inbox for retry
DELETE_EMAIL_AFTER_PRINT = False           # Set to True to delete emails after printing

# Logging
LOG_FILE = "flowprint.log"                 # Log file for debugging and audit trail
DEBUG = False                              # Enable debug output

# ==========================
# Logging Helper
# ==========================

def log_to_file(message, level="INFO"):
    """Write log entry to file with timestamp."""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except:
        pass  # Fail silently if logging fails

# ==========================
# Color Helpers
# ==========================

def strip_ansi(text):
    """Remove ANSI escape codes from text for length calculation."""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def red(text):
    """Apply red color."""
    if not COLORAMA_AVAILABLE:
        return text
    return Fore.RED + Style.BRIGHT + text + Style.RESET_ALL

def white(text):
    """Apply white color."""
    if not COLORAMA_AVAILABLE:
        return text
    return Fore.WHITE + text + Style.RESET_ALL

def dim_white(text):
    """Apply dim white color."""
    if not COLORAMA_AVAILABLE:
        return text
    return Fore.WHITE + Style.DIM + text + Style.RESET_ALL

# ==========================
# Console UI
# ==========================

class ConsoleUI:
    def __init__(self):
        self.status = "Initializing..."
        self.last_check = "Never"
        self.next_check = "Pending..."
        self.messages_found = 0
        self.jobs_processed = 0
        self.jobs_pending = 0
        self.auto_print_status = "Enabled ✓" if AUTO_PRINT_ENABLED else "Manual Mode 👤"
        self.last_cleanup = "Never"
        self.next_cleanup = "Calculating..."
        self.errors = []
        self.recent_jobs = []
        self.lock = threading.Lock()
        self.countdown_remaining = 0
        self.countdown_total = POLL_INTERVAL_SECONDS
        self.animation_frame = 0
        self.terminal_width = self.get_terminal_width()
        
    def get_terminal_width(self):
        """Get the current terminal width."""
        try:
            return shutil.get_terminal_size().columns
        except:
            return 120  # Default fallback
        
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def update_status(self, status):
        with self.lock:
            self.status = status
            log_to_file(f"Status: {status}")
    
    def update_check_time(self):
        with self.lock:
            self.last_check = datetime.now().strftime("%H:%M:%S")
            next_time = datetime.now() + timedelta(seconds=POLL_INTERVAL_SECONDS)
            self.next_check = next_time.strftime("%H:%M:%S")
    
    def update_cleanup_time(self, last_cleanup_time):
        with self.lock:
            self.last_cleanup = last_cleanup_time.strftime("%H:%M:%S")
            next_time = last_cleanup_time + timedelta(hours=TEMP_FILE_CLEANUP_HOURS)
            self.next_cleanup = next_time.strftime("%H:%M:%S")
    
    def set_messages_found(self, count):
        with self.lock:
            self.messages_found = count
    
    def increment_processed(self):
        with self.lock:
            self.jobs_processed += 1
    
    def set_pending(self, count):
        with self.lock:
            self.jobs_pending = count
    
    def set_countdown(self, remaining, total):
        with self.lock:
            self.countdown_remaining = remaining
            self.countdown_total = total
            self.animation_frame += 1
    
    def add_job(self, subject, action):
        with self.lock:
            timestamp = datetime.now().strftime("%H:%M:%S")
            job_entry = f"[{timestamp}] {subject[:50]} - {action}"
            self.recent_jobs.insert(0, job_entry)
            self.recent_jobs = self.recent_jobs[:3]  # Keep only last 3
            
            # Log to file with full details
            log_to_file(f"Job processed: {subject} - {action}", "SUCCESS")
    
    def add_error(self, error_msg):
        with self.lock:
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.errors.insert(0, f"[{timestamp}] {error_msg}")
            self.errors = self.errors[:3]
            
            # Log to file
            log_to_file(error_msg, "ERROR")
    
    def create_progress_bar(self, elapsed, total, width=None):
        """Create a sleek gradient progress bar."""
        if width is None:
            width = min(self.terminal_width - 20, 100)
            
        progress = elapsed / total if total > 0 else 0
        filled = int(width * progress)
        percentage = int(progress * 100)
        
        if not COLORAMA_AVAILABLE:
            bar = "█" * filled + "░" * (width - filled)
            return f"[{bar}] {percentage}%"
        
        # Create smooth gradient bar
        bar = ""
        for i in range(width):
            if i < filled:
                bar += red("█")
            else:
                bar += Fore.RED + Style.DIM + "▒" + Style.RESET_ALL
        
        return f"{red('[')} {bar} {red(']')} {red(str(percentage) + '%')}"
    
    def get_status_emoji(self):
        emojis = ["⚡", "✨", "🔥", "💫"]
        return emojis[self.animation_frame % len(emojis)]
    
    def separator(self, char="━"):
        """Create a full-width red separator line."""
        return red(char * self.terminal_width)
    
    def thin_separator(self, char="─"):
        """Create a full-width thin red separator line."""
        return red(char * self.terminal_width)
    
    def center_text(self, text):
        """Center text within terminal width."""
        visible_len = len(strip_ansi(text))
        padding = (self.terminal_width - visible_len) // 2
        return " " * padding + text
    
    def render(self):
        with self.lock:
            self.clear_screen()
            
            # Update terminal width
            self.terminal_width = self.get_terminal_width()
            
            print()
            print()
            
            # Title - centered
            print(self.center_text(red("    ███████╗██╗      ██████╗ ██╗    ██╗██████╗ ██████╗ ██╗███╗   ██╗████████╗")))
            print(self.center_text(red("    ██╔════╝██║     ██╔═══██╗██║    ██║██╔══██╗██╔══██╗██║████╗  ██║╚══██╔══╝")))
            print(self.center_text(red("    █████╗  ██║     ██║   ██║██║ █╗ ██║██████╔╝██████╔╝██║██╔██╗ ██║   ██║   ")))
            print(self.center_text(red("    ██╔══╝  ██║     ██║   ██║██║███╗██║██╔═══╝ ██╔══██╗██║██║╚██╗██║   ██║   ")))
            print(self.center_text(red("    ██║     ███████╗╚██████╔╝╚███╔███╔╝██║     ██║  ██║██║██║ ╚████║   ██║   ")))
            print(self.center_text(red("    ╚═╝     ╚══════╝ ╚═════╝  ╚══╝╚══╝ ╚═╝     ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝   ╚═╝   ")))
            print(self.center_text(red("🖨️  Automatic Email-to-Print Service  🖨️")))
            print()
            
            # Full-width separator
            print(self.separator())
            print()
            
            # System Info - with left margin
            margin = "    "
            print(margin + red("📧 Mailbox: ") + white(IMAP_USERNAME))
            print(margin + red("📁 Folder: ") + white(MAILBOX))
            print(margin + red("🔍 Filter: ") + white(SUBJECT_PREFIX))
            print(margin + red("🖨️  Mode: ") + white(self.auto_print_status))
            delete_status = "Enabled ⚠️" if DELETE_EMAIL_AFTER_PRINT else "Disabled ✓"
            print(margin + red("🗑️  Delete After Print: ") + white(delete_status))
            print()
            
            # Thin separator
            print(self.thin_separator())
            print()
            
            # Status
            emoji = self.get_status_emoji()
            print(margin + red(f"{emoji} Status: ") + white(self.status))
            print(margin + red("🕐 Last Check: ") + white(self.last_check))
            print(margin + red("🕑 Next Check: ") + white(self.next_check))
            
            # Progress bar
            if self.countdown_remaining > 0:
                elapsed = self.countdown_total - self.countdown_remaining
                progress = self.create_progress_bar(elapsed, self.countdown_total)
                print(margin + red(f"⏱️  Next Check In: {self.countdown_remaining}s"))
                print(margin + progress)
            print()
            
            # Thin separator
            print(self.thin_separator())
            print()
            
            # Statistics
            print(margin + red("📊 Messages Found: ") + white(str(self.messages_found)))
            print(margin + red("✅ Jobs Processed: ") + white(str(self.jobs_processed)))
            print(margin + red("⏳ Jobs Pending: ") + white(str(self.jobs_pending)))
            print()
            
            # Thin separator
            print(self.thin_separator())
            print()
            
            # Cleanup
            print(margin + red("🧹 Last Cleanup: ") + white(self.last_cleanup))
            print(margin + red("🕐 Next Cleanup: ") + white(self.next_cleanup))
            print()
            
            # Thin separator
            print(self.thin_separator())
            print()
            
            # Recent Jobs (only last 3)
            print(margin + red("📋 Recent Jobs:"))
            if self.recent_jobs:
                for job in self.recent_jobs:
                    print(margin + f"   {dim_white('•')} {white(job)}")
            else:
                print(margin + f"   {dim_white('No jobs processed yet.')}")
            print()
            
            # Errors
            if self.errors:
                print(self.thin_separator())
                print()
                print(margin + red("⚠️  Recent Errors:"))
                for error in self.errors:
                    print(margin + f"   {red('•')} {red(error)}")
                print()
            
            # Footer separator
            print(self.separator())
            print(self.center_text(red("Press Ctrl+C to exit")))
            print()


# ==========================
# Chrome Printer
# ==========================

class ChromePrinter:
    def __init__(self, ui):
        self.ui = ui
        self.chrome_path = self._resolve_chrome_path()

    def _resolve_chrome_path(self):
        if CHROME_PATH and os.path.exists(CHROME_PATH):
            return CHROME_PATH
        
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
        
        raise FileNotFoundError("Could not find Chrome. Set CHROME_PATH in config.")

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

    def print_html_file(self, html_path, auto_print=True):
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
                time.sleep(CHROME_PRINT_WAIT_SECONDS)
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
    def __init__(self, ui):
        self.ui = ui
        self.temp_dir = os.path.join(tempfile.gettempdir(), "flowprint_jobs")
        os.makedirs(self.temp_dir, exist_ok=True)
        self.tracked_files = {}
        self.last_cleanup = datetime.now()
        ui.update_cleanup_time(self.last_cleanup)
        
    def create_temp_file(self, subject, html_content):
        safe_label = "".join(c for c in subject if c.isalnum() or c in ("-", "_", " "))[:40]
        filename = (safe_label or "FlowPrint") + f"_{uuid.uuid4().hex[:8]}.html"
        temp_path = os.path.join(self.temp_dir, filename)
        
        with open(temp_path, "w", encoding="utf-8", errors="ignore") as f:
            f.write(html_content)
        
        self.tracked_files[temp_path] = datetime.now()
        return temp_path
    
    def should_cleanup(self):
        elapsed = datetime.now() - self.last_cleanup
        return elapsed.total_seconds() >= (TEMP_FILE_CLEANUP_HOURS * 3600)
    
    def cleanup_old_files(self):
        now = datetime.now()
        cutoff = now - timedelta(hours=TEMP_FILE_CLEANUP_HOURS)
        
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
            self.ui.update_cleanup_time(self.last_cleanup)
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
# IMAP Daemon
# ==========================

class ImapPrintDaemon:
    def __init__(self):
        self.conn = None
        self.ui = ConsoleUI()
        self.chrome_printer = ChromePrinter(self.ui)
        self.temp_manager = TempFileManager(self.ui)
        self.printed_uids = set()
        self._load_printed_uids()
        
        # Log startup
        log_to_file("=" * 80)
        log_to_file("FlowPrint Service Started")
        log_to_file(f"Mailbox: {IMAP_USERNAME}")
        log_to_file(f"Folder: {MAILBOX}")
        log_to_file(f"Auto-Print: {AUTO_PRINT_ENABLED}")
        log_to_file(f"Delete After Print: {DELETE_EMAIL_AFTER_PRINT}")

    def _load_printed_uids(self):
        if os.path.exists(PRINTED_UIDS_FILE):
            with open(PRINTED_UIDS_FILE, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    uid = line.strip()
                    if uid:
                        self.printed_uids.add(uid)

    def _save_printed_uid(self, uid):
        self.printed_uids.add(uid)
        with open(PRINTED_UIDS_FILE, "a", encoding="utf-8", errors="ignore") as f:
            f.write(uid + "\n")

    def connect(self):
        self.ui.update_status("Connecting to mailbox... 🔌")
        self.ui.render()
        
        if IMAP_USE_SSL:
            self.conn = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
        else:
            self.conn = imaplib.IMAP4(IMAP_HOST, IMAP_PORT)
        
        self.conn.login(IMAP_USERNAME, IMAP_PASSWORD)
        self.conn.select(MAILBOX)
        self.ui.update_status("Connected ✓")
        log_to_file("Connected to mailbox successfully")

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
        """Delete email from inbox after successful print. Only called when DELETE_EMAIL_AFTER_PRINT is True."""
        try:
            uid = uid_bytes.decode("ascii", errors="ignore")
            # Mark email for deletion
            self.conn.uid("store", uid_bytes, "+FLAGS", "\\Deleted")
            # Permanently expunge (delete) marked emails
            self.conn.expunge()
            log_to_file(f"Email UID {uid} deleted from inbox", "SUCCESS")
            return True
        except Exception as e:
            log_to_file(f"Failed to delete email UID: {str(e)}", "ERROR")
            return False

    def search_candidate_uids(self):
        self.ui.update_status("Searching for messages... 🔍")
        self.ui.render()
        
        criteria = f'(SUBJECT "{SUBJECT_PREFIX}")'
        status, data = self.conn.uid("search", None, criteria)

        if status != "OK" or not data or not data[0]:
            return []
        
        return data[0].split()

    def process_message(self, uid_bytes):
        uid = uid_bytes.decode("ascii", errors="ignore")
        if uid in self.printed_uids:
            return

        self.ui.update_status(f"Processing message UID {uid}... ⚙️")
        self.ui.render()
        
        status, data = self.conn.uid("fetch", uid_bytes, "(RFC822)")
        if status != "OK" or not data or not data[0]:
            self.ui.add_error(f"Failed to fetch UID {uid}")
            return

        raw = data[0][1]
        msg = email.message_from_bytes(raw)
        subject = get_subject(msg)

        if not subject_matches_prefix(subject, SUBJECT_PREFIX):
            self._save_printed_uid(uid)
            return

        html_body = get_best_body(msg)
        temp_path = self.temp_manager.create_temp_file(subject, html_body)

        print_successful = False

        if AUTO_PRINT_ENABLED:
            try:
                self.chrome_printer.print_html_file(temp_path, auto_print=True)
                self.ui.add_job(subject, "Auto-printed ✓")
                self.ui.increment_processed()
                print_successful = True
            except Exception as e:
                error_msg = f"Print failed: {str(e)[:50]}"
                self.ui.add_error(error_msg)
                log_to_file(f"Print failed for '{subject}': {str(e)}", "ERROR")
                print_successful = False
        else:
            try:
                self.chrome_printer.print_html_file(temp_path, auto_print=False)
                self.ui.add_job(subject, "Print dialog opened 🖨️")
                self.ui.increment_processed()
                print_successful = True
            except Exception as e:
                error_msg = f"Failed to open dialog: {str(e)[:50]}"
                self.ui.add_error(error_msg)
                log_to_file(f"Failed to open dialog for '{subject}': {str(e)}", "ERROR")
                print_successful = False

        # Only delete email if print was successful AND delete is enabled
        if print_successful and DELETE_EMAIL_AFTER_PRINT:
            if self.delete_email(uid_bytes):
                log_to_file(f"Email '{subject}' printed successfully and deleted from inbox", "SUCCESS")
            else:
                self.ui.add_error(f"Print succeeded but failed to delete email")

        # Always mark as seen and save UID
        self.mark_seen(uid_bytes)
        self._save_printed_uid(uid)

    def mark_seen(self, uid_bytes):
        try:
            self.conn.uid("store", uid_bytes, "+FLAGS", "\\Seen")
        except:
            pass

    def run_forever(self):
        self.ui.render()
        
        while True:
            try:
                if self.temp_manager.should_cleanup():
                    self.ui.update_status("Cleaning up old temp files... 🧹")
                    self.ui.render()
                    self.temp_manager.cleanup_old_files()
                
                self.disconnect()
                self.connect()

                uids = self.search_candidate_uids()
                self.ui.set_messages_found(len(uids))
                
                new_uids = [uid for uid in uids if uid.decode("ascii", errors="ignore") not in self.printed_uids]
                self.ui.set_pending(len(new_uids))
                
                if new_uids:
                    log_to_file(f"Found {len(new_uids)} new message(s) to process")
                
                self.ui.update_status("Processing messages... ⚙️")
                self.ui.render()

                for uid_bytes in new_uids:
                    try:
                        self.process_message(uid_bytes)
                    except Exception as e:
                        self.ui.add_error(f"Error processing UID")
                        log_to_file(f"Error processing UID: {str(e)}", "ERROR")

                self.ui.set_pending(0)
                self.ui.update_status("Idle - Waiting for next check 😴")
                self.ui.update_check_time()

            except imaplib.IMAP4.error as e:
                self.ui.add_error(f"IMAP error")
                self.ui.update_status("IMAP error - Reconnecting... ⚠️")
                self.ui.render()
                log_to_file(f"IMAP error: {str(e)}", "ERROR")
                self.disconnect()
                time.sleep(10)
                continue
            except Exception as e:
                self.ui.add_error(f"Unexpected error")
                self.ui.update_status("Error - Retrying... ⚠️")
                self.ui.render()
                log_to_file(f"Unexpected error: {str(e)}", "ERROR")
                time.sleep(10)
                continue

            for remaining in range(POLL_INTERVAL_SECONDS, 0, -1):
                self.ui.set_countdown(remaining, POLL_INTERVAL_SECONDS)
                self.ui.render()
                time.sleep(1)
            
            self.ui.set_countdown(0, POLL_INTERVAL_SECONDS)


# ==========================
# Entry Point
# ==========================

def main():
    daemon = ImapPrintDaemon()
    try:
        daemon.run_forever()
    except KeyboardInterrupt:
        daemon.ui.clear_screen()
        print()
        term_width = daemon.ui.terminal_width
        if COLORAMA_AVAILABLE:
            print(red("━" * term_width))
            print((" " * ((term_width - 20) // 2)) + red("🛑 SHUTTING DOWN..."))
            print(red("━" * term_width))
            print()
            print(red("🧹 Cleaning up temporary files..."))
        else:
            print("=" * term_width)
            print(" SHUTTING DOWN...".center(term_width))
            print("=" * term_width)
            print()
            print("Cleaning up temporary files...")
        
        log_to_file("Service shutting down (user initiated)")
        daemon.temp_manager.cleanup_all_files()
        
        if COLORAMA_AVAILABLE:
            print(red("📡 Disconnecting from mailbox..."))
            print()
            print(red("✓ FlowPrint stopped cleanly."))
            print(red("👋 Goodbye!"))
            print()
        else:
            print("Disconnecting from mailbox...")
            print()
            print("✓ FlowPrint stopped cleanly.")
            print()
        
        daemon.disconnect()
        log_to_file("Service stopped cleanly")
        log_to_file("=" * 80)


if __name__ == "__main__":
    main()
