$port = 8080
$connections = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
foreach ($conn in $connections) {
  if ($conn.OwningProcess -and $conn.OwningProcess -ne 0) {
    Write-Host "Stopping existing server on port $port (PID $($conn.OwningProcess))..."
    Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
  }
}

Set-Location $PSScriptRoot
Write-Host "Starting server at http://localhost:$port"
python -m http.server $port
