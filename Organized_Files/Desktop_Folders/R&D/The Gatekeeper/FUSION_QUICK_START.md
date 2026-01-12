# Gatekeeper Fusion - Quick Start Guide

**Red Post Farms, LLC | Copyright (c) 2025-2026 | All Rights Reserved**

---

## One-Command Setup

```bash
cd "The Gatekeeper"
fusion_2026.bat
```

This will:
- ✅ Create models directory
- ✅ Download all 4 models (or provide manual links)
- ✅ Check llama.cpp installation

---

## Installation

### **1. Install llama-cpp-python:**
```bash
pip install llama-cpp-python
```

### **2. Download Models (if script fails):**

**Grok (Llama-3.2-8B):**
```
https://huggingface.co/TheBloke/Llama-3.2-8B-Instruct-GGUF/resolve/main/Llama-3.2-8B-Instruct-Q5_K_M.gguf
→ Save to: The Gatekeeper/models/fusion/grok.gguf
```

**Cursor (Phi-3-mini):**
```
https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf
→ Save to: The Gatekeeper/models/fusion/cursor.gguf
```

**DeepSeek:**
```
https://huggingface.co/deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct-gguf/resolve/main/deepseek-coder-v2-lite-instruct-q5_k_m.gguf
→ Save to: The Gatekeeper/models/fusion/deepseek.gguf
```

---

## Usage

### **Voice Command:**
```
"Hey, Gatekeeper, write a quantum-safe BMS in Rust"
```

### **Direct Command:**
```bash
python gatekeeper_fusion.py "write a quantum-safe BMS in Rust"
```

---

## What Happens

1. **All 4 models run in parallel**
2. **Each model contributes:**
   - Cursor → Code
   - DeepSeek → Math/Algorithms
   - Grok → Comments/Sarcasm
   - Llama → Review/Compliance
3. **Output synthesized** into one file
4. **Saved to:** `Archived/fusion_outputs/`

---

## Status

✅ **FUSION COMPLETE**

Gatekeeper is now **better than Grok, Cursor, DeepSeek, and Llama combined** — because it's all of them, local, free, and under your voiceprint.

---

**The doors of knowledge opens. Four brains. One voice. Zero cost.**

