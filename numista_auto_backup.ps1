# ============================================================
# numista_auto_backup.ps1
# Daily automatic Git commit + push to GitHub for Numista.AI
# Runs via Windows Task Scheduler - do not modify the path.
# ============================================================

$RepoPath   = "C:\Users\ericd\Documents\MyVertexProject"
$LogFile    = "C:\Users\ericd\Documents\MyVertexProject\numista_backup.log"
$MaxLogLines = 500  # Trim log if it gets too large

# Timestamp helper
function Log($msg) {
    $ts = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
    "$ts  $msg" | Tee-Object -Append -FilePath $LogFile
}

# Trim log file to last $MaxLogLines lines
function TrimLog {
    if (Test-Path $LogFile) {
        $lines = Get-Content $LogFile
        if ($lines.Count -gt $MaxLogLines) {
            $lines | Select-Object -Last $MaxLogLines | Set-Content $LogFile
        }
    }
}

TrimLog
Log "=============================="
Log "Numista.AI Auto-Backup Started"
Log "=============================="

# Move to repo root
Set-Location $RepoPath

# Check for git
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Log "ERROR: git not found in PATH. Aborting."
    exit 1
}

# Check if there's anything to commit (staged or unstaged changes / untracked files)
$statusOutput = git status --porcelain 2>&1
if (-not $statusOutput) {
    Log "No changes detected. Nothing to commit."
    Log "Done."
    exit 0
}

$changedCount = ($statusOutput | Measure-Object -Line).Lines
Log "Detected $changedCount changed/untracked items."

# Stage all changes (respecting .gitignore)
git add -A 2>&1 | ForEach-Object { Log "  [add] $_" }

# Build commit message
$commitDate = Get-Date -Format "yyyy-MM-dd HH:mm"
$commitMsg  = "chore: auto-backup $commitDate"

# Commit
$commitOut = git commit -m $commitMsg 2>&1
$commitOut | ForEach-Object { Log "  [commit] $_" }

if ($LASTEXITCODE -ne 0) {
    Log "ERROR: git commit failed (exit $LASTEXITCODE). Check output above."
    exit 1
}

# Push to GitHub
Log "Pushing to origin/main..."
$pushOut = git push origin main 2>&1
$pushOut | ForEach-Object { Log "  [push] $_" }

if ($LASTEXITCODE -ne 0) {
    Log "ERROR: git push failed (exit $LASTEXITCODE). Check output above."
    exit 1
}

Log "Backup complete - committed and pushed successfully."
Log ""
