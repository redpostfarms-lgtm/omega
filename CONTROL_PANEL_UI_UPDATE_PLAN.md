# Control Panel UI Update Plan

**Date:** January 10, 2026  
**Status:** 📋 **PLANNING**

---

## User Requirements

1. ✅ **Remove "Gatekeeper" Name** - Already done (not in code)
2. 📝 **Add Minimal File List** - Show only critical files
3. 🎤 **Add OIP with Visual Effects** - Speech-synchronized animations
4. 🔧 **Adjust Layout** - Space for additional windows

---

## Implementation Notes

The control panel is a matplotlib-based GUI. The user wants:
- A file list section (left column) showing only critical files
- An OIP (Omega Introduction Panel) section with speech-synchronized visual effects
- Layout adjustments to accommodate these changes

This is a significant UI redesign that requires:
1. Adding new sections to the matplotlib GridSpec
2. Implementing audio monitoring for visual effects
3. Creating speech-synchronized animations
4. Managing file list display

**Status:** Ready to implement when user confirms approach.
