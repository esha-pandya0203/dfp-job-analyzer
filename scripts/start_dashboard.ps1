# Pennsylvania Employment Dashboard Launcher (PowerShell)
Write-Host "Starting Pennsylvania Employment Dashboard..." -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green

# Check if virtual environment exists
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "[ERROR] Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please create a virtual environment first:" -ForegroundColor Yellow
    Write-Host "  python -m venv .venv" -ForegroundColor Cyan
    Write-Host "  .venv\Scripts\activate" -ForegroundColor Cyan
    Write-Host "  pip install -r requirements.txt" -ForegroundColor Cyan
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if app.py exists
if (-not (Test-Path "app.py")) {
    Write-Host "[ERROR] app.py not found!" -ForegroundColor Red
    Write-Host "Please make sure you're in the correct directory." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if data files exist
if (-not (Test-Path "data\raw_data_project\pennsylvania_all_occupations_20250927_201529.csv")) {
    Write-Host "[WARNING] Data files not found!" -ForegroundColor Yellow
    Write-Host "The dashboard may not work properly without data files." -ForegroundColor Yellow
}

Write-Host "[INFO] Using virtual environment..." -ForegroundColor Cyan
Write-Host "[INFO] Starting Streamlit dashboard..." -ForegroundColor Cyan
Write-Host "[INFO] The dashboard will open at: http://localhost:8501" -ForegroundColor Green
Write-Host ""

# Start Streamlit
try {
    & ".venv\Scripts\python.exe" -m streamlit run app.py --server.port 8501 --server.address localhost
}
catch {
    Write-Host "[ERROR] Failed to start dashboard: $_" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
