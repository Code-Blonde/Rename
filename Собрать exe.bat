@echo off
chcp 65001 >nul
REM Запустите один раз на компьютере с Windows, чтобы собрать
REM отдельную программу "Помощник переименования.exe", которую можно
REM запускать БЕЗ установки Python.
REM Готовая программа появится в папке "dist".

cd /d "%~dp0"

echo Установка инструмента сборки (PyInstaller)...
py -m pip install --upgrade pyinstaller
if %errorlevel% neq 0 (
    python -m pip install --upgrade pyinstaller
)

echo.
echo Сборка программы ...
py -m PyInstaller --noconfirm --onefile --windowed --name "Помощник переименования" rename_zalif.py
if %errorlevel% neq 0 (
    python -m PyInstaller --noconfirm --onefile --windowed --name "Помощник переименования" rename_zalif.py
)

echo.
echo Готово. Загляните в папку "dist" - там файл "Помощник переименования.exe".
echo Этот один файл можно скопировать на компьютер отца.
pause
