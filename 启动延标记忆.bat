@echo off
cd /d "%~dp0"
start "" web_server.exe
timeout /t 3 /nobreak >nul
start http://127.0.0.1:8000/static/index.html
