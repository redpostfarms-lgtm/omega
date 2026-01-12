# Simple Problem Analysis - KISS Principle

## The Problem
Window closes immediately after opening when clicking Omega shortcut.

## Code Flow (Current)
1. `OMEGA_UI_LAUNCHER.py` → sets backend → creates ControlPanel → calls `panel.run()`
2. `panel.run()` → calls `_create_gui_panel()` → creates FuncAnimation → calls `plt.ion()` → returns
3. `panel.run()` → calls `plt.show(block=True)` → should block until window closed

## Simplest Possible Issues (in order of likelihood)

### Issue #1: plt.ion() conflicts with plt.show(block=True)
**Problem:** `plt.ion()` is called in `_create_gui_panel()` (line 558), then `plt.show(block=True)` is called in `run()` (line 967)
**Fact:** When `plt.ion()` is enabled, `plt.show(block=True)` might not block properly
**Fix:** Remove `plt.ion()` OR use `plt.ioff()` before `plt.show(block=True)`

### Issue #2: FuncAnimation doesn't need plt.ion()
**Problem:** FuncAnimation handles its own event loop, doesn't need interactive mode
**Fact:** FuncAnimation works with `plt.show(block=True)` without `plt.ion()`
**Fix:** Remove `plt.ion()` call

### Issue #3: Exception silently caught
**Problem:** If `_create_gui_panel()` raises exception, it falls back to text mode (line 976-980)
**Fact:** Window won't appear if exception occurs
**Fix:** Add debug output to see if exception occurs

### Issue #4: plt.show(block=True) doesn't block with FuncAnimation
**Problem:** FuncAnimation might interfere with blocking show
**Fact:** FuncAnimation should work with block=True, but might need plt.ioff()
**Fix:** Try plt.ioff() before plt.show(block=True)

## Simplest Fix (KISS)
**Remove plt.ion() call** - FuncAnimation doesn't need it, and it might be causing plt.show(block=True) to not block properly.

Let's try this simplest fix first!
