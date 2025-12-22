const OpenAI = require('openai');
const fs = require('fs');
const path = require('path');

// Manually parse .env.local because we are running with node directly
const envPath = path.join(__dirname, '.env.local');
const envContent = fs.readFileSync(envPath, 'utf-8');
const apiKeyMatch = envContent.match(/OPENAI_API_KEY=(.*)/);
const apiKey = apiKeyMatch ? apiKeyMatch[1].trim() : null;

console.log('API Key found:', apiKey ? 'Yes' : 'No');
if (apiKey) {
    console.log('API Key length:', apiKey.length);
    console.log('API Key start:', apiKey.substring(0, 5));
}

const openai = new OpenAI({
    apiKey: apiKey,
});

async function test() {
    try {
        console.log('Testing embedding...');
        const response = await openai.embeddings.create({
            model: "text-embedding-3-small",
            input: "test",
        });
        console.log('Success! Embedding length:', response.data[0].embedding.length);
    } catch (error) {
        console.error('Error:', error.message);
    }
}

test();
