
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Define constants locally to avoid import issues
const OLLAMA_CHAT_CONFIG = {
    temperature: 1.41,
    top_p: 0.9,
    num_predict: 1000,
};

// Configuration
// Using absolute path assumption relative to script location
const SOURCE_DIR = path.join(__dirname, '../src/lib/pesonaldata/DBmakedused/chunks');
const OLLAMA_HOST = process.env.OLLAMA_HOST || 'http://127.0.0.1:11434';
const OLLAMA_MODEL = process.env.OLLAMA_CHAT_MODEL || 'gemma2:9b';
const CONCURRENCY = 3;
const TEST_LIMIT = 0;

const CATEGORIES = ['Fact', 'Thought', 'Experience'];

async function classifyText(text) {
    const url = `${OLLAMA_HOST.replace(/\/$/, '')}/api/chat`;

    const truncatedText = text.length > 2000 ? text.substring(0, 2000) + "..." : text;

    const systemPrompt = `
You are a data classifier. Classify the given text into EXACTLY one of these three categories:
1. Fact (事実): Objective information, news, logs, specific events without personal opinion.
2. Thought (考え): Ideas, opinions, philosophy, introspection, planning, speculation.
3. Experience (体験): Personal narratives, memories, specific personal actions, feelings about an event.

Return ONLY the category name: "Fact", "Thought", or "Experience". Do not add any explanation or punctuation.
`;

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                model: OLLAMA_MODEL,
                stream: false,
                messages: [
                    { role: 'system', content: systemPrompt },
                    { role: 'user', content: truncatedText }
                ],
                options: {
                    temperature: 0.1,
                    num_predict: 10,
                }
            })
        });

        if (!response.ok) {
            throw new Error(`Ollama error: ${response.status}`);
        }

        const data = await response.json();
        let content = data.message?.content?.trim();

        content = content.replace(/['"]/g, '').replace(/\.$/, '');

        if (content.includes('Fact') || content.includes('事実')) return 'Fact';
        if (content.includes('Thought') || content.includes('考え')) return 'Thought';
        if (content.includes('Experience') || content.includes('体験')) return 'Experience';

        console.warn(`Ambiguous response: "${content}". Defaulting to Fact.`);
        return 'Fact';

    } catch (error) {
        console.error('Classification failed:', error);
        return 'Fact';
    }
}

async function processFile(file) {
    const filePath = path.join(SOURCE_DIR, file);
    try {
        const content = fs.readFileSync(filePath, 'utf-8');
        if (!content.trim()) return;

        console.log(`Classifying: ${file}...`);
        const category = await classifyText(content);
        console.log(`-> ${category}`);

        const targetDir = path.join(SOURCE_DIR, category);
        if (!fs.existsSync(targetDir)) {
            fs.mkdirSync(targetDir, { recursive: true });
        }

        const targetPath = path.join(targetDir, file);
        fs.renameSync(filePath, targetPath);

    } catch (e) {
        console.error(`Error processing ${file}:`, e);
    }
}

async function main() {
    if (!fs.existsSync(SOURCE_DIR)) {
        console.error(`Source directory not found: ${SOURCE_DIR}`);
        process.exit(1);
    }

    CATEGORIES.forEach(cat => {
        const dir = path.join(SOURCE_DIR, cat);
        if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    });

    const files = fs.readdirSync(SOURCE_DIR).filter(f => f.endsWith('.txt'));
    console.log(`Found ${files.length} files to classify.`);

    const filesToProcess = TEST_LIMIT > 0 ? files.slice(0, TEST_LIMIT) : files;

    for (let i = 0; i < filesToProcess.length; i += CONCURRENCY) {
        const batch = filesToProcess.slice(i, i + CONCURRENCY);
        await Promise.all(batch.map(f => processFile(f)));
    }

    console.log('Classification complete.');
}

main();
