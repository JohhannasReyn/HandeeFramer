# HandeeFramer for Sublime Text

A Sublime Text plugin that builds file and folder structures from text representations. Perfect for quickly scaffolding project structures without manually creating each file and folder.

---
---

## Features

- **Flexible Syntax**: Support for indented, shorthand (path-based), and box-drawing tree notation
- **Emoji Support**: Automatically removes emojis from file/folder names
- **OS-Compatible**: Filters out invalid characters for cross-platform compatibility
- **Non-Destructive**: Never overwrites existing files or folders
- **Smart Root Detection**: Automatically determines the appropriate root directory
- **Selection-Scoped Builds**: Build from the full document, or restrict builds to a selected subtree
- **Cross-Platform**: Works on Windows, Linux, and macOS

---
---

## Installation

### Via Package Control (Recommended)
1. Open Command Palette (`Ctrl+Shift+P` on Windows/Linux, `Cmd+Shift+P` on macOS)
2. Select "Package Control: Install Package"
3. Search for "HandeeFramer"
4. Press Enter to install

### Manual Installation
1. Go to your Sublime Text Packages directory:
   - Windows: `%APPDATA%\Sublime Text\Packages\`
   - macOS: `~/Library/Application Support/Sublime Text/Packages/`
   - Linux: `~/.config/sublime-text/Packages/`
2. Clone this repository or copy the plugin files into a "TreeBuilder" folder
3. Restart Sublime Text

---
---

## Usage

### Indented Notation

Use whitespace indentation to represent folder hierarchy:

```
project
  src
    main.cpp
    utils.cpp
  include
    utils.h
  README.md
```

Folders can be explicitly marked with a trailing slash:

```
project/
  src/
    main.cpp
```

### Shorthand Notation

Use forward slashes (`/`) or backslashes (`\`) to represent paths:

```
project/src/main.cpp
project/src/utils.cpp
project/include/utils.h
project/README.md
```

### Box-Drawing Tree Format

Use the visual tree format with emojis and box-drawing characters (like from `tree` command or documentation):

```
📁 project/
│
├── 📄 package.json
├── 📄 README.md
│
├── 📁 src/
│   ├── main.cpp
│   └── utils.cpp
│
└── 📁 tests/
    └── test.cpp
```

---
---

**Features:**
- Automatically removes emojis (📁, 📄, 🚀, etc.)
- Strips box-drawing characters (│, ├, └, ─)
- Preserves hierarchy based on visual indentation
- Perfect for pasting from documentation!

You can mix all three styles in the same document!

### Root Directory Rules

1. **Single Root**: If there's only one top-level folder, it becomes the root directory
2. **Multiple Roots**: If there are multiple items at the top level, the current file's directory becomes the root

**Example 1** (Single Root):
```
myproject
  src
    main.cpp
```
Creates: `C:\projects\myproject\src\main.cpp` (if your file is in `C:\projects\`)

**Example 2** (Multiple Roots):
```
frontend
  index.html
backend
  server.py
```
Creates both folders in the current directory: `C:\projects\frontend\` and `C:\projects\backend\`

---
---

## Commands

### Build Tree
- **Command Palette**: "HandeeFramer: Build Tree"
- **Keyboard**:
  - Windows/Linux: `Ctrl+Alt+B`
  - macOS: `Cmd+Alt+B`
- **Context Menu**:
  - With a selection: Right-click selected text → "Build Tree"
  - Without a selection: Right-click anywhere → "Build Tree"

Builds the file structure using the current editor content:

- If **text is selected**, HandeeFramer builds from the **selected portion only**.
- If **no selection** is present, HandeeFramer builds from the **entire document**.

---
---

## Examples

### Example 1: Simple Web Project

```
web-app
  css
    style.css
    reset.css
  js
    app.js
    utils.js
  index.html
  about.html
```

### Example 2: Python Package

```
mypackage/
  __init__.py
  core/
    __init__.py
    engine.py
  utils/
    __init__.py
    helpers.py
  tests/
    test_core.py
  setup.py
  README.md
```

### Example 3: Mixed Notation

```
src/models/user.py
src/models/product.py
src/controllers
  user_controller.py
  product_controller.py
tests/test_user.py
tests/test_product.py
config.yml
```

---
---

## Settings

Access settings via: `Preferences` → `Package Settings` → `HandeeFramer` → `Settings`

### Available settings:
---
**Show detailed output in console**:
 - "verbose": true | false (default),
---
**How to handle existing files/folders when encountered**:
 - "collision_behavior": "skip" (default) | "skip_silent"
---
**Show success message dialog after building tree**:
 - "show_success_dialog": true (default) | false

---
---

## Behavior Notes

- **Non-Destructive**: Existing files and folders are never modified or deleted
- **Empty Files**: All created files are empty (0 bytes)
- **Directory Creation**: Parent directories are automatically created as needed
- **Collision Handling**: If a file/folder already exists, it's skipped without error

---
---

## Troubleshooting

### "Please save the current file first"
The plugin needs a file location to determine where to create the structure. Save your document to a location first.

### Files aren't being created
- Ensure your document is saved
- Check that you have write permissions in the target directory
- Verify your syntax is correct (use consistent indentation)

### Wrong root directory
- If you have a single top-level folder, it will become the root
- If you want multiple folders at the same level, ensure they all have the same indentation

---
---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---
---

## License

MIT License - See LICENSE file for details

---
---

## Author

Created by John - Similar to the markdown2dir project

---
---

## Version History

- **1.0.0**: Initial release
  - Support for indented and shorthand notation
  - Non-destructive file/folder creation
  - Cross-platform keyboard shortcuts
  - Context menu integration
