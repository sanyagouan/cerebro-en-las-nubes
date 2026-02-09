$h = @{ Authorization = "Bearer $env:COOLIFY_API_TOKEN"; Accept = "application/json" }
$url = $env:COOLIFY_API_URL + "/api/v1/deployments"
$result = Invoke-RestMethod -Uri $url -Headers $h
Write-Host "Type: $($result.GetType().Name)"
Write-Host "Count: $($result.Count)"
if ($result -is [array]) {
    foreach ($d in $result[0..2]) {
        Write-Host "---"
        Write-Host "UUID: $($d.deployment_uuid)"
        Write-Host "Status: $($d.status)"
        Write-Host "App: $($d.application_name)"
        Write-Host "Created: $($d.created_at)"
    }
} else {
    Write-Host ($result | ConvertTo-Json -Depth 2)
}
