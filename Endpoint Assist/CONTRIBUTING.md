# Contributing to Endpoint Assist

Thank you for considering contributing to Endpoint Assist! This document provides guidelines and instructions for contributing.

## 📋 Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone.

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Windows 10/11 (for full WMI support)
- Git

### Development Setup

1. **Fork the repository**
   ```bash
   git clone https://github.com/Odysseus265/endpoint-assist.git
   cd endpoint-assist
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the development server**
   ```bash
   python app.py
   ```

## 🔧 Development Workflow

### Branching Strategy

- `main` - Production-ready code
- `develop` - Development branch
- `feature/*` - Feature branches
- `bugfix/*` - Bug fix branches
- `hotfix/*` - Urgent production fixes

### Creating a Feature

1. Create a new branch from `develop`:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit:
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

3. Push and create a Pull Request:
   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

**Examples:**
```
feat: add Excel report generation
fix: resolve memory leak in system monitoring
docs: update API documentation
test: add unit tests for authentication
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_app.py -v
```

### Writing Tests

- Place tests in the `tests/` directory
- Name test files with `test_` prefix
- Use descriptive test function names
- Aim for >80% code coverage

**Example:**
```python
def test_health_check_returns_ok(client):
    """Test that health endpoint returns OK status"""
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'
```

## 📝 Code Style

### Python Style Guide

- Follow [PEP 8](https://pep8.org/)
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and small
- Maximum line length: 100 characters

### JavaScript Style Guide

- Use ES6+ features
- Use `const` and `let`, avoid `var`
- Use async/await for asynchronous operations
- Add JSDoc comments for functions

### CSS Style Guide

- Use CSS custom properties (variables)
- Follow BEM naming convention when applicable
- Mobile-first responsive design
- Organize styles logically

## 🔍 Code Review Checklist

Before submitting a PR, ensure:

- [ ] Code follows the project's style guidelines
- [ ] All tests pass (`pytest`)
- [ ] New features have corresponding tests
- [ ] Documentation is updated if needed
- [ ] No debug code or console.log statements
- [ ] No hardcoded credentials or sensitive data
- [ ] Changes are backward compatible

## 📄 Pull Request Process

1. **Title**: Use a clear, descriptive title
2. **Description**: Explain what changes were made and why
3. **Testing**: Describe how changes were tested
4. **Screenshots**: Include for UI changes
5. **Breaking Changes**: Clearly mark any breaking changes

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How were changes tested?

## Screenshots (if applicable)

## Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Code follows style guide
```

## 🐛 Reporting Bugs

### Bug Report Template

- **Title**: Clear, concise description
- **Environment**: OS, Python version, browser
- **Steps to Reproduce**: Numbered steps
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Screenshots/Logs**: If applicable

## 💡 Feature Requests

### Feature Request Template

- **Title**: Clear feature name
- **Problem**: What problem does this solve?
- **Solution**: Proposed implementation
- **Alternatives**: Other solutions considered
- **Additional Context**: Any relevant information

## 📞 Contact

- **Issues**: Use GitHub Issues
- **Discussions**: Use GitHub Discussions

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Endpoint Assist! 🎉
