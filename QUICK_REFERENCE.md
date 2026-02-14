# HandeeFramer - Quick Reference Card

## Supported Formats

### 1️⃣ Indented Notation (Simple)
```
project
  src
    main.py
    utils.py
  tests
    test.py
  README.md
```
**Use when:** Writing from scratch, simple structures

---

### 2️⃣ Shorthand Notation (Fast)
```
project/src/main.py
project/src/utils.py
project/tests/test.py
project/README.md
```
**Use when:** Quick entry, linear paths

---

### 3️⃣ Box-Drawing Format (Visual)
```
📁 project/
│
├── 📄 package.json
├── 📄 README.md
│
├── 📁 src/
│   ├── main.py
│   └── utils.py
│
└── 📁 tests/
    └── test.py
```
**Use when:** Copying from documentation, README files

---

### 4️⃣ Mixed Format (Flexible)
```
📁 project/
│
├── 📁 src/
│   ├── core/engine.py
│   └── utils/helpers.py
│
├── tests
    test_core.py
    test_utils.py
│
└── config/settings.json
```
**Use when:** Maximum flexibility needed

---

## Automatic Cleaning

### Emojis Removed
✅ Before: `📁 folder`, `📄 file.txt`, `🚀 project`
✅ After: `folder`, `file.txt`, `project`

### Box Characters Removed
✅ Before: `│   ├── file.txt`
✅ After: `file.txt`

### Invalid Characters Filtered
❌ Removed: `< > : " | ? *`
❌ Removed: Control characters (0-31, 127)
✅ Spaces preserved and normalized

---

## Keyboard Shortcuts

| Action | Windows/Linux | macOS |
|--------|---------------|-------|
| Build Frame | `Ctrl+Alt+B` | `Cmd+Alt+B` |

---

## Directory Markers

### Explicit Directories
Add trailing slash to ensure folder creation:
```
empty_folder/
folder_with_content/
  file.txt
```

### Implicit Directories
Parent items are automatically folders:
```
parent
  child.txt    ← parent becomes a folder
```

---

## Root Directory Rules

### Single Root → New Folder
```
myproject
  src
    main.py
```
Creates: `current_dir/myproject/src/main.py`

### Multiple Roots → Current Directory
```
frontend
  index.html
backend
  server.py
```
Creates both in: `current_dir/`

---

## Tips & Tricks

### 📋 Copy from Documentation
Just paste directly! Box-drawing and emojis are handled automatically.

### 🎨 Use Emojis for Clarity
While editing, emojis help visualize - they're removed during build:
```
🎨 assets/
  🖼️ images/
  🎵 audio/
📝 docs/
🔧 tools/
```

### 🔄 Iterative Building
Safe to run multiple times - existing files are never overwritten!

### ⚡ Mix and Match
Combine formats for maximum efficiency:
```
project
  backend/api/routes.ts
  backend/api/models.ts
  frontend
    components/Button.tsx
  📄 README.md
```

---

## Common Patterns

### Python Package
```
mypackage/
  __init__.py
  module.py
  tests/
    __init__.py
    test_module.py
  setup.py
```

### Web Application
```
webapp/
  public/
    css/style.css
    js/app.js
  server/
    routes/api.js
  package.json
```

### C++ Project
```
project/
  src/
    main.cpp
    utils.cpp
  include/
    utils.h
  CMakeLists.txt
```

### Node.js/TypeScript
```
app/
  src/
    index.ts
    types.ts
  dist/
  package.json
  tsconfig.json
```

---

## Troubleshooting

### ❌ "Please save the current file first"
**Fix:** Save your document before running the command

### ❌ Files not appearing
**Check:**
- File is saved ✓
- Write permissions ✓
- Syntax is correct ✓

### ❌ Wrong structure
**Check:**
- Consistent indentation (2 or 4 spaces)
- No mixing tabs and spaces
- Verify trailing slashes for empty folders

---

## Access from Sublime Text

1. **Command Palette**: `Ctrl+Shift+P` → Type "HandeeFramer"
2. **Right-Click Menu**: Select text → Right-click → "Build HandeeFrame"
3. **Keyboard Shortcut**: Select text → Press `Ctrl+Alt+B`

---

**Version**: 1.0.0  
**License**: MIT  
**More Info**: See README.md
