# Start ChromaDB locally
# Requirement: pip install chromadb

$DB_PATH = "$PSScriptRoot/../src/data/chroma_db"
Write-Host "Starting ChromaDB..."
Write-Host "Database Path: $DB_PATH"
Write-Host "URL: http://localhost:8000"

# Create directory if not exists
if (-not (Test-Path $DB_PATH)) {
    New-Item -ItemType Directory -Force -Path $DB_PATH | Out-Null
}

# Check common user script paths and add to PATH
$UserScripts = "$env:APPDATA\Python\Python311\Scripts"
$LocalScripts = "$env:LOCALAPPDATA\Programs\Python\Python311\Scripts"

if (Test-Path "$UserScripts\chroma.exe") {
    Write-Host "Found chroma in UserScripts: $UserScripts"
    $env:PATH += ";$UserScripts"
} elseif (Test-Path "$LocalScripts\chroma.exe") {
    Write-Host "Found chroma in LocalScripts: $LocalScripts"
    $env:PATH += ";$LocalScripts"
} else {
    Write-Host "Could not find chroma.exe in common locations. Assuming it's in PATH or hoping for the best."
}

# Check if chroma is installed
try {
    chroma --version
} catch {
    Write-Error "ChromaDB CLI not found in PATH or common locations. Please add it to PATH manually."
    Write-Error "Try running: pip show -f chromadb"
    exit 1
}

# Run server
chroma run --path $DB_PATH
