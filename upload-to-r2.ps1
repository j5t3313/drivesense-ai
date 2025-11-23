$bucket = "drivesense-telemetry"
$localPath = "processed_data/indianapolis"

Get-ChildItem -Path $localPath -Recurse -File | ForEach-Object {
    $relativePath = "processed_data/indianapolis/" + $_.Name
    Write-Host "Uploading: $relativePath"
    wrangler r2 object put "$bucket/$relativePath" --file="$($_.FullName)"
}