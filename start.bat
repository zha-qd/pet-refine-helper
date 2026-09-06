@echo off
setlocal
cd /d "%~dp0"
set "PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK=True"
if exist "%~dp0runtime\pythonw.exe" (
    set "TCL_LIBRARY=%~dp0runtime\tcl\tcl8.6"
    set "TK_LIBRARY=%~dp0runtime\tcl\tk8.6"
    start "" "%~dp0runtime\pythonw.exe" "%~dp0bootstrap.py"
    exit /b
)
if exist "%~dp0.venv\Scripts\pythonw.exe" (
    start "" "%~dp0.venv\Scripts\pythonw.exe" "%~dp0bootstrap.py"
    exit /b
)
echo Runtime not found. Download and extract the Windows portable release,
echo or create a Python 3.10 venv and install requirements.txt. See README.md.
pause
