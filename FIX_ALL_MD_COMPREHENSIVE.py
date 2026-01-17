"""
Comprehensively fix ALL markdown linting errors across the entire workspace.
Fixes MD040 (fenced code language) and MD060 (table formatting) issues.
"""
import re
from pathlib import Path

def fix_fenced_code_blocks(content):
    """
    Fix MD040: Add 'text' language to fenced code blocks without language.
    Matches ``` at start of line, followed by newline (not already having a language).
    """
    # Pattern: ``` followed immediately by newline (no language specified)
    pattern = r'^```$'
    replacement = r'```text'
    fixed = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    return fixed

def fix_table_pipes(content):
    """
    Fix MD060: Add spaces around table pipes for proper formatting.
    Fixes separator rows like |---|---|---| to | --- | --- | --- |
    """
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Check if line is a table separator (contains only |, -, spaces, and no letters/numbers)
        if '|' in line and '-' in line:
            stripped = line.strip()
            # Check if it's only pipes and dashes (table separator)
            if all(c in '|-' for c in stripped):
                # This is a table separator row
                parts = stripped.split('|')
                fixed_parts = []
                
                for part in parts:
                    if part:  # Not empty
                        # Ensure spaces around dashes
                        fixed_parts.append(f" {part} ")
                    else:
                        fixed_parts.append(part)
                
                fixed_line = '|'.join(fixed_parts)
                fixed_lines.append(fixed_line)
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def fix_markdown_file(filepath):
    """Fix all markdown linting issues in a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply fixes
        content = fix_fenced_code_blocks(content)
        content = fix_table_pipes(content)
        
        # Only write if changes were made
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error fixing {filepath}: {e}")
        return False

def main():
    """Main function to fix all markdown files."""
    workspace_root = Path(__file__).parent
    fixed_count = 0
    skipped_count = 0
    total_count = 0
    
    print("=" * 70)
    print("COMPREHENSIVE MARKDOWN LINTING ERROR FIX")
    print("=" * 70)
    print()
    print("Scanning all .md files in workspace...")
    print()
    
    # Find all .md files recursively
    md_files = list(workspace_root.rglob("*.md"))
    print(f"Found {len(md_files)} markdown files")
    print()
    
    for md_file in md_files:
        total_count += 1
        relative_path = md_file.relative_to(workspace_root)
        
        # Skip files in certain directories
        if any(part in str(relative_path).split('\\') for part in ['.git', 'node_modules', '.venv', '__pycache__']):
            continue
        
        if fix_markdown_file(md_file):
            print(f"✅ {relative_path}")
            fixed_count += 1
        else:
            skipped_count += 1
    
    print()
    print("=" * 70)
    print(f"COMPLETE: Fixed {fixed_count} files | Skipped {skipped_count} files | Total: {total_count}")
    print("=" * 70)
    print()
    print("Run 'git status' to see changes, then commit if needed.")

if __name__ == "__main__":
    main()
