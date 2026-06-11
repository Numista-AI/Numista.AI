$cookies = "dwanonymous_b2cf918be9f3733e2d19f7e7beb4b6d7=acvbZsuqmyvGOefBI1gzTaZ7oC; cf_clearance=ebBcScFZR9QVZZF5j1C2TckIS801YQ0Uw29QtcnXOSw-1781120329-1.2.1.1-R6vYVGJoD4sXoMBg4exiTPFL93DBLwKZwMb8ElkvE7NZuC5Oj0v4AOxVEdgrBpjKJ6dtQWTXNgLwrIfvsO23CHdfo4ycurvfQUvmbd7.poM7ldsmIvVU8KGokoXjDlaCgEPaxBVkTmQTK_SkvCgDg7DjIEGK23Lj_w8L_FjOjiudPuTU14Uma.LwrKSNyF3qTYyFhM19zXFqWivhR7UrX9tjPOS6RjN0fzJpDc.Kg_notXz4pOvUxha6mhGKwy25h0M9k1Vt3dRkuLqAyxVeLVUbOqbEpwCJUh8xPDn63FcgJTH9BE.F.rzOnvaH50IPPgearHi_0RS7Q18zKvt0ZQ; dwsid=z2oWaK1J20eFDD3hp0kxLMV88iWVPn0M3bkl_XNCbAaF2Q3ulIi_n-TOxe7A1BcTkPzc7j6Jb-qtir-br1VPpA==; sid=vrnFb1d2N_YrqhgNhGpFoLSvISJvAZG9cx8; AWSALB=yA4jrsFgyR8WIqwUnBf+4op10KcJqn68XtbW5ZlpvyNdYasPkYt+Fsrkd+JEP438i5dohLe8CI6FxqTyU+lqUmMYwfC9l6uTxhFKX/CuW/1uJOie9cW2eK/z2SD1; AWSALBCORS=yA4jrsFgyR8WIqwUnBf+4op10KcJqn68XtbW5ZlpvyNdYasPkYt+Fsrkd+JEP438i5dohLe8CI6FxqTyU+lqUmMYwfC9l6uTxhFKX/CuW/1uJOie9cW2eK/z2SD1"

$outDir = "C:\Users\ericd\Documents\MyVertexProject\Manual downloaded Coin Images\US Mint\HighRes_Scrape"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$sections = @("circulating", "commemorative", "bullion", "numismatic", "historical")

foreach ($section in $sections) {
    $url = "https://www.usmint.gov/news/image-library/$section"
    Write-Host "Testing: $url"
    try {
        $response = Invoke-WebRequest -Uri $url -Headers @{
            "Cookie" = $cookies
            "User-Agent" = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"
            "Accept" = "text/html,application/xhtml+xml,*/*"
            "sec-fetch-dest" = "document"
            "sec-fetch-mode" = "navigate"
            "sec-fetch-site" = "same-origin"
        } -UseBasicParsing
        
        $html = $response.Content
        $matches = [regex]::Matches($html, 'https?://www\.usmint\.gov/content/dam/usmint/image-library/[^\s"''<>]+\.(?:jpg|jpeg|png)', 'IgnoreCase')
        $imgs = $matches.Value | Where-Object { $_ -notmatch '150x|300x|500x|thumb|icon' } | Sort-Object -Unique
        Write-Host "  Status: $($response.StatusCode)  Images found: $($imgs.Count)"
        $imgs | Select-Object -First 3 | ForEach-Object { Write-Host "  $_" }
        
        # Save HTML for analysis
        $html | Out-File "$outDir\${section}_page.html" -Encoding UTF8
    } catch {
        Write-Host "  ERROR: $($_.Exception.Message)"
    }
}
