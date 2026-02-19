# Find files with Git merge conflict markers
# Run from repo root after git pull reports conflicts: .\scripts\find-merge-conflicts.ps1

$root = if ($args[0]) { $args[0] } else { Join-Path $PSScriptRoot '..' }
$extensions = @('.py', '.ts', '.tsx', '.js', '.jsx', '.json', '.md', '.yml', '.yaml', '.sh')

$found = @()
Get-ChildItem -Path $root -Recurse -File -ErrorAction SilentlyContinue | Where-Object {
    $_.FullName -notmatch '[\\/]\.git[\\/]' -and
    $extensions -contains $_.Extension
} | ForEach-Object {
    $content = Get-Content -Path $_.FullName -Raw -ErrorAction SilentlyContinue
    if ($content -and $content -match '<<<<<<<') {
        $found += $_.FullName
    }
}

if ($found.Count -eq 0) {
    Write-Host "No conflict markers found."
} else {
    Write-Host "Files with conflict markers ($($found.Count)):"
    $found | ForEach-Object { Write-Host "  $_" }
}
