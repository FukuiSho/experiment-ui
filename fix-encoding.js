const fs = require('fs');
const path = require('path');

const envPath = path.join(__dirname, '.env.local');
// Read as buffer to handle encoding manually
const buffer = fs.readFileSync(envPath);

// Check for UTF-16 LE BOM
if (buffer[0] === 0xFF && buffer[1] === 0xFE) {
    console.log('Detected UTF-16 LE BOM. Converting to UTF-8...');
    const content = buffer.toString('utf16le');
    fs.writeFileSync(envPath, content, 'utf8');
    console.log('Conversion complete.');
} else {
    console.log('File does not appear to be UTF-16 LE.');
}
