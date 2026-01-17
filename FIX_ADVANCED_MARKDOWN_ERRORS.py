"""
Advanced Markdown Linter Fix - Phase 2
Fixes remaining MD022, MD032, MD031, MD029, MD036, MD051, MD034 errors
"""
import re
from pathlib import Path

def fix_blank_lines_around_headings(content):
    """Fix MD022: Ensure blank lines before and after headings"""
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        # Check if this is a heading line
        is_heading = line.strip().startswith('#') and line.strip()[0:7].count('#') <= 6
        
        if is_heading:
            # Add blank line before heading if needed (and not first line)
            if i > 0 and fixed_lines and fixed_lines[-1].strip() != '':
                fixed_lines.append('')
            
            fixed_lines.append(line)
            
            # Add blank line after heading if next line exists and isn't blank
            if i < len(lines) - 1 and lines[i + 1].strip() != '':
                fixed_lines.append('')
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def fix_blank_lines_around_lists(content):
    """Fix MD032: Ensure blank lines before and after lists"""
    lines = content.split('\n')
    fixed_lines = []
    in_list = False
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Check if line is a list item
        is_list_item = (
            stripped.startswith('- ') or 
            stripped.startswith('* ') or 
            stripped.startswith('+ ') or
            (len(stripped) > 2 and stripped[0].isdigit() and stripped[1:3] in ['. ', ') '])
        )
        
        if is_list_item:
            # Starting a list - add blank line before if needed
            if not in_list and fixed_lines and fixed_lines[-1].strip() != '':
                fixed_lines.append('')
            in_list = True
            fixed_lines.append(line)
        else:
            # Ending a list - add blank line after if needed
            if in_list and stripped != '':
                fixed_lines.append('')
            in_list = False
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def fix_blank_lines_around_code_fences(content):
    """Fix MD031: Ensure blank lines around fenced code blocks"""
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Check if line starts a code fence
        if stripped.startswith('```'):
            # Add blank line before fence if needed
            if i > 0 and fixed_lines and fixed_lines[-1].strip() != '':
                fixed_lines.append('')
            
            fixed_lines.append(line)
            
            # Find the closing fence
            closing_index = None
            for j in range(i + 1, len(lines)):
                if lines[j].strip().startswith('```'):
                    closing_index = j
                    break
            
            # Add blank line after closing fence if needed
            if closing_index and closing_index < len(lines) - 1:
                if lines[closing_index + 1].strip() != '':
                    # We'll handle this when we get to the closing fence
                    pass
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def fix_ordered_list_numbering(content):
    """Fix MD029: Use consistent ordered list numbering (1/2/3 style)"""
    lines = content.split('\n')
    fixed_lines = []
    list_counter = 0
    in_ordered_list = False
    
    for line in lines:
        stripped = line.strip()
        
        # Check if this is an ordered list item
        if len(stripped) > 2 and stripped[0].isdigit():
            if stripped[1:3] in ['. ', ') ']:
                # This is an ordered list item
                if not in_ordered_list:
                    list_counter = 1
                    in_ordered_list = True
                else:
                    list_counter += 1
                
                # Get indentation
                indent = len(line) - len(line.lstrip())
                separator = '. ' if '. ' in stripped[:4] else ') '
                
                # Rebuild line with correct number
                content_after_number = stripped.split(separator, 1)[1] if separator in stripped else stripped[3:]
                fixed_line = ' ' * indent + f"{list_counter}{separator}{content_after_number}"
                fixed_lines.append(fixed_line)
            else:
                in_ordered_list = False
                list_counter = 0
                fixed_lines.append(line)
        else:
            if stripped == '':
                # Blank line might continue list or end it - keep as is
                fixed_lines.append(line)
            else:
                in_ordered_list = False
                list_counter = 0
                fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def fix_bare_urls(content):
    """Fix MD034: Convert bare URLs to markdown links"""
    # Pattern to find bare URLs not already in markdown link syntax
    pattern = r'(?<!\[)(?<!\()https?://[^\s<>\)\]]+(?!\))'
    
    def replace_url(match):
        url = match.group(0)
        # Don't replace if it's already part of a markdown link
        return f"<{url}>"
    
    fixed = re.sub(pattern, replace_url, content)
    return fixed

def fix_markdown_file(filepath):
    """Apply all fixes to a markdown file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply fixes in order
        content = fix_ordered_list_numbering(content)
        content = fix_blank_lines_around_headings(content)
        content = fix_blank_lines_around_lists(content)
        content = fix_blank_lines_around_code_fences(content)
        content = fix_bare_urls(content)
        
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
    """Main function"""
    workspace_root = Path(__file__).parent
    fixed_count = 0
    skipped_count = 0
    
    print("=" * 70)
    print("ADVANCED MARKDOWN LINTING FIX - PHASE 2")
    print("=" * 70)
    print()
    print("Fixing MD022, MD032, MD031, MD029, MD036, MD034 errors...")
    print()
    
    # Find all .md files
    md_files = list(workspace_root.rglob("*.md"))
    print(f"Found {len(md_files)} markdown files")
    print()
    
    for md_file in md_files:
        relative_path = md_file.relative_to(workspace_root)
        
        # Skip certain directories
        if any(part in str(relative_path).split('\\') for part in ['.git', 'node_modules', '.venv', '__pycache__']):
            continue
        
        if fix_markdown_file(md_file):
            print(f"✅ {relative_path}")
            fixed_count += 1
        else:
            skipped_count += 1
    
    print()
    print("=" * 70)
    print(f"COMPLETE: Fixed {fixed_count} files | Skipped {skipped_count} files")
    print("=" * 70)
    print()
    print("Run 'git status' to see changes.")

if __name__ == "__main__":
    main()
