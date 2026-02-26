$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

$targetFiles = @(
  'unified_agent_framework.py',
  'omega_agent_council.py',
  'agents/development_agent.py',
  'agents/communication_agent.py'
)

$profileFiles = @(
  'config/agents/profiles/development_agent.json',
  'config/agents/profiles/communication_agent.json'
)

$councilDir = 'config/agent_council'
$logFiles = @(
  'logs/agents/town_hall.log',
  'omega_agents/agent_states.json',
  'omega_agents/learning_queue.json'
)

$markers = @('TODO', 'FIXME', 'PLACEHOLDER', 'TBD', 'mock', 'stub')

function Has-Symbol([string]$path, [string]$symbol) {
  if (-not (Test-Path $path)) { return $false }
  $content = Get-Content -Raw $path
  return $content.Contains($symbol)
}

$checks = [ordered]@{
  framework_exists = Test-Path 'unified_agent_framework.py'
  town_hall_api = Has-Symbol 'unified_agent_framework.py' 'def town_hall_post'
  agent_bundle_export = Has-Symbol 'unified_agent_framework.py' 'def export_agent_bundle'
  brain_access = Has-Symbol 'unified_agent_framework.py' 'class GatekeeperBrainAccess'
  omega_brain_api = Has-Symbol 'unified_agent_framework.py' 'def omega_query_brain'
  council_profile_loader = Has-Symbol 'omega_agent_council.py' 'def _load_agent_profiles'
  dev_profile_file = Test-Path 'config/agents/profiles/development_agent.json'
  comm_profile_file = Test-Path 'config/agents/profiles/communication_agent.json'
  council_profiles_count = if (Test-Path $councilDir) { (Get-ChildItem $councilDir -Filter *.json).Count } else { 0 }
}

$markerHits = @()
foreach ($f in $targetFiles) {
  if (-not (Test-Path $f)) { continue }
  $lines = Get-Content $f
  for ($i = 0; $i -lt $lines.Count; $i++) {
    $line = $lines[$i]
    foreach ($m in $markers) {
      if ($line -match [regex]::Escape($m)) {
        $markerHits += "${f}:$($i+1): $($line.Trim())"
        break
      }
    }
  }
}

$presentLogs = @($logFiles | Where-Object { Test-Path $_ })
$status = if (
  $checks.framework_exists -and
  $checks.town_hall_api -and
  $checks.agent_bundle_export -and
  $checks.brain_access -and
  $checks.council_profile_loader -and
  $checks.dev_profile_file -and
  $checks.comm_profile_file -and
  $checks.council_profiles_count -ge 6
) { 'pass' } else { 'fail' }

$report = [ordered]@{
  generated_at = (Get-Date -Format o)
  checks = $checks
  log_files_present = $presentLogs
  marker_hits = $markerHits
  status = $status
}

$outDir = 'audit_reports'
if (-not (Test-Path $outDir)) { New-Item -ItemType Directory -Path $outDir | Out-Null }
$ts = Get-Date -Format 'yyyyMMdd-HHmmss'
$jsonPath = Join-Path $outDir "agent_framework_forensic_$ts.json"
$mdPath = Join-Path $outDir "agent_framework_forensic_$ts.md"

$report | ConvertTo-Json -Depth 6 | Set-Content -Encoding UTF8 $jsonPath

$md = @()
$md += '# Agent Framework Forensic Scan'
$md += "Generated: $($report.generated_at)"
$md += ''
$md += '## Checks'
foreach ($k in $checks.Keys) {
  $md += "- ${k}: $($checks[$k])"
}
$md += ''
$md += '## Log Files Present'
if ($presentLogs.Count -gt 0) {
  foreach ($p in $presentLogs) { $md += "- $p" }
} else {
  $md += '- none'
}
$md += ''
$md += '## Marker Hits (targeted)'
if ($markerHits.Count -gt 0) {
  foreach ($h in $markerHits) { $md += "- $h" }
} else {
  $md += '- none'
}
$md += ''
$md += '## Status'
$md += "- $status"

$md | Set-Content -Encoding UTF8 $mdPath
Write-Output $mdPath
if ($status -ne 'pass') { exit 1 }
