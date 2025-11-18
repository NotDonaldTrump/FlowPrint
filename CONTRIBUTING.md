# 🤝 Contributing to FlowPrint

Thank you for your interest in contributing to FlowPrint! This document provides guidelines for contributing to the project.

---

## 📑 Table of Contents

- [Code of Conduct](#-code-of-conduct)
- [How Can I Contribute?](#-how-can-i-contribute)
- [Development Setup](#-development-setup)
- [Coding Standards](#-coding-standards)
- [Pull Request Process](#-pull-request-process)
- [Testing Guidelines](#-testing-guidelines)
- [Documentation](#-documentation)

---

## 🤗 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive experience for everyone.

### Expected Behavior

- ✅ Be respectful and inclusive
- ✅ Accept constructive criticism gracefully
- ✅ Focus on what's best for the community
- ✅ Show empathy towards others

### Unacceptable Behavior

- ❌ Harassment or discrimination
- ❌ Trolling or insulting comments
- ❌ Publishing others' private information
- ❌ Any unprofessional conduct

---

## 🎯 How Can I Contribute?

### Reporting Bugs

Found a bug? Help us fix it!

**Before submitting:**
1. ✅ Check [existing issues](https://github.com/NotDonaldTrump/FlowPrint/issues)
2. ✅ Verify you're using the latest version
3. ✅ Review [troubleshooting guide](README.md#-troubleshooting)

**Create an issue with:**

```markdown
## Bug Description
Clear description of what's wrong

## Steps to Reproduce
1. Step one
2. Step two
3. ...

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: Windows 10 / macOS 14 / Ubuntu 22.04
- Python version: 3.11.2
- FlowPrint version: (commit hash or release)
- Browser: Chrome 120

## Logs
```
Paste relevant log excerpts from flowprint.log
```

## Screenshots
If applicable, add screenshots
```

### Suggesting Features

Have an idea? We'd love to hear it!

**Create an issue with:**

```markdown
## Feature Description
Clear description of the proposed feature

## Problem It Solves
What problem does this address?

## Proposed Solution
How would you implement it?

## Alternatives Considered
What other approaches did you think about?

## Additional Context
Any other relevant information
```

### Improving Documentation

Documentation improvements are always welcome!

**Ways to help:**
- 📝 Fix typos or grammar
- 📚 Add examples or clarifications
- 🌍 Translate documentation
- 📊 Add diagrams or screenshots
- ✅ Update outdated information

---

## 💻 Development Setup

### Prerequisites

- Python 3.7 or higher
- Git
- Google Chrome
- Text editor or IDE (VS Code, PyCharm, etc.)

### Fork and Clone

1. **Fork the repository** on GitHub

2. **Clone your fork:**
   ```bash
   git clone https://github.com/YOUR-USERNAME/FlowPrint.git
   cd FlowPrint
   ```

3. **Add upstream remote:**
   ```bash
   git remote add upstream https://github.com/NotDonaldTrump/FlowPrint.git
   ```

### Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt

# Optional: Install development tools
pip install black pylint pytest
```

### Create a Branch

```bash
git checkout -b feature/your-feature-name
```

**Branch naming conventions:**
- `feature/` - New features
- `bugfix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test improvements

**Examples:**
- `feature/webhook-support`
- `bugfix/chrome-not-found`
- `docs/improve-readme`

---

## 📝 Coding Standards

### Python Style Guide

Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide.

**Key points:**

```python
# Use 4 spaces for indentation (no tabs)
def my_function(param1, param2):
    result = param1 + param2
    return result

# Maximum line length: 79 characters
# Use meaningful variable names
email_subject = get_subject(message)  # Good
s = get_subject(message)              # Bad

# Add docstrings to functions
def process_email(uid, message):
    """
    Process an email message and print it.
    
    Args:
        uid: Email unique identifier
        message: Email message object
        
    Returns:
        bool: True if successful, False otherwise
    """
    pass

# Use comments for complex logic
# Calculate wait time based on poll interval
wait_time = poll_interval * 0.8  # 80% of interval
```

### Code Formatting

**Use Black for automatic formatting:**

```bash
# Format a file
black FlowPrint.py

# Format all Python files
black .

# Check without modifying
black --check FlowPrint.py
```

### Linting

**Use pylint for code quality:**

```bash
# Lint a file
pylint FlowPrint.py

# Lint with specific config
pylint --disable=C0111 FlowPrint.py
```

### JavaScript/CSS Style

**For web interface files:**

```javascript
// Use camelCase for variables
let emailCount = 0;

// Use descriptive function names
function updateStatusDisplay(status) {
    // ...
}

// Add comments for complex logic
// Calculate progress percentage for countdown
const progress = (elapsed / totalTime) * 100;
```

```css
/* Use meaningful class names */
.status-banner { }
.job-history { }

/* Group related styles */
/* Button Styles */
.btn { }
.btn-primary { }
.btn-secondary { }

/* Use comments to separate sections */
/* =========================== */
/* Dashboard Layout            */
/* =========================== */
```

---

## 🔀 Pull Request Process

### Before Submitting

**Checklist:**

- [ ] ✅ Code follows style guidelines
- [ ] ✅ All tests pass
- [ ] ✅ New features have tests
- [ ] ✅ Documentation updated
- [ ] ✅ Commit messages are clear
- [ ] ✅ Branch is up to date with main

### Update Your Branch

```bash
# Fetch latest changes
git fetch upstream

# Rebase on main
git rebase upstream/main

# Push to your fork
git push origin feature/your-feature-name --force-with-lease
```

### Commit Messages

**Format:**

```
Type: Brief description (50 chars or less)

Detailed explanation if needed. Wrap at 72 characters.

- Can include bullet points
- Reference issues: Fixes #123
- Break into multiple lines if needed
```

**Types:**
- `Add:` New feature
- `Fix:` Bug fix
- `Update:` Update existing feature
- `Refactor:` Code refactoring
- `Docs:` Documentation changes
- `Test:` Test improvements
- `Chore:` Maintenance tasks

**Examples:**

```bash
# Good
git commit -m "Add: Webhook endpoint for direct printing"
git commit -m "Fix: Chrome not found on macOS ARM"
git commit -m "Docs: Update installation guide for Linux"

# Bad
git commit -m "fixed bug"
git commit -m "changes"
git commit -m "stuff"
```

### Create Pull Request

1. **Push your branch:**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Go to GitHub** and click "New Pull Request"

3. **Fill out the template:**

   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Documentation update
   - [ ] Code refactoring
   
   ## Related Issues
   Fixes #123
   Related to #456
   
   ## Testing
   - [ ] Tested on Windows
   - [ ] Tested on Linux
   - [ ] Tested on macOS
   - [ ] Manual testing completed
   - [ ] Automated tests added
   
   ## Screenshots
   (If applicable)
   
   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Documentation updated
   - [ ] All tests pass
   - [ ] Reviewed own changes
   ```

4. **Request review** from maintainers

### Review Process

**What to expect:**
1. ✅ Automated checks run (linting, tests)
2. ✅ Maintainer reviews code
3. ✅ Feedback provided (if needed)
4. ✅ Changes requested (if needed)
5. ✅ Approval and merge

**Response times:**
- Initial review: 2-7 days
- Follow-up reviews: 1-3 days

**Tips:**
- ✅ Be responsive to feedback
- ✅ Ask questions if unclear
- ✅ Break large PRs into smaller ones
- ✅ Keep PR focused on one thing

---

## 🧪 Testing Guidelines

### Manual Testing

**Before submitting PR, test:**

1. **Basic Functionality**
   - [ ] Service starts without errors
   - [ ] Dashboard loads correctly
   - [ ] Configuration can be saved
   - [ ] Email connection works
   - [ ] Emails are detected
   - [ ] Printing works correctly

2. **Edge Cases**
   - [ ] Wrong email credentials
   - [ ] Empty inbox
   - [ ] Malformed emails
   - [ ] Chrome not installed
   - [ ] Printer offline
   - [ ] No internet connection

3. **Multi-Platform** (if possible)
   - [ ] Windows 10/11
   - [ ] macOS (Intel and ARM)
   - [ ] Linux (Ubuntu, Debian, etc.)

### Writing Tests

**For new features, add tests:**

```python
# test_flowprint.py
import unittest
from FlowPrint import EmailPrintDaemon, ChromePrinter

class TestEmailPrintDaemon(unittest.TestCase):
    def test_subject_matches_prefix(self):
        """Test subject prefix matching"""
        daemon = EmailPrintDaemon()
        
        # Test matching subjects
        self.assertTrue(
            daemon.subject_matches_prefix(
                "[PRINT PACK] Order #1234", 
                "[PRINT PACK]"
            )
        )
        
        # Test non-matching subjects
        self.assertFalse(
            daemon.subject_matches_prefix(
                "Regular email", 
                "[PRINT PACK]"
            )
        )

if __name__ == '__main__':
    unittest.main()
```

**Run tests:**

```bash
python -m pytest test_flowprint.py
```

### Testing Checklist

**Complete this before submitting:**

| Test Category | Status | Notes |
|--------------|--------|-------|
| Email connection | ⬜ | Gmail, Outlook tested |
| Email detection | ⬜ | Prefix matching works |
| Printing | ⬜ | Auto and manual modes |
| Configuration | ⬜ | Save/load works |
| Dashboard | ⬜ | All buttons functional |
| Service mode | ⬜ | Runs as service |
| Error handling | ⬜ | Graceful failures |
| Log output | ⬜ | Helpful messages |

---

## 📚 Documentation

### Documentation Standards

**When adding features:**

1. **Update README.md**
   - Add to features list if major feature
   - Add to troubleshooting if adds complexity
   - Add configuration options

2. **Update INSTALLATION.md**
   - If changes installation process
   - If adds new dependencies

3. **Update FILE_STRUCTURE.md**
   - If adds new files
   - If changes directory structure

4. **Add inline comments**
   ```python
   # Good: Explains WHY
   # Wait 80% of poll interval to account for processing time
   time.sleep(poll_interval * 0.8)
   
   # Bad: Explains WHAT (code already shows this)
   # Sleep for poll_interval * 0.8
   time.sleep(poll_interval * 0.8)
   ```

5. **Update docstrings**
   ```python
   def process_message(self, uid_bytes):
       """
       Process a single email message.
       
       Downloads email, checks if already printed, extracts HTML
       content, and triggers printing if needed.
       
       Args:
           uid_bytes: Email UID as bytes from IMAP server
           
       Returns:
           bool: True if processed successfully, False on error
           
       Raises:
           IMAPError: If email cannot be fetched
           PrintError: If printing fails
       """
   ```

### Documentation Style

**Use clear, simple language:**
- ✅ Write for beginners
- ✅ Explain technical terms
- ✅ Use examples
- ✅ Add screenshots/diagrams
- ✅ Use formatting (bold, lists, tables)

**Good example:**
```markdown
FlowPrint monitors your email inbox and automatically prints 
emails that have a specific subject prefix (like "[PRINT PACK]"). 
This is perfect for Shopify stores that want to print orders 
automatically.
```

**Bad example:**
```markdown
FlowPrint implements an IMAP client daemon that polls a mailbox 
for messages matching a configurable subject regex pattern and 
invokes Chrome programmatically for kiosk printing.
```

---

## 🎓 Learning Resources

### Python Resources

- [Python Official Docs](https://docs.python.org/3/)
- [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [Flask Documentation](https://flask.palletsprojects.com/)

### Git Resources

- [Git Handbook](https://guides.github.com/introduction/git-handbook/)
- [GitHub Guides](https://guides.github.com/)
- [Atlassian Git Tutorials](https://www.atlassian.com/git/tutorials)

### Web Development

- [MDN Web Docs](https://developer.mozilla.org/)
- [Socket.IO Docs](https://socket.io/docs/)
- [CSS-Tricks](https://css-tricks.com/)

---

## 📞 Questions?

**Need help contributing?**

- 💬 Start a [Discussion](https://github.com/NotDonaldTrump/FlowPrint/discussions)
- 📧 Contact maintainers (see repository)
- 🐛 Open an issue for clarification

**Don't be afraid to:**
- Ask questions
- Admit you don't know something
- Request help with your contribution

---

## 🏆 Recognition

### Contributors

All contributors are recognized in:
- GitHub contributors page
- Release notes
- README acknowledgments

### Types of Contributions

**We value ALL contributions:**
- 💻 Code contributions
- 📝 Documentation improvements
- 🐛 Bug reports
- 💡 Feature suggestions
- 🧪 Testing
- 🌍 Translations
- ❓ Answering questions
- 📣 Promoting the project

---

## 📜 License Agreement

By contributing to FlowPrint, you agree that your contributions will be licensed under the [GNU General Public License v3.0](LICENSE).

**This means:**
- ✅ Your code must be GPL-3.0 compatible
- ✅ You retain copyright of your contributions
- ✅ You grant the project rights to use your contributions
- ✅ Your contributions will be freely available to all

---

<div align="center">

**Thank you for contributing to FlowPrint! 🎉**

Every contribution, no matter how small, makes a difference!

[Return to README](README.md) • [View Issues](https://github.com/NotDonaldTrump/FlowPrint/issues) • [Start Discussion](https://github.com/NotDonaldTrump/FlowPrint/discussions)

</div>