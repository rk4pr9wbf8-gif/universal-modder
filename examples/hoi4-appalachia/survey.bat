@echo off
rem Reads your Cold War mod and writes base_mod_report.txt for the agent.
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 survey_base_mod.py %*
) else (
  python survey_base_mod.py %*
)
pause
