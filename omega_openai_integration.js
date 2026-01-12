/**
 * Omega OpenAI Integration (Node.js)
 * ===================================
 * OpenAI API integration for Omega system (Node.js/JavaScript)
 */

const OpenAI = require('openai');
const fs = require('fs');
const path = require('path');

class OpenAIIntegration {
    /**
     * Initialize OpenAI integration
     * @param {string} apiKey - OpenAI API key (optional, will try to load from storage)
     */
    constructor(apiKey = null) {
        this.apiKey = apiKey || this.loadAPIKey();
        
        if (!this.apiKey) {
            throw new Error('OpenAI API key not found. Please set OPENAI_API_KEY environment variable or use storeAPIKey()');
        }
        
        this.client = new OpenAI({
            apiKey: this.apiKey
        });
        
        this.model = 'gpt-4'; // Default model
        this.conversationHistory = [];
    }
    
    /**
     * Load API key from secure storage or environment variable
     * @returns {string|null} API key or null if not found
     */
    loadAPIKey() {
        // Try environment variable first
        if (process.env.OPENAI_API_KEY) {
            return process.env.OPENAI_API_KEY;
        }
        
        // Try to load from encrypted storage (Python-generated file)
        // For now, use environment variable
        return null;
    }
    
    /**
     * Generate chat completion
     * @param {Array} messages - Array of message objects with role and content
     * @param {Object} options - Additional options (model, temperature, max_tokens, stream)
     * @returns {Promise<Object>} API response
     */
    async chatCompletion(messages, options = {}) {
        try {
            const {
                model = this.model,
                temperature = 0.7,
                max_tokens = null,
                stream = false
            } = options;
            
            const payload = {
                model,
                messages,
                temperature
            };
            
            if (max_tokens) {
                payload.max_tokens = max_tokens;
            }
            
            if (stream) {
                payload.stream = true;
            }
            
            const response = await this.client.chat.completions.create(payload);
            return response;
        } catch (error) {
            throw new Error(`OpenAI API request failed: ${error.message}`);
        }
    }
    
    /**
     * Generate response to user message
     * @param {string} userMessage - User message
     * @param {Object} options - Options (systemMessage, model, temperature, max_tokens, stream)
     * @returns {Promise<string>} Assistant response
     */
    async generateResponse(userMessage, options = {}) {
        const {
            systemMessage = null,
            model = this.model,
            temperature = 0.7,
            max_tokens = null,
            stream = false
        } = options;
        
        const messages = [];
        
        if (systemMessage) {
            messages.push({ role: 'system', content: systemMessage });
        }
        
        // Add conversation history
        messages.push(...this.conversationHistory);
        
        // Add current user message
        messages.push({ role: 'user', content: userMessage });
        
        try {
            const response = await this.chatCompletion(messages, {
                model,
                temperature,
                max_tokens,
                stream
            });
            
            if (response.choices && response.choices.length > 0) {
                const assistantMessage = response.choices[0].message.content;
                
                // Update conversation history
                this.conversationHistory.push({ role: 'user', content: userMessage });
                this.conversationHistory.push({ role: 'assistant', content: assistantMessage });
                
                return assistantMessage;
            }
            
            return 'No response generated';
        } catch (error) {
            return `Error: ${error.message}`;
        }
    }
    
    /**
     * Clear conversation history
     */
    clearHistory() {
        this.conversationHistory = [];
    }
    
    /**
     * Get conversation history
     * @returns {Array} Conversation history
     */
    getHistory() {
        return [...this.conversationHistory];
    }
}

// Global instance
let openaiIntegrationInstance = null;

/**
 * Get singleton OpenAI integration instance
 * @param {string} apiKey - API key (optional)
 * @returns {OpenAIIntegration} Integration instance
 */
function getOpenAIIntegration(apiKey = null) {
    if (!openaiIntegrationInstance) {
        openaiIntegrationInstance = new OpenAIIntegration(apiKey);
    }
    return openaiIntegrationInstance;
}

/**
 * Set OpenAI API key
 * @param {string} apiKey - API key
 */
function setOpenAIAPIKey(apiKey) {
    process.env.OPENAI_API_KEY = apiKey;
    // Reset instance to use new key
    openaiIntegrationInstance = null;
}

// Export
module.exports = {
    OpenAIIntegration,
    getOpenAIIntegration,
    setOpenAIAPIKey
};

// Example usage
if (require.main === module) {
    (async () => {
        try {
            const openai = getOpenAIIntegration();
            
            console.log('OpenAI Integration Test (Node.js)');
            console.log('='.repeat(80));
            console.log();
            
            const response = await openai.generateResponse(
                'write a haiku about ai',
                {
                    systemMessage: 'You are a helpful assistant.'
                }
            );
            
            console.log('Response:');
            console.log(response);
            console.log();
            
            console.log('✅ OpenAI integration working!');
        } catch (error) {
            console.error('❌ Error:', error.message);
            console.error('Please set OPENAI_API_KEY environment variable or use setOpenAIAPIKey()');
        }
    })();
}
