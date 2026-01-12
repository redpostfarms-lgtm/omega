#!/bin/bash
# NVIDIA Integration - Example Usage (Based on provided code)
# ============================================================

# Configuration
stream=false

# Check for API key
if [ -z "$NVIDIA_API_KEY" ]; then
    echo "Error: NVIDIA_API_KEY environment variable not set." >&2
    echo "Set it with: export NVIDIA_API_KEY=your_key" >&2
    exit 1
fi

# Set accept header based on stream setting
if [ "$stream" = true ]; then
    accept_header='Accept: text/event-stream'
else
    accept_header='Accept: application/json'
fi

# Create payload JSON
cat > payload.json <<EOF
{
  "model": "meta/llama-4-maverick-17b-128e-instruct",
  "messages": [{"role":"user","content":"Hello! Explain quantum computing in simple terms."}],
  "max_tokens": 512,
  "temperature": 1.00,
  "top_p": 1.00,
  "frequency_penalty": 0.00,
  "presence_penalty": 0.00,
  "stream": false
}
EOF

# Make request
echo "Making request to NVIDIA API..."
echo ""

response=$(curl -s https://integrate.api.nvidia.com/v1/chat/completions \
  -H "Authorization: Bearer $NVIDIA_API_KEY" \
  -H "Content-Type: application/json" \
  -H "$accept_header" \
  -d @payload.json)

# Display response
echo "Response:"
echo "$response" | jq '.'

# Extract and display response text (if jq is available)
if command -v jq &> /dev/null; then
    echo ""
    echo "--- Response Text ---"
    echo "$response" | jq -r '.choices[0].message.content'
else
    echo ""
    echo "Note: Install 'jq' for better JSON parsing: sudo apt-get install jq"
fi

# Cleanup
rm -f payload.json
