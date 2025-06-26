@echo off
REM === Ustawienia ===
set "PROJECT_DIR=%~dp0"
set "VENV_DIR=%PROJECT_DIR%\.venv"
set "PYTHON_EXE=%VENV_DIR%\Scripts\python.exe"
set "REQUIREMENTS=%PROJECT_DIR%\requirements.txt"

echo Sprawdzam środowisko wirtualne...

IF EXIST "%PYTHON_EXE%" (
    echo Środowisko .venv już istnieje.
) ELSE (
    echo Tworzenie środowiska .venv...
    python -m venv "%VENV_DIR%"
    IF ERRORLEVEL 1 (
        echo Błąd: Nie można utworzyć środowiska wirtualnego.
        pause
        exit /b 1
    )
)

echo Aktywuję środowisko i instaluję zależności...
call "%VENV_DIR%\Scripts\activate.bat"
"%PYTHON_EXE%" -m pip install --upgrade pip

IF EXIST "%REQUIREMENTS%" (
    "%PYTHON_EXE%" -m pip install -r "%REQUIREMENTS%"
) ELSE (
    echo Uwaga: Nie znaleziono pliku requirements.txt
)

echo Uruchamiam PyCharma...
where /q pycharm64.exe && start pycharm64.exe "%PROJECT_DIR%" || echo Uwaga: Nie znaleziono PyCharma w PATH.

echo Gotowe!
pause
