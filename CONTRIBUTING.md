# Contributing to Outage Agent

Thank you for your interest in contributing to the Outage Agent project! This document provides guidelines and instructions for contributing.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/Outage-agent-by-Tensorlake.git`
3. Create a virtual environment: `python -m venv venv`
4. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
5. Install dependencies: `pip install -r requirements.txt`

## Development Setup

1. Set up your API keys (see `QUICKSTART.md`)
2. Test locally: `python outage_agent.py`
3. Test the Streamlit UI: `streamlit run streamlit_app.py`

## Making Changes

1. Create a new branch: `git checkout -b feature/your-feature-name`
2. Make your changes
3. Test thoroughly
4. Commit your changes: `git commit -m "Description of changes"`
5. Push to your fork: `git push origin feature/your-feature-name`
6. Open a Pull Request

## Code Style

- Follow PEP 8 Python style guide
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions focused and small

## Testing

Before submitting a PR, please:
- Test locally with `python outage_agent.py`
- Test the Streamlit UI
- Verify no API keys are exposed in your code
- Check that all existing functionality still works

## Pull Request Guidelines

- Provide a clear description of changes
- Reference any related issues
- Ensure all tests pass
- Update documentation if needed
- Keep commits focused and logical

## Areas for Contribution

- Bug fixes
- Feature enhancements
- Documentation improvements
- UI/UX improvements
- Performance optimizations
- Additional tools/integrations

## Questions?

Open an issue on GitHub for questions or discussions.

Thank you for contributing! 🎉

