
import { ChromaClient } from 'chromadb';

const CHROMA_URL = 'http://[::1]:8000';
const COLLECTION_NAME = 'limitless_logs';
const OLLAMA_HOST = 'http://127.0.0.1:11434';
const OLLAMA_MODEL = 'gemma3:27b';

async function chatWithOllama(prompt) {
    const res = await fetch(`${OLLAMA_HOST}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            model: OLLAMA_MODEL,
            stream: false,
            messages: [{ role: 'user', content: prompt }]
        })
    });
    const data = await res.json();
    return data.message.content;
}

async function getChromaCount(filterCategories) {
    const client = new ChromaClient({ path: CHROMA_URL });
    const collection = await client.getCollection({
        name: COLLECTION_NAME,
        embeddingFunction: { generate: async (t) => t.map(() => []) }
    });

    const where = filterCategories.length > 0 ? { category: { "$in": filterCategories } } : undefined;
    const result = await collection.get({ where: where });
    return result.ids.length;
}

async function testQuery(userQuery) {
    console.log(`\n--- Query: "${userQuery}" ---`);

    // 1. Router Simulation
    const intentPrompt = `
Analyze the user's query and decide which data categories to search.
Categories:
1. Fact (事実): Questions about events, logs, specific information.
2. Thought (考え): Questions about opinions, ideas, philosophy, reasons.
3. Experience (体験): Questions about personal stories, memories, feelings.

Return valid categories as a comma-separated list.
User Query: "${userQuery}"
`;
    const classification = await chatWithOllama(intentPrompt);
    console.log(`Router Output: "${classification.trim()}"`);

    let categories = [];
    if (classification.includes('Fact') || classification.includes('事実')) categories.push('Fact');
    if (classification.includes('Thought') || classification.includes('考え')) categories.push('Thought');
    if (classification.includes('Experience') || classification.includes('体験')) categories.push('Experience');

    console.log(`Mapped Categories: [${categories.join(', ')}]`);

    // 2. Count Matching Docs in Chroma (Simulation of filtered search)
    // We just check if such categories exist and have documents
    try {
        const count = await getChromaCount(categories);
        console.log(`Potential Hits in DB: ${count}`);
    } catch (e) {
        console.error("Chroma check failed:", e);
    }
}

async function main() {
    await testQuery("先週の金曜日何してた？"); // Expect Fact/Experience
    await testQuery("プログラミングについてどう思う？"); // Expect Thought
}

main();
