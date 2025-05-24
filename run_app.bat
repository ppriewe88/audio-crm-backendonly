REM execute this script from power shell by executing the following line
REM Start-Process -FilePath "C:\Users\pprie\OneDrive\Dokumente\Python_Projekte\9_localrag\easy-local-rag-backendonly\run_app.bat"

@echo off
REM path to virtual environment. ADAPT TO YOUR LOCAL ENVIRONMENT!
set VENV_DIR=C:\Users\pprie\OneDrive\Dokumente\Python_Projekte\9_localrag\easy-local-rag-backendonly\

REM 1.1 activate virtual environment
call "%VENV_DIR%venv\Scripts\activate.bat"
echo [%time%] starting virtual environment ...
if errorlevel 1 (
    echo [ERROR] starting virtual environment: FAILURE
    timeout /t 5 >nul
    exit /b 1
)

REM 1.2. confirmation and short sleeping time
echo [%time%] virtual environment running...
timeout /t 5 >nul

@REM REM 2.1. start api server in background (venv context)
@echo off
REM configuration 
set SCRIPT_DIR=%VENV_DIR%\src
set PY_EXE=%VENV_DIR%\venv\Scripts\python.exe
set SCRIPT=localrag_api.py
REM start in background
cd /d "%SCRIPT_DIR%"
echo [%time%] starting API server on http://127.0.0.1:8000...
start "" "%PY_EXE%" "%SCRIPT%"

REM 2.2. confirmation and short sleeping time
echo [%time%] API-Server running on http://127.0.0.1:8000!
timeout /t 5 >nul