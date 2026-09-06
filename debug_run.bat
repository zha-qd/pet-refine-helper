@echo off
setlocal
cd /d "%~dp0"
set "TCL_LIBRARY=%~dp0runtime\tcl\tcl8.6"
set "TK_LIBRARY=%~dp0runtime\tcl\tk8.6"
if exist "%~dp0runtime\python.exe" (
    "%~dp0runtime\python.exe" "%~dp0auto_refine_gui.py"
) else (
    "%~dp0.venv\Scripts\python.exe" "%~dp0auto_refine_gui.py"
)
pause
