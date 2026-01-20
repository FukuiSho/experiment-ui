
import fs from 'fs';
import readline from 'readline';
import path from 'path';

const BENCHMARK_FILE = path.join(process.cwd(), 'benchmark.jsonl');
const OUTPUT_FILE = path.join(process.cwd(), 'benchmark_results.jsonl');
const API_URL = 'http://localhost:3000/api/chat';

// Get limit from command line args, default to Infinity (all)
const limitArg = process.argv[2] ? parseInt(process.argv[2]) : Infinity;
const LIMIT = isNaN(limitArg) ? Infinity : limitArg;

// Format duration helper
function formatDuration(ms: number): string {
    const seconds = Math.floor((ms / 1000) % 60);
    const minutes = Math.floor((ms / (1000 * 60)) % 60);
    const hours = Math.floor((ms / (1000 * 60 * 60)) % 24);
    const days = Math.floor(ms / (1000 * 60 * 60 * 24));
    return `${days}d ${hours}h ${minutes}m ${seconds}s`;
}

async function runBenchmark() {
    if (!fs.existsSync(BENCHMARK_FILE)) {
        console.error(`Benchmark file not found: ${BENCHMARK_FILE}`);
        process.exit(1);
    }

    // Count lines efficiently if running all or large subset to show progress
    // For now, we'll just log as we go.

    const fileStream = fs.createReadStream(BENCHMARK_FILE);
    const rl = readline.createInterface({
        input: fileStream,
        crlfDelay: Infinity
    });

    let count = 0;
    let processedContext = 0;
    const startTimeTotal = Date.now();

    console.log(`Starting benchmark run. Target Limit: ${LIMIT === Infinity ? 'ALL' : LIMIT}`);
    console.log(`Results will be appended to: ${OUTPUT_FILE}`);

    for await (const line of rl) {
        if (count >= LIMIT) break;
        if (!line.trim()) continue;

        try {
            const data = JSON.parse(line);

            // Skip if no query (validation)
            if (!data.query) continue;

            const query = data.query;
            const expected = data.expected_response;

            process.stdout.write(`[${count + 1}] Processing: "${query.substring(0, 30).replace(/\n/g, ' ')}..." `);

            const reqStart = Date.now();
            let response;
            let errorMsg = null;

            try {
                // Set a timeout for the fetch to avoid hanging forever
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 60000); // 60s timeout

                const res = await fetch(API_URL, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: query, condition: 'P' }),
                    signal: controller.signal
                });
                clearTimeout(timeoutId);

                if (!res.ok) {
                    throw new Error(`API Error: ${res.status}`);
                }

                const json = await res.json();
                response = json.reply;
            } catch (err: any) {
                errorMsg = err.message;
                response = `ERROR: ${err.message}`;
            }
            const reqEnd = Date.now();
            const latency = reqEnd - reqStart;

            console.log(`| Latency: ${latency}ms ${errorMsg ? `| FAILED: ${errorMsg}` : ''}`);

            const resultEntry = {
                id: data.id,
                query: query,
                expected_response: expected,
                generated_response: response,
                latency_ms: latency,
                timestamp: new Date().toISOString()
            };

            fs.appendFileSync(OUTPUT_FILE, JSON.stringify(resultEntry) + '\n');
            count++;

            // Calculate stats every line
            const totalElapsed = Date.now() - startTimeTotal;
            const avgLatency = totalElapsed / count;
            // If LIMIT is known, calculate ETA
            if (LIMIT !== Infinity) {
                const remaining = LIMIT - count;
                const eta = remaining * avgLatency;
                // Log ETA every 5 items
                if (count % 5 === 0) {
                    console.log(`   > Progress: ${count}/${LIMIT} | Avg: ${Math.round(avgLatency)}ms | ETA: ${formatDuration(eta)}`);
                }
            } else {
                // If running all, just show average
                if (count % 5 === 0) {
                    console.log(`   > Count: ${count} | Avg Latency: ${Math.round(avgLatency)}ms`);
                }
            }

        } catch (e: any) {
            console.error('Error parsing line:', e.message);
        }
    }

    console.log(`Benchmark completed. Processed ${count} items.`);
    console.log(`Total Time: ${formatDuration(Date.now() - startTimeTotal)}`);
}

runBenchmark().catch(console.error);
