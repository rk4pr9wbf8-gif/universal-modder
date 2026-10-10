@echo off
rem Builds The Veiled Hollows for vanilla 1936, even if a Cold War mod is subscribed.
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 build_mod.py --base none %*
) else (
  python build_mod.py --base none %*
)
pause
