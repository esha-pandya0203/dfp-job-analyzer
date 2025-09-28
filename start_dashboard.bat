@echo off
echo Starting Pennsylvania Employment Dashboard...
echo.

REM Change to the project directory
cd /d "%~dp0"

REM Check if virtual environment exists
if exist ".venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
) else (
    echo No virtual environment found, using system Python...
)

REM Launch the dashboard
echo Launching Streamlit dashboard...
streamlit run app.py

pause