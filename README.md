# FlowPrint 🖨️

**Automatic Email-to-Print Service for Shopify Orders**

FlowPrint is a Python-based service that monitors an IMAP mailbox and automatically prints HTML-formatted emails via Google Chrome. Perfect for Shopify stores looking to automate order printing workflows.

![FlowPrint Console](https://img.shields.io/badge/Python-3.7+-blue.svg)
![License](https://img.shields.io/badge/License-GPL%203.0-green.svg)

---

## 🎯 What Does FlowPrint Do?

FlowPrint acts as a "print endpoint" for your Shopify store. It:

- ✅ Monitors your email inbox continuously
- ✅ Detects emails with a specific subject prefix (e.g., `[PRINT PACK]`)
- ✅ Automatically prints the HTML body via Chrome with kiosk printing
- ✅ Tracks printed emails to avoid duplicates
- ✅ Provides a beautiful real-time console UI
- ✅ Manages temporary files automatically
- ✅ Logs all activities to a file
- ✅ Optionally deletes emails after successful printing

---

## 📋 Prerequisites

### Required Software

1. **Python 3.7 or higher**
   - Download from [python.org](https://www.python.org/downloads/)
   - Ensure you check "Add Python to PATH" during installation

2. **Google Chrome**
   - Download from [google.com/chrome](https://www.google.com/chrome/)
   - Must be installed in default location or path specified in config

3. **Email Account with IMAP Access**
   - Gmail, Outlook, or any IMAP-compatible email service
   - IMAP must be enabled in your email settings

### Optional (but recommended)

- **colorama** Python package for colored console output
  ```bash
  pip install colorama
  ```

---

## 🚀 Quick Start Guide

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/flowprint.git
cd flowprint
```

### Step 2: Install Dependencies

```bash
pip install colorama
```

### Step 3: Configure FlowPrint

Open `FlowPrint.py` and edit the configuration section at the top:

```python
# ==========================
# CONFIGURATION
# ==========================

IMAP_HOST = "imap.gmail.com"          # Your IMAP server
IMAP_PORT = 993                        # IMAP SSL port (usually 993)
IMAP_USE_SSL = True                    # Use SSL connection
IMAP_USERNAME = "your-email@gmail.com" # Your email address
IMAP_PASSWORD = "your-app-password"    # Your email password or app password

MAILBOX = "Inbox"                      # Mailbox folder to monitor
POLL_INTERVAL_SECONDS = 30             # How often to check for new emails
SUBJECT_PREFIX = "[PRINT PACK]"        # Subject filter prefix

AUTO_PRINT_ENABLED = True              # True = auto-print, False = open print dialog
DELETE_EMAIL_AFTER_PRINT = False       # Delete email after successful print (use with caution!)
```

### Step 4: Run FlowPrint

```bash
python FlowPrint.py
```

You should see the FlowPrint console interface appear with real-time status updates.

---

## 📧 Setting Up Email for Gmail

If using Gmail, you'll need to create an **App Password**:

1. Go to your [Google Account](https://myaccount.google.com/)
2. Select **Security** → **2-Step Verification** (enable if not already)
3. Scroll down to **App passwords**
4. Select **Mail** and your device
5. Copy the generated 16-character password
6. Use this password in `IMAP_PASSWORD` (not your regular Gmail password)

**IMAP must be enabled:**
1. Open Gmail → Settings (gear icon) → See all settings
2. Go to **Forwarding and POP/IMAP** tab
3. Enable **IMAP access**
4. Save changes

---

## 🛍️ Shopify Integration Guide

### Overview

FlowPrint integrates with Shopify using **Shopify Flow** to automatically send order details to your email, which FlowPrint then prints.

### Step-by-Step Shopify Flow Setup

#### 1. Create Custom Email Template (Required First!)

Before setting up Shopify Flow, you need an email template that includes the `[PRINT PACK]` subject prefix.

**Navigate to: Shopify Admin → Settings → Notifications**

1. Scroll to **Order notifications**
2. Find any order notification (e.g., "Order confirmation") - we'll use this as a base
3. Click on it to see the template structure
4. **Don't edit the existing template** - you'll create a new one in Flow

#### 2. Access Shopify Flow

**Navigate to: Shopify Admin → Apps → Shopify Flow**

If you don't see Flow:
- You need **Shopify Plus**, OR
- Install the **Shopify Flow app** from the Shopify App Store (available on Advanced plans and higher)

#### 3. Create New Workflow

1. Click **Create workflow**
2. Name it: `FlowPrint - Auto Print Orders`

#### 4. Configure the Trigger

**Trigger: Order created**

1. Click **Select a trigger**
2. Choose **Order** → **Order created**
3. This fires when any new order is placed

Optional filters (click **Add condition** under trigger):
- Filter by fulfillment status (e.g., only unfulfilled orders)
- Filter by financial status (e.g., only paid orders)
- Filter by tags, shipping method, etc.

#### 5. Add Email Action

1. Click **Add action**
2. Search for and select **Send internal email**
3. Configure the email:

**To:** Your monitored email address (e.g., `orders@yourdomain.com`)

**Subject:** 
```
[PRINT PACK] Order {{order.name}}
```
⚠️ **CRITICAL:** The subject MUST start with `[PRINT PACK]` (or whatever you set as `SUBJECT_PREFIX` in FlowPrint.py)

**Body:** Use the example template provided (see below), or create your own using Liquid template language.

#### 6. Example Email Template for Flow

Here's a basic starter template. Paste this into the **Body** field:

```liquid
<style>
  body, p, td, div, th, h1, h2, strong { 
    font-family: Arial, sans-serif;
  }
  table { 
    width: 100%; 
    border-collapse: collapse; 
  }
  th, td {
    border: 1px solid #ddd;
    padding: 8px;
  }
  th {
    background-color: #f5f5f5;
    font-weight: 600;
  }
</style>

<div style="text-align: center; margin-bottom: 2em;">
  <h1>New Order: {{order.name}}</h1>
  <p>Order Date: {{order.createdAt | date: "%B %e, %Y at %I:%M %p"}}</p>
</div>

<h2>Order Summary</h2>
<table>
  <tr>
    <td><strong>Order Number</strong></td>
    <td>{{order.name}}</td>
  </tr>
  <tr>
    <td><strong>Customer</strong></td>
    <td>{{order.customer.firstName}} {{order.customer.lastName}}</td>
  </tr>
  <tr>
    <td><strong>Email</strong></td>
    <td>{{order.email}}</td>
  </tr>
  <tr>
    <td><strong>Phone</strong></td>
    <td>{{order.phone}}</td>
  </tr>
  <tr>
    <td><strong>Total</strong></td>
    <td>${{order.currentTotalPrice}}</td>
  </tr>
</table>

<h2>Shipping Address</h2>
<p>
  {{order.shippingAddress.name}}<br/>
  {{order.shippingAddress.address1}}<br/>
  {% if order.shippingAddress.address2 != blank %}{{order.shippingAddress.address2}}<br/>{% endif %}
  {{order.shippingAddress.city}}, {{order.shippingAddress.provinceCode}} {{order.shippingAddress.zip}}<br/>
  {{order.shippingAddress.country}}<br/>
  {% if order.shippingAddress.phone != blank %}Phone: {{order.shippingAddress.phone}}{% endif %}
</p>

<h2>Order Items</h2>
<table>
  <thead>
    <tr>
      <th>Quantity</th>
      <th>Product</th>
      <th>SKU</th>
      <th>Price</th>
    </tr>
  </thead>
  <tbody>
    {% for lineItem in order.lineItems %}
    <tr>
      <td style="text-align: center;">{{lineItem.quantity}}</td>
      <td>{{lineItem.title}}</td>
      <td>{{lineItem.sku}}</td>
      <td>${{lineItem.originalUnitPrice}}</td>
    </tr>
    {% endfor %}
  </tbody>
  <tfoot>
    <tr>
      <td colspan="3" style="text-align: right;"><strong>Subtotal</strong></td>
      <td>${{order.subtotalPrice}}</td>
    </tr>
    <tr>
      <td colspan="3" style="text-align: right;"><strong>Tax</strong></td>
      <td>${{order.totalTax}}</td>
    </tr>
    <tr>
      <td colspan="3" style="text-align: right;"><strong>Shipping</strong></td>
      <td>${{order.totalShippingPrice}}</td>
    </tr>
    <tr>
      <td colspan="3" style="text-align: right;"><strong>TOTAL</strong></td>
      <td><strong>${{order.currentTotalPrice}}</strong></td>
    </tr>
  </tfoot>
</table>

{% if order.note != blank %}
<h2>Order Note</h2>
<p style="border: 2px solid orange; padding: 10px; background-color: #fff3e0;">
  {{order.note}}
</p>
{% endif %}
```

#### 7. Advanced Template Customization

See `example-template.html` in this repository for a more sophisticated multi-page template with:
- Staff summary page
- Packing slip
- Tax invoice
- Shipping method color coding
- Product images
- Professional styling

You can customize the template with:
- **Liquid variables:** Access any order data (see [Shopify Liquid documentation](https://shopify.dev/api/liquid))
- **HTML/CSS:** Style your printouts however you like
- **Page breaks:** Use `<div class="page-break"></div>` with CSS `page-break-after: always;`
- **Conditional logic:** Show/hide sections based on order properties

#### 8. Test the Workflow

1. **Save** the workflow
2. **Turn it on** (toggle in top right)
3. Place a test order in your Shopify store
4. Check that:
   - Email arrives in your monitored inbox
   - Subject starts with `[PRINT PACK]`
   - FlowPrint detects and prints it

#### 9. Common Shopify Flow Filters

Add conditions to control when printing happens:

**Print only paid orders:**
```
Order → Financial status → is equal to → Paid
```

**Print only unfulfilled orders:**
```
Order → Fulfillment status → is equal to → Unfulfilled
```

**Skip pickup orders:**
```
Order → Shipping line → title → does not contain → Pickup
```

**Print only specific shipping methods:**
```
Order → Shipping line → title → contains → Express
```

**Print orders over $X:**
```
Order → Total price → is greater than → 100
```

---

## ⚙️ Configuration Options Explained

### Email Settings

```python
IMAP_HOST = "mail.example.com"
```
Your IMAP mail server hostname. Common values:
- Gmail: `imap.gmail.com`
- Outlook/Hotmail: `imap-mail.outlook.com`
- Yahoo: `imap.mail.yahoo.com`
- Office 365: `outlook.office365.com`

```python
IMAP_PORT = 993
```
IMAP port. Usually 993 for SSL, or 143 for non-SSL (not recommended).

```python
IMAP_USE_SSL = True
```
Whether to use SSL encryption (always recommended).

```python
IMAP_USERNAME = "your-email@domain.com"
```
Your full email address.

```python
IMAP_PASSWORD = "your-password"
```
Your email password or app-specific password.

```python
MAILBOX = "Inbox"
```
Which folder to monitor. Common options:
- `"Inbox"` - Main inbox
- `"Orders"` - Custom folder you created
- `"[Gmail]/All Mail"` - Gmail's all mail (not recommended - checks everything)

### Behavior Settings

```python
POLL_INTERVAL_SECONDS = 30
```
How often (in seconds) to check for new emails. Lower = faster response, higher = less server load.
- Recommended: 15-60 seconds
- Minimum: 5 seconds (respect server limits)

```python
SUBJECT_PREFIX = "[PRINT PACK]"
```
Only emails with subjects starting with this exact text will be printed. Case-insensitive.

```python
AUTO_PRINT_ENABLED = True
```
- `True`: Automatically sends to default printer (kiosk mode)
- `False`: Opens Chrome with print dialog for manual confirmation

```python
DELETE_EMAIL_AFTER_PRINT = False
```
⚠️ **USE WITH CAUTION**
- `True`: Permanently deletes email from inbox after successful print
- `False`: Keeps email in inbox (marked as read)

**Recommendation:** Start with `False` until you're confident everything works correctly.

```python
CHROME_PATH = ""
```
Path to Chrome executable. Leave blank for auto-detection. Set manually if Chrome isn't found:
- Windows: `r"C:\Program Files\Google\Chrome\Application\chrome.exe"`
- Mac: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`
- Linux: `/usr/bin/google-chrome`

```python
CHROME_PRINT_WAIT_SECONDS = 8
```
How long (in seconds) to wait for Chrome to print before force-closing. Increase if prints are cut off.

```python
TEMP_FILE_CLEANUP_HOURS = 6
```
How long to keep temporary HTML files before auto-cleanup. Increase if you need longer history.

### File Paths

```python
PRINTED_UIDS_FILE = "printed_uids.txt"
```
File storing UIDs of processed emails (prevents duplicates). Don't delete this file unless you want to reprocess all emails.

```python
LOG_FILE = "flowprint.log"
```
Log file for debugging and audit trail.

---

## 🎨 Console Interface

FlowPrint features a beautiful real-time console interface showing:

```
    ███████╗██╗      ██████╗ ██╗    ██╗██████╗ ██████╗ ██╗███╗   ██╗████████╗
    ██╔════╝██║     ██╔═══██╗██║    ██║██╔══██╗██╔══██╗██║████╗  ██║╚══██╔══╝
    █████╗  ██║     ██║   ██║██║ █╗ ██║██████╔╝██████╔╝██║██╔██╗ ██║   ██║   
    ██╔══╝  ██║     ██║   ██║██║███╗██║██╔═══╝ ██╔══██╗██║██║╚██╗██║   ██║   
    ██║     ███████╗╚██████╔╝╚███╔███╔╝██║     ██║  ██║██║██║ ╚████║   ██║   
    ╚═╝     ╚══════╝ ╚═════╝  ╚══╝╚══╝ ╚═╝     ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝   ╚═╝   
```

**Status Information:**
- Current connection status
- Last check time
- Next scheduled check with countdown
- Messages found / processed / pending
- Recent job history
- Error log

**Progress Bar:** Shows time remaining until next email check with animated countdown

**Statistics:** Real-time counters for monitoring activity

---

## 📂 File Structure

```
flowprint/
├── FlowPrint.py              # Main application
├── README.md                 # This file
├── LICENSE                   # GPL-3.0 license
├── example-template.html     # Advanced Shopify template example
├── printed_uids.txt          # Processed email tracking (auto-generated)
├── flowprint.log             # Activity log (auto-generated)
└── temp/                     # Temporary HTML files (auto-managed)
```

---

## 🔧 Troubleshooting

### "Could not find Chrome" Error

**Solution:** Set `CHROME_PATH` manually in the configuration:

```python
# Windows
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

# Mac
CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# Linux
CHROME_PATH = "/usr/bin/google-chrome"
```

### Emails Not Being Detected

1. **Check subject prefix:** Ensure email subjects start with exact prefix (e.g., `[PRINT PACK]`)
2. **Check IMAP settings:** Verify credentials and IMAP access is enabled
3. **Check mailbox name:** Ensure `MAILBOX = "Inbox"` matches your folder name (case-sensitive)
4. **Check the log file:** `flowprint.log` will show connection attempts and errors

### Prints Are Cut Off or Incomplete

**Solution:** Increase wait time before Chrome closes:

```python
CHROME_PRINT_WAIT_SECONDS = 15  # Increase from default 8
```

### Gmail "Authentication Failed" Error

**Solutions:**
1. Enable **2-Step Verification** on your Google account
2. Create an **App Password** (see Gmail setup section above)
3. Use the app password, not your regular Gmail password
4. Ensure **IMAP is enabled** in Gmail settings

### Nothing Happens When Email Arrives

1. Check `AUTO_PRINT_ENABLED` is set to `True`
2. Verify default printer is set in Windows/Mac/Linux
3. Check printer is online and has paper
4. Review `flowprint.log` for error messages

### Windows Security Warning

When running for the first time, Windows may show a security warning. Click "More info" → "Run anyway"

To run as a Windows service (advanced):
- Use NSSM (Non-Sucking Service Manager)
- Configure Task Scheduler to run at startup
- Use third-party service wrapper tools

---

## 🔐 Security Considerations

1. **Email Credentials:**
   - Never commit passwords to version control
   - Use app-specific passwords when available
   - Consider environment variables for production:
     ```python
     import os
     IMAP_PASSWORD = os.getenv('FLOWPRINT_PASSWORD', 'fallback-password')
     ```

2. **Email Content:**
   - Emails may contain sensitive customer information
   - Ensure proper physical security of printed documents
   - Consider encryption for sensitive data in templates

3. **DELETE_EMAIL_AFTER_PRINT:**
   - Only enable after thorough testing
   - Ensure you have backup/archive strategy for orders
   - Consider keeping emails and using a "processed" tag instead

4. **Network Security:**
   - Always use SSL for IMAP (`IMAP_USE_SSL = True`)
   - Use secure networks, especially in production
   - Consider VPN for remote print servers

---

## 🚀 Advanced Usage

### Running as a Background Service

#### Windows (Task Scheduler)

1. Open Task Scheduler
2. Create Basic Task → Name it "FlowPrint"
3. Trigger: "When the computer starts"
4. Action: "Start a program"
5. Program: `C:\Path\To\python.exe`
6. Arguments: `C:\Path\To\FlowPrint.py`
7. Set to run whether user is logged in or not

#### Linux (systemd)

Create `/etc/systemd/system/flowprint.service`:

```ini
[Unit]
Description=FlowPrint Auto-Print Service
After=network.target

[Service]
Type=simple
User=yourusername
WorkingDirectory=/path/to/flowprint
ExecStart=/usr/bin/python3 /path/to/flowprint/FlowPrint.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable flowprint
sudo systemctl start flowprint
sudo systemctl status flowprint
```

#### macOS (launchd)

Create `~/Library/LaunchAgents/com.flowprint.plist`:

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
        <string>/path/to/FlowPrint.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

Load with:
```bash
launchctl load ~/Library/LaunchAgents/com.flowprint.plist
```

### Multiple Print Configurations

Run multiple instances with different configs:

1. Copy `FlowPrint.py` to `FlowPrint-Warehouse.py`
2. Modify configuration in each file
3. Each instance monitors different email or uses different subject prefix

Example use cases:
- Different departments (warehouse, office, shipping)
- Different printers for different order types
- Separate instances for orders vs. returns

### Custom Email Processing Logic

Modify the `process_message()` function to add custom logic:

```python
def process_message(self, uid_bytes):
    # Your custom logic here
    # Examples:
    # - Parse order details from subject/body
    # - Send to different printers based on order value
    # - Add custom headers/footers to print
    # - Trigger external APIs or webhooks
    # - Update external databases
```

---

## 📊 Monitoring & Logging

### Log File Format

FlowPrint writes to `flowprint.log` with the format:

```
[2024-01-15 14:30:22] [INFO] Service started
[2024-01-15 14:30:25] [SUCCESS] Connected to mailbox
[2024-01-15 14:31:10] [SUCCESS] Job processed: Order #1234 - Auto-printed ✓
[2024-01-15 14:32:00] [ERROR] Print failed: Chrome timeout
```

### Monitoring Tips

1. **Tail the log in real-time:**
   ```bash
   # Linux/Mac
   tail -f flowprint.log
   
   # Windows PowerShell
   Get-Content flowprint.log -Wait
   ```

2. **Check for errors:**
   ```bash
   grep ERROR flowprint.log
   ```

3. **Count processed jobs:**
   ```bash
   grep "Job processed" flowprint.log | wc -l
   ```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Code Style

- Follow PEP 8 guidelines
- Add comments for complex logic
- Update README for new features

---

## 📜 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

**TL;DR:** You can freely use, modify, and distribute this software, but any modifications must also be open source under GPL-3.0.

---

## ❓ FAQ

**Q: Does this work with printers other than default?**  
A: Currently prints to system default printer. For specific printers, modify Chrome print settings or use printer-specific Chrome switches.

**Q: Can I print to PDF instead of physical printer?**  
A: Yes! Set your default printer to "Microsoft Print to PDF" (Windows) or "Save as PDF" (Mac).

**Q: How many emails can it handle per hour?**  
A: Tested with 100+ emails/hour. Depends on print speed and `CHROME_PRINT_WAIT_SECONDS`.

**Q: Does it work with other e-commerce platforms?**  
A: Yes! Any platform that can send formatted emails works. Just configure the automation to send emails with the subject prefix.

**Q: Can I use it without Shopify?**  
A: Absolutely! FlowPrint works with any email source. Just ensure emails have the correct subject prefix.

**Q: What if my server/computer restarts?**  
A: FlowPrint resumes automatically from where it left off (tracked via `printed_uids.txt`). Set it up as a service for auto-start.

**Q: Can multiple computers run FlowPrint on the same email?**  
A: Not recommended - leads to duplicate prints. Use separate email addresses or subject prefixes for multiple endpoints.

**Q: Is there a web dashboard?**  
A: Not currently. FlowPrint is a console application. Future versions may include web UI.

---

## 🙏 Acknowledgments

- Built for the Shopify community
- Inspired by the need for simple, reliable automated printing
- Thanks to all contributors and users!

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/yourusername/flowprint/issues](https://github.com/NotDonaldTrump/FlowPrint/issues)

---

## 🗺️ Roadmap

Planned features:
- [ ] Web based configuration interface
- [ ] Webhook endpoints (no email required)
- [ ] Print queue management
- [ ] Email template builder
- [ ] Cloud-hosted service option
- [ ] Mobile app for monitoring
- [ ] Print history with search

---

**Made for the DIY Shopify community**
