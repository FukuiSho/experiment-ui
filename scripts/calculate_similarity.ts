
import fs from 'fs';
import readline from 'readline';
import path from 'path';

const RESULTS_FILE = path.join(process.cwd(), 'benchmark_results.jsonl');

// Levenshtein Distance
function levenshtein(a: string, b: string): number {
    const matrix = Array.from({ length: b.length + 1 }, (_, i) => [i]);
    for (let j = 0; j <= a.length; j++) matrix[0][j] = j;

    for (let i = 1; i <= b.length; i++) {
        for (let j = 1; j <= a.length; j++) {
            if (b.charAt(i - 1) === a.charAt(j - 1)) {
                matrix[i][j] = matrix[i - 1][j - 1];
            } else {
                matrix[i][j] = Math.min(
                    matrix[i - 1][j - 1] + 1, // substitution
                    matrix[i][j - 1] + 1,     // insertion
                    matrix[i - 1][j] + 1      // deletion
                );
            }
        }
    }
    return matrix[b.length][a.length];
}

// Normalized Levenshtein Similarity (0 to 1)
function normalizedLevenshtein(a: string, b: string): number {
    if (a.length === 0 && b.length === 0) return 1;
    if (a.length === 0 || b.length === 0) return 0;
    const maxLen = Math.max(a.length, b.length);
    const dist = levenshtein(a, b);
    return 1 - (dist / maxLen);
}

// Jaccard Similarity (Bigrams)
function getBigrams(str: string): Set<string> {
    const bigrams = new Set<string>();
    for (let i = 0; i < str.length - 1; i++) {
        bigrams.add(str.substring(i, i + 2));
    }
    return bigrams;
}

function jaccard(a: string, b: string): number {
    const biA = getBigrams(a);
    const biB = getBigrams(b);
    if (biA.size === 0 && biB.size === 0) return 1;
    if (biA.size === 0 || biB.size === 0) return 0;

    let intersection = 0;
    biA.forEach(item => {
        if (biB.has(item)) intersection++;
    });

    const union = biA.size + biB.size - intersection;
    return intersection / union;
}

async function calculate() {
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
    let sumLevenshtein = 0;
    let sumJaccard = 0;
    const scores = [];

    console.log("Processing similarity scores...");

    for await (const line of rl) {
        if (!line.trim()) continue;
        try {
            const data = JSON.parse(line);
            const expected = data.expected_response || "";
            const generated = data.generated_response || "";

            // Skip errors
            if (generated.startsWith("ERROR:")) continue;

            const levScore = normalizedLevenshtein(expected, generated);
            const jacScore = jaccard(expected, generated);

            sumLevenshtein += levScore;
            sumJaccard += jacScore;
            count++;

            scores.push({ ...data, levScore, jacScore });

            if (count % 1000 === 0) process.stdout.write(".");

        } catch (e) {
            // ignore
        }
    }
    console.log("\nDone.");

    if (count === 0) {
        console.log("No valid metrics found.");
        return;
    }

    const avgLev = sumLevenshtein / count;
    const avgJac = sumJaccard / count;

    // Output stats
    console.log("=== Text Similarity Analysis ===");
    console.log(`Examples processed: ${count}`);
    console.log(`Average Normalized Levenshtein Score: ${avgLev.toFixed(4)}`);
    console.log(`Average Jaccard Similarity (Bigram): ${avgJac.toFixed(4)}`);
    console.log("--------------------------------");

    // Sort by Levenshtein to show best/worst
    scores.sort((a, b) => b.levScore - a.levScore);

    const topN = 50;
    const outputFile = path.join(process.cwd(), 'high_similarity_samples.txt');
    const outputLines = [];

    outputLines.push("=== Top 50 High Similarity Responses ===");
    scores.slice(0, topN).forEach((s, i) => {
        outputLines.push(`\n[${i + 1}] NormLev: ${s.levScore.toFixed(4)} | Jaccard: ${s.jacScore.toFixed(4)}`);
        outputLines.push(`    Query:     ${s.query}`);
        outputLines.push(`    Expected:  ${s.expected_response}`);
        outputLines.push(`    Generated: ${s.generated_response.replace(/\n/g, ' ')}`);
    });

    fs.writeFileSync(outputFile, outputLines.join('\n'));
    console.log(`\nTop ${topN} high similarity samples saved to: ${outputFile}`);

    // Still print top 3 to console
    console.log("\nTop 3 Matches (High Similarity):");
    scores.slice(0, 3).forEach((s, i) => {
        console.log(`[${i + 1}] Score: ${s.levScore.toFixed(2)}`);
        console.log(`    Expected:  ${s.expected_response}`);
        console.log(`    Generated: ${s.generated_response.replace(/\n/g, '')}`);
    });
}

calculate().catch(console.error);
