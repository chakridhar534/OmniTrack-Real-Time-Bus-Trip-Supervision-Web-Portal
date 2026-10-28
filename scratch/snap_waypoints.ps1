$points = Get-Content 'scratch/real_nh40_route.json' -Raw | ConvertFrom-Json

$waypoints = @(
  @{ name = "KondaReddy Fort (Kurnool)"; lat = 15.8281; lng = 78.0373; time = "07:30 AM"; etaSec = 360 },
  @{ name = "Control Room & Rajvihar"; lat = 15.8235; lng = 78.0425; time = "07:38 AM"; etaSec = 540 },
  @{ name = "Sv Complex & Station Road"; lat = 15.8190; lng = 78.0490; time = "07:44 AM"; etaSec = 720 },
  @{ name = "Medical College & C Camp"; lat = 15.8115; lng = 78.0610; time = "07:52 AM"; etaSec = 900 },
  @{ name = "Nandyal Checkpost"; lat = 15.7980; lng = 78.0820; time = "08:00 AM"; etaSec = 1100 },
  @{ name = "G. Pullareddy Engg College"; lat = 15.7830; lng = 78.1065; time = "08:08 AM"; etaSec = 1300 },
  @{ name = "B. Thandrapadu Junction"; lat = 15.7650; lng = 78.1320; time = "08:15 AM"; etaSec = 1500 },
  @{ name = "Raaga Mayuri Highway Resorts"; lat = 15.7480; lng = 78.1580; time = "08:22 AM"; etaSec = 1750 },
  @{ name = "NH 40 Orvakal Rock Garden"; lat = 15.7120; lng = 78.2150; time = "08:32 AM"; etaSec = 2100 },
  @{ name = "Nannur Bus Stop"; lat = 15.6880; lng = 78.2520; time = "08:42 AM"; etaSec = 2500 },
  @{ name = "Gutupalli Tollway (NH 40)"; lat = 15.6650; lng = 78.2850; time = "08:50 AM"; etaSec = 2900 },
  @{ name = "Hussainapuram Junction"; lat = 15.6380; lng = 78.3180; time = "08:58 AM"; etaSec = 3300 },
  @{ name = "Kalvabugga Milestone"; lat = 15.6050; lng = 78.3520; time = "09:08 AM"; etaSec = 3800 },
  @{ name = "Panyam Bypass (NH 40)"; lat = 15.5350; lng = 78.4320; time = "09:22 AM"; etaSec = 4400 },
  @{ name = "Santiram Hospital & Medical College"; lat = 15.5080; lng = 78.4620; time = "09:32 AM"; etaSec = 4900 },
  @{ name = "RGM College (RGMCET) Campus"; lat = 15.4858; lng = 78.4839; time = "09:45 AM"; etaSec = 0 }
)

$snapped = @()
for ($i = 0; $i -lt $waypoints.Count; $i++) {
    $wp = $waypoints[$i]
    if ($i -eq 0) {
        $pt = $points[0]
        $snapped += [PSCustomObject]@{ name = $wp.name; lat = [math]::Round([double]$pt[1], 5); lng = [math]::Round([double]$pt[0], 5); time = $wp.time; etaSec = $wp.etaSec }
        continue
    }
    if ($i -eq ($waypoints.Count - 1)) {
        $pt = $points[-1]
        $snapped += [PSCustomObject]@{ name = $wp.name; lat = [math]::Round([double]$pt[1], 5); lng = [math]::Round([double]$pt[0], 5); time = $wp.time; etaSec = $wp.etaSec }
        continue
    }

    $bestDist = 999999999
    $bestPt = $null
    foreach ($pt in $points) {
        $dLat = [double]$pt[1] - $wp.lat
        $dLng = [double]$pt[0] - $wp.lng
        $dist = ($dLat * $dLat) + ($dLng * $dLng)
        if ($dist -lt $bestDist) {
            $bestDist = $dist
            $bestPt = $pt
        }
    }
    $snapped += [PSCustomObject]@{ name = $wp.name; lat = [math]::Round([double]$bestPt[1], 5); lng = [math]::Round([double]$bestPt[0], 5); time = $wp.time; etaSec = $wp.etaSec }
}

$snappedJson = $snapped | ConvertTo-Json -Depth 4
Set-Content -Path "scratch/snapped_waypoints.json" -Value $snappedJson
Write-Host "Saved snapped waypoints!"
