# Omega Control Panel - UI Requirements Specification

**Date:** January 2026  
**Status:** 📋 Requirements Documentation  
**Version:** 1.0

---

## Overview

This document specifies the requirements and design for the Omega Control Panel User Interface, including both the native GUI and web interface options.

**Related Documents:**
- `UI_SCREENSHOTS_REFERENCE.md` - Screenshots and design images reference
- `UI_IMAGES_SPECIFICATION.md` - Detailed image specifications
- `WEB_INTERFACE_ANALYSIS.md` - Web interface analysis

**Screenshots Location:**
- All UI screenshots are in: `images/` directory
- Main design screenshot: `images/CONTROL PANEL FOR omega.png`
- Logo files: `images/omega_logo_red_gold_wreath.png` and `.ico`
- To copy for sharing: Run `COPY_UI_SCREENSHOTS.py`

---

## Core Requirements

### 1. Window Behavior (CRITICAL)

**Requirement:** The UI window must stay open and remain interactive.

**Current Issue:** Window was closing immediately after opening.

**Solution Implemented:**
- ✅ Removed `plt.ion()` (interactive mode) that interfered with blocking
- ✅ Added `plt.ioff()` before `plt.show(block=True)` to ensure proper blocking
- ✅ Window now stays open until user closes it

**Specification:**
- Window must remain visible and accessible
- Window must stay responsive and interactive
- Window should only close when user explicitly closes it
- Process must remain alive while window is open
- No automatic closing or disappearing

---

## Native GUI (Matplotlib) - Current Implementation

### Layout Structure

The control panel uses a **3x4 grid layout** with the following sections:

#### Left Column (Spans All Rows)
- **File List Section** (Gray background: #F5F5F5)
  - Shows 8 important files
  - Status indicators (✓/✗)
  - Color-coded (green/red)
  - Truncated long names

#### Top Row
- **OIP Section** (Omega Introduction Panel - White/Gray: #F8F8F8)
  - KITT scanner effect (synchronized with speech)
  - Falls back to waveform visualization
  - Audio monitoring (`response.wav`, `omega_intro.wav`)
  
- **Red Section** (Main Status - #FFCCCC)
  - System status (RUNNING/STOPPED)
  - Last update timestamp
  - Update interval
  - Hardware/Integration availability

- **Yellow Section** (Notifications & Controls - #FFFFCC)
  - Notifications display
  - Temperature pie chart
  - Fan speed control
  - RGB control
  - **Push to Talk button**

#### Middle Row
- **Green Section** (Integrated Systems - Spans 3 columns, #CCFFCC)
  - System list (NVIDIA, Hugging Face, OpenAI, etc.)
  - CPU usage bar chart
  - Temperature annotations
  - Processing power display

#### Bottom Row
- **Blue Section** (Process Improvements - #CCCCFF)
  - CPU/Memory/Disk usage warnings
  - Priority levels (High/Medium/Low)
  - Target percentages
  - **Enter button**

- **Orange Section** (Optional Processes - Spans 2 columns, #FFE5CC)
  - Optional learning/processes list
  - Usefulness scores
  - Categories
  - **Mute/Unmute button**
  - **Volume Control**

### Visual Features

1. **KITT Scanner Effect**
   - Location: OIP Section
   - Style: Knight Rider KITT-style horizontal scanning bars
   - Animation: Smooth wave motion (left-to-right)
   - Synchronized with audio/speech

2. **Color Coding**
   - Status indicators: Green (✓) / Red (✗)
   - Priority levels: High/Medium/Low with appropriate colors
   - Notifications: Info/Warning/Error/Success color coding

3. **Real-time Updates**
   - FuncAnimation handles automatic updates
   - Update interval: 2 seconds
   - Smooth transitions
   - No flickering

4. **Window Specifications**
   - Size: 16x10 inches
   - Title: "OMEGA CONTROL PANEL"
   - Backend: TkAgg (with Qt5Agg/Qt4Agg fallback)
   - Display: Uses `plt.show(block=True)` to stay open

### Interactive Controls

1. **Push to Talk Button** (Yellow Section)
   - Activates voice input
   - Toggle functionality

2. **Enter Button** (Blue Section)
   - Processes improvements
   - Action trigger

3. **Mute/Unmute Button** (Orange Section)
   - Audio control
   - Toggle functionality

4. **Volume Control** (Orange Section)
   - Slider or input
   - Range: 0.0 to 1.0

5. **Fan Speed Control** (Hardware)
   - Slider control
   - Range: 0-100%
   - Real-time adjustment

6. **RGB Control** (Hardware)
   - Color picker
   - Enable/Disable toggle
   - Real-time adjustment

---

## Web Interface (Flask) - Alternative Option

### Access Requirements

**Requirement:** UI should be accessible from any device/browser.

**Implementation:**
- ✅ Flask-based web interface
- ✅ REST API endpoints
- ✅ Responsive web design
- ✅ Mobile-friendly layout

### Web Interface Features

1. **Dashboard Layout**
   - System stats cards (CPU, Memory, Disk, Temperature)
   - Notifications section
   - Integrated systems list
   - Hardware controls section

2. **Real-time Updates**
   - Auto-refresh every 2 seconds
   - Smooth updates without page reload
   - WebSocket support (optional)

3. **Hardware Controls** (Web)
   - Fan speed slider
   - RGB color picker
   - RGB enable/disable toggle
   - Real-time updates

4. **API Endpoints**
   - `/api/status` - Overall status
   - `/api/system` - System information
   - `/api/notifications` - Notifications
   - `/api/integrated-systems` - Systems list
   - `/api/fan-speed` - Set fan speed (POST)
   - `/api/rgb` - Control RGB (POST)

### Web UI Design

- **Color Scheme:** Modern gradient background (purple/blue)
- **Cards:** White cards with shadows
- **Typography:** System fonts (San Francisco, Segoe UI, Roboto)
- **Responsive:** Works on desktop, tablet, mobile
- **Real-time:** Auto-refresh, smooth updates

---

## Launch Requirements

### Native GUI Launch

**Method 1: Desktop Shortcut**
- File: `OMEGA_UI_LAUNCHER.py`
- Shortcut: `Omega.lnk` on Desktop
- Behavior: Opens native GUI window
- Must stay open until closed

**Method 2: Command Line**
```bash
python OMEGA_UI_LAUNCHER.py
```

**Requirements:**
- ✅ Window appears immediately
- ✅ Window stays visible
- ✅ Window remains interactive
- ✅ Process stays alive
- ✅ No automatic closing

### Web Interface Launch

**Method 1: Web Launcher**
```bash
python OMEGA_WEB_LAUNCHER.py
```

**Method 2: Direct**
```bash
python omega_control_panel_web.py
python omega_control_panel_web.py --port 8080
python omega_control_panel_web.py --host 0.0.0.0  # Remote access
```

**Access:**
- Local: http://localhost:5000
- Remote: http://YOUR_IP:5000

---

## Functional Requirements

### Data Display

1. **System Status**
   - CPU usage (percentage)
   - CPU temperature (°C)
   - Memory usage (percentage)
   - Disk usage (percentage)
   - System status (RUNNING/STOPPED)

2. **Notifications**
   - Recent notifications (last 20)
   - Color-coded by level (info/warning/error/success)
   - Timestamp display
   - Auto-scroll for new items

3. **Integrated Systems**
   - System name
   - Status (active/inactive/error)
   - CPU usage
   - Temperature
   - Processing power
   - Last update timestamp

4. **Process Improvements**
   - Process name
   - Current percentage
   - Target percentage
   - Priority (high/medium/low)
   - Description

5. **Optional Processes**
   - Process name
   - Description
   - Usefulness score (0-100)
   - Category
   - Last scanned timestamp

### Control Functions

1. **Fan Speed Control**
   - Set fan speed (0-100%)
   - Real-time adjustment
   - Visual feedback

2. **RGB Lighting Control**
   - Set RGB color (hex color picker)
   - Enable/Disable toggle
   - Real-time adjustment
   - Visual feedback

3. **Voice Controls**
   - Push to Talk button
   - Mute/Unmute toggle
   - Volume control (0.0-1.0)

4. **Process Controls**
   - Enter button (process improvements)
   - Action triggers

---

## Technical Requirements

### Native GUI (Matplotlib)

1. **Backend Requirements**
   - Matplotlib with TkAgg backend (primary)
   - Qt5Agg/Qt4Agg fallback support
   - FuncAnimation for updates
   - Blocking display (`plt.show(block=True)`)

2. **Performance Requirements**
   - Update interval: 2 seconds
   - Smooth animations
   - No lag or stuttering
   - Responsive controls

3. **Platform Support**
   - Windows (primary)
   - Linux (supported)
   - macOS (supported)

### Web Interface (Flask)

1. **Server Requirements**
   - Flask web framework
   - CORS support (flask-cors)
   - Optional: WebSocket support (flask-socketio)

2. **API Requirements**
   - RESTful API design
   - JSON responses
   - POST endpoints for controls
   - Error handling

3. **Browser Support**
   - Modern browsers (Chrome, Firefox, Safari, Edge)
   - Mobile browsers
   - Responsive design

---

## Integration Requirements

### Shared Backend

**Requirement:** Both interfaces use the same data source.

**Implementation:**
- Both use `ControlPanel` class
- Shared data structures
- Consistent data between interfaces
- No conflicts

### Concurrent Operation

**Requirement:** Both interfaces can run simultaneously.

**Implementation:**
- Separate processes/instances
- Shared data source
- No conflicts
- Independent operation

---

## User Experience Requirements

### Native GUI

1. **Visibility**
   - Window must be visible immediately
   - No hidden windows
   - Always accessible
   - Can minimize/maximize normally

2. **Interactivity**
   - All controls must be responsive
   - No lag or delay
   - Smooth animations
   - Clear visual feedback

3. **Reliability**
   - No crashes
   - Error handling
   - Graceful degradation
   - Stable operation

### Web Interface

1. **Accessibility**
   - Access from any device
   - Remote access capability
   - Mobile-friendly
   - Responsive design

2. **Usability**
   - Intuitive interface
   - Clear controls
   - Visual feedback
   - Easy navigation

3. **Performance**
   - Fast loading
   - Smooth updates
   - No lag
   - Efficient updates

---

## Future Enhancements (Optional)

1. **Authentication**
   - Optional login/password
   - User sessions
   - Access control

2. **HTTPS Support**
   - Secure connections
   - SSL/TLS certificates
   - Encrypted data

3. **WebSocket Real-time Updates**
   - Push updates instead of polling
   - Lower latency
   - Better performance

4. **Customization**
   - Theme selection
   - Layout customization
   - Personal preferences

5. **Mobile App**
   - Native mobile app
   - Push notifications
   - Enhanced mobile experience

---

## Testing Requirements

### Native GUI Testing

1. ✅ Window opens successfully
2. ✅ Window stays open
3. ✅ All sections visible
4. ✅ Controls functional
5. ✅ Updates working
6. ✅ No crashes

### Web Interface Testing

1. ✅ Server starts successfully
2. ✅ Dashboard loads
3. ✅ API endpoints working
4. ✅ Controls functional
5. ✅ Real-time updates working
6. ✅ Mobile responsive

---

## Documentation

- ✅ Code documentation
- ✅ API documentation
- ✅ User guide (this document)
- ✅ Setup instructions
- ✅ Troubleshooting guide

---

## Summary

The Omega Control Panel UI requirements emphasize:
1. **Reliability** - Window must stay open and be accessible
2. **Functionality** - All features must work correctly
3. **Usability** - Intuitive and responsive interface
4. **Flexibility** - Both native and web options
5. **Integration** - Shared backend, consistent data

**Current Status:** ✅ Requirements documented and implemented

---

## Notes

- This document will be updated as requirements evolve
- User feedback will be incorporated
- New features will be added to this specification
- Testing results will be documented here

**Last Updated:** January 2026  
**Document Version:** 1.0
