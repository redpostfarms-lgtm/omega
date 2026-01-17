# NVIDIA API Integration - Bash/Shell Version ✅

**Date:** January 10, 2026  
**Status:** ✅ **COMPLETE**

---

## ✅ What Was Added

### Bash/Shell Integration Scripts
- **File**: `omega_nvidia_integration.sh` - Full integration module
- **File**: `omega_nvidia_integration_example.sh` - Example usage based on your code
- **File**: `omega_nvidia_integration_wrapper.sh` - Simple function wrapper
- **Status**: ✅ Complete and ready to use

---

## Features

### Full Integration Script (`omega_nvidia_integration.sh`)
- ✅ Function-based integration
- ✅ Chat completion support
- ✅ Simple response generation
- ✅ Conversation support
- ✅ Streaming support
- ✅ Error handling
- ✅ Can be sourced or run directly

### Example Script (`omega_nvidia_integration_example.sh`)
- ✅ Based on your exact code structure
- ✅ Simple, direct implementation
- ✅ Easy to understand and modify

### Wrapper Script (`omega_nvidia_integration_wrapper.sh`)
- ✅ Simple function wrapper
- ✅ Easy to source and use
- ✅ Minimal dependencies

---

## Setup

### 1. Make Scripts Executable

```bash
chmod +x omega_nvidia_integration.sh
chmod +x omega_nvidia_integration_example.sh
chmod +x omega_nvidia_integration_wrapper.sh
```text

### 2. Set API Key

```bash
export NVIDIA_API_KEY=your_api_key_here
```text

### 3. Optional: Install jq for JSON Parsing

```bash
# Ubuntu/Debian
sudo apt-get install jq

# macOS
brew install jq

# CentOS/RHEL
sudo yum install jq
```text

---

## Usage

### Option 1: Using the Example Script (Based on Your Code)

```bash
# Set API key
export NVIDIA_API_KEY=your_api_key_here

# Run the example
./omega_nvidia_integration_example.sh
```text

### Option 2: Using the Full Integration Script

```bash
# Source the script to use functions
source omega_nvidia_integration.sh

# Or make executable and run directly
chmod +x omega_nvidia_integration.sh
./omega_nvidia_integration.sh "Hello! How are you?"
```text

### Option 3: Using Functions (After Sourcing)

```bash
# Source the script
source omega_nvidia_integration.sh

# Generate simple response
nvidia_generate_response "Hello! How are you?"

# With custom parameters
nvidia_generate_response "Explain quantum computing" 1024 0.7

# Conversation with history
messages='[{"role":"user","content":"Hello!"},{"role":"assistant","content":"Hi!"},{"role":"user","content":"What can you do?"}]'
nvidia_conversation "$messages"
```text

### Option 4: Using the Wrapper (Simplest)

```bash
# Source the wrapper
source omega_nvidia_integration_wrapper.sh

# Use the function
nvidia_generate_response "Hello! How are you?"
```text

### Option 5: Direct curl Usage (Your Original Code)

```bash
# Set variables
stream=false

if [ "$stream" = true ]; then
    accept_header='Accept: text/event-stream'
else
    accept_header='Accept: application/json'
fi

# Create payload
cat > payload.json <<EOF
{
  "model": "meta/llama-4-maverick-17b-128e-instruct",
  "messages": [{"role":"user","content":"Hello!"}],
  "max_tokens": 512,
  "temperature": 1.00,
  "top_p": 1.00,
  "frequency_penalty": 0.00,
  "presence_penalty": 0.00,
  "stream": false
}
EOF

# Make request
curl https://integrate.api.nvidia.com/v1/chat/completions \
  -H "Authorization: Bearer $NVIDIA_API_KEY" \
  -H "Content-Type: application/json" \
  -H "$accept_header" \
  -d @payload.json

# Cleanup
rm payload.json
```text

---

## Available Functions

### `nvidia_chat_completion(messages, max_tokens, temperature, top_p, frequency_penalty, presence_penalty, stream)`
Full chat completion with all parameters.

**Parameters:**
- `messages` - JSON array of message objects (as string)
- `max_tokens` - Maximum tokens (default: 512)
- `temperature` - Sampling temperature (default: 1.00)
- `top_p` - Nucleus sampling (default: 1.00)
- `frequency_penalty` - Frequency penalty (default: 0.00)
- `presence_penalty` - Presence penalty (default: 0.00)
- `stream` - Stream responses (default: false)

### `nvidia_generate_response(prompt, max_tokens, temperature, ...)`
Simple response generation from a prompt.

### `nvidia_conversation(conversation_history, ...)`
Continue a conversation with history.

---

## Examples

### Simple Response

```bash
source omega_nvidia_integration.sh
nvidia_generate_response "Hello! How are you?"
```text

### Custom Parameters

```bash
nvidia_generate_response "Explain quantum computing" 1024 0.7
```text

### Conversation

```bash
messages='[{"role":"user","content":"Hello!"},{"role":"assistant","content":"Hi!"},{"role":"user","content":"What is AI?"}]'
nvidia_conversation "$messages"
```text

### Full Chat Completion

```bash
messages='[{"role":"user","content":"Hello!"}]'
response=$(nvidia_chat_completion "$messages" 512 1.0 1.0 0.0 0.0 false)
echo "$response" | jq '.'
```text

---

## Streaming Support

For streaming responses, set `STREAM=true` in the script or use:

```bash
messages='[{"role":"user","content":"Tell me a story"}]'
nvidia_chat_completion "$messages" 512 1.0 1.0 0.0 0.0 true
```text

---

## Error Handling

The scripts include error handling:

```bash
if [ -z "$NVIDIA_API_KEY" ]; then
    echo "Error: NVIDIA_API_KEY not set" >&2
    exit 1
fi
```text

---

## Comparison: All Versions

### Python Version (`omega_nvidia_integration.py`)
- ✅ Full-featured integration
- ✅ Object-oriented design
- ✅ Recommended for Omega (Python-based)
- ✅ Best for complex applications

### Node.js Version (`omega_nvidia_integration.js`)
- ✅ Full-featured integration
- ✅ Object-oriented design
- ✅ Useful for Node.js projects
- ✅ Good for web applications

### Bash/Shell Version (`omega_nvidia_integration.sh`)
- ✅ Full-featured integration
- ✅ Function-based design
- ✅ Perfect for shell scripts and automation
- ✅ No additional dependencies (except curl)
- ✅ Great for system administration

All three versions provide the same functionality and can be used based on your project requirements.

---

## Windows Usage

On Windows, you can use these scripts with:

1. **Git Bash** - Full bash support
2. **WSL (Windows Subsystem for Linux)** - Native Linux support
3. **Cygwin** - Unix-like environment
4. **PowerShell** - Use Python or Node.js versions instead

---

## Status: ✅ READY

**Python, Node.js, and Bash integrations are complete and ready to use!**

1. Get your NVIDIA API key from: https://developer.nvidia.com/playground
2. Set the API key: `export NVIDIA_API_KEY=your_key`
3. Use the appropriate version for your needs:
   - **Python**: `omega_nvidia_integration.py` (for Omega)
   - **Node.js**: `omega_nvidia_integration.js` (for Node.js)
   - **Bash**: `omega_nvidia_integration.sh` (for shell scripts)

---
