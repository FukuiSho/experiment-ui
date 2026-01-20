
import fs from 'fs';
import readline from 'readline';
import path from 'path';

const INPUT_FILE = path.join(process.cwd(), 'benchmark_results.jsonl');
const OUTPUT_FILE = path.join(process.cwd(), 'benchmark_semantic_scores.jsonl');
const OLLAMA_HOST = process.env.OLLAMA_HOST || 'http://127.0.0.1:11434';
const EMBED_MODEL = process.env.OLLAMA_EMBED_MODEL || 'nomic-embed-text';

// --- Embedding Helper ---
async function generateEmbedding(text: string): Promise<number[]> {
    try {
        const url = `${OLLAMA_HOST.replace(/\/$/, '')}/api/embeddings`;
        const res = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ model: EMBED_MODEL, prompt: text }),
        });

        if (!res.ok) {
            throw new Error(`Ollama error: ${res.status} ${res.statusText}`);
        }

        const data = await res.json();
        return data.embedding;
    } catch (error) {
        console.error("Embedding Error:", error);
        return [];
    }
}

// --- Math Helpers ---
function cosineSimilarity(vecA: number[], vecB: number[]): number {
    if (vecA.length !== vecB.length || vecA.length === 0) return 0;

    let dotProduct = 0;
    let normA = 0;
    let normB = 0;

    for (let i = 0; i < vecA.length; i++) {
        dotProduct += vecA[i] * vecB[i];
        normA += vecA[i] * vecA[i];
        normB += vecB[i] * vecB[i];
    }

    if (normA === 0 || normB === 0) return 0;
    return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
}

// --- Main Process ---
async function main() {
    if (!fs.existsSync(INPUT_FILE)) {
        console.error(`Input file not found: ${INPUT_FILE}`);
        process.exit(1);
    }

    const fileStream = fs.createReadStream(INPUT_FILE);
    const rl = readline.createInterface({
        input: fileStream,
        crlfDelay: Infinity
    });

    console.log(`Calculating Semantic Similarity using model: ${EMBED_MODEL}...`);
    console.log(`Results will be saved to: ${OUTPUT_FILE}`);

    // Check if output file exists to resume? (Simplification: overwrite for detailed run or append)
    // We will append to allow stopping/starting if needed, but for now let's overwrite to clean start.
    fs.writeFileSync(OUTPUT_FILE, '');

    let count = 0;
    let totalScore = 0;
    const scores: number[] = [];

    const startTime = Date.now();

    for await (const line of rl) {
        if (!line.trim()) continue;
        try {
            const data = JSON.parse(line);
            const expected = data.expected_response || "";
            const generated = data.generated_response || "";

            if (!expected || !generated || generated.startsWith("ERROR:")) continue;

            // Generate embeddings
            const [embExpected, embGenerated] = await Promise.all([
                generateEmbedding(expected),
                generateEmbedding(generated)
            ]);

            if (embExpected.length === 0 || embGenerated.length === 0) continue;

            const score = cosineSimilarity(embExpected, embGenerated);

            count++;
            totalScore += score;
            scores.push(score);

            const result = {
                id: data.id,
                semantic_similarity: score,
                expected_response: expected,
                generated_response: generated
            };

            fs.appendFileSync(OUTPUT_FILE, JSON.stringify(result) + '\n');

            if (count % 10 === 0) {
                const avg = totalScore / count;
                const elapsed = (Date.now() - startTime) / 1000;
                process.stdout.write(`\rProcessed: ${count} | Current Avg: ${avg.toFixed(4)} | Time: ${elapsed.toFixed(0)}s`);
            }

        } catch (e: any) {
            console.error(`\nError processing line: ${e.message}`);
        }
    }

    console.log("\n\n=== Semantic Similarity Analysis Complete ===");
    if (count > 0) {
        const avg = totalScore / count;
        console.log(`Total Items: ${count}`);
        console.log(`Average Cosine Similarity: ${avg.toFixed(4)}`);

        // Percentiles
        scores.sort((a, b) => a - b);
        const p50 = scores[Math.floor(scores.length * 0.50)];
        const p90 = scores[Math.floor(scores.length * 0.90)];
        console.log(`Median (P50): ${p50.toFixed(4)}`);
        console.log(`P90: ${p90.toFixed(4)}`);
    } else {
        console.log("No valid items processed.");
    }
}

main().catch(console.error);
