# Store GitHub token in Windows Credential Manager
$token = "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"
$username = "redpostfarms"

Write-Host "Storing GitHub token..." -ForegroundColor Cyan

# Use cmdkey to store in Windows Credential Manager
$target = "git:https://github.com"
cmdkey /generic:$target /user:$username /pass:$token

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Token stored successfully!" -ForegroundColor Green
    
    Write-Host "`nTesting authentication..." -ForegroundColor Cyan
    git fetch origin --dry-run 2>&1 | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Authentication successful!" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Repository may not exist on GitHub yet" -ForegroundColor Yellow
        Write-Host "   Create it at: https://github.com/new" -ForegroundColor Yellow
        Write-Host "   Repository name: The-Gatekeeper" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ Failed to store token" -ForegroundColor Red
}
