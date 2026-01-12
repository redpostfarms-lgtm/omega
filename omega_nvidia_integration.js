/**
 * Omega NVIDIA API Integration (Node.js/JavaScript)
 * ==================================================
 * Integration with NVIDIA Developer Playground API
 */

const axios = require('axios');
const { readFile } = require('node:fs/promises');

class NVIDIAIntegration {
  constructor(apiKey = null) {
    this.apiKey = apiKey || process.env.NVIDIA_API_KEY;
    this.baseUrl = "https://integrate.api.nvidia.com/v1";
    this.invokeUrl = `${this.baseUrl}/chat/completions`;
  }

  /**
   * Generate chat completion using NVIDIA API
   * @param {Object} options - Configuration options
   * @param {Array} options.messages - Array of message objects with role and content
   * @param {string} options.model - Model name (default: llama-4-maverick-17b-128e-instruct)
   * @param {number} options.maxTokens - Maximum tokens to generate (default: 512)
   * @param {number} options.temperature - Sampling temperature (default: 1.0)
   * @param {number} options.topP - Nucleus sampling parameter (default: 1.0)
   * @param {number} options.frequencyPenalty - Frequency penalty (default: 0.0)
   * @param {number} options.presencePenalty - Presence penalty (default: 0.0)
   * @param {boolean} options.stream - Whether to stream responses (default: false)
   * @returns {Promise} Response data or stream
   */
  async chatCompletion({
    messages,
    model = "meta/llama-4-maverick-17b-128e-instruct",
    maxTokens = 512,
    temperature = 1.0,
    topP = 1.0,
    frequencyPenalty = 0.0,
    presencePenalty = 0.0,
    stream = false
  }) {
    if (!this.apiKey) {
      throw new Error("NVIDIA API key not set. Set NVIDIA_API_KEY environment variable or pass apiKey parameter.");
    }

    const headers = {
      "Authorization": `Bearer ${this.apiKey}`,
      "Accept": stream ? "text/event-stream" : "application/json",
      "Content-Type": "application/json"
    };

    const payload = {
      model: model,
      messages: messages,
      max_tokens: maxTokens,
      temperature: temperature,
      top_p: topP,
      frequency_penalty: frequencyPenalty,
      presence_penalty: presencePenalty,
      stream: stream
    };

    try {
      const response = await axios.post(this.invokeUrl, payload, {
        headers: headers,
        responseType: stream ? 'stream' : 'json',
        timeout: 60000
      });

      if (stream) {
        return this._handleStreamResponse(response);
      } else {
        return response.data;
      }
    } catch (error) {
      if (error.response) {
        throw new Error(`NVIDIA API request failed: ${error.response.status} - ${error.response.statusText}`);
      } else {
        throw new Error(`NVIDIA API request failed: ${error.message}`);
      }
    }
  }

  /**
   * Handle streaming responses
   * @private
   */
  _handleStreamResponse(response) {
    return new Promise((resolve, reject) => {
      const chunks = [];
      response.data.on('data', (chunk) => {
        const lines = chunk.toString().split('\n');
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6); // Remove "data: " prefix
            if (data === '[DONE]') {
              resolve(chunks);
              return;
            }
            try {
              chunks.push(JSON.parse(data));
            } catch (e) {
              // Skip invalid JSON
            }
          }
        }
      });
      response.data.on('error', reject);
      response.data.on('end', () => resolve(chunks));
    });
  }

  /**
   * Generate a simple text response from a prompt
   * @param {string} prompt - Input prompt
   * @param {Object} options - Additional options for chatCompletion
   * @returns {Promise<string>} Generated text response
   */
  async generateResponse(prompt, options = {}) {
    const messages = [{ role: "user", content: prompt }];
    
    const result = await this.chatCompletion({
      messages: messages,
      stream: false,
      ...options
    });

    if (result.choices && result.choices.length > 0) {
      return result.choices[0].message.content;
    } else {
      throw new Error(`Unexpected response format: ${JSON.stringify(result)}`);
    }
  }

  /**
   * Continue a conversation with history
   * @param {Array} conversationHistory - Array of message objects
   * @param {Object} options - Additional options for chatCompletion
   * @returns {Promise<string>} Generated response
   */
  async conversation(conversationHistory, options = {}) {
    const result = await this.chatCompletion({
      messages: conversationHistory,
      stream: false,
      ...options
    });

    if (result.choices && result.choices.length > 0) {
      return result.choices[0].message.content;
    } else {
      throw new Error(`Unexpected response format: ${JSON.stringify(result)}`);
    }
  }
}

// Singleton instance
let nvidiaIntegrationInstance = null;

/**
 * Get singleton NVIDIA integration instance
 * @param {string} apiKey - Optional API key
 * @returns {NVIDIAIntegration} Integration instance
 */
function getNVIDIAIntegration(apiKey = null) {
  if (!nvidiaIntegrationInstance) {
    nvidiaIntegrationInstance = new NVIDIAIntegration(apiKey);
  } else if (apiKey) {
    nvidiaIntegrationInstance.apiKey = apiKey;
  }
  return nvidiaIntegrationInstance;
}

/**
 * Set NVIDIA API key globally
 * @param {string} apiKey - API key
 */
function setNVIDIAAPIKey(apiKey) {
  if (!nvidiaIntegrationInstance) {
    nvidiaIntegrationInstance = new NVIDIAIntegration(apiKey);
  } else {
    nvidiaIntegrationInstance.apiKey = apiKey;
  }
  process.env.NVIDIA_API_KEY = apiKey;
}

// Export
module.exports = {
  NVIDIAIntegration,
  getNVIDIAIntegration,
  setNVIDIAAPIKey
};

// Example usage (if run directly)
if (require.main === module) {
  const apiKey = process.env.NVIDIA_API_KEY;

  if (!apiKey) {
    console.log("NVIDIA_API_KEY environment variable not set.");
    console.log("Set it with: export NVIDIA_API_KEY=your_key");
    console.log("Or: $env:NVIDIA_API_KEY='your_key' (Windows PowerShell)");
  } else {
    const nvidia = getNVIDIAIntegration();

    // Simple prompt
    const prompt = "Hello! How are you?";
    console.log(`Prompt: ${prompt}`);

    nvidia.generateResponse(prompt)
      .then(response => {
        console.log(`Response: ${response}`);
      })
      .catch(error => {
        console.error(`Error: ${error.message}`);
      });
  }
}
