@echo off
cd /d "C:\Users\kis\obsidian-vault"
git pull origin main
timeout /t 300 /nobreak >nul
goto :start
