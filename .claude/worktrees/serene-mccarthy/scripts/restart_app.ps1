$h = @{ Authorization = "Bearer $env:COOLIFY_API_TOKEN"; Accept = "application/json"; "Content-Type" = "application/json" }
$url = $env:COOLIFY_API_URL + "/api/v1/applications/g40o0os008wc8sgoog84w48c/restart"
try {
    $result = Invoke-RestMethod -Uri $url -Headers $h -Method POST
    Write-Host "[OK] Restart/Deploy iniciado" -ForegroundColor Green
    $result | ConvertTo-Json
} catch {
    Write-Host "[FAIL restart] Intentando start..." -ForegroundColor Yellow
    $url2 = $env:COOLIFY_API_URL + "/api/v1/applications/g40o0os008wc8sgoog84w48c/start"
    $result2 = Invoke-RestMethod -Uri $url2 -Headers $h -Method POST
    Write-Host "[OK] Start iniciado" -ForegroundColor Green
    $result2 | ConvertTo-Json
}
