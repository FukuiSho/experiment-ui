
import * as fs from 'fs';
import * as path from 'path';

const SOURCE_DIR = 'src/lib/pesonaldata/unlabeldata';
const OUTPUT_DIR = 'src/lib/pesonaldata/DBmakedused/chunks';

// Ensure output directory exists
if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

function sanitizeFilename(name: string): string {
    // Allow Japanese characters, letters, numbers, underscores, dashes, dots
    return name.replace(/[^a-zA-Z0-9\u3000-\u303F\u3040-\u309F\u30A0-\u30FF\uFF00-\uFFEF\u4E00-\u9FAF_\-\.]/g, '_');
}

async function processLimitless(dir: string) {
    const lifelogsPath = path.join(dir, 'lifelogs.json');
    if (fs.existsSync(lifelogsPath)) {
        console.log(`Processing Limitless: ${lifelogsPath}`);
        try {
            const content = fs.readFileSync(lifelogsPath, 'utf-8');
            const data = JSON.parse(content);

            if (Array.isArray(data)) {
                console.log(`Found ${data.length} Limitless items.`);
                let count = 0;
                for (const entry of data) {
                    if (entry.title && (entry.markdown || entry.transcript)) {
                        const id = entry.id || 'unknown';
                        const title = entry.title;
                        const text = entry.markdown || entry.transcript || '';
                        // Limitless markdown often has "Unknown (Date): message".
                        const filename = `limitless_${sanitizeFilename(title)}_${id}.txt`;
                        fs.writeFileSync(path.join(OUTPUT_DIR, filename), text);
                        count++;
                    }
                }
                console.log(`Saved ${count} Limitless files.`);
            }
        } catch (e) {
            console.error('Error processing Limitless:', e);
        }
    }
}

async function processLine(dir: string) {
    const files = fs.readdirSync(dir);
    console.log(`Found ${files.length} files in LINE directory.`);
    for (const file of files) {
        if (file.endsWith('.txt')) {
            console.log(`Processing LINE: ${file}`);
            const content = fs.readFileSync(path.join(dir, file), 'utf-8');
            const lines = content.split('\n');
            let outputLines: string[] = [];
            let currentDate = '';

            for (const line of lines) {
                // Check for date line: 2022/04/28(木) or 2022/04/28
                const dateMatch = line.match(/^(\d{4}\/\d{2}\/\d{2}(?:\(.+\))?)/);
                if (dateMatch) {
                    currentDate = dateMatch[1];
                    continue;
                }

                // Format: HH:MM\tSpeaker\tMessage (tab separated seems to be the format based on inspection)
                const parts = line.split('\t');
                if (parts.length >= 3) {
                    const time = parts[0];
                    const speaker = parts[1];
                    const message = parts.slice(2).join(' ').trim();
                    // Skip stamps/photos if only that
                    if (message === '[スタンプ]' || message === '[写真]' || message === '[動画]') continue;

                    outputLines.push(`[${currentDate} ${time}] ${speaker}: ${message}`);
                }
            }

            if (outputLines.length > 0) {
                const filename = `line_${sanitizeFilename(file)}`;
                fs.writeFileSync(path.join(OUTPUT_DIR, filename), outputLines.join('\n'));
            }
        }
    }
}

async function processTxtFolder(dir: string, prefix: string) {
    const files = fs.readdirSync(dir);
    console.log(`Found ${files.length} files in ${prefix} directory.`);
    for (const file of files) {
        if (file.endsWith('.txt')) {
            console.log(`Processing ${prefix}: ${file}`);
            const content = fs.readFileSync(path.join(dir, file), 'utf-8');
            const filename = `${prefix}_${sanitizeFilename(file)}`;
            fs.writeFileSync(path.join(OUTPUT_DIR, filename), content);
        }
    }
}

async function processGPT(dir: string) {
    // Look for conversations.json in subdirectories
    function findConversations(currentDir: string) {
        const items = fs.readdirSync(currentDir);
        for (const item of items) {
            const fullPath = path.join(currentDir, item);
            if (fs.statSync(fullPath).isDirectory()) {
                findConversations(fullPath);
            } else if (item === 'conversations.json') {
                console.log(`Processing GPT: ${fullPath}`);
                try {
                    const content = fs.readFileSync(fullPath, 'utf-8');
                    const data = JSON.parse(content);
                    if (Array.isArray(data)) {
                        console.log(`Found ${data.length} GPT conversations.`);
                        let count = 0;
                        for (const conv of data) {
                            const title = conv.title || 'Untitled';
                            let text = '';
                            if (conv.mapping) {
                                // Sort by create_time if possible, but mapping keys are UUIDs.
                                // Usually we traverse starting from current_node or root? 
                                // Or just iterate values and sort by create_time?
                                const messages = Object.values(conv.mapping)
                                    .map((m: any) => m.message)
                                    .filter((m: any) => m && m.content && m.content.parts)
                                    .sort((a: any, b: any) => a.create_time - b.create_time);

                                for (const message of messages) {
                                    const author = message.author.role;
                                    const parts = message.content.parts.join('');
                                    if (parts) {
                                        text += `${author}: ${parts}\n\n`;
                                    }
                                }
                            }
                            if (text) {
                                const filename = `gpt_${sanitizeFilename(title)}_${conv.id}.txt`;
                                fs.writeFileSync(path.join(OUTPUT_DIR, filename), text);
                                count++;
                            }
                        }
                        console.log(`Saved ${count} GPT files.`);
                    }
                } catch (e) {
                    console.error(`Error processing GPT json: ${e}`);
                }
            }
        }
    }
    findConversations(dir);
}

async function processTwitter(dir: string) {
    // Look for tweets.js in subdirectories/data
    function findTweets(currentDir: string) {
        const items = fs.readdirSync(currentDir);
        for (const item of items) {
            const fullPath = path.join(currentDir, item);
            if (fs.statSync(fullPath).isDirectory()) {
                if (item === 'data' && fs.existsSync(path.join(fullPath, 'tweets.js'))) {
                    processTweetsJs(path.join(fullPath, 'tweets.js'));
                } else {
                    findTweets(fullPath);
                }
            }
        }
    }

    function processTweetsJs(filePath: string) {
        console.log(`Processing Twitter: ${filePath}`);
        try {
            let content = fs.readFileSync(filePath, 'utf-8');
            // Remove "window.YTD.tweets.part0 = " prefix
            content = content.replace(/^window\.YTD\.tweets\.part0\s*=\s*/, '');
            const data = JSON.parse(content);

            if (Array.isArray(data)) {
                console.log(`Found ${data.length} tweets.`);
                let allTweets = '';
                for (const item of data) {
                    const tweet = item.tweet;
                    if (tweet && tweet.full_text) {
                        const date = tweet.created_at;
                        allTweets += `[${date}] ${tweet.full_text}\n\n`;
                    }
                }
                const filename = `twitter_tweets.txt`;
                fs.writeFileSync(path.join(OUTPUT_DIR, filename), allTweets);
                console.log(`Saved Twitter tweets.`);
            }
        } catch (e) {
            console.error('Error processing tweets.js:', e);
        }
    }

    findTweets(dir);
}

async function main() {
    console.log('Starting normalization...');
    const subdirs = fs.readdirSync(SOURCE_DIR);
    for (const subdir of subdirs) {
        const fullPath = path.join(SOURCE_DIR, subdir);
        if (!fs.statSync(fullPath).isDirectory()) continue;

        if (subdir === 'limitless') {
            await processLimitless(fullPath);
        } else if (subdir === 'LINE') {
            await processLine(fullPath);
        } else if (subdir === 'pcmemo' || subdir === 'smartphonememo') {
            await processTxtFolder(fullPath, subdir);
        } else if (subdir === 'GPT') {
            await processGPT(fullPath);
        } else if (subdir === 'twitter') {
            await processTwitter(fullPath);
        } else {
            console.log(`Trying generic text processing for: ${subdir}`);
            await processTxtFolder(fullPath, subdir);
        }
    }
    console.log('Normalization complete.');
}

main().catch(console.error);
