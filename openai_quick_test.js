/**
 * OpenAI Quick Test - Corrected Version
 * ======================================
 * This is the corrected version of the user's code
 */

const OpenAI = require('openai');
const { getOpenAIAPIKey } = require('./omega_api_keys_node');

// Get API key from secure storage or environment variable
const apiKey = getOpenAIAPIKey() || process.env.OPENAI_API_KEY;

if (!apiKey) {
    console.error('❌ OpenAI API key not found!');
    console.error('Please set OPENAI_API_KEY environment variable');
    console.error('Or store it using: python STORE_API_KEY.py');
    process.exit(1);
}

const openai = new OpenAI({
    apiKey: apiKey,
});

async function main() {
    try {
        // CORRECTED: Use chat.completions.create() instead of responses.create()
        // CORRECTED: Use gpt-4 instead of gpt-5-nano (which doesn't exist yet)
        // CORRECTED: Use messages array instead of input parameter
        // CORRECTED: Use response.choices[0].message.content instead of output_text
        
        console.log('Testing OpenAI API...');
        console.log('-'.repeat(80));
        console.log();
        
        const response = await openai.chat.completions.create({
            model: "gpt-4", // Using gpt-4 (gpt-5-nano doesn't exist yet)
            messages: [
                {
                    role: "user",
                    content: "write a haiku about ai"
                }
            ],
            max_tokens: 100,
            temperature: 0.7
        });
        
        // CORRECTED: Standard OpenAI API response format
        const outputText = response.choices[0].message.content;
        
        console.log('Response:');
        console.log('-'.repeat(80));
        console.log(outputText);
        console.log('-'.repeat(80));
        
    } catch (error) {
        console.error('❌ Error:', error.message);
        
        if (error.response) {
            console.error('Status:', error.response.status);
            console.error('Error details:', JSON.stringify(error.response.data, null, 2));
        }
        
        console.log();
        console.log('CORRECTIONS MADE:');
        console.log('1. Changed openai.responses.create() → openai.chat.completions.create()');
        console.log('2. Changed model: "gpt-5-nano" → model: "gpt-4"');
        console.log('3. Changed input parameter → messages array');
        console.log('4. Changed result.output_text → response.choices[0].message.content');
        console.log('5. Removed store parameter (not part of standard API)');
    }
}

main();
