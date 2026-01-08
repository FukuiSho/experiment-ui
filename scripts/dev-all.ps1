$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot

Push-Location $repoRoot
try {
    if (-not (Test-Path -LiteralPath (Join-Path $repoRoot 'node_modules'))) {
        Write-Host 'node_modules が無いので npm install を実行します...' -ForegroundColor Yellow
        npm install
    }

    Write-Host 'フロント(Next.js) + cloneAI(FastAPI) を起動します...' -ForegroundColor Cyan
    npm run dev:all
}
finally {
    Pop-Location
}
