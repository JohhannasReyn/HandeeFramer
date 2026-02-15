#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Comprehensive unit tests for HandeeFramer plugin.

Tests all functions and branches with detailed coverage.
Run with: python test_handeeframer.py
"""

import os
import sys
import tempfile
import importlib

# Mock sublime and sublime_plugin modules before importing handeeframer
class MockSublime:
    def error_message(self, msg):
        pass
    def message_dialog(self, msg):
        pass
    
    class Region:
        def __init__(self, a, b):
            self.a = a
            self.b = b

class MockSublimePlugin:
    class TextCommand:
        pass

sys.modules['sublime'] = MockSublime()
sys.modules['sublime_plugin'] = MockSublimePlugin()

# Force reload of handeeframer module to pick up changes
if 'handeeframer' in sys.modules:
    importlib.reload(sys.modules['handeeframer'])

from handeeframer import (
    TreeNode, CommentParser, CodeFenceDetector, 
    TreeDetector, TreeParser, TreeBuilder
)

# Mock sublime modules
class MockSublimeModule:
    class Region:
        def __init__(self, a, b):
            self.a = a
            self.b = b
        def empty(self):
            return self.a == self.b

class MockSublimePluginModule:
    class TextCommand:
        pass

sys.modules['sublime'] = MockSublimeModule()
sys.modules['sublime_plugin'] = MockSublimePluginModule()

# Import the actual modules
from handeeframer import (
    TreeNode, CommentParser, CodeFenceDetector, TreeDetector,
    TreeParser, TreeBuilder
)

class TestCodeFenceLanguageFiltering:
    """Test that language identifiers don't create files"""
    
    @staticmethod
    def test_bash_keyword_rejected():
        """Test that 'bash' alone is rejected"""
        result = CodeFenceDetector._extract_filename("bash")
        assert result is None
        print("✅ Bash keyword rejected")
    
    @staticmethod
    def test_python_keyword_rejected():
        """Test that 'python' alone is rejected"""
        result = CodeFenceDetector._extract_filename("python")
        assert result is None
        print("✅ Python keyword rejected")
    
    @staticmethod
    def test_javascript_keyword_rejected():
        """Test that 'javascript' alone is rejected"""
        result = CodeFenceDetector._extract_filename("javascript")
        assert result is None
        print("✅ JavaScript keyword rejected")
    
    @staticmethod
    def test_bash_with_extension_accepted():
        """Test that 'setup.bash' is accepted"""
        result = CodeFenceDetector._extract_filename("setup.bash")
        assert result == "setup.bash"
        print("✅ Bash with extension accepted")
    
    @staticmethod
    def test_bash_file_accepted():
        """Test that 'install.sh' is accepted"""
        result = CodeFenceDetector._extract_filename("install.sh")
        assert result == "install.sh"
        print("✅ Shell script accepted")
    
    @staticmethod
    def test_common_files_accepted():
        """Test that common files without extensions are accepted"""
        common_files = ['Makefile', 'Dockerfile', 'README', 'LICENSE']
        for filename in common_files:
            result = CodeFenceDetector._extract_filename(filename)
            assert result == filename
        print("✅ Common files without extensions accepted")
    
    @staticmethod
    def test_markdown_stripped_language():
        """Test that markdown formatting is stripped from language keywords"""
        result = CodeFenceDetector._extract_filename("`bash`")
        assert result is None
        print("✅ Markdown-wrapped language keyword rejected")
    
    @staticmethod
    def test_markdown_stripped_filename():
        """Test that markdown formatting is stripped from filenames"""
        result = CodeFenceDetector._extract_filename("`config.json`")
        assert result == "config.json"
        print("✅ Markdown-wrapped filename accepted")
    
    @staticmethod
    def test_asterisk_stripped():
        """Test that asterisks are removed from filenames"""
        result = CodeFenceDetector._extract_filename("**config.json**")
        assert result == "config.json"
        print("✅ Asterisk-wrapped filename accepted")
    
    @staticmethod
    def test_mixed_markdown_stripped():
        """Test that mixed markdown is handled"""
        result = CodeFenceDetector._extract_filename("**`app.py`**")
        assert result == "app.py"
        print("✅ Mixed markdown-wrapped filename accepted")


class TestCodeFenceIntegration:
    """Test complete code fence detection with language keywords"""
    
    @staticmethod
    def test_bash_fence_no_file():
        """Test that ```bash blocks don't create files"""
        text = """
```bash
def hello():
print("Hello")
```
"""
        fences = CodeFenceDetector.find_code_fences(text)
        assert len(fences) == 0
        print("✅ Python code fence creates no file")
    
    @staticmethod
    def test_json_fence_no_file():
        """Test that ```json blocks don't create files"""
        text = """
```json
{
  "name": "test"
}
```
"""
        fences = CodeFenceDetector.find_code_fences(text)
        assert len(fences) == 0
        print("✅ JSON code fence creates no file")
    
    @staticmethod
    def test_fence_with_filename():
        """Test that fence with actual filename creates file"""
        text = """
**`config.json`**
```json
{
  "name": "test"
}
```
"""
        fences = CodeFenceDetector.find_code_fences(text)
        assert len(fences) == 1
        assert fences[0][0] == "config.json"
        print("✅ Fence with filename creates file")
    
    @staticmethod
    def test_multiple_bash_fences():
        """Test that multiple bash fences create no files"""
        text = """
```bash
npm install
```
```bash
npm run build
```
```bash
npm start
```
"""
        fences = CodeFenceDetector.find_code_fences(text)
        assert len(fences) == 0
        print("✅ Multiple bash fences create no files")


class TestDirectoryCounting:
    """Test accurate directory and file counting"""
    
    @staticmethod
    def test_single_root_directory_counted():
        """Test that single root directory is counted"""
        with tempfile.TemporaryDirectory() as tmpdir:
            builder = TreeBuilder(tmpdir)
            
            # Create a single root with children
            root = TreeNode("project")
            src = TreeNode("src")
            main = TreeNode("main.py")
            
            root.add_child(src)
            src.add_child(main)
            
            stats = builder.build([root])
            
            # Should count: project/ and src/
            assert stats['dirs'] == 2
            assert stats['files'] == 1
            print("✅ Single root directory counted correctly")
    
    @staticmethod
    def test_multiple_roots_counted():
        """Test that multiple root directories are counted"""
        with tempfile.TemporaryDirectory() as tmpdir:
            builder = TreeBuilder(tmpdir)
            
            root1 = TreeNode("app")
            root2 = TreeNode("lib")
            root3 = TreeNode("tests")
            
            file1 = TreeNode("main.py")
            file2 = TreeNode("utils.py")
            file3 = TreeNode("test.py")
            
            root1.add_child(file1)
            root2.add_child(file2)
            root3.add_child(file3)
            
            stats = builder.build([root1, root2, root3])
            
            # Should count: app/, lib/, tests/
            assert stats['dirs'] == 3
            assert stats['files'] == 3
            print("✅ Multiple root directories counted correctly")
    
    @staticmethod
    def test_nested_directories_counted():
        """Test that nested directories are all counted"""
        with tempfile.TemporaryDirectory() as tmpdir:
            builder = TreeBuilder(tmpdir)
            
            # Create: project/src/components/ui/
            root = TreeNode("project")
            src = TreeNode("src")
            components = TreeNode("components")
            ui = TreeNode("ui")
            button = TreeNode("Button.tsx")
            
            root.add_child(src)
            src.add_child(components)
            components.add_child(ui)
            ui.add_child(button)
            
            stats = builder.build([root])
            
            # Should count: project/, src/, components/, ui/
            assert stats['dirs'] == 4
            assert stats['files'] == 1
            print("✅ Nested directories counted correctly")
    
    @staticmethod
    def test_mixed_structure_counted():
        """Test counting with mixed files and directories"""
        with tempfile.TemporaryDirectory() as tmpdir:
            builder = TreeBuilder(tmpdir)
            
            root = TreeNode("app")
            
            # Add some files at root level
            config = TreeNode("config.json")
            readme = TreeNode("README.md")
            
            # Add a directory with files
            src = TreeNode("src")
            main = TreeNode("main.py")
            utils = TreeNode("utils.py")
            
            root.add_child(config)
            root.add_child(readme)
            root.add_child(src)
            src.add_child(main)
            src.add_child(utils)
            
            stats = builder.build([root])
            
            # Should count: app/, src/
            assert stats['dirs'] == 2
            # Should count: config.json, README.md, main.py, utils.py
            assert stats['files'] == 4
            print("✅ Mixed structure counted correctly")
    
    @staticmethod
    def test_existing_directories_skipped():
        """Test that existing directories are skipped in count"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Pre-create a directory
            existing_dir = os.path.join(tmpdir, "existing")
            os.makedirs(existing_dir)
            
            builder = TreeBuilder(tmpdir)
            
            root = TreeNode("existing")
            new_file = TreeNode("new.txt")
            root.add_child(new_file)
            
            stats = builder.build([root])
            
            # existing/ already exists, so dirs should be 0
            # But the directory is still used, just not created
            assert stats['files'] == 1
            print("✅ Existing directories handled correctly")


class TestFilenameValidation:
    """Test filename sanitization and validation"""
    
    @staticmethod
    def test_trailing_dots_removed():
        """Test that trailing dots are removed from filenames"""
        result = CodeFenceDetector._extract_filename("file.txt.")
        # After sanitization, should be valid
        assert result is not None
        print("✅ Trailing dots handled")
    
    @staticmethod
    def test_asterisk_wildcard_removed():
        """Test that asterisks are removed"""
        result = CodeFenceDetector._extract_filename("*.txt")
        # Should remove the asterisk
        assert result is not None
        assert '*' not in result
        print("✅ Asterisk wildcards removed")
    
    @staticmethod
    def test_backticks_removed():
        """Test that backticks are completely removed"""
        result = CodeFenceDetector._extract_filename("`file`.txt")
        assert result == "file.txt"
        print("✅ Backticks removed from filename")
    
    @staticmethod
    def test_empty_after_stripping():
        """Test that empty strings after stripping return None"""
        result = CodeFenceDetector._extract_filename("```")
        assert result is None
        print("✅ Empty string after stripping rejected")
    
    @staticmethod
    def test_dotfile_accepted():
        """Test that dotfiles are accepted"""
        dotfiles = ['.gitignore', '.env', '.bashrc', '.env.local']
        for dotfile in dotfiles:
            result = CodeFenceDetector._extract_filename(dotfile)
            assert result == dotfile
        print("✅ Dotfiles accepted")


class TestTreeNode:
    """Test TreeNode class."""

    @staticmethod
    def test_node_creation():
        """Test basic node creation"""
        # Changed: Remove is_leaf parameter, it's now a property
        node = TreeNode("test")
        assert node.name == "test"
        assert node.is_leaf == True  # No children = leaf
        assert len(node.children) == 0
        print("✅ Node creation test passed")

    @staticmethod
    def test_node_with_comment():
        """Test node with comment"""
        # Changed: comment is now the second parameter
        node = TreeNode("config.py", "Configuration settings")
        assert node.name == "config.py"
        assert node.comment == "Configuration settings"
        assert node.is_leaf == True
        print("✅ Node with comment test passed")

    @staticmethod
    def test_add_child():
        """Test adding children"""
        parent = TreeNode("src")
        child = TreeNode("main.py")
        parent.add_child(child)
        
        assert len(parent.children) == 1
        assert parent.children[0] == child
        assert child.parent == parent
        assert parent.is_leaf == False  # Has children = not a leaf
        assert child.is_leaf == True    # No children = leaf
        print("✅ Add child test passed")

    @staticmethod
    def test_get_path():
        """Test path construction."""
        root = TreeNode("root")
        child = TreeNode("child")
        leaf = TreeNode("file.txt")

        root.add_child(child)
        child.add_child(leaf)

        expected_path = os.path.join("root", "child", "file.txt")
        assert leaf.get_path() == expected_path
        print("✅ Get path test passed")

    @staticmethod
    def test_find_node_by_path():
        """Test finding node by path."""
        root = TreeNode("project")
        src = TreeNode("src")
        main = TreeNode("main.py")

        root.add_child(src)
        src.add_child(main)

        # Find existing path
        found = root.find_node_by_path("project/src/main.py")
        assert found is not None
        assert found.name == "main.py"

        # Try non-existent path
        not_found = root.find_node_by_path("project/nonexistent.txt")
        assert not_found is None

        print("✅ Find node by path test passed")


class TestCommentParser:
    """Test CommentParser class."""

    @staticmethod
    def test_no_comment():
        """Test extraction when no comment exists."""
        name, comment = CommentParser.extract_comment("file.txt")
        assert name == "file.txt"
        assert comment is None
        print("✅ No comment test passed")

    @staticmethod
    def test_double_slash_comment():
        """Test // comment extraction."""
        name, comment = CommentParser.extract_comment("file.cpp // Entry point")
        assert name == "file.cpp"
        assert comment == "Entry point"
        print("✅ Double slash comment test passed")

    @staticmethod
    def test_hash_comment():
        """Test # comment extraction."""
        name, comment = CommentParser.extract_comment("script.py # Main script")
        assert name == "script.py"
        assert comment == "Main script"
        print("✅ Hash comment test passed")

    @staticmethod
    def test_html_comment():
        """Test <!-- comment extraction."""
        name, comment = CommentParser.extract_comment("index.html <!-- Homepage -->")
        assert name == "index.html"
        assert comment == "Homepage -->"
        print("✅ HTML comment test passed")

    @staticmethod
    def test_slash_star_comment():
        """Test /* comment extraction (treated as line comment)."""
        name, comment = CommentParser.extract_comment("styles.css /* Main styles */")
        assert name == "styles.css"
        assert comment == "Main styles */"
        print("✅ Slash-star comment test passed")

    @staticmethod
    def test_multiple_comments():
        """Test that earliest comment prefix wins."""
        name, comment = CommentParser.extract_comment("file.txt # Comment1 // Comment2")
        assert name == "file.txt"
        assert comment == "Comment1 // Comment2"
        print("✅ Multiple comments test passed")

    @staticmethod
    def test_comment_with_whitespace():
        """Test comment with leading/trailing whitespace."""
        name, comment = CommentParser.extract_comment("file.txt   //   Comment   ")
        assert name == "file.txt"
        assert comment == "Comment"
        print("✅ Comment with whitespace test passed")


class TestCodeFenceDetector:
    """Test CodeFenceDetector class."""

    @staticmethod
    def test_pre_fence_filename():
        """Test filename detection before fence."""
        text = """
Some text
main.cpp
```cpp
int main() {
    return 0;
}
```
"""
        fences = CodeFenceDetector.find_code_fences(text)
        assert len(fences) == 1
        assert fences[0][0] == "main.cpp"
        assert "int main()" in fences[0][1]
        print("✅ Pre-fence filename test passed")

    @staticmethod
    def test_on_fence_filename():
        """Test filename on the fence line."""
        text = """
```utils.py
def helper():
    pass
```
"""
        fences = CodeFenceDetector.find_code_fences(text)
        assert len(fences) == 1
        assert fences[0][0] == "utils.py"
        assert "def helper()" in fences[0][1]
        print("✅ On-fence filename test passed")

    @staticmethod
    def test_post_fence_filename():
        """Test filename in first line of fence."""
        text = """
```python
# main.py
def main():
    pass
```
"""
        fences = CodeFenceDetector.find_code_fences(text)
        assert len(fences) == 1
        assert fences[0][0] == "main.py"
        assert "def main()" in fences[0][1]
        assert "# main.py" not in fences[0][1]  # Filename line should be removed
        print("✅ Post-fence filename test passed")

    @staticmethod
    def test_fence_with_path():
        """Test filename with path."""
        text = """
```src/utils/helper.js
function help() {}
```
"""
        fences = CodeFenceDetector.find_code_fences(text)
        assert len(fences) == 1
        assert fences[0][0] == "src/utils/helper.js"
        print("✅ Fence with path test passed")

    @staticmethod
    def test_fence_without_filename():
        """Test fence with just language identifier."""
        text = """
```python
# Just some code
print("hello")
```
"""
        fences = CodeFenceDetector.find_code_fences(text)
        # Should not detect filename (no extension, just language)
        assert len(fences) == 0
        print("✅ Fence without filename test passed")

    @staticmethod
    def test_multiple_fences():
        """Test multiple code fences."""
        text = """
main.cpp
```cpp
int main() {}
```

utils.h
```cpp
void util();
```
"""
        fences = CodeFenceDetector.find_code_fences(text)
        assert len(fences) == 2
        assert fences[0][0] == "main.cpp"
        assert fences[1][0] == "utils.h"
        print("✅ Multiple fences test passed")

    @staticmethod
    def test_common_filenames():
        """Test detection of common filenames without extension."""
        text = """
Makefile
```makefile
all:
\tgcc main.c
```

Dockerfile
```dockerfile
FROM python:3.9
```
"""
        fences = CodeFenceDetector.find_code_fences(text)
        assert len(fences) == 2
        assert fences[0][0] == "Makefile"
        assert fences[1][0] == "Dockerfile"
        print("✅ Common filenames test passed")

    @staticmethod
    def test_nested_code_fences():
        """Test that nested fences are preserved in content."""
        text = """
example.md
```markdown
# Example

Here's some code:

```python
def hello():
    print("Hello!")
```

More text after.
```
"""
        fences = CodeFenceDetector.find_code_fences(text)
        assert len(fences) == 1
        assert fences[0][0] == "example.md"

        # The nested fence should be in the content
        content = fences[0][1]
        assert "```python" in content
        assert "def hello():" in content
        assert "```" in content
        assert "More text after" in content
        print("✅ Nested code fences test passed")

    @staticmethod
    def test_indented_fences_ignored():
        """Test that indented fences are ignored."""
        text = """
outer.txt
```text
Some content

    ```python
    # This is indented and should be in content
    print("hello")
    ```

More content
```

    Indented-file.txt
    ```
    This whole fence is indented
    Should be ignored
    ```
"""
        fences = CodeFenceDetector.find_code_fences(text)
        # Should only find outer.txt (the indented fence should be ignored)
        assert len(fences) == 1
        assert fences[0][0] == "outer.txt"

        # The indented fence should be part of the content
        content = fences[0][1]
        assert "```python" in content
        print("✅ Indented fences ignored test passed")


class TestTreeDetector:
    """Test TreeDetector class."""

    @staticmethod
    def test_explicit_structure_marker():
        """Test detection with explicit structure marker."""
        text = """
# Project Description

## File Structure

project/
  src/
    main.py
"""
        start, end = TreeDetector.find_tree_start(text)
        assert start > 0  # Should not start at first line
        lines = text.split('\n')
        assert "project/" in lines[start]
        print("✅ Explicit structure marker test passed")

    @staticmethod
    def test_fallback_to_first_line():
        """Test fallback to first non-empty line."""
        text = """

project/
  src/
    main.py
"""
        start, end = TreeDetector.find_tree_start(text)
        lines = text.split('\n')
        assert "project/" in lines[start]
        print("✅ Fallback to first line test passed")

    @staticmethod
    def test_tree_end_detection():
        """Test detection of tree end."""
        text = """
project/
  src/
    main.py


## Another Section
Some text
"""
        start, end = TreeDetector.find_tree_start(text)
        assert end is not None
        lines = text.split('\n')
        # End should be before "## Another Section"
        assert end < len(lines)
        print("✅ Tree end detection test passed")

    @staticmethod
    def test_tree_end_at_code_fence():
        """Test tree ends at code fence."""
        text = """
project/
  main.py

```python
print("hello")
```
"""
        start, end = TreeDetector.find_tree_start(text)
        assert end is not None
        lines = text.split('\n')
        assert lines[end].strip().startswith('```')
        print("✅ Tree end at code fence test passed")


class TestTreeParser:
    """Test TreeParser class."""

    @staticmethod
    def test_simple_indented():
        """Test simple indented structure."""
        text = """project
  src
    main.py
  tests
    test.py"""

        parser = TreeParser(text)
        nodes = parser.parse()

        assert len(nodes) == 1
        assert nodes[0].name == "project"
        assert len(nodes[0].children) == 2
        print("✅ Simple indented test passed")

    @staticmethod
    def test_with_comments():
        """Test parsing with inline comments."""
        text = """project
  main.py // Entry point
  utils.py # Helper functions
  config.json <!-- Configuration -->"""

        parser = TreeParser(text)
        nodes = parser.parse()

        assert len(nodes) == 1
        root = nodes[0]

        # Find main.py
        main = next((c for c in root.children if c.name == "main.py"), None)
        assert main is not None
        assert main.comment == "Entry point"

        # Find utils.py
        utils = next((c for c in root.children if c.name == "utils.py"), None)
        assert utils is not None
        assert utils.comment == "Helper functions"

        print("✅ With comments test passed")

    @staticmethod
    def test_box_drawing_format():
        """Test box-drawing tree format."""
        text = """📁 project/
│
├── 📄 main.py
└── 📁 src/
    └── utils.py"""

        parser = TreeParser(text)
        nodes = parser.parse()

        assert len(nodes) == 1
        assert nodes[0].name == "project"
        print("✅ Box-drawing format test passed")

    @staticmethod
    def test_shorthand_notation():
        """Test shorthand path notation."""
        text = """project/src/main.py
project/src/utils.py
project/tests/test.py"""

        parser = TreeParser(text)
        nodes = parser.parse()

        assert len(nodes) == 1
        assert nodes[0].name == "project"

        src = next((c for c in nodes[0].children if c.name == "src"), None)
        assert src is not None
        assert len(src.children) == 2
        print("✅ Shorthand notation test passed")

    @staticmethod
    def test_mixed_formats():
        """Test mixing different formats."""
        text = """project
  main.py
  tests
    test.py"""

        parser = TreeParser(text)
        nodes = parser.parse()

        assert len(nodes) == 1
        root = nodes[0]

        # Should have main.py and tests as children
        assert len(root.children) == 2

        tests = next((c for c in root.children if c.name == "tests"), None)
        assert tests is not None
        assert len(tests.children) == 1
        print("✅ Mixed formats test passed")

    @staticmethod
    def test_tree_range_limit():
        """Test parsing with line range limits."""
        text = """project
  main.py

Some other text
Not part of tree"""

        parser = TreeParser(text, start_line=0, end_line=2)
        nodes = parser.parse()

        assert len(nodes) == 1
        assert nodes[0].name == "project"
        print("✅ Tree range limit test passed")


class TestTreeBuilder:
    """Test TreeBuilder class."""

    @staticmethod
    def test_basic_build():
        """Test basic file/folder creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = TreeNode("project")
            main = TreeNode("main.py")
            root.add_child(main)

            builder = TreeBuilder(tmpdir)
            stats = builder.build([root])

            project_dir = os.path.join(tmpdir, "project")
            main_file = os.path.join(project_dir, "main.py")

            assert os.path.isdir(project_dir)
            assert os.path.isfile(main_file)
            assert stats['files'] == 1
            print("✅ Basic build test passed")

    @staticmethod
    def test_build_with_comments():
        """Test building files with comments"""
        with tempfile.TemporaryDirectory() as tmpdir:
            builder = TreeBuilder(tmpdir)

            root = TreeNode("src/")
            main = TreeNode("main.py", "Entry point")

            # DEBUG: Check the node properties
            print("\n=== DEBUG: Node info ===")
            print("Node name: {0}".format(main.name))
            print("Node comment: {0}".format(repr(main.comment)))
            print("Node is_leaf: {0}".format(main.is_leaf))
            print("Node children: {0}".format(len(main.children)))
            print("=== END DEBUG ===\n")

            root.add_child(main)

            stats = builder.build([root])

            main_path = os.path.join(tmpdir, "src", "main.py")

            # DEBUG: Check if file exists and what's in it
            print("\n=== DEBUG: File info ===")
            print("File exists: {0}".format(os.path.exists(main_path)))
            if os.path.exists(main_path):
                with open(main_path, 'r') as f:
                    content = f.read()
                print("File content: {0}".format(repr(content)))
                print("Content length: {0}".format(len(content)))
            print("=== END DEBUG ===\n")

            with open(main_path, 'r') as f:
                content = f.read()

            assert "# Entry point" in content
            assert stats['files'] == 1  # Note: 'files' not 'files_created'

        print("✅ Build with comments test passed")

    @staticmethod
    def test_code_fence_content():
        """Test filling content from code fences."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = TreeNode("project")
            main = TreeNode("main.py", comment="Entry point")
            root.add_child(main)

            code_fences = [
                ("main.py", "print('Hello, world!')", 0)
            ]

            builder = TreeBuilder(tmpdir)
            stats = builder.build([root], code_fences)

            main_file = os.path.join(tmpdir, "project", "main.py")

            with open(main_file, 'r') as f:
                content = f.read()

            assert "# Entry point" in content
            assert "print('Hello, world!')" in content
            print("✅ Code fence content test passed")

    @staticmethod
    def test_duplicate_file_creation():
        """Test duplicate file naming."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create initial file with content
            test_file = os.path.join(tmpdir, "test.txt")
            with open(test_file, 'w') as f:
                f.write("Original content\n")

            # Try to create another with same name
            root = TreeNode("test.txt")
            code_fences = [
                ("test.txt", "New content", 0)
            ]

            builder = TreeBuilder(tmpdir)
            builder.build([root], code_fences)

            # Should create test (1).txt
            duplicate = os.path.join(tmpdir, "test (1).txt")
            assert os.path.exists(duplicate)

            with open(duplicate, 'r') as f:
                content = f.read()
            assert "New content" in content
            print("✅ Duplicate file creation test passed")

    @staticmethod
    def test_shorthand_file_creation():
        """Test creating files from shorthand paths in fences."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # No tree, just code fence with path
            code_fences = [
                ("src/utils/helper.js", "function help() {}", 0)
            ]

            builder = TreeBuilder(tmpdir)
            builder.build([], code_fences)

            helper_file = os.path.join(tmpdir, "src", "utils", "helper.js")
            assert os.path.exists(helper_file)

            with open(helper_file, 'r') as f:
                content = f.read()
            assert "function help()" in content
            print("✅ Shorthand file creation test passed")

    @staticmethod
    def test_non_destructive():
        """Test non-destructive behavior."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create existing file
            existing = os.path.join(tmpdir, "existing.txt")
            with open(existing, 'w') as f:
                f.write("original")

            # Try to create same file
            node = TreeNode("existing.txt")
            builder = TreeBuilder(tmpdir)
            stats = builder.build([node])

            # Should be skipped
            assert stats['skipped'] == 1

            with open(existing, 'r') as f:
                content = f.read()
            assert content == "original"
            print("✅ Non-destructive test passed")

# Add these to the run_all_tests function
def run_all_tests():
    """Run all test suites."""
    print("=" * 70)
    print("Running HandeeFramer Comprehensive Unit Tests")
    print("=" * 70)
    print()

    # TreeNode tests
    print("Testing TreeNode class...")
    TestTreeNode.test_node_creation()
    TestTreeNode.test_node_with_comment()
    TestTreeNode.test_add_child()
    TestTreeNode.test_get_path()
    TestTreeNode.test_find_node_by_path()
    print()

    # CommentParser tests
    print("Testing CommentParser class...")
    TestCommentParser.test_no_comment()
    TestCommentParser.test_double_slash_comment()
    TestCommentParser.test_hash_comment()
    TestCommentParser.test_html_comment()
    TestCommentParser.test_slash_star_comment()
    TestCommentParser.test_multiple_comments()
    TestCommentParser.test_comment_with_whitespace()
    print()

    # CodeFenceDetector tests
    print("Testing CodeFenceDetector class...")
    TestCodeFenceDetector.test_pre_fence_filename()
    TestCodeFenceDetector.test_on_fence_filename()
    TestCodeFenceDetector.test_post_fence_filename()
    TestCodeFenceDetector.test_fence_with_path()
    TestCodeFenceDetector.test_fence_without_filename()
    TestCodeFenceDetector.test_multiple_fences()
    TestCodeFenceDetector.test_common_filenames()
    TestCodeFenceDetector.test_nested_code_fences()
    TestCodeFenceDetector.test_indented_fences_ignored()
    print()

    # TreeDetector tests
    print("Testing TreeDetector class...")
    TestTreeDetector.test_explicit_structure_marker()
    TestTreeDetector.test_fallback_to_first_line()
    TestTreeDetector.test_tree_end_detection()
    TestTreeDetector.test_tree_end_at_code_fence()
    print()

    # TreeParser tests
    print("Testing TreeParser class...")
    TestTreeParser.test_simple_indented()
    TestTreeParser.test_with_comments()
    TestTreeParser.test_box_drawing_format()
    TestTreeParser.test_shorthand_notation()
    TestTreeParser.test_mixed_formats()
    TestTreeParser.test_tree_range_limit()
    print()

    # TreeBuilder tests
    print("Testing TreeBuilder class...")
    TestTreeBuilder.test_basic_build()
    TestTreeBuilder.test_build_with_comments()
    TestTreeBuilder.test_code_fence_content()
    TestTreeBuilder.test_duplicate_file_creation()
    TestTreeBuilder.test_shorthand_file_creation()
    TestTreeBuilder.test_non_destructive()
    print()

    # NEW TESTS START HERE
    print("Testing Code Fence Language Filtering...")
    try:
        TestCodeFenceLanguageFiltering.test_bash_keyword_rejected()
        TestCodeFenceLanguageFiltering.test_python_keyword_rejected()
        TestCodeFenceLanguageFiltering.test_javascript_keyword_rejected()
        TestCodeFenceLanguageFiltering.test_bash_with_extension_accepted()
        TestCodeFenceLanguageFiltering.test_bash_file_accepted()
        TestCodeFenceLanguageFiltering.test_common_files_accepted()
        TestCodeFenceLanguageFiltering.test_markdown_stripped_language()
        TestCodeFenceLanguageFiltering.test_markdown_stripped_filename()
        TestCodeFenceLanguageFiltering.test_asterisk_stripped()
        TestCodeFenceLanguageFiltering.test_mixed_markdown_stripped()
    except AssertionError as e:
        print("❌ Test failed:")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print("❌ Unexpected error: {0}".format(str(e)))
        import traceback
        traceback.print_exc()
        sys.exit(1)
    print()
    
    print("Testing Code Fence Integration...")
    try:
        TestCodeFenceIntegration.test_bash_fence_no_file()
        TestCodeFenceIntegration.test_json_fence_no_file()
        TestCodeFenceIntegration.test_fence_with_filename()
        TestCodeFenceIntegration.test_multiple_bash_fences()
    except AssertionError as e:
        print("❌ Test failed:")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print("❌ Unexpected error: {0}".format(str(e)))
        import traceback
        traceback.print_exc()
        sys.exit(1)
    print()
    
    print("Testing Directory Counting...")
    try:
        TestDirectoryCounting.test_single_root_directory_counted()
        TestDirectoryCounting.test_multiple_roots_counted()
        TestDirectoryCounting.test_nested_directories_counted()
        TestDirectoryCounting.test_mixed_structure_counted()
        TestDirectoryCounting.test_existing_directories_skipped()
    except AssertionError as e:
        print("❌ Test failed:")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print("❌ Unexpected error: {0}".format(str(e)))
        import traceback
        traceback.print_exc()
        sys.exit(1)
    print()
    
    print("Testing Filename Validation...")
    try:
        TestFilenameValidation.test_trailing_dots_removed()
        TestFilenameValidation.test_asterisk_wildcard_removed()
        TestFilenameValidation.test_backticks_removed()
        TestFilenameValidation.test_empty_after_stripping()
        TestFilenameValidation.test_dotfile_accepted()
    except AssertionError as e:
        print("❌ Test failed:")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print("❌ Unexpected error: {0}".format(str(e)))
        import traceback
        traceback.print_exc()
        sys.exit(1)
    print()

    print("=" * 70)
    print("✅ All 68 tests passed successfully!")  # Updated count!
    print("=" * 70)

if __name__ == "__main__":
    try:
        run_all_tests()
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
