$content = Get-Content 'scratch/real_nh40_route.json' -Raw | ConvertFrom-Json
Write-Host "Count: $($content.Count)"

# Downsample slightly to ~150 smooth curve points (taking every 5th point plus first and last)
# or keep all points. 742 points is very fast in Leaflet polyline!
$latlngs = @()
foreach ($pt in $content) {
    $lat = [math]::Round([double]$pt[1], 5)
    $lng = [math]::Round([double]$pt[0], 5)
    $latlngs += "[$lat, $lng]"
}

$outputJs = "const NH40_HIGHWAY_ROUTE = [" + ($latlngs -join ", ") + "];"
Set-Content -Path "scratch/nh40_latlngs.js" -Value $outputJs
Write-Host "Wrote scratch/nh40_latlngs.js with $($latlngs.Count) points"
