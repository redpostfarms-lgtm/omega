/**
 * Test OpenAI API Integration (Node.js)
 * ======================================
 * Test the OpenAI API with proper endpoints and models
 */

const { getOpenAIIntegration, setOpenAIAPIKey } = require('./omega_openai_integration');

async function testOpenAIAPI() {
    console.log('='.repeat(80));
    console.log('OPENAI API TEST (Node.js)');
    console.log('='.repeat(80));
    console.log();
    
    // Check if API key is set
    if (!process.env.OPENAI_API_KEY) {
        console.log('⚠️  OPENAI_API_KEY environment variable not set');
        console.log('Set it with: export OPENAI_API_KEY=your_key');
        console.log('Or use: setOpenAIAPIKey("your_key")');
        console.log();
        return false;
    }
    
    console.log(`✅ API key found (length: ${process.env.OPENAI_API_KEY.length} characters)`);
    console.log(`   Key prefix: ${process.env.OPENAI_API_KEY.substring(0, 15)}...`);
    console.log();
    
    try {
        const openai = getOpenAIIntegration();
        
        console.log('Testing OpenAI Chat Completions API...');
        console.log('-'.repeat(80));
        console.log();
        
        console.log('Model: gpt-4');
        console.log('Request: write a haiku about ai');
        console.log();
        console.log('Sending request...');
        console.log();
        
        const response = await openai.generateResponse(
            'write a haiku about ai',
            {
                systemMessage: 'You are a helpful assistant.',
                model: 'gpt-4',
                temperature: 0.7,
                max_tokens: 100
            }
        );
        
        console.log('✅ API Response:');
        console.log('-'.repeat(80));
        console.log(response);
        console.log('-'.repeat(80));
        console.log();
        console.log('✅ OpenAI API test successful!');
        return true;
    } catch (error) {
        console.error('❌ API request failed');
        console.error(`Error: ${error.message}`);
        return false;
    }
}

async function testAlternativeEndpoint() {
    console.log();
    console.log('='.repeat(80));
    console.log('TESTING ALTERNATIVE ENDPOINT');
    console.log('='.repeat(80));
    console.log();
    
    console.log('⚠️  Note: /v1/responses endpoint does not exist in standard OpenAI API');
    console.log('The standard OpenAI API uses /v1/chat/completions');
    console.log('Using the standard endpoint is recommended');
    console.log();
}

// Main
(async () => {
    const success = await testOpenAIAPI();
    await testAlternativeEndpoint();
    
    console.log();
    console.log('='.repeat(80));
    if (success) {
        console.log('✅ OPENAI API TEST COMPLETE - API WORKING');
    } else {
        console.log('❌ OPENAI API TEST FAILED - CHECK API KEY AND NETWORK');
    }
    console.log('='.repeat(80));
})();
