$h = @{
    Authorization = "Bearer $env:COOLIFY_API_TOKEN"
    Accept = "application/json"
}

$appUuid = "g40o0os008wc8sgoog84w48c"
$url = "$env:COOLIFY_API_URL/api/v1/deploy?uuid=$appUuid&force=true"

Write-Host "Deploying cerebro-backend..." -ForegroundColor Cyan
Write-Host "URL: $url" -ForegroundColor Gray

try {
    $result = Invoke-RestMethod -Uri $url -Headers $h -Method GET
    Write-Host "[OK] Deploy iniciado" -ForegroundColor Green
    $result | ConvertTo-Json -Depth 5
} catch {
    Write-Host "[FAIL] $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $reader.BaseStream.Position = 0
        $responseBody = $reader.ReadToEnd()
        Write-Host "Response: $responseBody" -ForegroundColor Yellow
    }
}
