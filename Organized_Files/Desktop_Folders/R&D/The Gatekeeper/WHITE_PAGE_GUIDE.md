# Gatekeeper - White Page Generator

## Overview

**White Page Generator** - Creates a blank document with standard formatting, ready for use.

## Voice Commands

### Generate White Page
```
"Hey, Gatekeeper, generate white page"
"Hey, Gatekeeper, white page"
```

**What it does:**
- Opens Word (or LibreOffice Writer if offline)
- Creates a new blank document titled "White Page - YYYY-MM-DD.docx"
- Format: A4, 1-inch margins, Arial 11pt, line spacing 1.15
- Header: "System initialized. Gatekeeper standing by."
- Footer: "Page 1 of 1"
- Auto-saves to `D:\RPF_BRAIN\Archived\docs\`
- Says: "White page ready. File saved."

### Send White Page (with Download Link)
```
"Hey, Gatekeeper, send white page"
```

**What it does:**
- Creates the white page document
- Opens the folder (`D:\RPF_BRAIN\Archived\docs\`)
- Copies download link to clipboard (file:// URL)
- Ready to paste anywhere (OneDrive, USB, email, etc.)
- Says: "White page ready. Link copied to clipboard. Folder opened."

## Document Format

### Specifications
- **Page Size:** A4 (8.27" x 11.69")
- **Margins:** 1 inch (all sides)
- **Font:** Arial 11pt
- **Line Spacing:** 1.15
- **Header:** "System initialized. Gatekeeper standing by."
- **Footer:** "Page 1 of 1"

### File Location
```
D:\RPF_BRAIN\Archived\docs\White Page - YYYY-MM-DD.docx
```

## Download Link Format

### Local File URL
```
file://D:/RPF_BRAIN/Archived/docs/White%20Page%20-%202026-01-01.docx
```

### Cloud Sync
If you sync `D:\RPF_BRAIN\Archived\docs\` to:
- **OneDrive:** Link becomes OneDrive share link
- **Google Drive:** Link becomes Google Drive share link
- **Dropbox:** Link becomes Dropbox share link

**One click. No extra work.**

## Usage Examples

### Example 1: Generate White Page
```
User: "Hey, Gatekeeper, generate white page"
Gatekeeper: "White page ready. File saved."
Result: Document opens in Word, saved to docs folder
```

### Example 2: Send White Page
```
User: "Hey, Gatekeeper, send white page"
Gatekeeper: "White page ready. Link copied to clipboard. Folder opened."
Result: 
  - Document created
  - Folder opened
  - Link copied: file://D:/RPF_BRAIN/Archived/docs/White%20Page%20-%202026-01-01.docx
  - Ready to paste anywhere
```

## Technical Details

### Word Document Creation
1. **Primary Method:** python-docx library
2. **Fallback Method:** COM automation (Windows Word)
3. **Offline Method:** LibreOffice Writer (ODT format)

### Clipboard Functionality
1. **Primary Method:** win32clipboard (Windows)
2. **Fallback Method:** pyperclip
3. **Final Fallback:** PowerShell Set-Clipboard

### File Naming
- Format: `White Page - YYYY-MM-DD.docx`
- Example: `White Page - 2026-01-01.docx`
- Date-based naming prevents overwrites

## Integration

### Voice Listener
- Commands: "white page", "generate white page", "send white page"
- Auto-detects command type
- Routes to appropriate handler

### File System
- Auto-creates `docs\` directory if missing
- Saves to `D:\RPF_BRAIN\Archived\docs\`
- Opens folder after creation (send mode)

## Status

✅ **ACTIVE** - White page generator ready.

**Just say: "Hey, Gatekeeper, generate white page" or "Hey, Gatekeeper, send white page"**

---

**White page = ready. Link = ready. Just say it.**

