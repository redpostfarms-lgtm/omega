/**
 * Omega API Keys Manager - Node.js Bridge
 * ========================================
 * Bridge to access Python-stored API keys from Node.js
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

/**
 * Get OpenAI API key from Python storage or environment variable
 * @returns {string|null} API key or null if not found
 */
function getOpenAIAPIKey() {
    // Try environment variable first
    if (process.env.OPENAI_API_KEY) {
        return process.env.OPENAI_API_KEY;
    }
    
    // Try to get from Python secure storage
    try {
        // Run Python script to get the key
        const pythonScript = `
import sys
from omega_api_keys_enhanced import get_openai_key
try:
    key = get_openai_key()
    if key:
        print(key)
    else:
        sys.exit(1)
except:
    sys.exit(1)
`;
        
        const key = execSync(`python -c "${pythonScript}"`, {
            encoding: 'utf-8',
            stdio: ['pipe', 'pipe', 'ignore']
        }).trim();
        
        if (key) {
            return key;
        }
    } catch (error) {
        // Python script failed or key not found
        // Fall back to environment variable
    }
    
    return null;
}

/**
 * Set OpenAI API key in environment variable
 * @param {string} apiKey - API key
 */
function setOpenAIAPIKey(apiKey) {
    process.env.OPENAI_API_KEY = apiKey;
}

module.exports = {
    getOpenAIAPIKey,
    setOpenAIAPIKey
};
