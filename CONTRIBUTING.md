# Contributing to HandeeFramer

Thank you for your interest in contributing to HandeeFramer! This document provides guidelines and instructions for contributing.

## Development Setup

1. **Fork the Repository**
   ```bash
   git clone https://github.com/JohhannasReyn/HandeeFramer.git
   cd HandeeFramer
   ```

2. **Install in Sublime Text**
   - Locate your Sublime Text Packages directory:
     - Windows: `%APPDATA%\Sublime Text\Packages\`
     - macOS: `~/Library/Application Support/Sublime Text/Packages/`
     - Linux: `~/.config/sublime-text/Packages/`
   - Create a symlink or copy the plugin directory to `Packages/HandeeFramer/`
   - Restart Sublime Text

3. **Enable Development Mode**
   - Open Sublime Text Console: `View → Show Console` or `` Ctrl+` ``
   - Set verbose logging in settings if needed

## Code Structure

```
HandeeFramer/
├── handeeframer.py              # Main plugin code
├── *.sublime-settings           # Settings files
├── *.sublime-commands           # Command definitions
├── *.sublime-keymap             # Keyboard shortcuts
├── *.sublime-menu               # Menu integrations
├── README.md                    # User documentation
├── CONTRIBUTING.md              # This file
├── EXAMPLES.md                  # Usage examples
└── messages/                    # Package Control messages
```

## Key Components

### TreeNode Class
Represents a node in the file tree structure.
- `name`: Node name
- `is_leaf`: Boolean indicating if this is a file (True) or directory (False)
- `children`: List of child TreeNode objects
- `parent`: Reference to parent TreeNode

### TreeParser Class
Parses text into TreeNode structures.
- Handles indented notation (whitespace-based)
- Handles shorthand notation (path separators)
- Supports mixing both notations

### TreeBuilder Class
Builds actual file/folder structures from TreeNode objects.
- Non-destructive operation
- Tracks created/skipped items
- Handles errors gracefully

## Coding Guidelines

### Python Style
- Follow PEP 8 style guide
- Use 4 spaces for indentation (no tabs)
- Maximum line length: 100 characters
- Use descriptive variable names

### Documentation
- Add docstrings to all classes and methods
- Use clear comments for complex logic
- Update README.md for user-facing changes
- Update EXAMPLES.md for new syntax support

### Error Handling
- Use try/except blocks for file operations
- Provide meaningful error messages to users
- Log errors to Sublime Text console
- Never crash - always fail gracefully

## Testing

### Manual Testing
1. Create test files with various tree structures
2. Test both "Build from Selection" and "Build from Document"
3. Verify non-destructive behavior (existing files aren't overwritten)
4. Test on all supported platforms (Windows, macOS, Linux)

### Test Cases to Cover
- Single root directory
- Multiple root items
- Indented notation with various whitespace amounts
- Shorthand notation with forward slashes
- Shorthand notation with backslashes
- Mixed notation
- Explicit directory markers (trailing slashes)
- Deep nesting (5+ levels)
- Empty lines in input
- Edge cases (empty input, invalid syntax)

### Before Submitting
- [ ] Test on your platform
- [ ] Verify keyboard shortcuts work
- [ ] Check context menu integration
- [ ] Test with saved and unsaved files
- [ ] Verify error messages are helpful
- [ ] Update documentation if needed

## Submitting Changes

### Pull Request Process

1. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Your Changes**
   - Write clear, concise commit messages
   - Keep commits focused and atomic
   - Test thoroughly

3. **Update Documentation**
   - Update README.md if user-facing
   - Add examples to EXAMPLES.md if relevant
   - Update version in messages.json

4. **Submit Pull Request**
   - Provide clear description of changes
   - Reference any related issues
   - Include test results
   - Request review

### Commit Message Format
```
[Type] Brief description

Detailed explanation of what changed and why.

Fixes #123
```

Types:
- `[Feature]` - New functionality
- `[Fix]` - Bug fix
- `[Docs]` - Documentation changes
- `[Refactor]` - Code restructuring
- `[Test]` - Test additions/changes
- `[Chore]` - Maintenance tasks

## Feature Requests

Have an idea for HandeeFramer?

1. Check existing issues to avoid duplicates
2. Open a new issue with:
   - Clear description of the feature
   - Use cases and examples
   - Potential implementation approach (optional)

## Bug Reports

Found a bug? Please report it!

### Required Information
1. **Sublime Text Version**: (e.g., Build 4169)
2. **Plugin Version**: (e.g., 1.0.0)
3. **Operating System**: (e.g., Windows 11, macOS 14, Ubuntu 22.04)
4. **Steps to Reproduce**:
   ```
   1. Open a file
   2. Type this text: ...
   3. Run command...
   4. See error
   ```
5. **Expected Behavior**: What should happen
6. **Actual Behavior**: What actually happens
7. **Console Output**: (View → Show Console)
8. **Sample Input**: The text you were trying to parse

## Code Review Guidelines

### For Reviewers
- Be respectful and constructive
- Test the changes locally
- Check for edge cases
- Verify documentation is updated
- Ensure code follows style guidelines

### For Contributors
- Respond to feedback promptly
- Be open to suggestions
- Ask questions if unclear
- Keep discussions focused

## Questions?

- Open an issue for general questions
- Check existing documentation first
- Be specific and provide context

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to HandeeFramer!
