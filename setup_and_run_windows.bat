@echo off
setlocal EnableExtensions

cd /d "%~dp0"

echo ==========================================
echo   SCADA - Instalacion y Ejecucion Windows
echo ==========================================

if not exist "requirements.txt" (
    echo [ERROR] No se encontro requirements.txt en la carpeta actual.
    goto :fail
)

set "PY_CMD="
where py >nul 2>&1
if %ERRORLEVEL%==0 (
    set "PY_CMD=py -3"
) else (
    where python >nul 2>&1
    if %ERRORLEVEL%==0 (
        set "PY_CMD=python"
    )
)

if "%PY_CMD%"=="" (
    echo [ERROR] Python no esta instalado o no esta en PATH.
    echo Instala Python 3.10+ desde https://www.python.org/downloads/windows/
    goto :fail
)

echo [INFO] Usando: %PY_CMD%

if not exist ".venv\Scripts\python.exe" (
    echo [INFO] Creando entorno virtual...
    %PY_CMD% -m venv .venv
    if not %ERRORLEVEL%==0 (
        echo [ERROR] No se pudo crear el entorno virtual.
        goto :fail
    )
)

echo [INFO] Activando entorno virtual...
call ".venv\Scripts\activate.bat"
if not %ERRORLEVEL%==0 (
    echo [ERROR] No se pudo activar el entorno virtual.
    goto :fail
)

echo [INFO] Actualizando pip...
python -m pip install --upgrade pip
if not %ERRORLEVEL%==0 (
    echo [ERROR] Fallo al actualizar pip.
    goto :fail
)

echo [INFO] Instalando dependencias...
python -m pip install -r requirements.txt
if not %ERRORLEVEL%==0 (
    echo [ERROR] Fallo al instalar dependencias.
    goto :fail
)

echo [INFO] Iniciando aplicacion SCADA...
python main.py
set "APP_EXIT=%ERRORLEVEL%"

if not "%APP_EXIT%"=="0" (
    echo [WARN] La aplicacion termino con codigo %APP_EXIT%.
)

goto :end

:fail
echo.
echo Proceso terminado con errores.
set "APP_EXIT=1"

:end
echo.
pause
exit /b %APP_EXIT%
