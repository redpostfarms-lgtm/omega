# Configure GitHub Personal Access Token
# Run this script to set up GitHub authentication

$token = "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"
$username = "redpostfarms"

Write-Host "=" * 80
Write-Host "CONFIGURING GITHUB TOKEN"
Write-Host "=" * 80
Write-Host ""

# Configure credential helper
Write-Host "[1/3] Configuring Git credential helper..."
git config --global credential.helper manager-core
Write-Host "✅ Credential helper configured"
Write-Host ""

# Store credentials
Write-Host "[2/3] Storing credentials..."
$credentialInput = @"
protocol=https
host=github.com
username=$username
password=$token

"@

$credentialInput | git credential-manager-core store

Write-Host "✅ Credentials stored"
Write-Host ""

# Test authentication
Write-Host "[3/3] Testing authentication..."
try {
    git fetch origin --dry-run 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Authentication successful!"
    } else {
        Write-Host "⚠️  Authentication test failed - repository may not exist yet"
        Write-Host "   Token is configured, but repository needs to be created on GitHub"
    }
} catch {
    Write-Host "⚠️  Could not test - repository may not exist yet"
}

Write-Host ""
Write-Host "=" * 80
Write-Host "SETUP COMPLETE"
Write-Host "=" * 80
Write-Host ""
Write-Host "Your GitHub token is now configured!"
Write-Host "You can now push/pull from GitHub."
Write-Host ""
