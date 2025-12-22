const fs = require('fs');
const path = require('path');

const envPath = path.join(__dirname, '.env.local');
const content = fs.readFileSync(envPath, 'utf-8');

console.log('--- Start of File ---');
console.log(JSON.stringify(content));
console.log('--- End of File ---');
