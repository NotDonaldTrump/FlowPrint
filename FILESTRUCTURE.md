# 📁 FlowPrint File Structure

This document describes the complete file structure of the FlowPrint repository and explains what each file does.

---

## 📂 Repository Overview

```
FlowPrint/
│
├── 📄 FlowPrint.py                          # Main application file
├── 📄 requirements.txt                       # Python dependencies
│
├── 📋 README.md                              # Main documentation
├── 📋 INSTALLATION.md                        # Installation guide
├── 📋 SECURITY.md                            # Security guidelines
├── 📋 FILE_STRUCTURE.md                      # This file
├── 📋 CONTRIBUTING.md                        # Contribution guidelines
├── 📄 LICENSE                                # GPL-3.0 License
│
├── 📄 example-shopify-flow-email-template.html  # Sample Shopify Flow template
│
├── 📂 templates/                             # HTML templates for web interface
│   └── index.html                           # Main dashboard template
│
└── 📂 static/                                # Static web assets
    ├── 📂 css/                              # Stylesheets
    │   └── style.css                        # Main dashboard styles
    └── 📂 js/                               # JavaScript files
        └── app.js                           # Dashboard functionality
```

---

## 📄 Core Application Files

### `FlowPrint.py`
**The main application file** - Contains all FlowPrint functionality:

- **Configuration Management**: Loads/saves settings from `flowprint_config.json`
- **Email Monitoring**: Connects to IMAP server and monitors inbox
- **Printing Logic**: Handles Chrome printing via subprocess
- **Web Dashboard**: Flask web server with SocketIO for real-time updates
- **Logging System**: Writes activity logs to `flowprint.log`
- **Dependency Checker**: Auto-installs missing Python packages on first run

**Key Components:**
- `ConfigManager` class - Manages configuration
- `ChromePrinter` class - Handles printing operations
- `EmailDaemon` class - IMAP monitoring and processing
- Flask routes - Web dashboard endpoints
- SocketIO handlers - Real-time dashboard updates

### `requirements.txt`
**Python dependencies list:**
```
Flask==3.0.0
flask-socketio==5.3.5
python-socketio==5.10.0
python-engineio==4.8.0
Werkzeug==3.0.1
```

These are automatically installed when you run `FlowPrint.py` for the first time.

---

## 📋 Documentation Files

### `README.md`
**Main documentation** - The first file users should read:
- What FlowPrint is and how it works
- Quick start guide
- Installation instructions
- Configuration guide
- Shopify integration steps
- Email server setup (Gmail, Outlook, etc.)
- Running as a service
- Troubleshooting
- FAQ
- Security best practices

### `INSTALLATION.md`
**Detailed installation guide** for different environments:
- Prerequisites and system requirements
- First-time setup process
- Manual mode configuration
- Testing and validation
- Production deployment
- Running as a system service (Windows, Linux, macOS)
- Headless server setup
- Docker deployment (optional)

### `SECURITY.md`
**Security guidelines and best practices:**
- Email credential protection
- Configuration file security
- Physical security considerations
- Network security
- Compliance considerations (GDPR, PCI-DSS)
- Incident response
- Security updates

### `FILE_STRUCTURE.md`
**This file** - Documents the repository structure and file purposes.

### `CONTRIBUTING.md`
**Contribution guidelines** for developers:
- How to contribute
- Code style guidelines
- Testing requirements
- Pull request process
- Issue reporting
- Feature requests

### `LICENSE`
**GNU General Public License v3.0** - Legal terms for using and distributing FlowPrint.

---

## 🛍️ Shopify Integration

### `example-shopify-flow-email-template.html`
**Complete Shopify Flow email template** with three pages:

**Page 1: Staff Summary**
- Order number and basic details
- Customer information
- Order totals
- Payment and shipping status

**Page 2: Packing List**
- Detailed item list with SKUs
- Quantities and prices
- Line item notes
- Order notes for staff

**Page 3: Shipping Label**
- Large, easy-to-read shipping address
- Customer contact information
- Special delivery instructions

**Customization:**
- Uses Shopify Liquid template language
- Fully customizable HTML/CSS
- Includes print-specific media queries
- Page break support

---

## 🎨 Web Dashboard Files

### `templates/index.html`
**Main dashboard template** - Single-page web application:

**Features:**
- Real-time service status display
- Configuration interface with tabs
- Live statistics and job monitoring
- Theme toggle (dark/light mode)
- Manual email check button
- Start/Stop service controls

**Sections:**
- Header with controls
- Status banner
- Configuration panel (3 tabs: Email, Behavior, Advanced)
- Statistics display
- Recent jobs list

### `static/css/style.css`
**Dashboard stylesheet:**
- Modern, clean design
- Dark and light theme support
- Responsive layout
- Custom form styling
- Status indicators and animations
- Print-friendly media queries

### `static/js/app.js`
**Dashboard JavaScript:**
- SocketIO connection management
- Real-time status updates
- Configuration save/load
- Tab switching
- Theme persistence
- Manual check functionality
- Statistics updates

---

## 🗂️ Generated Files

These files are created automatically by FlowPrint:

### `flowprint_config.json`
**User configuration file** - Created on first save:
```json
{
  "imap_host": "imap.gmail.com",
  "imap_port": 993,
  "imap_use_ssl": true,
  "imap_username": "your-email@example.com",
  "imap_password": "app-password",
  "mailbox": "Inbox",
  "poll_interval_seconds": 30,
  "subject_prefix": "[PRINT PACK]",
  "auto_print_enabled": true,
  "delete_email_after_print": false,
  "chrome_path": "",
  "chrome_print_wait_seconds": 8,
  "temp_file_cleanup_enabled": true,
  "temp_file_cleanup_hours": 6,
  "printed_uids_file": "printed_uids.txt",
  "log_file": "flowprint.log",
  "theme": "dark"
}
```

**Security Note:** This file contains your email password. Keep it secure!

### `flowprint.log`
**Activity log file** - Records all FlowPrint operations:
```
[2024-11-18 14:30:22] [INFO] Service started
[2024-11-18 14:30:25] [SUCCESS] Connected to imap.gmail.com
[2024-11-18 14:31:10] [SUCCESS] Printed: Order #1234
[2024-11-18 14:32:00] [ERROR] Print failed: Chrome timeout
```

**Log Levels:**
- `INFO` - General information
- `SUCCESS` - Successful operations
- `WARNING` - Non-critical issues
- `ERROR` - Errors that need attention

### `printed_uids.txt`
**Printed email tracking file** - Prevents duplicate prints:
```
12345
12346
12347
```

Each line is an email UID that has been successfully printed. FlowPrint checks this file before printing to avoid duplicates.

**Important:** Don't delete this file unless you want to reprint all emails!

### `temp_*.html` files
**Temporary HTML files** - Created in system temp directory:
- Created when printing each email
- Contains the extracted HTML body
- Automatically cleaned up based on config settings
- Default cleanup interval: 6 hours

---

## 🔧 File Permissions

### Recommended Permissions

**Linux/macOS:**
```bash
# Configuration file (contains password)
chmod 600 flowprint_config.json

# Log file (readable by user only)
chmod 644 flowprint.log

# Main script (executable)
chmod 755 FlowPrint.py

# Printed UIDs (read/write by user only)
chmod 600 printed_uids.txt
```

**Windows:**
- Right-click `flowprint_config.json` → Properties → Security
- Remove all users except your account
- Set to "Read & Write" for your account only

---

## 📦 Deployment Considerations

### What to Include in Version Control

✅ **Include:**
- `FlowPrint.py`
- `requirements.txt`
- All documentation files
- `templates/` folder
- `static/` folder
- `example-shopify-flow-email-template.html`
- `LICENSE`
- `.gitignore`

❌ **Exclude (add to `.gitignore`):**
- `flowprint_config.json` (contains password)
- `flowprint.log` (log file)
- `printed_uids.txt` (tracking file)
- `temp_*.html` (temporary files)
- `__pycache__/` (Python cache)
- `*.pyc` (compiled Python)

### Sample `.gitignore`
```gitignore
# FlowPrint generated files
flowprint_config.json
flowprint.log
printed_uids.txt
temp_*.html

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# OS
.DS_Store
Thumbs.db
```

---

## 🐳 Optional: Docker Deployment

While not included by default, you can create a Docker setup:

### `Dockerfile` (create if needed)
```dockerfile
FROM python:3.11-slim

# Install Chrome
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "FlowPrint.py"]
```

### `docker-compose.yml` (create if needed)
```yaml
version: '3.8'

services:
  flowprint:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./flowprint_config.json:/app/flowprint_config.json
      - ./flowprint.log:/app/flowprint.log
      - ./printed_uids.txt:/app/printed_uids.txt
    restart: unless-stopped
```

---

## 📊 File Size Expectations

Typical file sizes in a running FlowPrint installation:

| File | Typical Size | Notes |
|------|-------------|-------|
| `FlowPrint.py` | ~35 KB | Main application |
| `flowprint_config.json` | ~500 bytes | Configuration |
| `flowprint.log` | Grows over time | Rotatable if needed |
| `printed_uids.txt` | Grows slowly | ~50 bytes per email |
| `requirements.txt` | ~100 bytes | Dependencies list |
| `templates/index.html` | ~12 KB | Dashboard template |
| `static/css/style.css` | ~18 KB | Stylesheet |
| `static/js/app.js` | ~23 KB | JavaScript |

**Maintenance:**
- Log file can grow large over time - consider log rotation
- `printed_uids.txt` grows with each printed email
- Temp files are auto-cleaned by FlowPrint

---

## 🔄 Backup Strategy

### What to Back Up

**Essential (Daily):**
- `flowprint_config.json` - Your settings
- `printed_uids.txt` - Print tracking

**Important (Weekly):**
- `flowprint.log` - Activity history
- Customized template files

**For Disaster Recovery:**
- Entire FlowPrint directory
- Documented printer settings
- Email server configuration details

### Backup Command (Linux/macOS)
```bash
#!/bin/bash
# Simple backup script
tar -czf flowprint-backup-$(date +%Y%m%d).tar.gz \
    flowprint_config.json \
    printed_uids.txt \
    flowprint.log \
    example-shopify-flow-email-template.html
```

---

## 📞 Support

For questions about the file structure or where to find specific functionality:

- 🐛 **Issues**: [GitHub Issues](https://github.com/NotDonaldTrump/FlowPrint/issues)
- 📂 **Repository**: [github.com/NotDonaldTrump/FlowPrint](https://github.com/NotDonaldTrump/FlowPrint)
- 📖 **Documentation**: [README.md](README.md)

---

**Last Updated:** 18/11/2025