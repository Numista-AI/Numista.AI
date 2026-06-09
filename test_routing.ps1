###############################################################################
#  test_routing.ps1  -- Verify item_type routing on problem invoices
###############################################################################

$API      = "https://numista-backend-568985927038.us-central1.run.app"
$EMAIL    = "test@numista.ai"
$SCAN_DIR = ".\Scans AJ June 2026"

$TARGETS = @(
    @{ File="Receipt_2026-06-03_102331.pdf"; Label="STAMP TEST (West Point stamp)";    ExpectStamp=$true;  ExpectSet=$false },
    @{ File="Receipt_2026-06-03_092205.pdf"; Label="SET TEST   (Ike Set auto-expand)"; ExpectStamp=$false; ExpectSet=$true  },
    @{ File="Receipt_2026-06-03_102135.pdf"; Label="MIXED TEST (supplies + coins)";    ExpectStamp=$false; ExpectSet=$false },
    @{ File="Receipt_2026-06-03_101410.pdf"; Label="REGRESSION (clean coin invoice)";  ExpectStamp=$false; ExpectSet=$false }
)

$pass = 0; $fail = 0; $warn = 0

function Write-Result {
    param($label, $ok, $msg)
    if ($ok -eq $true)        { $icon = "[PASS]"; $script:pass++ }
    elseif ($ok -eq $false)   { $icon = "[FAIL]"; $script:fail++ }
    else                      { $icon = "[WARN]"; $script:warn++ }
    Write-Host "  $icon  $label -- $msg"
}

Write-Host ""
Write-Host "================================================================="
Write-Host "  Numista.AI -- Item Routing Verification  $(Get-Date -Format 'HH:mm:ss')"
Write-Host "================================================================="
Write-Host ""

foreach ($t in $TARGETS) {
    $path = Join-Path $SCAN_DIR $t.File
    if (-not (Test-Path $path)) {
        Write-Host "  [SKIP] $($t.File) not found"
        $warn++
        continue
    }

    Write-Host "  Submitting: $($t.File) ..."
    $start = Get-Date

    try {
        $boundary = [System.Guid]::NewGuid().ToString("N")
        $fileBytes = [System.IO.File]::ReadAllBytes($path)
        $fileName  = [System.IO.Path]::GetFileName($path)

        $body = [System.Collections.Generic.List[byte]]::new()

        $emailPart = "--$boundary`r`nContent-Disposition: form-data; name=`"user_email`"`r`n`r`n$EMAIL`r`n"
        $body.AddRange([System.Text.Encoding]::UTF8.GetBytes($emailPart))

        $fileHeader = "--$boundary`r`nContent-Disposition: form-data; name=`"file`"; filename=`"$fileName`"`r`nContent-Type: application/pdf`r`n`r`n"
        $body.AddRange([System.Text.Encoding]::UTF8.GetBytes($fileHeader))
        $body.AddRange($fileBytes)

        $footer = "`r`n--$boundary--`r`n"
        $body.AddRange([System.Text.Encoding]::UTF8.GetBytes($footer))

        $resp = Invoke-WebRequest `
            -Method POST `
            -Uri "$API/api/process_invoice" `
            -ContentType "multipart/form-data; boundary=$boundary" `
            -Body $body.ToArray() `
            -TimeoutSec 180

        $elapsed = [int]((Get-Date) - $start).TotalSeconds
        $json    = $resp.Content | ConvertFrom-Json

        Write-Host ""
        Write-Host "  --- $($t.Label) ($($elapsed)s) ---"
        Write-Host "      status:           $($json.status)"
        Write-Host "      extracted_items:  $($json.extracted_items)  (coins/currency/medals -> review_queue)"
        Write-Host "      set_records:      $($json.set_records)"
        Write-Host "      set_coins_inside: $($json.set_coins_inside)"
        Write-Host "      pending_items:    $($json.pending_items)  (stamps -> pending_items)"
        Write-Host "      supplies_logged:  $($json.supplies_logged)"
        Write-Host ""

        # Item types breakdown
        if ($json.data) {
            $typeCounts = $json.data | Group-Object item_type | Select-Object Name, Count
            Write-Host "      item_type breakdown:"
            foreach ($tc in $typeCounts) {
                Write-Host "        $($tc.Name): $($tc.Count)"
            }
            Write-Host ""
        }

        # ---- STAMP checks ----
        if ($t.ExpectStamp) {
            Write-Result "Stamp routed to pending_items" ($json.pending_items -gt 0) "pending_items=$($json.pending_items) (expect >0)"

            $coinMisfire = $json.data | Where-Object {
                $_.item_type -eq "coin" -and
                ($_.Denomination -match "Nickel|Buffalo|5.?c|5 cent" -or $_.Year -eq "1937") -and
                ($_.Theme_Subject -match "Military|West Point|Academy" -or $_.Denomination -match "Military|West Point")
            }
            Write-Result "1937 West Point NOT a coin" (-not $coinMisfire) $(if ($coinMisfire) { "STILL misclassified as coin!" } else { "Correct -- not in coin list" })

            $stampItems = $json.data | Where-Object { $_.item_type -eq "stamp" }
            Write-Result "Stamp item_type present in data" ($stampItems.Count -gt 0 -or $json.pending_items -gt 0) "$($stampItems.Count) stamp(s) in response data, $($json.pending_items) in pending_items"
        }

        # ---- SET checks ----
        if ($t.ExpectSet) {
            Write-Result "Set records detected" ($json.set_records -gt 0) "set_records=$($json.set_records) (expect >0)"
            Write-Result "Set contains coins (set_coins_inside >= 8)" ($json.set_coins_inside -ge 8) "set_coins_inside=$($json.set_coins_inside)"

            $setItems = $json.data | Where-Object { $_.item_type -eq "set" }
            foreach ($si in $setItems) {
                $cCount = 0
                if ($si.set_contents) { $cCount = @($si.set_contents).Count }
                $denom = if ($si.Denomination) { $si.Denomination } else { "(no denom)" }
                Write-Result "Set '$denom' has set_contents" ($cCount -gt 0) "$cCount coins in set_contents"
                Write-Result "Set '$denom' has set_cost_label" ($si.set_cost_label -ne $null) "set_cost_label=$($si.set_cost_label)"
            }
        }

        # ---- REGRESSION checks ----
        if (-not $t.ExpectStamp -and -not $t.ExpectSet) {
            Write-Result "Coins extracted (regression)" ($json.extracted_items -gt 0) "extracted_items=$($json.extracted_items)"
            Write-Result "No spurious pending_items" ($json.pending_items -eq 0) "pending_items=$($json.pending_items)"
        }

    } catch {
        $elapsed = [int]((Get-Date) - $start).TotalSeconds
        Write-Result $t.Label $false "HTTP ERROR after $($elapsed)s -- $($_.Exception.Message)"
    }

    Write-Host "  -----------------------------------------------------------------"
    Write-Host ""
}

Write-Host ""
Write-Host "================================================================="
Write-Host "  PASS: $pass   FAIL: $fail   WARN: $warn"
Write-Host "================================================================="
Write-Host ""
