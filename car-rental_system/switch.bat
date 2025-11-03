@echo off
set BRANCH=%1
echo Closing VS Code...
taskkill /f /im Code.exe >nul 2>&1
echo Cleaning Git locks...
del /f .git\index.lock >nul 2>&1
git reset --hard >nul 2>&1
echo Switching to %BRANCH%...
git checkout %BRANCH%
echo Done!