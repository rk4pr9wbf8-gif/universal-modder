@echo off
rem Reads the unmodded game and writes base_mod_report.txt for the agent (for the Cold War world).
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 survey_base_mod.py --vanilla %*
) else (
  python survey_base_mod.py --vanilla %*
)
pause
