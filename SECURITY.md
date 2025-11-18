# 🔐 FlowPrint Security Guidelines

Security best practices and guidelines for deploying and operating FlowPrint safely.

---

## 📑 Table of Contents

- [Security Overview](#-security-overview)
- [Threat Model](#-threat-model)
- [Email Security](#-email-security)
- [Configuration Security](#-configuration-security)
- [Network Security](#-network-security)
- [Physical Security](#-physical-security)
- [Access Control](#-access-control)
- [Data Protection](#-data-protection)
- [Compliance Considerations](#-compliance-considerations)
- [Security Monitoring](#-security-monitoring)
- [Incident Response](#-incident-response)
- [Security Checklist](#-security-checklist)

---

## 🎯 Security Overview

FlowPrint processes sensitive customer information including:
- ❗ Customer names and contact details
- ❗ Shipping addresses
- ❗ Order contents and values
- ❗ Email credentials (stored locally)

**Your Responsibilities:**
- Secure the computer running FlowPrint
- Protect email credentials
- Ensure physical security of printed documents
- Maintain regular security updates
- Monitor for suspicious activity

---

## ⚠️ Threat Model

### Potential Security Risks

| Threat | Impact | Mitigation |
|--------|--------|------------|
| **Stolen email credentials** | Unauthorized access to emails | Use app passwords, 2FA |
| **Config file exposure** | Email password revealed | File permissions, don't commit to Git |
| **Printed document theft** | Customer data breach | Physical security, supervised printer |
| **Network interception** | Email snooping | Use SSL/TLS, secure networks |
| **Unauthorized dashboard access** | Service manipulation | Firewall rules, localhost-only binding |
| **Malicious emails** | System compromise | Input validation, sandboxed Chrome |

### Risk Levels by Deployment

**Low Risk (Home Office):**
- Single user environment
- Physical control of equipment
- Trusted local network

**Medium Risk (Small Business):**
- Multiple employees with access
- Shared network
- Moderate print volumes

**High Risk (Large Operation):**
- Many employees handling orders
- High-value customer data
- Regulatory compliance requirements
- Public or shared facility

---

## 📧 Email Security

### Use App-Specific Passwords

**Never use your main email password!** Create dedicated app passwords:

#### Gmail App Password
```
1. Go to: https://myaccount.google.com/security
2. Enable 2-Step Verification
3. Scroll to "App passwords"
4. Select: Mail → Other → "FlowPrint"
5. Copy 16-character password
6. Use this password in FlowPrint
```

**Benefits:**
- ✅ Can be revoked independently
- ✅ Doesn't expose main password
- ✅ Specific to FlowPrint
- ✅ Easier to rotate

#### Outlook/Microsoft 365
```
1. Go to: https://account.microsoft.com/security
2. Enable 2FA if not already
3. Generate app password
4. Use in FlowPrint configuration
```

### Email Account Security

**Best Practices:**

1. **Dedicated Account:**
   ```
   ✅ Create: orders-print@yourdomain.com
   ❌ Don't use: owner@yourdomain.com
   ```
   
   Benefits:
   - Isolated from personal email
   - Limited blast radius if compromised
   - Easier to monitor and audit

2. **Enable 2FA:**
   - Protects account even if password leaks
   - Required for app passwords in most services

3. **Regular Password Rotation:**
   ```
   Schedule: Every 90 days
   Process:
   1. Generate new app password
   2. Update FlowPrint config
   3. Revoke old app password
   4. Test functionality
   ```

4. **Monitor Login Activity:**
   - Check email provider's security dashboard
   - Look for unusual login locations
   - Review connected devices regularly

### SSL/TLS Configuration

**Always use SSL for IMAP connections:**

```python
# FlowPrint Configuration
IMAP_USE_SSL: ✅ TRUE (Always!)
IMAP_PORT: 993 (SSL port)
```

**Never:**
- ❌ Use unencrypted IMAP (port 143)
- ❌ Disable SSL verification
- ❌ Send credentials over unencrypted connections

---

## 🔧 Configuration Security

### Protecting `flowprint_config.json`

This file contains your email password in **plain text**!

#### File Permissions (Linux/macOS)

```bash
# Set strict permissions (owner read/write only)
chmod 600 flowprint_config.json

# Verify permissions
ls -l flowprint_config.json
# Should show: -rw------- (600)
```

#### File Permissions (Windows)

```cmd
# Via GUI:
1. Right-click flowprint_config.json
2. Properties → Security tab
3. Click "Advanced"
4. Remove all users except your account
5. Set your account to "Read & Write" only
```

```powershell
# Via PowerShell:
$acl = Get-Acl flowprint_config.json
$acl.SetAccessRuleProtection($true, $false)
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    $env:USERNAME, "FullControl", "Allow"
)
$acl.AddAccessRule($rule)
Set-Acl flowprint_config.json $acl
```

### Git Security

**Critical: Never commit configuration to Git!**

#### Add to `.gitignore`

```gitignore
# FlowPrint secrets and generated files
flowprint_config.json
flowprint.log
printed_uids.txt
temp_*.html

# Sensitive data
*.password
*.secret
*.key
```

#### Check for Accidental Commits

```bash
# Search Git history for config file
git log --all -- flowprint_config.json

# If found, remove from history (be careful!)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch flowprint_config.json" \
  --prune-empty --tag-name-filter cat -- --all
```

### Environment Variables (Advanced)

For production deployments, use environment variables:

#### Setup

```bash
# Linux/macOS - in ~/.bashrc or service file
export FLOWPRINT_EMAIL="orders@mystore.com"
export FLOWPRINT_PASSWORD="app-password-here"

# Windows - System Properties → Environment Variables
# Or via PowerShell:
[System.Environment]::SetEnvironmentVariable(
    'FLOWPRINT_PASSWORD', 
    'app-password-here', 
    'User'
)
```

#### Modify FlowPrint.py

```python
import os

DEFAULT_CONFIG = {
    "imap_username": os.getenv('FLOWPRINT_EMAIL', ''),
    "imap_password": os.getenv('FLOWPRINT_PASSWORD', ''),
    # ... rest of config
}
```

**Benefits:**
- ✅ No password in config file
- ✅ Different passwords per environment
- ✅ Easier secret rotation

---

## 🌐 Network Security

### Dashboard Access Control

**Default:** Dashboard binds to `localhost` only (secure)

```python
# Secure (default) - only accessible from local computer
socketio.run(app, host='127.0.0.1', port=5000)

# Less secure - accessible from network
socketio.run(app, host='0.0.0.0', port=5000)
```

#### If You Need Remote Access:

**Option 1: SSH Tunnel (Most Secure)**
```bash
# From remote computer
ssh -L 5000:localhost:5000 user@flowprint-server

# Then open: http://localhost:5000
```

**Option 2: VPN** (Recommended)
- Set up VPN to FlowPrint network
- Access dashboard through VPN
- No exposed ports to internet

**Option 3: Reverse Proxy with Authentication**
```nginx
# Nginx config example
server {
    listen 443 ssl;
    server_name flowprint.yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        auth_basic "FlowPrint Access";
        auth_basic_user_file /etc/nginx/.htpasswd;
        
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Firewall Configuration

#### Linux (UFW)

```bash
# Default deny all incoming
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH (important!)
sudo ufw allow 22/tcp

# Allow FlowPrint only from local network
sudo ufw allow from 192.168.1.0/24 to any port 5000

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

#### Windows Firewall

```powershell
# Allow FlowPrint only from local network
New-NetFirewallRule `
    -DisplayName "FlowPrint Dashboard" `
    -Direction Inbound `
    -LocalPort 5000 `
    -Protocol TCP `
    -RemoteAddress 192.168.1.0/24 `
    -Action Allow
```

### Network Best Practices

1. **Use Wired Connection:**
   - More stable than WiFi
   - Less susceptible to snooping
   - Better for critical infrastructure

2. **Avoid Public WiFi:**
   - Never run FlowPrint on public networks
   - Use VPN if remote access needed

3. **Segment Network:**
   - Place FlowPrint on isolated VLAN
   - Limit access from other network segments

---

## 🏢 Physical Security

### Printer Location

**Best Practices:**

✅ **DO:**
- Place printer in secure, monitored area
- Use locked room if possible
- Implement sign-out procedures for prints
- Install security cameras (if high-value data)
- Shred unclaimed prints after X days

❌ **DON'T:**
- Leave printer in public area
- Allow unsupervised access
- Let prints sit overnight
- Use printer near windows/public view

### Computer Security

**The FlowPrint Computer Must Be Secure:**

1. **Physical Access:**
   - Lock computer when unattended
   - Use cable lock for laptop
   - Place in secured room/cabinet
   - BIOS/firmware password

2. **Login Security:**
   - Strong user password
   - Auto-lock after inactivity (5 minutes)
   - Full disk encryption (Windows BitLocker, macOS FileVault, Linux LUKS)

3. **Screen Privacy:**
   - Lock screen when away: `Win+L` (Windows) or `Ctrl+Cmd+Q` (Mac)
   - Use privacy screen filter if in open area

### Document Handling

**Standard Operating Procedure:**

```markdown
1. Print job completes
2. Staff member retrieves within 5 minutes
3. Verify order number matches pick list
4. Place in secure order staging area
5. Shred any misprints immediately
6. Reconcile end of day (verify all prints accounted for)
```

---

## 🔐 Access Control

### User Permissions

**Principle of Least Privilege:**

| Role | Access Level | Permissions |
|------|-------------|-------------|
| **Administrator** | Full access | Configure, start/stop, view all |
| **Operator** | Limited access | Start/stop service, view status |
| **Picker** | No access | Only handles printed orders |

### Multi-User Environments

If multiple people need access:

1. **Separate Accounts:**
   ```bash
   # Linux - create flowprint user
   sudo useradd -m -s /bin/bash flowprint
   sudo passwd flowprint
   
   # Install FlowPrint in /opt/flowprint
   sudo mkdir /opt/flowprint
   sudo chown flowprint:flowprint /opt/flowprint
   ```

2. **Audit Logging:**
   - Log all dashboard access
   - Track configuration changes
   - Record start/stop actions

3. **Session Management:**
   - Implement session timeouts
   - Require re-authentication for sensitive actions

---

## 🛡️ Data Protection

### Printed Documents

**Data Lifecycle:**

```
Order Created → Email Sent → Printed → Picked → Shipped → [Retention?]
```

**Retention Policy Example:**
```
- Active Orders: Secured until shipped
- Shipped Orders: Shred after 30 days
- Returns: Keep 90 days
- Disputes: Keep per legal requirement
```

### Email Data

**Considerations:**

1. **Email Retention:**
   ```
   DELETE_EMAIL_AFTER_PRINT: false (Recommended)
   
   Why? 
   - Backup if printer fails
   - Audit trail
   - Reprint capability
   ```

2. **Email Cleanup:**
   - Manual: Archive processed emails monthly
   - Automated: Use email filters to move to "Processed" folder

### Log Files

**`flowprint.log` Security:**

```bash
# Contains: timestamps, order numbers, email subjects
# May contain: customer names (in subjects)

# Secure log file
chmod 600 flowprint.log

# Rotate logs regularly
# Linux - logrotate config
/path/to/flowprint.log {
    daily
    rotate 30
    compress
    missingok
    notifempty
}
```

---

## 📋 Compliance Considerations

### GDPR (Europe)

If processing EU customer data:

| Requirement | FlowPrint Implementation |
|------------|-------------------------|
| **Data Minimization** | Only print necessary customer info |
| **Purpose Limitation** | Use data only for order fulfillment |
| **Storage Limitation** | Implement retention policy, shred old prints |
| **Integrity & Confidentiality** | Physical security, encryption at rest |
| **Data Subject Rights** | Ability to delete email after print |

**Compliance Steps:**
1. Document data flow in Privacy Policy
2. Implement print retention/destruction policy
3. Train staff on data handling
4. Maintain audit logs

### PCI-DSS (Payment Card Data)

**Important:** FlowPrint should **never** print full credit card numbers!

✅ **Safe:**
```
Payment: Visa ending in 1234
Status: Paid
```

❌ **Unsafe:**
```
Card Number: 4532-1234-5678-9012
CVV: 123
```

**Shopify Flow Configuration:**
- Never include `{{payment.creditCardNumber}}`
- Use `{{payment.creditCardLastFourDigits}}` instead
- Don't include CVV in any template

### CCPA (California)

If selling to California residents:

- **Right to Know:** Document what customer data is printed
- **Right to Delete:** Implement secure destruction process
- **Notice at Collection:** Privacy policy explains print process

---

## 👁️ Security Monitoring

### What to Monitor

**Daily Checks:**
```bash
# Check for auth failures in log
grep -i "auth\|fail\|error" flowprint.log

# Monitor print volume (unusual spikes?)
grep "SUCCESS.*Printed" flowprint.log | wc -l
```

**Weekly Reviews:**
- Email account login history
- FlowPrint log file review
- Printed UIDs file growth
- System resource usage

**Monthly Audits:**
- Review firewall rules
- Check file permissions
- Update dependencies
- Rotate credentials

### Alerting

**Set up alerts for:**
- Repeated authentication failures
- Service crashes/restarts
- Unusual print volumes
- Disk space warnings

**Example monitoring script:**
```bash
#!/bin/bash
# Simple monitoring script

# Check if service is running
if ! pgrep -f "FlowPrint.py" > /dev/null; then
    echo "ALERT: FlowPrint not running!" | mail -s "FlowPrint Down" admin@example.com
fi

# Check for recent errors
ERROR_COUNT=$(grep -c ERROR /path/to/flowprint.log)
if [ $ERROR_COUNT -gt 10 ]; then
    echo "ALERT: $ERROR_COUNT errors in log" | mail -s "FlowPrint Errors" admin@example.com
fi
```

---

## 🚨 Incident Response

### If Credentials Are Compromised

**Immediate Actions (within 1 hour):**

1. **Revoke Access:**
   ```
   - Revoke app password immediately
   - Change main email password
   - Log out all email sessions
   ```

2. **Stop FlowPrint:**
   ```bash
   # Stop service
   sudo systemctl stop flowprint  # Linux
   # Or kill process manually
   ```

3. **Assess Damage:**
   ```
   - Check email account for unauthorized access
   - Review email sent/received during compromise
   - Check for data exfiltration
   ```

4. **Generate New Credentials:**
   ```
   - Create new app password
   - Update flowprint_config.json
   - Secure file permissions
   - Restart service
   ```

5. **Document Incident:**
   ```markdown
   Date: YYYY-MM-DD HH:MM
   Incident: Credentials compromised
   Detection: [How discovered]
   Actions: [What was done]
   Impact: [Customer data affected?]
   Prevention: [New controls implemented]
   ```

### If Printed Data Is Lost/Stolen

**Immediate Actions:**

1. **Contain:**
   - Determine what data was on prints
   - Identify affected customers

2. **Notify:**
   - Customer notifications (if required by law)
   - Management/legal team
   - Insurance provider (if applicable)

3. **Mitigate:**
   - Implement additional physical security
   - Review and update procedures
   - Retrain staff

---

## ✅ Security Checklist

### Initial Setup

```
□ Python and Chrome installed from official sources
□ FlowPrint downloaded from official GitHub repo
□ Gmail/Outlook app password created (not main password)
□ 2FA enabled on email account
□ flowprint_config.json permissions set to 600 (Linux/Mac)
□ Configuration file excluded from Git (.gitignore)
□ SSL enabled for IMAP (port 993)
□ Dashboard bound to localhost only
□ First test print verified successful
```

### Production Deployment

```
□ Dedicated email account for printing
□ Computer physically secured (locked room/cabinet)
□ Screen lock enabled (5 minute timeout)
□ Full disk encryption enabled
□ Firewall rules configured
□ Service set to auto-start on boot
□ Printer in secure location
□ Document handling procedures documented
□ Staff trained on security procedures
□ Incident response plan created
```

### Ongoing Maintenance

```
□ Monthly: Review access logs
□ Monthly: Check for FlowPrint updates
□ Monthly: Review printed_uids.txt growth
□ Quarterly: Rotate app passwords
□ Quarterly: Review and test incident response plan
□ Quarterly: Security awareness training for staff
□ Annually: Full security audit
□ Annually: Review and update security policies
```

---

## 📚 Additional Resources

### Security Standards

- **NIST Cybersecurity Framework**: [nist.gov/cyberframework](https://www.nist.gov/cyberframework)
- **OWASP Top 10**: [owasp.org/top10](https://owasp.org/www-project-top-ten/)
- **CIS Controls**: [cisecurity.org/controls](https://www.cisecurity.org/controls/)

### Compliance Resources

- **GDPR**: [gdpr.eu](https://gdpr.eu/)
- **CCPA**: [oag.ca.gov/privacy/ccpa](https://oag.ca.gov/privacy/ccpa)
- **PCI-DSS**: [pcisecuritystandards.org](https://www.pcisecuritystandards.org/)

### Security Tools

```bash
# Check for leaked credentials (local hash check)
pip install git-secrets

# Monitor file changes
# Linux
sudo apt install aide

# Scan for vulnerabilities in dependencies
pip install safety
safety check
```

---

## 🆘 Reporting Security Issues

**Found a security vulnerability in FlowPrint?**

**DO:**
- ✅ Email security concerns privately: [your-email@example.com]
- ✅ Include detailed reproduction steps
- ✅ Give reasonable time to fix (30 days)

**DON'T:**
- ❌ Post security issues publicly on GitHub
- ❌ Exploit vulnerabilities without permission
- ❌ Disclose until patch is available

**We take security seriously and will:**
- Respond within 48 hours
- Provide timeline for fix
- Credit you in release notes (if desired)
- Release security advisory when patched

---

## 📞 Support

Questions about security?

- 🔐 **Security Email**: [TBD - add your security contact]
- 📖 **Main Docs**: [README.md](../README.md)
- 🐛 **Issues**: [GitHub Issues](https://github.com/NotDonaldTrump/FlowPrint/issues) (non-security bugs only)

---

<div align="center">

**🔒 Security is everyone's responsibility**

*Keep FlowPrint and your customer data secure!*

</div>

---

**Last Updated:** 18/11/2025