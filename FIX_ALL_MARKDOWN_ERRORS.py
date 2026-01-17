"""
Automatically fix all markdown linting errors in the workspace.
Fixes MD040 (fenced code language) and MD060 (table formatting) issues.
"""
import re
from pathlib import Path

# Files with errors based on error report
FILES_TO_FIX = [
    "OMEGA_DUAL_VOICE_SYSTEM_STATUS.md",
    "VOICE_SYSTEM_EXECUTION_SUMMARY.md",
    "FFMPEG_INSTALLATION_REQUIRED.md",
    "VOICE_ANALYSIS_COMPLETE.md",
    "VOICE_SYSTEM_FINAL_STATUS.md",
    "SYSTEM_INTEGRATION_COMPLETE.md"
]

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
        # Check if line is a table separator (contains only |, -, and no letters/numbers)
        if '|' in line and '-' in line and not any(c.isalnum() for c in line):
            # This is likely a table separator row
            # Split by | and process each cell
            parts = line.split('|')
            fixed_parts = []
            
            for part in parts:
                stripped = part.strip()
                if stripped:  # Not empty
                    # Ensure spaces around dashes
                    if '-' in stripped:
                        # Replace consecutive dashes with spaced version
                        fixed_parts.append(f" {stripped} ")
                    else:
                        fixed_parts.append(f" {stripped} ")
                else:
                    fixed_parts.append(part)  # Keep empty parts as-is
            
            fixed_line = '|'.join(fixed_parts)
            fixed_lines.append(fixed_line)
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
    
    print("=" * 60)
    print("FIXING MARKDOWN LINTING ERRORS")
    print("=" * 60)
    print()
    
    for filename in FILES_TO_FIX:
        filepath = workspace_root / filename
        if filepath.exists():
            print(f"Processing: {filename}...", end=" ")
            if fix_markdown_file(filepath):
                print("✅ FIXED")
                fixed_count += 1
            else:
                print("⚠️ No changes needed")
        else:
            print(f"❌ Not found: {filename}")
    
    print()
    print("=" * 60)
    print(f"COMPLETE: Fixed {fixed_count} / {len(FILES_TO_FIX)} files")
    print("=" * 60)
    print()
    print("Run 'git status' to see changes, then commit if needed.")

if __name__ == "__main__":
    main()
