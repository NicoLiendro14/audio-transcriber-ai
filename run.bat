@echo off

set venv_dir=.venv
set main_file=main_refactored.py

echo Intentando activar el entorno virtual...
call %venv_dir%\Scripts\activate

if not exist %venv_dir% (
    echo Creando entorno virtual...
    python -m venv %venv_dir%
    
    echo Activando el entorno virtual...
    call %venv_dir%\Scripts\activate
    
    echo Instalando dependencias...
    pip install -r requirements.txt
)

if %errorlevel% neq 0 (
    goto error
)

echo Ejecutando %main_file%...
python %main_file%

if %errorlevel% neq 0 (
    goto error
)

echo Cerrando el entorno virtual...
deactivate

echo Presiona cualquier tecla para salir...
pause >nul
goto :eof

:error
echo Ha ocurrido un error. Presiona cualquier tecla para salir...
pause >nul
