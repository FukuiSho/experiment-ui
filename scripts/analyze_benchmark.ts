
import fs from 'fs';
import readline from 'readline';
import path from 'path';

const RESULTS_FILE = path.join(process.cwd(), 'benchmark_results.jsonl');

async function analyze() {
    if (!fs.existsSync(RESULTS_FILE)) {
        console.error(`Results file not found: ${RESULTS_FILE}`);
        process.exit(1);
    }

    const fileStream = fs.createReadStream(RESULTS_FILE);
    const rl = readline.createInterface({
        input: fileStream,
        crlfDelay: Infinity
    });

    let count = 0;
    let totalLatency = 0;
    let minLatency = Infinity;
    let maxLatency = -Infinity;
    let errorCount = 0;
    const latencies: number[] = [];
    let weirdResponseCount = 0; // e.g. empty or very short

    for await (const line of rl) {
        if (!line.trim()) continue;
        try {
            const data = JSON.parse(line);
            const latency = data.latency_ms;

            count++;
            totalLatency += latency;
            minLatency = Math.min(minLatency, latency);
            maxLatency = Math.max(maxLatency, latency);
            latencies.push(latency);

            const response = data.generated_response || "";
            if (typeof response === 'string') {
                if (response.startsWith("ERROR:")) {
                    errorCount++;
                } else if (response.trim().length === 0) {
                    weirdResponseCount++;
                }
            } else {
                weirdResponseCount++;
            }

        } catch (e) {
            // Ignore parse errors for analysis
        }
    }

    if (count === 0) {
        console.log("No result data found.");
        return;
    }

    // Calculate P50, P95, P99
    latencies.sort((a, b) => a - b);
    const p50 = latencies[Math.floor(latencies.length * 0.50)];
    const p95 = latencies[Math.floor(latencies.length * 0.95)];
    const p99 = latencies[Math.floor(latencies.length * 0.99)];
    const avgLatency = totalLatency / count;

    console.log("=== Benchmark Analysis Report ===");
    console.log(`Total Requests: ${count}`);
    console.log(`Success Rate: ${((count - errorCount) / count * 100).toFixed(2)}%`);
    console.log(`Error Count: ${errorCount}`);
    console.log(`Empty/Invalid Responses: ${weirdResponseCount}`);
    console.log("---------------------------------");
    console.log("Latency Metrics (ms):");
    console.log(`  Average: ${avgLatency.toFixed(2)}`);
    console.log(`  Min:     ${minLatency}`);
    console.log(`  Max:     ${maxLatency}`);
    console.log(`  P50 (Median): ${p50}`);
    console.log(`  P95:     ${p95}`);
    console.log(`  P99:     ${p99}`);
    console.log("---------------------------------");
    console.log(`Throughput (est): ${(1000 / avgLatency).toFixed(2)} req/sec (sequential)`);
}

analyze().catch(console.error);
