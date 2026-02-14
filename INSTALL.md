# HandeeFramer - Installation and Setup Guide

## Quick Start

### Option 1: Manual Installation

1. **Locate your Sublime Text Packages directory:**
   - **Windows**: `%APPDATA%\Sublime Text\Packages\`
   - **macOS**: `~/Library/Application Support/Sublime Text/Packages/`
   - **Linux**: `~/.config/sublime-text/Packages/`

2. **Create the HandeeFramer directory:**
   ```bash
   cd [Packages directory]
   mkdir HandeeFramer
   ```

3. **Copy all files from this folder into the HandeeFramer directory**

4. **Restart Sublime Text**

5. **Verify installation:**
   - Open Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P`)
   - Type "HandeeFramer" - you should see the commands

### Option 2: Via Git (For Development)

```bash
cd [Sublime Text Packages directory]
git clone https://github.com/JohhannasReyn/HandeeFramer.git HandeeFramer
```

Then restart Sublime Text.

## First Use

1. Create a new file or open an existing one
2. Save it somewhere (the plugin needs a location to build the structure)
3. Type your file structure:
   ```
   myproject
     src
       main.py
       utils.py
     tests
       test_main.py
   ```
4. Select the text (or use the whole document)
5. Press `Ctrl+Alt+B` (or `Cmd+Alt+B` on macOS)
6. Your structure will be created!

## Keyboard Shortcuts

### Windows/Linux
- `Ctrl+Alt+B` - Build HandeeFrame

### macOS
- `Cmd+Alt+B` - Build HandeeFrame

## Command Palette

Access via `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (macOS):
- "HandeeFramer: Build Frame"

## Context Menu

Right-click in any file to access:
- "Build HandeeFrame"

## Syntax Quick Reference

### Indented Notation
```
project
  folder1
    file1.txt
    file2.txt
  folder2
    file3.txt
```

### Shorthand Notation
```
project/folder1/file1.txt
project/folder1/file2.txt
project/folder2/file3.txt
```

### Mixed Notation
```
project
  folder1/file1.txt
  folder2
    file3.txt
```

### Explicit Directories (with trailing slash)
```
project/
  empty_folder/
  folder_with_files/
    file.txt
```

## Settings

Access via: `Preferences → Package Settings → HandeeFramer → Settings`

Default settings:
```json
{
    "verbose": false,
    "collision_behavior": "skip",
    "show_success_dialog": true
}
```

## Troubleshooting

### "Please save the current file first"
**Solution**: Save your document before running the command. The plugin needs a location to know where to create the structure.

### Files aren't being created
**Check:**
1. Is your file saved?
2. Do you have write permissions in that directory?
3. Is your syntax correct? (check indentation)

### Wrong directory structure
**Tips:**
- Use consistent indentation (2 or 4 spaces recommended)
- Check for extra spaces or tabs
- Verify trailing slashes if you want explicit directories

### Command not appearing
**Solution**: 
1. Verify all files are in the correct location
2. Restart Sublime Text
3. Check Console (View → Show Console) for errors

## Testing

Run the included test suite:
```bash
python test_handeeframer.py
```

All tests should pass ✅

## Development

See `CONTRIBUTING.md` for guidelines on contributing to this project.

## Support

- **Documentation**: See `README.md`
- **Examples**: See `EXAMPLES.md`
- **Issues**: Report on GitHub

## License

MIT License - See `LICENSE` file
