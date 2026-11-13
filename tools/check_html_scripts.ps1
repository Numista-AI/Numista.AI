param (
    [string]$WebDir = "$PSScriptRoot/../numista_mobile/web"
)

$ErrorActionPreference = "Continue"
$htmlFiles = Get-ChildItem -Path "$WebDir/*.html"
$totalFiles = 0
$failedFiles = 0

Write-Host "=========================================="
Write-Host "Running node --check on HTML script blocks"
Write-Host "=========================================="

foreach ($file in $htmlFiles) {
    $totalFiles++
    $content = [System.IO.File]::ReadAllText($file.FullName)
    $pattern = '(?si)<script(?:\s+[^>]*)?>(.*?)</script>'
    $matches = [System.Text.RegularExpressions.Regex]::Matches($content, $pattern)
    $filePassed = $true

    if ($matches.Count -eq 0) {
        Write-Host "PASS: $($file.Name) (no scripts found)" -ForegroundColor Green
        continue
    }

    $idx = 0
    foreach ($m in $matches) {
        $idx++
        $scriptContent = $m.Groups[1].Value
        $tag = $m.Value.Substring(0, $m.Value.IndexOf('>') + 1)
        if ($tag -match 'src=') {
            continue
        }

        if ($tag -match 'type=["'']application/ld\+json["'']') {
            # Validate JSON
            try {
                $null = ConvertFrom-Json -InputObject $scriptContent -ErrorAction Stop
            } catch {
                $filePassed = $false
                Write-Host "FAIL: $($file.Name) (JSON-LD block #$idx)" -ForegroundColor Red
                Write-Host "$($_.Exception.Message)" -ForegroundColor DarkRed
            }
            continue
        }

        $isModule = ($tag -match 'type=["'']module["'']')
        $ext = if ($isModule) { ".mjs" } else { ".js" }

        $tempFile = [System.IO.Path]::Combine([System.IO.Path]::GetTempPath(), "check_script_$($idx)" + $ext)
        [System.IO.File]::WriteAllText($tempFile, $scriptContent)

        $checkOutput = & node --check $tempFile 2>&1
        $exitCode = $LASTEXITCODE
        Remove-Item -Path $tempFile -Force -ErrorAction SilentlyContinue

        if ($exitCode -ne 0) {
            $filePassed = $false
            Write-Host "FAIL: $($file.Name) (script block #$idx)" -ForegroundColor Red
            Write-Host "$checkOutput" -ForegroundColor DarkRed
        }
    }

    if ($filePassed) {
        Write-Host "PASS: $($file.Name)" -ForegroundColor Green
    } else {
        $failedFiles++
    }
}

Write-Host "=========================================="
Write-Host "Summary: $($totalFiles - $failedFiles)/$totalFiles HTML files passed."

if ($failedFiles -gt 0) {
    Write-Host "ERROR: $failedFiles HTML file(s) failed script check." -ForegroundColor Red
    exit 1
} else {
    Write-Host "SUCCESS: All HTML scripts passed node --check." -ForegroundColor Green
    exit 0
}
