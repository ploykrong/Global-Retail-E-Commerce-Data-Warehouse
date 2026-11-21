Write-Host "Global Retail Data Warehouse & Executive Dashboard" -ForegroundColor Green
Write-Host "Launching Dashboard at http://localhost:8501 ..." -ForegroundColor Magenta

Set-Location $PSScriptRoot
& "$PSScriptRoot\env\Scripts\python.exe" -m streamlit run "$PSScriptRoot\dashboard\app.py" --server.port=8501 --server.address=localhost
