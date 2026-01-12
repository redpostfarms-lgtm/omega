/**
 * NVIDIA Integration - Example Usage
 * ===================================
 * Based on the provided code example
 */

const axios = require('axios');

// Configuration
const invokeUrl = "https://integrate.api.nvidia.com/v1/chat/completions";
const stream = false;
const apiKey = process.env.NVIDIA_API_KEY || "YOUR_API_KEY";

// Headers
const headers = {
  "Authorization": `Bearer ${apiKey}`,
  "Accept": stream ? "text/event-stream" : "application/json",
  "Content-Type": "application/json"
};

// Payload
const payload = {
  "model": "meta/llama-4-maverick-17b-128e-instruct",
  "messages": [
    {
      "role": "user",
      "content": "Hello! Explain quantum computing in simple terms."
    }
  ],
  "max_tokens": 512,
  "temperature": 1.00,
  "top_p": 1.00,
  "frequency_penalty": 0.00,
  "presence_penalty": 0.00,
  "stream": stream
};

// Make request
axios.post(invokeUrl, payload, {
  headers: headers,
  responseType: stream ? 'stream' : 'json'
})
  .then(response => {
    if (stream) {
      response.data.on('data', (chunk) => {
        console.log(chunk.toString());
      });
      response.data.on('end', () => {
        console.log('Stream ended');
      });
    } else {
      console.log(JSON.stringify(response.data, null, 2));
      
      // Extract and display the response text
      if (response.data.choices && response.data.choices.length > 0) {
        console.log('\n--- Response Text ---');
        console.log(response.data.choices[0].message.content);
      }
    }
  })
  .catch(error => {
    if (error.response) {
      console.error('Error:', error.response.status, error.response.statusText);
      console.error('Details:', error.response.data);
    } else {
      console.error('Error:', error.message);
    }
  });
