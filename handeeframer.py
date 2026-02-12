import sublime
import sublime_plugin
import os
import re
from datetime import datetime


# ========================================
# DEBUG CONFIGURATION
# ========================================
# Set to True to always keep log files (even on success)
# Set to False to auto-delete logs when no errors occur
DEBUG_MODE = True
# ========================================


class BuildLogger:
    """Handles logging for HandeeFramer builds."""
    
    def __init__(self, root_path):
        self.root_path = root_path
        self.log_path = os.path.join(root_path, 'handeeframer_log.txt')
        self.entries = []
        self.has_errors = False
        self.start_time = datetime.now()
        
        # Initialize log
        self._write_header()
    
    def _write_header(self):
        """Write log file header."""
        self.entries.append("=" * 70)
        self.entries.append("HandeeFramer Build Log")
        self.entries.append("=" * 70)
        self.entries.append("Started: {0}".format(self.start_time.strftime('%Y-%m-%d %H:%M:%S')))
        self.entries.append("Root Path: {0}".format(self.root_path))
        self.entries.append("Debug Mode: {0}".format(DEBUG_MODE))
        self.entries.append("=" * 70)
        self.entries.append("")
    
    def info(self, message, context=None):
        """Log an info message."""
        timestamp = datetime.now().strftime('%H:%M:%S.%')[:-3]
        self.entries.append("[{0}] INFO: {1}")
        if context:
            self.entries.append("  Context: {2}")
    
    def warning(self, message, context=None):
        """Log a warning message."""
        timestamp = datetime.now().strftime('.format(timestamp, message, context)%H:%M:%S.%')[:-3]
        self.entries.append("[{0}] WARNING: {1}")
        if context:
            self.entries.append("  Context: {2}")
    
    def error(self, message, exception=None, context=None):
        """Log an error message."""
        self.has_errors = True
        timestamp = datetime.now().strftime('.format(timestamp, message, context)%H:%M:%S.%')[:-3]
        self.entries.append("[{0}] ERROR: {1}")
        if exception:
            self.entries.append("  Exception: {2}: {3}")
            import traceback
            tb = traceback.format_exc()
            self.entries.append("  Traceback:")
            for line in tb.split('.format(timestamp, message, type(exception).__name__, str(exception))\n'):
                if line.strip():
                    self.entries.append("    {0}".format(line))
        if context:
            self.entries.append("  Context: {0}".format(context))
    
    def section(self, title):
        """Start a new log section."""
        self.entries.append("")
        self.entries.append("-" * 70)
        self.entries.append("  {0}".format(title))
        self.entries.append("-" * 70)
    
    def finalize(self):
        """Write log to file and clean up if no errors."""
        # Add footer
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        self.entries.append("")
        self.entries.append("=" * 70)
        self.entries.append("Completed: {0}".format(end_time.strftime('%Y-%m-%d %H:%M:%S')))
        self.entries.append("Duration: {0:.2f} seconds".format(duration))
        self.entries.append("Status: {0}".format('FAILED' if self.has_errors else 'SUCCESS'))
        self.entries.append("=" * 70)
        
        # Write to file
        try:
            with open(self.log_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.entries))
            
            # Delete if no errors and not in debug mode
            if not self.has_errors and not DEBUG_MODE:
                try:
                    os.remove(self.log_path)
                except Exception:
                    pass  # Ignore cleanup errors
        except Exception as e:
            print("HandeeFramer: Failed to write log file: {0}".format(e))
    
    def get_log_path(self):
        """Get the path to the log file."""
        return self.log_path if (self.has_errors or DEBUG_MODE) else None


class TreeNode:
    """Represents a node in the file tree structure."""
    
    def __init__(self, name, is_leaf=False, parent=None, comment=None):
        self.name = name
        self.is_leaf = is_leaf
        self.children = []
        self.parent = parent
        self.comment = comment  # Store inline comments for files
    
    def add_child(self, child):
        """Add a child node to this node."""
        if not self.is_leaf:
            child.parent = self
            self.children.append(child)
    
    def get_path(self):
        """Get the full path from root to this node."""
        if self.parent is None:
            return self.name
        return os.path.join(self.parent.get_path(), self.name)
    
    def find_node_by_path(self, path):
        """Find a node by its relative path."""
        parts = path.replace('\\', '/').split('/')
        current = self
        
        # If searching from root, start fresh
        if current.name != parts[0]:
            return None
        
        # Navigate through parts
        for part in parts[1:]:
            found = False
            for child in current.children:
                if child.name == part:
                    current = child
                    found = True
                    break
            if not found:
                return None
        
        return current
    
    def __repr__(self):
        leaf_status = "FILE" if self.is_leaf else "DIR"
        comment_info = ", comment='{0}'".format(self.comment) if self.comment else ""
        return "TreeNode({0}, {1}, children={2}{3})".format(self.name, leaf_status, len(self.children), comment_info)


class CommentParser:
    """Parses and extracts comments from file/folder names."""
    
    # Comment prefixes in order of checking
    COMMENT_PREFIXES = ['<!--', '<--', '//', '/*', '#']
    
    @staticmethod
    def extract_comment(text):
        """Extract comment from text.
        
        Returns: (name_without_comment, comment_text_or_none)
        """
        # Find the earliest comment prefix
        earliest_pos = len(text)
        earliest_prefix = None
        
        for prefix in CommentParser.COMMENT_PREFIXES:
            pos = text.find(prefix)
            if pos != -1 and pos < earliest_pos:
                earliest_pos = pos
                earliest_prefix = prefix
        
        if earliest_prefix is None:
            # No comment found
            return text.strip(), None
        
        # Split at comment
        name_part = text[:earliest_pos].rstrip()
        comment_part = text[earliest_pos + len(earliest_prefix):].strip()
        
        return name_part, comment_part if comment_part else None


class CodeFenceDetector:
    """Detects and extracts code fences with filenames."""
    
    @staticmethod
    def find_code_fences(text, logger=None):
        """Find all code fences in text.
        
        Only processes root-level (non-indented) code fences.
        Nested fences inside are preserved in content.
        
        Returns: list of (filename, content, line_number) tuples
        """
        if logger:
            logger.section("Code Fence Detection")
        
        lines = text.split('\n')
        fences = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Check if this is a root-level fence (no leading whitespace)
            stripped = line.strip()
            indent_level = len(line) - len(stripped)
            
            # Only process non-indented fences
            if indent_level == 0 and stripped.startswith('```'):
                if logger:
                    logger.info("Found root-level fence at line {0}".format(i), "Line content: {0}".format(line[:50]))
                
                filename = None
                fence_start = i
                
                # Strategy 1: Check line before fence (pre-fence)
                if i > 0:
                    prev_line = lines[i - 1].strip()
                    if prev_line and not prev_line.startswith('```'):
                        potential_name = CodeFenceDetector._extract_filename(prev_line)
                        if potential_name:
                            filename = potential_name
                            if logger:
                                logger.info("Filename from pre-fence", "Filename: {0}".format(filename))
                
                # Strategy 2: Check on the fence line (on-fence)
                if not filename:
                    fence_content = stripped[3:]  # Remove ```
                    if fence_content and not fence_content.isalpha():
                        potential_name = CodeFenceDetector._extract_filename(fence_content)
                        if potential_name:
                            filename = potential_name
                            if logger:
                                logger.info("Filename from on-fence", "Filename: {0}".format(filename))
                
                # Find fence end and content (handle nested fences)
                i += 1
                content_lines = []
                nesting_level = 0  # Track nested fences
                
                while i < len(lines):
                    current_line = lines[i]
                    current_stripped = current_line.strip()
                    current_indent = len(current_line) - len(current_stripped)
                    
                    # Check if this line is a fence delimiter
                    if current_stripped.startswith('```'):
                        fence_marker = current_stripped[3:].strip()
                        
                        # Determine if this is opening or closing
                        # Opening: has marker (```python, ```json, etc.) OR is indented
                        # Closing: no marker (just ```) AND at root level (indent == 0)
                        
                        is_opening = fence_marker != '' or current_indent > 0
                        is_closing = fence_marker == '' and current_indent == 0
                        
                        if is_opening:
                            # This is a nested/indented fence opening
                            nesting_level += 1
                            content_lines.append(current_line)
                            if logger:
                                logger.info("Nested fence opened at line {0}".format(i), 
                                          "Marker: '{0}', indent: {1}, level: {2}".format(fence_marker, current_indent, nesting_level))
                        elif is_closing:
                            # Root-level closing fence
                            if nesting_level > 0:
                                # We're still inside nested content
                                nesting_level -= 1
                                content_lines.append(current_line)
                                if logger:
                                    logger.info("Nested fence closed at line {0}".format(i), "Level: {0}".format(nesting_level))
                            else:
                                # This closes our fence
                                if logger:
                                    logger.info("Root fence closed at line {0}".format(i))
                                break
                        else:
                            # Shouldn't happen but include it
                            content_lines.append(current_line)
                    else:
                        # Regular content line
                        content_lines.append(current_line)
                    
                    i += 1
                
                # Strategy 3: Check first line of content (post-fence)
                if not filename and content_lines:
                    first_line = content_lines[0].strip()
                    if first_line:
                        potential_name = CodeFenceDetector._extract_filename_from_comment(first_line)
                        if potential_name:
                            filename = potential_name
                            # Remove the filename line from content
                            content_lines = content_lines[1:]
                            if logger:
                                logger.info("Filename from post-fence", "Filename: {0}".format(filename))
                
                if filename:
                    content = '\n'.join(content_lines)
                    fences.append((filename, content, fence_start))
                    if logger:
                        logger.info("Code fence added", "{0} ({1} chars)".format(filename, len(content)))
                elif logger:
                    logger.warning("Code fence at line {0} has no filename".format(fence_start), "Skipping")
            
            i += 1
        
        if logger:
            logger.info("Total fences detected: {0}".format(len(fences)))
        
        return fences
    
    @staticmethod
    def _extract_filename(text):
        """Extract filename from text, returns None if not a valid filename.
        
        Handles markdown formatting like **`filename`** by stripping ** and ``
        Also handles trailing text like **`filename`** (note) by removing it
        """
        text = text.strip()
        
        # Remove markdown bold+backtick pattern and any trailing text
        # Pattern: **`filename`** (note) -> filename
        # Pattern: **`filename`** -> filename
        # Pattern: `filename` -> filename
        
        # First, find and extract content between backticks if present
        if '`' in text:
            # Find the first ` and last ` 
            first_backtick = text.find('`')
            last_backtick = text.rfind('`')
            if first_backtick != -1 and last_backtick != -1 and first_backtick < last_backtick:
                # Extract content between backticks
                text = text[first_backtick+1:last_backtick]
        
        # Remove any remaining asterisks
        text = text.strip('*').strip()
        
        # Check for common filenames without extensions
        common_files = ['Makefile', 'Dockerfile', 'LICENSE', 'README', 'CHANGELOG', 
                       'CONTRIBUTING', 'AUTHORS', 'INSTALL', 'Gemfile', 'Rakefile']
        
        if text in common_files:
            return text
        
        # Must have an extension or be a dotfile
        if '.' in text or text.startswith('.'):
            # Check for path separators or single word
            if '/' in text or '\\' in text or len(text.split()) == 1:
                # Has path or is single word
                if len(text) < 200:  # Reasonable filename length
                    return text
        
        return None
    
    @staticmethod
    def _extract_filename_from_comment(line):
        """Extract filename from a comment line like '// filename.cpp'."""
        # Check for comment prefixes
        for prefix in ['///', '//', '#', '<!--', '<--']:
            if line.startswith(prefix):
                remainder = line[len(prefix):].strip()
                # Extract filename (before any additional comment)
                filename, _ = CommentParser.extract_comment(remainder)
                filename = filename.strip()
                
                if CodeFenceDetector._extract_filename(filename):
                    return filename
        
        return None


class TreeDetector:
    """Detects where the file tree starts in a document."""
    
    STRUCTURE_KEYWORDS = [
        'structure', 'file structure', 'tree', 'file tree',
        'directory structure', 'folder structure', 'project structure'
    ]
    
    @staticmethod
    def find_tree_start(text):
        """Find where the tree structure starts in the text.
        
        Returns: (start_line_index, end_line_index_or_none)
        """
        lines = text.split('\n')
        
        # Strategy 1: Look for explicit structure markers
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            
            # Check for markers like "## Structure", "# File Tree:", etc.
            for keyword in TreeDetector.STRUCTURE_KEYWORDS:
                if keyword in line_lower:
                    # Tree starts on next non-empty line
                    for j in range(i + 1, len(lines)):
                        if lines[j].strip():
                            return j, TreeDetector._find_tree_end(lines, j)
        
        # Strategy 2: Assume tree starts at first non-empty line
        for i, line in enumerate(lines):
            if line.strip():
                return i, TreeDetector._find_tree_end(lines, i)
        
        return 0, None
    
    @staticmethod
    def _find_tree_end(lines, start_idx):
        """Find where the tree likely ends.
        
        Returns: line index where tree ends, or None if unclear
        """
        # Tree ends when we hit:
        # - A code fence
        # - A markdown heading (if we've seen at least a few tree lines)
        # - Multiple consecutive empty lines
        
        tree_line_count = 0
        empty_line_count = 0
        
        for i in range(start_idx, len(lines)):
            line = lines[i].strip()
            
            # Code fence detected
            if line.startswith('```'):
                if tree_line_count > 0:
                    return i
            
            # Empty line
            if not line:
                empty_line_count += 1
                if empty_line_count >= 3:  # Multiple empty lines
                    return i
            else:
                empty_line_count = 0
                tree_line_count += 1
            
            # Markdown heading (after we've seen some tree)
            if tree_line_count > 3 and line.startswith('#'):
                return i
        
        return None  # Tree goes to end of document


class TreeParser:
    """Parses text representation of file trees into TreeNode structures."""
    
    # Box-drawing characters used in tree diagrams
    BOX_CHARS = {'│', '├', '└', '─', '┌', '┐', '┘', '┤', '┬', '┴', '┼', '═', '║', '╔', '╗', '╚', '╝', '╠', '╣', '╦', '╩', '╬'}
    
    # OS-incompatible filename characters (excluding parentheses - Next.js route groups use them)
    WINDOWS_INVALID = {'<', '>', ':', '"', '|', '?', '*'}
    # Note: Forward slash (/) and backslash (\) are handled separately for path parsing
    # Parentheses ( ) are allowed for Next.js route groups like app/(dashboard)/
    # Square brackets [ ] are allowed for Next.js dynamic routes like [id]/
    # Control characters (0-31) and DEL (127)
    CONTROL_CHARS = set(chr(i) for i in range(32)) | {chr(127)}
    
    def __init__(self, text, start_line=0, end_line=None):
        """Initialize parser with text and optional line range."""
        self.text = text
        all_lines = text.split('\n')
        
        # Extract only the tree portion
        if end_line is None:
            self.lines = all_lines[start_line:]
        else:
            self.lines = all_lines[start_line:end_line]
    
    @staticmethod
    def remove_emojis(text):
        """Remove all emoji characters from text."""
        # Emoji pattern - covers most emoji ranges
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U00002702-\U000027B0"  # dingbats
            "\U000024C2-\U0001F251"  # enclosed characters
            "\U0001F900-\U0001F9FF"  # supplemental symbols
            "\U0001FA00-\U0001FA6F"  # chess symbols
            "\U0001FA70-\U0001FAFF"  # symbols and pictographs extended-a
            "\U00002600-\U000026FF"  # miscellaneous symbols
            "\U00002700-\U000027BF"  # dingbats
            "]+",
            flags=re.UNICODE
        )
        return emoji_pattern.sub('', text)
    
    @staticmethod
    def sanitize_filename(name):
        """Clean filename to be OS-compatible (but preserve slashes for paths)."""
        # Remove emojis
        name = TreeParser.remove_emojis(name)
        
        # Remove box-drawing characters
        for char in TreeParser.BOX_CHARS:
            name = name.replace(char, '')
        
        # Remove Windows-invalid characters (except slashes which we handle separately)
        for char in TreeParser.WINDOWS_INVALID:
            name = name.replace(char, '')
        
        # Remove control characters
        for char in TreeParser.CONTROL_CHARS:
            name = name.replace(char, '')
        
        # Strip whitespace
        name = name.strip()
        
        # Replace multiple spaces with single space
        name = re.sub(r'\s+', ' ', name)
        
        return name
    
    @staticmethod
    def clean_line_prefix(line):
        """Remove box-drawing tree characters from the beginning of a line.
        
        Returns: (cleaned_line, indent_level)
        """
        # Pattern to match box-drawing characters and spaces at the start
        pattern = r'^([\s│├└─]+)'
        
        match = re.match(pattern, line)
        if match:
            prefix = match.group(1)
            indent_level = len(prefix)
            cleaned = line[len(prefix):]
            return cleaned, indent_level
        
        # No box-drawing prefix, count normal whitespace
        indent = len(line) - len(line.lstrip())
        return line.lstrip(), indent
    
    def parse(self):
        """Parse the text and return a list of root nodes."""
        nodes = []
        stack = []  # (indent_level, node)
        
        for line in self.lines:
            if not line.strip():
                continue
            
            # Clean the line - remove box-drawing characters and get indent
            cleaned_line, indent = self.clean_line_prefix(line)
            
            if not cleaned_line.strip():
                continue
            
            # Extract comment from the line
            name_part, comment = CommentParser.extract_comment(cleaned_line.strip())
            
            if not name_part:
                continue
            
            # Check for shorthand notation (preserve slashes for now)
            stripped = name_part.strip()
            has_slashes = '/' in stripped or '\\' in stripped
            path_parts = stripped.replace('\\', '/').split('/')
            is_shorthand = has_slashes and len([p for p in path_parts if p]) > 1
            
            if is_shorthand:
                self._parse_shorthand(stripped, nodes, stack, indent, comment)
            else:
                # Sanitize the name (no slashes to preserve here)
                sanitized = stripped
                # Remove slashes from single names
                for char in ['/', '\\']:
                    sanitized = sanitized.replace(char, '')
                sanitized = self.sanitize_filename(sanitized)
                
                if sanitized:
                    self._parse_indented(sanitized, nodes, stack, indent, comment)
        
        return nodes
    
    def _parse_shorthand(self, path_string, nodes, stack, base_indent, comment=None):
        """Parse shorthand notation and clean each path component."""
        parts = path_string.replace('\\', '/').split('/')
        
        # Clean each part individually
        cleaned_parts = []
        for part in parts:
            # Remove slashes from individual parts
            part_clean = part
            for char in ['/', '\\']:
                part_clean = part_clean.replace(char, '')
            part_clean = self.sanitize_filename(part_clean)
            if part_clean:
                cleaned_parts.append(part_clean)
        
        if not cleaned_parts:
            return
        
        # Find parent based on indentation
        parent_node = None
        while stack and stack[-1][0] >= base_indent:
            stack.pop()
        if stack:
            parent_node = stack[-1][1]
        
        # Find or create the root
        root = None
        if parent_node:
            for child in parent_node.children:
                if child.name == cleaned_parts[0]:
                    root = child
                    break
            if root is None:
                root_comment = comment if len(cleaned_parts) == 1 else None
                root = TreeNode(cleaned_parts[0], is_leaf=(len(cleaned_parts) == 1), comment=root_comment)
                parent_node.add_child(root)
        else:
            for node in nodes:
                if node.name == cleaned_parts[0]:
                    root = node
                    break
            if root is None:
                root_comment = comment if len(cleaned_parts) == 1 else None
                root = TreeNode(cleaned_parts[0], is_leaf=(len(cleaned_parts) == 1), comment=root_comment)
                nodes.append(root)
        
        # Build the path
        current = root
        for i, part in enumerate(cleaned_parts[1:], 1):
            is_last = (i == len(cleaned_parts) - 1)
            is_leaf = is_last
            node_comment = comment if is_last else None
            
            # Look for existing child
            child = None
            for c in current.children:
                if c.name == part:
                    child = c
                    break
            
            if child is None:
                child = TreeNode(part, is_leaf=is_leaf, comment=node_comment)
                current.add_child(child)
            elif is_last and comment and not child.comment:
                # Update comment if it doesn't have one
                child.comment = comment
            
            current = child
        
        # Add root to stack if no parent
        if not parent_node:
            stack.append((base_indent, root))
    
    def _parse_indented(self, name, nodes, stack, indent, comment=None):
        """Parse indented notation with pre-cleaned name."""
        is_explicit_dir = name.endswith('/') or name.endswith('\\')
        name = name.rstrip('/\\').strip()
        
        if not name:
            return
        
        is_leaf = not is_explicit_dir
        node = TreeNode(name, is_leaf=is_leaf, comment=comment)
        
        # Find the correct parent based on indentation
        while stack and stack[-1][0] >= indent:
            stack.pop()
        
        if stack:
            parent = stack[-1][1]
            if parent.is_leaf:
                parent.is_leaf = False
            parent.add_child(node)
        else:
            nodes.append(node)
        
        # Add to stack so it can be a potential parent
        stack.append((indent, node))


class TreeBuilder:
    """Builds the actual file/folder structure from TreeNode objects."""
    
    def __init__(self, root_path, logger=None):
        self.root_path = root_path
        self.logger = logger or BuildLogger(root_path)
        self.created_dirs = set()
        self.created_files = set()
        self.skipped = set()
        self.node_map = {}  # Map full paths to nodes for content filling
    
    def build(self, nodes, code_fences=None):
        """Build the file structure from the tree nodes.
        
        Args:
            nodes: List of root TreeNode objects
            code_fences: Optional list of (filename, content, line_num) tuples
        """
        try:
            self.logger.section("Building File Structure")
            self.logger.info("Processing {0} root node(s)".format(len(nodes)))
            
            # First pass: create all files and directories
            for node in nodes:
                self._build_node(node, self.root_path)
            
            self.logger.info("Created {0} directories".format(len(self.created_dirs)))
            self.logger.info("Created {0} files".format(len(self.created_files)))
            self.logger.info("Skipped {0} existing items".format(len(self.skipped)))
            
            # Second pass: fill in content from code fences
            if code_fences:
                self.logger.section("Filling Content from Code Fences")
                self._fill_content_from_fences(nodes, code_fences)
            
            return {
                'dirs': len(self.created_dirs),
                'files': len(self.created_files),
                'skipped': len(self.skipped)
            }
        except Exception as e:
            self.logger.error("Build failed", e, "Root path: {0}".format(self.root_path))
            raise
    
    def _build_node(self, node, parent_path):
        """Recursively build a node and its children."""
        try:
            full_path = os.path.join(parent_path, node.name)
            
            # Store node mapping for later content filling
            self.node_map[full_path] = node
            
            if node.is_leaf:
                # Create file
                if os.path.exists(full_path):
                    self.skipped.add(full_path)
                    self.logger.info("Skipped existing file: {0}".format(full_path))
                else:
                    try:
                        os.makedirs(os.path.dirname(full_path), exist_ok=True)
                        # Create file with comment if it exists
                        with open(full_path, 'w', encoding='utf-8') as f:
                            if node.comment:
                                comment_line = self._format_comment(full_path, node.comment)
                                f.write(comment_line + '\n')
                        self.created_files.add(full_path)
                        self.logger.info("Created file: {0}".format(full_path), 
                                       "With comment: {0}".format(node.comment) if node.comment else None)
                    except Exception as e:
                        self.logger.error("Failed to create file: {0}".format(full_path), e)
            else:
                # Create directory
                if os.path.exists(full_path):
                    if not os.path.isdir(full_path):
                        self.skipped.add(full_path)
                        self.logger.warning("Path exists but is not a directory: {0}".format(full_path))
                        return
                else:
                    try:
                        os.makedirs(full_path, exist_ok=True)
                        self.created_dirs.add(full_path)
                        self.logger.info("Created directory: {0}".format(full_path))
                    except Exception as e:
                        self.logger.error("Failed to create directory: {0}".format(full_path), e)
                        return
                
                # Build children
                for child in node.children:
                    self._build_node(child, full_path)
        
        except Exception as e:
            self.logger.error("Error building node: {0}".format(node.name), e, 
                            "Parent: {0}".format(parent_path))
            raise
    
    def _format_comment(self, filepath, comment):
        """Format comment with appropriate syntax based on file extension."""
        ext = os.path.splitext(filepath)[1].lower()
        
        # Python, Ruby, Shell, YAML, etc.
        if ext in ['.py', '.rb', '.sh', '.bash', '.yml', '.yaml', '.toml', '.con']:
            return "# {0}"
        # C-style languages
        elif ext in ['.format(comment).c', '.cpp', '.h', '.hpp', '.java', '.js', '.ts', '.jsx', '.tsx', 
                     '.cs', '.go', '.rs', '.swift', '.kt', '.scala', '.php']:
            return "// {0}".format(comment)
        # HTML, XML
        elif ext in ['.html', '.xml', '.svg']:
            return "<!-- {0} -->".format(comment)
        # CSS, SCSS, SASS
        elif ext in ['.css', '.scss', '.sass', '.less']:
            return "/* {0} */".format(comment)
        # SQL
        elif ext in ['.sql']:
            return "-- {0}".format(comment)
        # Default
        else:
            return "# {0}".format(comment)
    
    def _fill_content_from_fences(self, nodes, code_fences):
        """Fill file content from code fences."""
        self.logger.info("Processing {0} code fences".format(len(code_fences)))
        
        for filename, content, line_num in code_fences:
            try:
                self.logger.info("Processing fence: {0}".format(filename), "From line {0}, {1} chars".format(line_num, len(content)))
                
                # Try to find the file in our node map
                matched_path = self._find_matching_file(filename, nodes)
                
                if matched_path:
                    self.logger.info("Matched to tree path: {0}".format(matched_path))
                    node = self.node_map.get(matched_path)
                    
                    # Check if file exists and what's in it
                    if os.path.exists(matched_path):
                        with open(matched_path, 'r', encoding='utf-8') as f:
                            existing_content = f.read()
                        
                        # Check if it's only our comment
                        is_only_comment = False
                        if node and node.comment:
                            comment_line = self._format_comment(matched_path, node.comment)
                            if existing_content.strip() == comment_line.strip():
                                is_only_comment = True
                        
                        # Determine action
                        if not existing_content.strip() or is_only_comment:
                            # Empty or only has our comment - safe to append
                            with open(matched_path, 'a', encoding='utf-8') as f:
                                if existing_content and not existing_content.endswith('\n'):
                                    f.write('\n')
                                f.write(content)
                            self.logger.info("Appended content to: {0}".format(matched_path))
                        else:
                            # File has other content - create duplicate
                            new_path = self._get_duplicate_filename(matched_path)
                            with open(new_path, 'w', encoding='utf-8') as f:
                                f.write(content)
                            self.created_files.add(new_path)
                            self.logger.warning("File had content, created duplicate: {0}".format(new_path))
                    else:
                        # File doesn't exist yet - create it
                        os.makedirs(os.path.dirname(matched_path), exist_ok=True)
                        with open(matched_path, 'w', encoding='utf-8') as f:
                            if node and node.comment:
                                comment_line = self._format_comment(matched_path, node.comment)
                                f.write(comment_line + '\n')
                            f.write(content)
                        self.created_files.add(matched_path)
                        self.logger.info("Created new file with content: {0}".format(matched_path))
                else:
                    # Path not in tree - create it as shorthand
                    self.logger.info("Not in tree, creating as shorthand: {0}".format(filename))
                    self._create_from_shorthand(filename, content)
            
            except Exception as e:
                self.logger.error("Failed to process fence: {0}".format(filename), e, 
                                "Line {0}, content length: {1}".format(line_num, len(content)))
                # Continue with other fences
    
    def _find_matching_file(self, filename, nodes):
        """Find a file in the tree that matches the filename/path."""
        # Check if it's a full path or just a filename
        if '/' in filename or '\\' in filename:
            # It's a path - try to match exactly
            normalized_path = filename.replace('\\', '/')
            
            # Try each root node
            for node in nodes:
                candidate = os.path.join(self.root_path, normalized_path)
                if candidate in self.node_map:
                    return candidate
        else:
            # Just a filename - search for it
            for path in self.node_map.keys():
                if os.path.basename(path) == filename:
                    return path
        
        return None
    
    def _create_from_shorthand(self, filepath, content):
        """Create a file from shorthand path notation."""
        full_path = os.path.join(self.root_path, filepath.replace('\\', '/'))
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, 'w') as f:
            f.write(content)
        self.created_files.add(full_path)
    
    def _get_duplicate_filename(self, filepath):
        """Get a duplicate filename with (N) suffix."""
        directory = os.path.dirname(filepath)
        filename = os.path.basename(filepath)
        name, ext = os.path.splitext(filename)
        
        counter = 1
        while True:
            new_name = "{0} ({1}){2}".format(name, counter, ext)
            new_path = os.path.join(directory, new_name)
            if not os.path.exists(new_path):
                return new_path
            counter += 1


class BuildHandeeFrameCommand(sublime_plugin.TextCommand):
    """Smart command that builds from selection if available, otherwise from document."""
    
    def run(self, edit):
        # Check if text is selected
        selection = self.view.sel()
        has_selection = selection and len(selection) > 0 and not selection[0].empty()
        
        if has_selection:
            # Build from selection
            region = selection[0]
            text = self.view.substr(region)
            source = "selection"
        else:
            # Build from entire document
            region = sublime.Region(0, self.view.size())
            text = self.view.substr(region)
            source = "document"
        
        if not text.strip():
            sublime.error_message("No content to build from.")
            return
        
        self._build_tree(text, source)
    
    def _build_tree(self, text, source):
        """Parse and build the tree structure."""
        # Determine root path first (needed for logger)
        current_file = self.view.file_name()
        if not current_file:
            sublime.error_message(
                "HandeeFramer requires a saved file.\n\n"
                "Please save your file first (Ctrl+S / Cmd+S),\n"
                "then run the command again."
            )
            return
        
        root_path = os.path.dirname(current_file)
        logger = BuildLogger(root_path)
        
        try:
            logger.info("Building from {0}".format(source))
            logger.info("Document: {0}".format(current_file))
            logger.info("Text length: {0} characters".format(len(text)))
            
            # Detect tree start and end
            logger.section("Tree Detection")
            tree_start, tree_end = TreeDetector.find_tree_start(text)
            logger.info("Tree range: lines {0} to {1}".format(tree_start, tree_end))
            
            # Parse the tree
            logger.section("Tree Parsing")
            parser = TreeParser(text, start_line=tree_start, end_line=tree_end)
            nodes = parser.parse()
            
            if not nodes:
                logger.error("No valid tree structure found")
                sublime.error_message("No valid tree structure found.")
                return
            
            logger.info("Parsed {0} root node(s)".format(len(nodes)))
            
            # Detect code fences
            code_fences = CodeFenceDetector.find_code_fences(text, logger)
            
            # Check if we need to use the parent directory as root
            if len(nodes) > 1:
                # Multiple root nodes, use current directory as root
                logger.info("Multiple roots detected, using current directory")
            else:
                # Single root node, use it as the root directory
                logger.info("Single root detected: {0}".format(nodes[0].name))
                root_path = os.path.join(root_path, nodes[0].name)
                nodes = nodes[0].children if not nodes[0].is_leaf else []
            
            logger.info("Final root path: {0}".format(root_path))
            
            # Build the structure
            builder = TreeBuilder(root_path, logger)
            stats = builder.build(nodes, code_fences)
            
            logger.info("Build completed successfully")
            logger.finalize()
            
            # Show results
            log_info = "\nLog: {0}".format(logger.get_log_path()) if logger.get_log_path() else ""
            log_info = "\nLog: {0}".format(logger.get_log_path()) if logger.get_log_path() else ""
            message = (
                "HandeeFramer built successfully!\n\n"
                "Source: {0}\n"
                "Created {1} directories\n"
                "Created {2} files\n"
                "Skipped {3} existing items\n"
                "Processed {4} code blocks"
                "{5}"
            ).format(source.capitalize(), stats['dirs'], stats['files'], 
                     stats['skipped'], len(code_fences), log_info)
            sublime.message_dialog(message)
        
        except Exception as e:
            logger.error("Build failed with exception", e)
            logger.finalize()
            sublime.error_message(
                "HandeeFramer encountered an error.\n\n"
                "Error: {0}\n\n"
                "Check log: {1}".format(str(e), logger.get_log_path())
            )
    
    def is_enabled(self):
        """Enable if view has content."""
        return self.view.size() > 0


# Keep old commands for backward compatibility (they just call the new one)
class BuildTreeFromSelectionCommand(sublime_plugin.TextCommand):
    """Legacy command - redirects to unified command."""
    def run(self, edit):
        self.view.run_command('build_handee_frame')
    def is_enabled(self):
        return self.view.size() > 0


class BuildTreeFromDocumentCommand(sublime_plugin.TextCommand):
    """Legacy command - redirects to unified command."""
    def run(self, edit):
        self.view.run_command('build_handee_frame')
    def is_enabled(self):
        return self.view.size() > 0
