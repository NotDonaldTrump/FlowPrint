# 📖 FlowPrint Installation Guide

Complete installation guide for FlowPrint - from first-time setup to production deployment.

---

## 📑 Table of Contents

- [System Requirements](#-system-requirements)
- [Quick Installation](#-quick-installation)
- [First-Time Setup](#-first-time-setup)
- [Testing & Validation](#-testing--validation)
- [Production Deployment](#-production-deployment)
- [Running as a Service](#-running-as-a-service)
- [Headless Server Setup](#-headless-server-setup)
- [Advanced Configuration](#-advanced-configuration)

---

## 💻 System Requirements

### Minimum Requirements

| Component | Requirement | Notes |
|-----------|------------|-------|
| **OS** | Windows 10+, macOS 10.14+, Ubuntu 18.04+ | Any modern OS with Python support |
| **Python** | 3.7 or higher | Check with `python --version` |
| **RAM** | 2 GB available | More if handling high volumes |
| **Disk Space** | 500 MB free | Includes Chrome and dependencies |
| **Browser** | Google Chrome | Must be installed (not Chromium) |
| **Network** | Internet connection | For IMAP and dependency installation |

### Recommended Specifications

| Component | Recommended | Why |
|-----------|------------|-----|
| **RAM** | 4 GB+ | Smooth operation with multiple concurrent prints |
| **CPU** | Dual-core 2.0 GHz+ | Faster Chrome rendering |
| **Disk Space** | 2 GB+ | Log file growth, temp files |
| **Network** | Stable broadband | Reliable email monitoring |

---

## ⚡ Quick Installation

**For experienced users - get up and running in 2 minutes:**

```bash
# Clone repository
git clone https://github.com/NotDonaldTrump/FlowPrint.git
cd FlowPrint

# Run FlowPrint (auto-installs dependencies)
python FlowPrint.py

# Dashboard opens at http://localhost:5000
# Configure settings and click Start!
```

**Done!** Continue reading for detailed setup instructions.

---

## 🔧 First-Time Setup

### Step 1: Install Prerequisites

#### Install Python

**Windows:**
1. Download from [python.org/downloads](https://www.python.org/downloads/)
2. Run installer
3. ✅ **IMPORTANT:** Check "Add Python to PATH"
4. Click "Install Now"
5. Verify installation:
   ```cmd
   python --version
   ```

**macOS:**
```bash
# Using Homebrew (recommended)
brew install python3

# Verify
python3 --version
```

**Linux (Ubuntu/Debian):**
```bash
# Python is usually pre-installed
python3 --version

# If not installed:
sudo apt update
sudo apt install python3 python3-pip
```

#### Install Google Chrome

**Windows & macOS:**
1. Download from [google.com/chrome](https://www.google.com/chrome/)
2. Run installer
3. Install in default location

**Linux:**
```bash
# Ubuntu/Debian
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f

# Or use repository
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
sudo apt update
sudo apt install google-chrome-stable
```

### Step 2: Download FlowPrint

**Option A: Git Clone (Recommended)**
```bash
git clone https://github.com/NotDonaldTrump/FlowPrint.git
cd FlowPrint
```

**Option B: Download ZIP**
1. Go to [github.com/NotDonaldTrump/FlowPrint](https://github.com/NotDonaldTrump/FlowPrint)
2. Click "Code" → "Download ZIP"
3. Extract to your desired location
4. Open terminal/command prompt in extracted folder

### Step 3: First Run

FlowPrint automatically installs dependencies on first run:

```bash
python FlowPrint.py
```

**What happens:**
1. ✅ Checks for missing Python packages
2. ✅ Installs Flask, Flask-SocketIO, etc.
3. ✅ Starts web server
4. ✅ Opens dashboard at `http://localhost:5000`

**Troubleshooting First Run:**

<details>
<summary><b>Python command not found</b></summary>

Try these alternatives:
```bash
python3 FlowPrint.py   # Linux/Mac
py FlowPrint.py        # Windows
py -3 FlowPrint.py     # Windows with multiple Python versions
```
</details>

<details>
<summary><b>Permission denied (Linux/Mac)</b></summary>

Make the script executable:
```bash
chmod +x FlowPrint.py
./FlowPrint.py
```
</details>

<details>
<summary><b>Port 5000 already in use</b></summary>

Another application is using port 5000. Either:
- Stop the other application
- Or edit `FlowPrint.py` and change the port:
  ```python
  socketio.run(app, host='0.0.0.0', port=5001)  # Change to 5001
  ```
</details>

---

## 🎯 Testing & Validation

### Initial Configuration Test

1. **Open Dashboard:**
   - Navigate to `http://localhost:5000`
   - You should see the FlowPrint dashboard

2. **Configure Email Settings:**
   
   **For Gmail:**
   ```
   IMAP Server: imap.gmail.com
   Port: 993
   Use SSL: ✅ Enabled
   Email: your-email@gmail.com
   Password: [your app password]
   Mailbox: Inbox
   ```
   
   [How to create Gmail app password →](../README.md#gmail-configuration)

3. **Configure Behavior:**
   ```
   Polling Interval: 30 seconds (for testing)
   Subject Prefix: [PRINT PACK]
   Auto Print: ❌ DISABLED (for first test)
   Delete After Print: ❌ DISABLED
   ```

4. **Save Configuration:**
   - Click "💾 Save" button
   - Verify success message appears

### First Print Test

**IMPORTANT:** Run your first print in manual mode to configure Chrome print settings!

1. **Disable Auto-Print:**
   - Behavior tab → Auto Print: OFF
   - Save configuration

2. **Start Service:**
   - Click "▶ Start" button
   - Verify status changes to "Running"

3. **Send Test Email:**
   - Send email to your configured address
   - Subject: `[PRINT PACK] Test Order #001`
   - Body: Simple HTML like:
     ```html
     <h1>Test Print</h1>
     <p>This is a test order.</p>
     <p>If you see this printed, FlowPrint is working!</p>
     ```

4. **Configure Chrome Print Dialog:**
   - Chrome print dialog will open
   - Select your printer
   - Choose paper size (Letter or A4)
   - Set margins (usually "Default")
   - Click "Print" or "Save"

5. **Verify Output:**
   - Check if document printed correctly
   - Verify formatting looks good
   - Adjust Chrome settings if needed

### Enable Auto-Print

Once manual printing works perfectly:

1. **Enable Auto-Print:**
   - Stop service (click "■ Stop")
   - Behavior tab → Auto Print: ON
   - Save configuration

2. **Test Auto-Print:**
   - Start service
   - Send another test email
   - Verify it prints automatically without dialog

3. **Monitor Dashboard:**
   - Watch "Messages Found" counter
   - Check "Jobs Processed" increases
   - Review "Recent Jobs" list

---

## 🚀 Production Deployment

### Pre-Production Checklist

Before deploying to production, verify:

- ✅ Email credentials are correct and secure (app password)
- ✅ Test prints look perfect (formatting, margins, etc.)
- ✅ Subject prefix matches Shopify Flow configuration
- ✅ Printer is set as default and always powered on
- ✅ Computer stays powered on 24/7 or auto-starts service
- ✅ Email account has sufficient storage
- ✅ Network connection is stable
- ✅ Firewall allows Python and Chrome
- ✅ Physical printer location is secure

### Production Settings

Recommended settings for production:

```
Polling Interval: 30-60 seconds
Auto Print: ✅ Enabled
Delete After Print: ❌ Disabled (or use with extreme caution)
Chrome Print Wait: 8-10 seconds
Temp Cleanup: ✅ Enabled
Cleanup Interval: 6 hours
```

### Security Hardening

1. **Secure Configuration File:**
   ```bash
   # Linux/macOS - restrict permissions
   chmod 600 flowprint_config.json
   
   # Windows - via GUI
   # Right-click → Properties → Security
   # Remove all users except your account
   ```

2. **Use Dedicated Email:**
   - Create a separate email account just for FlowPrint
   - Use app-specific password
   - Enable 2FA on account

3. **Physical Security:**
   - Lock computer when not in use
   - Secure printer room/area
   - Implement document pickup procedures

4. **Network Security:**
   - Use wired connection if possible
   - Configure firewall rules
   - Consider VPN for remote servers

---

## 🔄 Running as a Service

Configure FlowPrint to start automatically and run in the background.

### Windows - Task Scheduler (Recommended)

**Best for production Windows deployments:**

1. **Open Task Scheduler:**
   - Press `Win + R`
   - Type: `taskschd.msc`
   - Press Enter

2. **Create Basic Task:**
   - Click "Create Basic Task..."
   - Name: `FlowPrint Service`
   - Description: `Automatic email-to-print service`

3. **Configure Trigger:**
   - Trigger: "When the computer starts"
   - Click Next

4. **Configure Action:**
   - Action: "Start a program"
   - Program: `C:\Path\To\python.exe`
   - Arguments: `"C:\Path\To\FlowPrint\FlowPrint.py"`
   - Start in: `C:\Path\To\FlowPrint`
   - Click Next

5. **Advanced Settings:**
   - Right-click task → Properties
   - General tab:
     - ✅ "Run whether user is logged on or not"
     - ✅ "Run with highest privileges"
   - Settings tab:
     - ✅ "Allow task to be run on demand"
     - ✅ "Run task as soon as possible after scheduled start is missed"
     - ❌ "Stop the task if it runs longer than"

6. **Test Service:**
   - Right-click task → Run
   - Open browser to `http://localhost:5000`
   - Verify dashboard loads

**Useful Commands:**
```cmd
# View task
schtasks /query /tn "FlowPrint Service"

# Run task
schtasks /run /tn "FlowPrint Service"

# Stop task
schtasks /end /tn "FlowPrint Service"

# Delete task
schtasks /delete /tn "FlowPrint Service"
```

---

### Linux - systemd Service

**Best for production Linux deployments:**

1. **Create Service File:**
   ```bash
   sudo nano /etc/systemd/system/flowprint.service
   ```

2. **Add Configuration:**
   ```ini
   [Unit]
   Description=FlowPrint Automatic Email-to-Print Service
   After=network-online.target
   Wants=network-online.target
   
   [Service]
   Type=simple
   User=yourusername
   Group=yourusername
   WorkingDirectory=/home/yourusername/FlowPrint
   ExecStart=/usr/bin/python3 /home/yourusername/FlowPrint/FlowPrint.py
   
   # Restart policy
   Restart=always
   RestartSec=10
   
   # Security
   PrivateTmp=yes
   NoNewPrivileges=true
   
   # Logging
   StandardOutput=journal
   StandardError=journal
   SyslogIdentifier=flowprint
   
   [Install]
   WantedBy=multi-user.target
   ```

3. **Enable and Start:**
   ```bash
   # Reload systemd
   sudo systemctl daemon-reload
   
   # Enable service (auto-start on boot)
   sudo systemctl enable flowprint
   
   # Start service now
   sudo systemctl start flowprint
   
   # Check status
   sudo systemctl status flowprint
   ```

4. **View Logs:**
   ```bash
   # Follow logs in real-time
   sudo journalctl -u flowprint -f
   
   # View recent logs
   sudo journalctl -u flowprint -n 50
   
   # View logs since today
   sudo journalctl -u flowprint --since today
   ```

**Useful Commands:**
```bash
sudo systemctl start flowprint      # Start service
sudo systemctl stop flowprint       # Stop service
sudo systemctl restart flowprint    # Restart service
sudo systemctl status flowprint     # View status
sudo systemctl enable flowprint     # Enable auto-start
sudo systemctl disable flowprint    # Disable auto-start
```

---

### macOS - launchd

**For macOS production deployments:**

1. **Create LaunchAgent:**
   ```bash
   nano ~/Library/LaunchAgents/com.flowprint.plist
   ```

2. **Add Configuration:**
   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
   <plist version="1.0">
   <dict>
       <key>Label</key>
       <string>com.flowprint</string>
       
       <key>ProgramArguments</key>
       <array>
           <string>/usr/local/bin/python3</string>
           <string>/Users/yourusername/FlowPrint/FlowPrint.py</string>
       </array>
       
       <key>WorkingDirectory</key>
       <string>/Users/yourusername/FlowPrint</string>
       
       <key>RunAtLoad</key>
       <true/>
       
       <key>KeepAlive</key>
       <true/>
       
       <key>StandardOutPath</key>
       <string>/tmp/flowprint.log</string>
       
       <key>StandardErrorPath</key>
       <string>/tmp/flowprint.error.log</string>
       
       <key>ThrottleInterval</key>
       <integer>10</integer>
   </dict>
   </plist>
   ```

3. **Load Service:**
   ```bash
   # Load the service
   launchctl load ~/Library/LaunchAgents/com.flowprint.plist
   
   # Verify it's running
   launchctl list | grep flowprint
   ```

4. **View Logs:**
   ```bash
   # Output log
   tail -f /tmp/flowprint.log
   
   # Error log
   tail -f /tmp/flowprint.error.log
   ```

**Useful Commands:**
```bash
# Load service
launchctl load ~/Library/LaunchAgents/com.flowprint.plist

# Unload (stop) service
launchctl unload ~/Library/LaunchAgents/com.flowprint.plist

# Check if running
launchctl list | grep flowprint

# View service details
launchctl list com.flowprint
```

---

## 🖥️ Headless Server Setup

Running FlowPrint on a server without a display (e.g., in a server room or cloud):

### Prerequisites

- Headless Linux server (Ubuntu Server, Debian, etc.)
- Chrome or Chromium browser
- X Virtual Frame Buffer (Xvfb) for headless Chrome

### Installation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip -y

# Install Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f -y

# Install Xvfb (virtual display)
sudo apt install xvfb -y

# Clone FlowPrint
git clone https://github.com/NotDonaldTrump/FlowPrint.git
cd FlowPrint

# Run FlowPrint (installs dependencies)
python3 FlowPrint.py
```

### Configure for Headless Operation

1. **Modify FlowPrint.py** (if Chrome has issues):
   
   Find the Chrome launch command and add headless flags:
   ```python
   chrome_args = [
       "--headless",
       "--disable-gpu",
       "--no-sandbox",
       "--disable-dev-shm-usage"
   ]
   ```

2. **Create Wrapper Script** (alternative):
   ```bash
   nano start-flowprint.sh
   ```
   
   Add:
   ```bash
   #!/bin/bash
   export DISPLAY=:99
   Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
   cd /path/to/FlowPrint
   python3 FlowPrint.py
   ```
   
   Make executable:
   ```bash
   chmod +x start-flowprint.sh
   ```

3. **Configure Systemd Service:**
   ```bash
   sudo nano /etc/systemd/system/flowprint.service
   ```
   
   Add:
   ```ini
   [Unit]
   Description=FlowPrint Service
   After=network.target
   
   [Service]
   Type=simple
   User=yourusername
   Environment="DISPLAY=:99"
   ExecStartPre=/usr/bin/Xvfb :99 -screen 0 1024x768x24
   ExecStart=/usr/bin/python3 /path/to/FlowPrint/FlowPrint.py
   WorkingDirectory=/path/to/FlowPrint
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

4. **Access Dashboard Remotely:**
   
   **Option A: SSH Tunnel**
   ```bash
   ssh -L 5000:localhost:5000 user@server-ip
   # Then open http://localhost:5000 in local browser
   ```
   
   **Option B: Bind to All Interfaces** (Less secure)
   
   Edit FlowPrint.py:
   ```python
   socketio.run(app, host='0.0.0.0', port=5000)
   ```
   
   Then access via: `http://server-ip:5000`
   
   **⚠️ Security:** Use firewall rules or VPN!

---

## 🔧 Advanced Configuration

### Environment Variables

For enhanced security, use environment variables:

1. **Set Environment Variables:**
   
   **Linux/macOS:**
   ```bash
   export FLOWPRINT_IMAP_PASSWORD="your-app-password"
   export FLOWPRINT_EMAIL="your-email@example.com"
   ```
   
   **Windows:**
   ```cmd
   set FLOWPRINT_IMAP_PASSWORD=your-app-password
   set FLOWPRINT_EMAIL=your-email@example.com
   ```

2. **Modify FlowPrint.py** to read from environment:
   ```python
   import os
   
   # In DEFAULT_CONFIG section:
   DEFAULT_CONFIG = {
       "imap_username": os.getenv('FLOWPRINT_EMAIL', ''),
       "imap_password": os.getenv('FLOWPRINT_IMAP_PASSWORD', ''),
       # ... rest of config
   }
   ```

3. **Persist in Service Files:**
   
   **systemd:**
   ```ini
   [Service]
   Environment="FLOWPRINT_EMAIL=your-email@example.com"
   Environment="FLOWPRINT_IMAP_PASSWORD=your-app-password"
   ```
   
   **Windows Task Scheduler:**
   - Use a batch file wrapper that sets variables before running Python

### Custom Python Virtual Environment

For isolated dependencies:

```bash
# Create virtual environment
python3 -m venv flowprint-env

# Activate
source flowprint-env/bin/activate  # Linux/Mac
flowprint-env\Scripts\activate     # Windows

# Install dependencies
pip install Flask flask-socketio

# Run FlowPrint
python FlowPrint.py

# Deactivate when done
deactivate
```

Update service files to use the venv Python:
```
ExecStart=/path/to/flowprint-env/bin/python3 /path/to/FlowPrint.py
```

### Custom Port Configuration

To use a different port:

1. Edit `FlowPrint.py`:
   ```python
   socketio.run(app, host='0.0.0.0', port=8080)  # Change port
   ```

2. Update firewall rules:
   ```bash
   # Linux
   sudo ufw allow 8080/tcp
   
   # Windows - via GUI or PowerShell
   New-NetFirewallRule -DisplayName "FlowPrint" -Direction Inbound -Protocol TCP -LocalPort 8080 -Action Allow
   ```

---

## 🐛 Installation Troubleshooting

### Python Issues

<details>
<summary><b>Python not found / not in PATH</b></summary>

**Windows:**
1. Reinstall Python
2. Check "Add Python to PATH"
3. Or add manually: System Properties → Environment Variables → Path

**Linux/macOS:**
```bash
# Check Python location
which python3

# Add to PATH in ~/.bashrc or ~/.zshrc
export PATH="/usr/local/bin:$PATH"
```
</details>

<details>
<summary><b>pip install fails / permission denied</b></summary>

**Solution 1: User install**
```bash
pip install --user Flask flask-socketio
```

**Solution 2: Use sudo (Linux)**
```bash
sudo pip3 install Flask flask-socketio
```

**Solution 3: Virtual environment** (recommended)
```bash
python3 -m venv venv
source venv/bin/activate
pip install Flask flask-socketio
```
</details>

### Chrome Issues

<details>
<summary><b>Chrome not found by FlowPrint</b></summary>

1. Verify Chrome is installed:
   ```bash
   # Windows
   dir "C:\Program Files\Google\Chrome\Application\chrome.exe"
   
   # macOS
   ls "/Applications/Google Chrome.app"
   
   # Linux
   which google-chrome
   ```

2. If in custom location, set in dashboard:
   - Advanced tab → Chrome Path
   - Enter full path to chrome executable

3. Restart FlowPrint after setting path
</details>

### Network Issues

<details>
<summary><b>Can't access dashboard at localhost:5000</b></summary>

1. Check if FlowPrint is running:
   ```bash
   # Look for Python process
   ps aux | grep FlowPrint  # Linux/Mac
   tasklist | findstr python  # Windows
   ```

2. Check if port is in use:
   ```bash
   # Linux/Mac
   lsof -i :5000
   
   # Windows
   netstat -ano | findstr :5000
   ```

3. Try different browser

4. Check firewall settings
</details>

---

## 📚 Next Steps

After successful installation:

1. ✅ **Configure Email Settings** - [Email Server Setup](../README.md#-email-server-setup)
2. ✅ **Set Up Shopify Integration** - [Shopify Guide](../README.md#️-shopify-integration)
3. ✅ **Test Thoroughly** - Send multiple test emails
4. ✅ **Deploy to Production** - Set up as service
5. ✅ **Monitor Operations** - Check logs regularly

---

## 📞 Support

Need help with installation?

- 🐛 **Issues**: [GitHub Issues](https://github.com/NotDonaldTrump/FlowPrint/issues)
- 📖 **Main Docs**: [README.md](../README.md)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/NotDonaldTrump/FlowPrint/discussions)

---

**Installation Guide Last Updated:** 18/11/2025