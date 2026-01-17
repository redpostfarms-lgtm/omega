# LLM Ingestion Instructions

## Quick Injection

### For Ollama:
```bash
ollama create gatekeeper -f SYSTEM_PROMPT.txt
```text

Or use the compact version:
```bash
ollama create gatekeeper -f LLM_INJECT.txt
```text

### For Direct Prompt Injection:
Copy the contents of `SYSTEM_PROMPT.txt` or `LLM_INJECT.txt` and paste as system prompt.

### For Mixtral/Llama3 via API:
```python
import requests

with open('SYSTEM_PROMPT.txt', 'r') as f:
    system_prompt = f.read()

response = requests.post('http://localhost:11434/api/generate', json={
    'model': 'llama3',
    'prompt': 'Hey, Gatekeeper, status',
    'system': system_prompt
})
```text

## Two Versions

1. **SYSTEM_PROMPT.txt** - Full, detailed version with complete context
2. **LLM_INJECT.txt** - Compact, optimized for token efficiency

## Usage

### One-Shot Injection:
Feed either file to your LLM as a system prompt. The Gatekeeper personality and knowledge will be loaded.

### Testing:
After injection, test with:
- "Hey, Gatekeeper, status"
- "Gatekeeper, what's the derivative of solar power?"
- "Gatekeeper, new REAP grant 15k"

Expected responses should match the examples in the prompt.

## Notes

- The prompt is self-contained - no external files needed
- All knowledge domains are included
- Templates are embedded
- Voice patterns are defined
- Security protocols are included

The Gatekeeper is ready for LLM ingestion.

