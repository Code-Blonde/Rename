@echo off
chcp 65001 >nul
REM Дважды щёлкните по этому файлу, чтобы открыть программу.
REM Сначала пробуем py, затем python.

cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
    py rename_zalif.py
    goto :eof
)

where python >nul 2>nul
if %errorlevel%==0 (
    python rename_zalif.py
    goto :eof
)

echo.
echo Python пока не установлен.
echo Установите его с сайта https://www.python.org/downloads/
echo и при установке поставьте галочку "Add python.exe to PATH".
echo.
pause
