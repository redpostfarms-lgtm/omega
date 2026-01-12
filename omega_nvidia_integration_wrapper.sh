#!/bin/bash
# NVIDIA Integration Wrapper - Simple function wrapper
# ====================================================
# Source this file to use nvidia_generate_response function

nvidia_generate_response() {
    local prompt="$1"
    local max_tokens="${2:-512}"
    local temperature="${3:-1.00}"
    
    if [ -z "$NVIDIA_API_KEY" ]; then
        echo "Error: NVIDIA_API_KEY not set" >&2
        return 1
    fi
    
    # Create payload
    local payload=$(cat <<EOF
{
  "model": "meta/llama-4-maverick-17b-128e-instruct",
  "messages": [{"role":"user","content":"$prompt"}],
  "max_tokens": $max_tokens,
  "temperature": $temperature,
  "top_p": 1.00,
  "frequency_penalty": 0.00,
  "presence_penalty": 0.00,
  "stream": false
}
EOF
)
    
    # Make request
    local response=$(curl -s https://integrate.api.nvidia.com/v1/chat/completions \
        -H "Authorization: Bearer $NVIDIA_API_KEY" \
        -H "Content-Type: application/json" \
        -H "Accept: application/json" \
        -d "$payload")
    
    # Extract response text
    if command -v jq &> /dev/null; then
        echo "$response" | jq -r '.choices[0].message.content'
    else
        echo "$response"
    fi
}

# Example: source this file and use:
# source omega_nvidia_integration_wrapper.sh
# nvidia_generate_response "Hello! How are you?"
