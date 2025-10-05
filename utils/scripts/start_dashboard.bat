@echo off
echo Starting Pennsylvania Employment Dashboard...
echo ================================================

REM Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    echo Please create a virtual environment first:
    echo   python -m venv .venv
    echo   .venv\Scripts\activate
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)

REM Activate virtual environment and run Streamlit
echo [INFO] Using virtual environment...
.venv\Scripts\python.exe -m streamlit run app.py --server.port 8501 --server.address localhost

pause
