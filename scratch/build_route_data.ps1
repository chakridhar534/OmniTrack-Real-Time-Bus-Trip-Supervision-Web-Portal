$coordsJs = Get-Content 'scratch/nh40_latlngs.js' -Raw
$waypointsJson = Get-Content 'scratch/snapped_waypoints.json' -Raw

$content = @"
/* ========================================================
   OmniTrack — NH 40 Highway Route Geometry (Kurnool to RGMCET Nandyal)
   Contains exact 742 road-snapped coordinates and 16 bus stops
   ======================================================== */

$coordsJs

const NH40_WAYPOINTS = $waypointsJson;

if (typeof window !== 'undefined') {
  window.NH40_HIGHWAY_ROUTE = NH40_HIGHWAY_ROUTE;
  window.NH40_WAYPOINTS = NH40_WAYPOINTS;
}
"@

Set-Content -Path "js/route-data.js" -Value $content
Write-Host "Wrote js/route-data.js successfully!"
