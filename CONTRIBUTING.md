# Contributing to FlowPrint

Thank you for considering contributing to FlowPrint! This document outlines the process for contributing to this project.

## How Can I Contribute?

### Reporting Bugs

If you find a bug, please create an issue on GitHub with:
- A clear, descriptive title
- Steps to reproduce the issue
- Expected vs. actual behavior
- Your environment (OS, Python version, etc.)
- Relevant log excerpts from `flowprint.log`

### Suggesting Enhancements

Enhancement suggestions are welcome! Please create an issue with:
- A clear description of the enhancement
- Why this enhancement would be useful
- Potential implementation approach (if you have ideas)

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following the code style guidelines
3. **Test thoroughly** - ensure FlowPrint runs without errors
4. **Update documentation** if you've changed functionality
5. **Write clear commit messages**
6. **Submit a pull request** with a clear description of changes

## Code Style Guidelines

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions focused and modular
- Maintain the existing code structure

## Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/flowprint.git
cd flowprint

# Install dependencies
pip install -r requirements.txt

# Make your changes
# Test your changes
python FlowPrint.py

# Create a branch
git checkout -b feature/your-feature-name

# Commit and push
git add .
git commit -m "Add: description of your changes"
git push origin feature/your-feature-name
```

## Testing Guidelines

Before submitting a pull request:

1. Test with different email providers (Gmail, Outlook, etc.)
2. Test both auto-print and manual modes
3. Verify the console UI renders correctly
4. Check that temp file cleanup works
5. Test error handling (wrong credentials, network issues, etc.)
6. Ensure backward compatibility

## License

By contributing to FlowPrint, you agree that your contributions will be licensed under the GPL-3.0 License.

## Questions?

Feel free to open an issue for questions or discussion!

---

**Thank you for contributing to FlowPrint! 🎉**
