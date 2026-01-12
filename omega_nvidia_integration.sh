#!/bin/bash
# Omega NVIDIA API Integration (Bash/Shell)
# ==========================================
# Integration with NVIDIA Developer Playground API

# Configuration
INVOKE_URL="https://integrate.api.nvidia.com/v1/chat/completions"
MODEL="meta/llama-4-maverick-17b-128e-instruct"
STREAM=false

# Check for API key
if [ -z "$NVIDIA_API_KEY" ]; then
    echo "Error: NVIDIA_API_KEY environment variable not set." >&2
    echo "Set it with: export NVIDIA_API_KEY=your_key" >&2
    exit 1
fi

# Set accept header based on stream setting
if [ "$STREAM" = true ]; then
    ACCEPT_HEADER="Accept: text/event-stream"
else
    ACCEPT_HEADER="Accept: application/json"
fi

# Function to generate chat completion
nvidia_chat_completion() {
    local messages="$1"
    local max_tokens="${2:-512}"
    local temperature="${3:-1.00}"
    local top_p="${4:-1.00}"
    local frequency_penalty="${5:-0.00}"
    local presence_penalty="${6:-0.00}"
    local stream="${7:-false}"
    
    # Create payload JSON
    local payload=$(cat <<EOF
{
  "model": "$MODEL",
  "messages": $messages,
  "max_tokens": $max_tokens,
  "temperature": $temperature,
  "top_p": $top_p,
  "frequency_penalty": $frequency_penalty,
  "presence_penalty": $presence_penalty,
  "stream": $stream
}
EOF
)
    
    # Set accept header
    if [ "$stream" = true ]; then
        local accept_header="Accept: text/event-stream"
    else
        local accept_header="Accept: application/json"
    fi
    
    # Make request
    curl -s "$INVOKE_URL" \
        -H "Authorization: Bearer $NVIDIA_API_KEY" \
        -H "Content-Type: application/json" \
        -H "$accept_header" \
        -d "$payload"
}

# Function to generate simple response
nvidia_generate_response() {
    local prompt="$1"
    shift
    
    # Create messages array
    local messages="[{\"role\":\"user\",\"content\":\"$prompt\"}]"
    
    # Get response
    local response=$(nvidia_chat_completion "$messages" "$@")
    
    # Extract text from response (requires jq)
    if command -v jq &> /dev/null; then
        echo "$response" | jq -r '.choices[0].message.content'
    else
        echo "$response"
    fi
}

# Function to continue conversation
nvidia_conversation() {
    local conversation_history="$1"
    shift
    
    # Get response
    local response=$(nvidia_chat_completion "$conversation_history" "$@")
    
    # Extract text from response (requires jq)
    if command -v jq &> /dev/null; then
        echo "$response" | jq -r '.choices[0].message.content'
    else
        echo "$response"
    fi
}

# Example usage
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    # Check if running as script (not sourced)
    
    if [ -z "$1" ]; then
        echo "Usage: $0 <prompt>"
        echo "Or source this file and use:"
        echo "  source $0"
        echo "  nvidia_generate_response \"Hello! How are you?\""
        exit 1
    fi
    
    prompt="$1"
    echo "Prompt: $prompt"
    echo ""
    echo "Response:"
    nvidia_generate_response "$prompt"
fi
