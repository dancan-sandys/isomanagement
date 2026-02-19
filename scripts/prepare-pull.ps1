# Stage the files that would be overwritten by merge, commit, then pull.
# Run from repo root: .\scripts\prepare-pull.ps1

$files = @(
    "frontend/src/components/HACCP/HACCPWorkspace.tsx",
    "frontend/src/components/HACCP/ProductDialog.tsx",
    "frontend/src/mocks/mockBackend.ts",
    "frontend/src/pages/HACCP.tsx",
    "frontend/src/pages/HACCPProductDetail.tsx",
    "frontend/src/services/api.ts",
    "frontend/src/services/haccpAPI.ts",
    "frontend/src/services/traceabilityAPI.ts",
    "frontend/src/store/slices/authSlice.ts",
    "frontend/src/store/slices/haccpSlice.ts",
    "frontend/src/theme/navigationConfig.ts"
)

$root = Join-Path $PSScriptRoot ".."
Set-Location $root

foreach ($f in $files) {
    if (Test-Path $f) {
        git add $f
        Write-Host "Staged: $f"
    } else {
        Write-Host "Skip (not found): $f"
    }
}

git status
Write-Host ""
Write-Host "Committing..."
git commit -m "Preserve local HACCP and API changes before merge"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Commit failed or nothing to commit. Check git status."
    exit 1
}

Write-Host "Pulling origin master..."
git pull origin master
