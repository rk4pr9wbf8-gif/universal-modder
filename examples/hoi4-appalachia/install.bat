@echo off
rem Builds The Veiled Hollows into Documents\Paradox Interactive\Hearts of Iron IV\mod.
rem Needs Python 3 (https://www.python.org/downloads/ or "python" from the Microsoft Store).
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 build_mod.py %*
) else (
  python build_mod.py %*
)
pause
