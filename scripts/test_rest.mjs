
const CHROMA_URL = 'http://[::1]:8000';

async function main() {
    try {
        console.log("Testing /api/v2/heartbeat...");
        const res = await fetch(`${CHROMA_URL}/api/v2/heartbeat`);
        console.log("Status:", res.status);
        const text = await res.text();
        console.log("Body:", text);

        console.log("\nTesting /api/v1/collections...");
        const res2 = await fetch(`${CHROMA_URL}/api/v1/collections`);
        console.log("Status:", res2.status);
        const text2 = await res2.text(); // Should be list of collections
        console.log("Body:", text2);

    } catch (e) {
        console.error("Fetch failed:", e);
    }
}

main();
