# PowerShell script to start Pennsylvania Employment Dashboard
Write-Host "Starting Pennsylvania Employment Dashboard..." -ForegroundColor Green
Write-Host ""

# Change to the script directory
Set-Location $PSScriptRoot

# Check if virtual environment exists
if (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & .venv\Scripts\Activate.ps1
} else {
    Write-Host "No virtual environment found, using system Python..." -ForegroundColor Yellow
}

# Launch the dashboard
Write-Host "Launching Streamlit dashboard..." -ForegroundColor Green
streamlit run app.py