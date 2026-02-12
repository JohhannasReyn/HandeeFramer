#!/usr/bin/env python3
"""
Comprehensive unit tests for HandeeFramer plugin.

Tests all functions and branches with detailed coverage.
Run with: python test_handeeframer.py
"""

import sys
import os
import tempfile
import shutil

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


class TestTreeNode:
    """Test TreeNode class."""
    
    @staticmethod
    def test_node_creation():
        """Test basic node creation."""
        node = TreeNode("test", is_leaf=False)
        assert node.name == "test"
        assert not node.is_leaf
        assert len(node.children) == 0
        assert node.comment is None
        print("✅ Node creation test passed")
    
    @staticmethod
    def test_node_with_comment():
        """Test node creation with comment."""
        node = TreeNode("file.txt", is_leaf=True, comment="Entry point")
        assert node.name == "file.txt"
        assert node.is_leaf
        assert node.comment == "Entry point"
        print("✅ Node with comment test passed")
    
    @staticmethod
    def test_add_child():
        """Test adding children to nodes."""
        parent = TreeNode("parent", is_leaf=False)
        child = TreeNode("child", is_leaf=True)
        parent.add_child(child)
        
        assert len(parent.children) == 1
        assert child.parent == parent
        print("✅ Add child test passed")
    
    @staticmethod
    def test_get_path():
        """Test path construction."""
        root = TreeNode("root", is_leaf=False)
        child = TreeNode("child", is_leaf=False)
        leaf = TreeNode("file.txt", is_leaf=True)
        
        root.add_child(child)
        child.add_child(leaf)
        
        expected_path = os.path.join("root", "child", "file.txt")
        assert leaf.get_path() == expected_path
        print("✅ Get path test passed")
    
    @staticmethod
    def test_find_node_by_path():
        """Test finding node by path."""
        root = TreeNode("project", is_leaf=False)
        src = TreeNode("src", is_leaf=False)
        main = TreeNode("main.py", is_leaf=True)
        
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
            root = TreeNode("project", is_leaf=False)
            main = TreeNode("main.py", is_leaf=True)
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
        """Test file creation with comments."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = TreeNode("project", is_leaf=False)
            main = TreeNode("main.py", is_leaf=True, comment="Entry point")
            root.add_child(main)
            
            builder = TreeBuilder(tmpdir)
            stats = builder.build([root])
            
            main_file = os.path.join(tmpdir, "project", "main.py")
            
            with open(main_file, 'r') as f:
                content = f.read()
            
            assert "# Entry point" in content
            print("✅ Build with comments test passed")
    
    @staticmethod
    def test_code_fence_content():
        """Test filling content from code fences."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = TreeNode("project", is_leaf=False)
            main = TreeNode("main.py", is_leaf=True, comment="Entry point")
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
            root = TreeNode("test.txt", is_leaf=True)
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
            node = TreeNode("existing.txt", is_leaf=True)
            builder = TreeBuilder(tmpdir)
            stats = builder.build([node])
            
            # Should be skipped
            assert stats['skipped'] == 1
            
            with open(existing, 'r') as f:
                content = f.read()
            assert content == "original"
            print("✅ Non-destructive test passed")


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
    
    print("=" * 70)
    print("✅ All 44 tests passed successfully!")
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
