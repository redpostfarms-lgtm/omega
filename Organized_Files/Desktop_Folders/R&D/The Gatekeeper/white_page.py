# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# GATEKEEPER - White Page Generator
# Creates a blank document with standard formatting

import sys
import io
import subprocess
from pathlib import Path
from datetime import datetime

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BRAIN = Path(r'D:\RPF_BRAIN')
ARCHIVED = BRAIN / 'Archived'
DOCS_DIR = ARCHIVED / 'docs'
DOCS_DIR.mkdir(parents=True, exist_ok=True)

def generate_white_page():
    """Generate a white page document."""
    try:
        # Try python-docx first (Word)
        try:
            from docx import Document
            from docx.shared import Inches, Pt
            
            doc = Document()
            
            # Set page size to A4
            section = doc.sections[0]
            section.page_height = Inches(11.69)  # A4 height
            section.page_width = Inches(8.27)    # A4 width
            
            # Set margins (1 inch = 914400 EMU)
            section.top_margin = Inches(1)
            section.bottom_margin = Inches(1)
            section.left_margin = Inches(1)
            section.right_margin = Inches(1)
            
            # Add header
            header = section.header
            header_para = header.paragraphs[0]
            header_para.text = "System initialized. Gatekeeper standing by."
            header_run = header_para.runs[0]
            header_run.font.name = 'Arial'
            header_run.font.size = Pt(11)
            
            # Add footer
            footer = section.footer
            footer_para = footer.paragraphs[0]
            footer_para.text = "Page 1 of 1"
            footer_run = footer_para.runs[0]
            footer_run.font.name = 'Arial'
            footer_run.font.size = Pt(11)
            
            # Set default font for document
            style = doc.styles['Normal']
            font = style.font
            font.name = 'Arial'
            font.size = Pt(11)
            
            # Set line spacing to 1.15
            paragraph_format = style.paragraph_format
            paragraph_format.line_spacing = 1.15
            
            # Add empty paragraph (blank page)
            doc.add_paragraph()
            
            # Save file
            date_str = datetime.now().strftime('%Y-%m-%d')
            filename = f"White Page - {date_str}.docx"
            file_path = DOCS_DIR / filename
            doc.save(str(file_path))
            
            return str(file_path), filename
            
        except ImportError:
            # Fallback: Use COM automation for Word (Windows)
            if sys.platform == 'win32':
                try:
                    import win32com.client
                    
                    word = win32com.client.Dispatch("Word.Application")
                    word.Visible = True
                    doc = word.Documents.Add()
                    
                    # Set page size to A4 (convert inches to points: 1 inch = 72 points)
                    # A4: 8.27" x 11.69"
                    doc.PageSetup.PageWidth = 8.27 * 72  # A4 width in points
                    doc.PageSetup.PageHeight = 11.69 * 72  # A4 height in points
                    
                    # Set margins (1 inch = 72 points)
                    doc.PageSetup.TopMargin = 72
                    doc.PageSetup.BottomMargin = 72
                    doc.PageSetup.LeftMargin = 72
                    doc.PageSetup.RightMargin = 72
                    
                    # Note: Inches() is not available in COM, using points directly
                    
                    # Set default font
                    doc.Content.Font.Name = "Arial"
                    doc.Content.Font.Size = 11
                    doc.Content.ParagraphFormat.LineSpacing = 1.15 * 12  # 1.15 line spacing
                    
                    # Add header
                    header = doc.Sections(1).Headers(1)
                    header.Range.Text = "System initialized. Gatekeeper standing by."
                    header.Range.Font.Name = "Arial"
                    header.Range.Font.Size = 11
                    
                    # Add footer
                    footer = doc.Sections(1).Footers(1)
                    footer.Range.Text = "Page 1 of 1"
                    footer.Range.Font.Name = "Arial"
                    footer.Range.Font.Size = 11
                    
                    # Save file
                    date_str = datetime.now().strftime('%Y-%m-%d')
                    filename = f"White Page - {date_str}.docx"
                    file_path = DOCS_DIR / filename
                    doc.SaveAs(str(file_path))
                    
                    return str(file_path), filename
                    
                except Exception as e:
                    # Final fallback: Create simple text file
                    date_str = datetime.now().strftime('%Y-%m-%d')
                    filename = f"White Page - {date_str}.txt"
                    file_path = DOCS_DIR / filename
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write("System initialized. Gatekeeper standing by.\n\n")
                        f.write("Page 1 of 1\n")
                    
                    return str(file_path), filename
            else:
                # Linux/Mac: Try LibreOffice
                date_str = datetime.now().strftime('%Y-%m-%d')
                filename = f"White Page - {date_str}.odt"
                file_path = DOCS_DIR / filename
                
                # Create simple ODT file (LibreOffice Writer)
                # This is a minimal ODT structure
                odt_content = """<?xml version="1.0" encoding="UTF-8"?>
<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0">
  <office:body>
    <office:text>
      <text:p>System initialized. Gatekeeper standing by.</text:p>
    </office:text>
  </office:body>
</office:document>"""
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(odt_content)
                
                return str(file_path), filename
                
    except Exception as e:
        raise Exception(f"Error generating white page: {e}")

def open_word_or_writer(file_path):
    """Open document in Word or LibreOffice Writer."""
    try:
        if sys.platform == 'win32':
            # Try Word first
            try:
                subprocess.Popen(['winword.exe', str(file_path)], shell=True)
                return True
            except:
                # Try LibreOffice Writer
                try:
                    subprocess.Popen(['soffice', '--writer', str(file_path)], shell=True)
                    return True
                except:
                    # Open with default application
                    subprocess.Popen(['start', '', str(file_path)], shell=True)
                    return True
        else:
            # Linux/Mac: Try LibreOffice Writer
            try:
                subprocess.Popen(['libreoffice', '--writer', str(file_path)])
                return True
            except:
                # Open with default application
                subprocess.Popen(['xdg-open', str(file_path)])  # Linux
                return True
    except:
        return False

def copy_to_clipboard(text):
    """Copy text to clipboard."""
    try:
        if sys.platform == 'win32':
            try:
                import win32clipboard
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardText(text)
                win32clipboard.CloseClipboard()
                return True
            except ImportError:
                # Fallback: use pyperclip
                try:
                    import pyperclip
                    pyperclip.copy(text)
                    return True
                except ImportError:
                    # Final fallback: use PowerShell
                    try:
                        subprocess.run(
                            ['powershell', '-Command', f'Set-Clipboard -Value "{text}"'],
                            check=True,
                            capture_output=True
                        )
                        return True
                    except:
                        return False
        else:
            # Linux: xclip or xsel
            try:
                subprocess.run(['xclip', '-selection', 'clipboard'], input=text.encode(), check=True)
                return True
            except:
                try:
                    subprocess.run(['xsel', '--clipboard', '--input'], input=text.encode(), check=True)
                    return True
                except:
                    return False
    except:
        return False

def open_folder(folder_path):
    """Open folder in file explorer."""
    try:
        if sys.platform == 'win32':
            subprocess.Popen(['explorer', str(folder_path)])
        else:
            subprocess.Popen(['xdg-open', str(folder_path)])  # Linux
            # Mac: subprocess.Popen(['open', str(folder_path)])
        return True
    except:
        return False

def create_white_page():
    """Create white page document."""
    file_path, filename = generate_white_page()
    open_word_or_writer(file_path)
    return file_path, filename

def send_white_page():
    """Create white page and copy download link to clipboard."""
    file_path, filename = generate_white_page()
    
    # Create file:// URL
    file_url = Path(file_path).as_uri()
    
    # Copy to clipboard
    copy_to_clipboard(file_url)
    
    # Open folder
    open_folder(DOCS_DIR)
    
    return file_path, filename, file_url

def say(text: str):
    """Speak text."""
    try:
        from voice_tuner import load_tune, apply_tune
        tune = load_tune()
        apply_tune(tune)
        
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty('rate', 110)
        engine.setProperty('volume', 0.7)
        engine.say(text)
        engine.runAndWait()
    except:
        print(text)

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'send':
        file_path, filename, file_url = send_white_page()
        print(f"White page ready: {filename}")
        print(f"Download link (copied to clipboard): {file_url}")
        say("White page ready. Link copied to clipboard. Folder opened.")
    else:
        file_path, filename = create_white_page()
        print(f"White page ready: {filename}")
        say("White page ready. File saved.")

