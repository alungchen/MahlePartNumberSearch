@echo off
setlocal

cd /d "%~dp0"

REM If server is already running, just open browser.
python -c "import urllib.request,sys; urllib.request.urlopen('http://127.0.0.1:8000/', timeout=2); sys.exit(0)" >nul 2>&1
if %errorlevel%==0 (
    start "" "http://127.0.0.1:8000"
    echo Web server is already running. Browser opened.
    goto :eof
)

REM Start server in a new terminal window.
start "Mahle Web Server" cmd /k "cd /d ""%~dp0"" && python web_app.py"

REM Wait a moment for server startup, then open browser.
timeout /t 3 /nobreak >nul
start "" "http://127.0.0.1:8000"

echo Web server started (or starting). Browser opened.
