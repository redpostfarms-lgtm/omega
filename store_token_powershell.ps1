# PowerShell script to store GitHub token in Windows Credential Manager
$token = "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"
$username = "redpostfarms"

Write-Host "Storing GitHub token in Windows Credential Manager..." -ForegroundColor Cyan

# Use git credential fill/store to store the token
$credentialInput = @"
protocol=https
host=github.com
username=$username
password=$token

"@

try {
    $credentialInput | git credential-manager store
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Token stored successfully!" -ForegroundColor Green
        
        Write-Host "`nTesting authentication..." -ForegroundColor Cyan
        git fetch origin --dry-run 2>&1 | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Authentication successful!" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Repository may not exist on GitHub yet" -ForegroundColor Yellow
            Write-Host "   Create it at: https://github.com/new" -ForegroundColor Yellow
        }
    } else {
        Write-Host "⚠️  Token storage may have failed" -ForegroundColor Yellow
        Write-Host "`nManual setup:" -ForegroundColor Cyan
        Write-Host "1. Open Windows Credential Manager" -ForegroundColor White
        Write-Host "2. Go to Windows Credentials" -ForegroundColor White
        Write-Host "3. Add Generic Credential:" -ForegroundColor White
        Write-Host "   - Internet address: git:https://github.com" -ForegroundColor Gray
        Write-Host "   - Username: $username" -ForegroundColor Gray
        Write-Host "   - Password: $token" -ForegroundColor Gray
    }
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
    Write-Host "`nPlease use manual method above" -ForegroundColor Yellow
}
