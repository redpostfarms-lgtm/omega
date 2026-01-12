# Simple Fix Analysis - KISS Principle

## Problem: Window closes immediately after opening

## Step-by-Step Investigation

### Issue #1: plt import in run() method
**Question:** Is `plt` available in the `run()` method?
**Check:** Line 967 calls `plt.show(block=True)` but is `plt` imported at module level?
**Status:** NEEDS CHECK

### Issue #2: plt.ion() placement
**Question:** Is `plt.ion()` called before `plt.show()`?
**Current:** `plt.ion()` is called in `_create_gui_panel()` (line 558)
**Then:** `plt.show(block=True)` is called in `run()` (line 967)
**Status:** MIGHT BE OK - but let's verify

### Issue #3: Exception handling
**Question:** Are exceptions being silently caught?
**Check:** Lines 976-980 catch Exception and fall back to text mode
**Status:** COULD BE HIDING ERRORS

### Issue #4: plt.show(block=True) with FuncAnimation
**Question:** Does FuncAnimation work with plt.show(block=True)?
**Research:** FuncAnimation should work with block=True, but there might be issues
**Status:** NEEDS VERIFICATION

### Issue #5: No figure to show
**Question:** Is the figure created before plt.show() is called?
**Check:** `_create_gui_panel()` creates `self.fig` (line 510)
**Then:** `run()` calls `plt.show(block=True)` (line 967)
**Status:** SHOULD BE OK

## Simplest Possible Fixes (in order of simplicity)

1. **Add explicit plt import in run() method** - Simple, might fix it
2. **Move plt.ion() to just before plt.show()** - Simple, might help
3. **Add debug print statements** - Simple, helps identify problem
4. **Try plt.ioff() instead of plt.ion()** - Simple, might be the issue
5. **Remove plt.ion() entirely** - Simple, FuncAnimation might not need it

Let's test these one by one.
