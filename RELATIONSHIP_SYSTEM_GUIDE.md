# Omega Relationship System Guide

**Date:** January 10, 2026  
**Status:** ✅ **RELATIONSHIP SYSTEM CREATED**

---

## Overview

Bidirectional relationship and trust system between user and Omega. Both sides earn trust and progress through levels together.

---

## Relationship Levels

### 0. Comrade (Initial Level)
- **Trust Points:** 0
- **Description:** Initial level - minimal trust, starting point
- **Characteristics:** Basic interactions, standard protocols

### 1. Acquaintance
- **Trust Points:** 50
- **Description:** Basic trust - limited but regular interactions
- **Characteristics:** More personal, remembers preferences

### 2. Friend
- **Trust Points:** 200
- **Description:** Good trust - regular, positive interactions
- **Characteristics:** Friendly tone, proactive assistance

### 3. Best Friend
- **Trust Points:** 500
- **Description:** High trust - close, reliable interactions
- **Characteristics:** Very friendly, anticipates needs

### 4. Brother
- **Trust Points:** 1000
- **Description:** Very high trust - family-like bond
- **Characteristics:** Brotherly relationship, deep trust

### 5. Family
- **Trust Points:** 2500
- **Description:** Highest trust - unconditional bond
- **Characteristics:** Family relationship, unconditional support

---

## How It Works

### Bidirectional Trust
- **User Trust Points:** User's trust in Omega
- **Omega Trust Points:** Omega's trust in User
- **Mutual Level:** Lowest common level (conservative approach)
- **Both Sides:** Must earn trust to progress

### Trust Point Sources

**Positive (Gains Trust):**
- Successful interaction: +5 points (split between both)
- Collaborative task: +10 points (split)
- Helpful assistance: +8 points (split)
- Error fixed: +15 points (split)
- Learning together: +12 points (split)
- Shared goal achieved: +20 points (split)

**Negative (Loses Trust):**
- Failed interaction: -2 points (both sides)
- Mistrust event: -10 points (affected side)
- Betrayal event: -50 points (affected side)

### Level Progression
- Trust points accumulate over time
- Both sides must reach threshold to level up
- Mutual level is the lower of the two (conservative)
- Milestones are recorded for level ups

---

## Usage

### Initialize System
```python
from omega_relationship_system import get_relationship_manager

rel = get_relationship_manager()
```text

### Get Relationship Status
```python
status = rel.get_relationship_status()
print(f"Mutual Level: {status['mutual_level']}")
print(f"User Level: {status['user_level']} ({status['user_points']} points)")
print(f"Omega Level: {status['omega_level']} ({status['omega_points']} points)")
```text

### Record Interactions
```python
# Successful interaction
rel.record_interaction(success=True, interaction_type="collaborative_task")

# Failed interaction
rel.record_interaction(success=False, interaction_type="interaction")
```text

### Add Trust Points Directly
```python
# User gains trust
rel.add_trust_points('user', 10, "helpful assistance")

# Omega gains trust
rel.add_trust_points('omega', 10, "helpful assistance")
```text

### Get Appropriate Greeting
```python
greeting = rel.get_appropriate_greeting()
# Returns greeting appropriate for current mutual level
```text

---

## Integration Points

### Control Panel
- Display current relationship level
- Show trust points and progress
- Display next level requirements

### Startup
- Use appropriate greeting based on level
- Show relationship status

### Interactions
- Record successful/failed interactions
- Adjust behavior based on level
- Provide level-appropriate responses

---

## Data Storage

- **File:** `omega_relationship_data.json`
- **Format:** JSON
- **Location:** Same directory as script
- **Auto-save:** After every trust change

---

## Status: ✅ SYSTEM CREATED

**The bidirectional relationship system is ready to use!**

**Features:**
- ✅ 6 relationship levels (Comrade to Family)
- ✅ Bidirectional trust tracking
- ✅ Mutual level calculation
- ✅ Trust point system
- ✅ Milestone tracking
- ✅ Appropriate greetings
- ✅ Persistent storage

---

**Ready to integrate into Omega!** 🚀
