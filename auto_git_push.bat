@echo off
echo 🚀 Auto Git Push - %date% %time%
echo.

cd /d "%~dp0"

python auto_git_push.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Auto Git Push completed successfully!
) else (
    echo.
    echo ❌ Auto Git Push failed!
)

echo.
pause
