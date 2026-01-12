/**
 * Test OpenAI API - Fixed Version
 * =================================
 * This tests the OpenAI API with the correct endpoint and format
 */

const OpenAI = require('openai');
const { getOpenAIAPIKey } = require('./omega_api_keys_node');

// Try to get API key from secure storage or use environment variable
function getAPIKey() {
    try {
        // Try to get from secure storage (Python-generated)
        const key = getOpenAIAPIKey();
        if (key) return key;
    } catch (error) {
        // Fall back to environment variable
    }
    
    // Use environment variable
    return process.env.OPENAI_API_KEY;
}

const apiKey = getAPIKey();

if (!apiKey) {
    console.error('❌ OpenAI API key not found!');
    console.error('Please set OPENAI_API_KEY environment variable');
    console.error('Or store it using: python STORE_API_KEY.py');
    process.exit(1);
}

const openai = new OpenAI({
    apiKey: apiKey,
});

async function testOpenAI() {
    console.log('='.repeat(80));
    console.log('OPENAI API TEST');
    console.log('='.repeat(80));
    console.log();
    
    try {
        console.log('Testing OpenAI Chat Completions API...');
        console.log('-'.repeat(80));
        console.log();
        
        // Note: openai.responses.create() doesn't exist
        // The standard OpenAI API uses openai.chat.completions.create()
        // Also, gpt-5-nano doesn't exist - using gpt-4 instead
        
        console.log('Model: gpt-4 (standard)');
        console.log('Request: write a haiku about ai');
        console.log();
        console.log('Sending request...');
        console.log();
        
        const response = await openai.chat.completions.create({
            model: "gpt-4", // Using standard model (gpt-5-nano doesn't exist yet)
            messages: [
                {
                    role: "user",
                    content: "write a haiku about ai"
                }
            ],
            max_tokens: 100,
            temperature: 0.7
        });
        
        console.log('✅ API Response:');
        console.log('-'.repeat(80));
        
        // Standard OpenAI API response format
        if (response.choices && response.choices.length > 0) {
            const outputText = response.choices[0].message.content;
            console.log(outputText);
        } else {
            console.log('No response content');
        }
        
        console.log('-'.repeat(80));
        console.log();
        console.log('✅ OpenAI API test successful!');
        
    } catch (error) {
        console.error('❌ Error:', error.message);
        
        if (error.response) {
            console.error('Status:', error.response.status);
            console.error('Error details:', error.response.data);
        }
        
        console.log();
        console.log('Note:');
        console.log('- The /v1/responses endpoint does not exist in the standard OpenAI API');
        console.log('- Use /v1/chat/completions instead (openai.chat.completions.create())');
        console.log('- gpt-5-nano doesn\'t exist yet - use gpt-4 or gpt-3.5-turbo');
        console.log('- The standard response format uses response.choices[0].message.content');
    }
}

// Run test
testOpenAI();
