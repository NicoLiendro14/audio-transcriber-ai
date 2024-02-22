# Obtener la ruta del script actual
$scriptPath = $PSScriptRoot

# Construir la ruta completa del archivo de salida
$outFile = Join-Path -Path $scriptPath -ChildPath 'python-3.10.0-amd64.exe'

# Descargar el archivo ejecutable de Python
Invoke-WebRequest -UseBasicParsing -Uri 'https://www.python.org/ftp/python/3.10.0/python-3.10.0-amd64.exe' -OutFile $outFile

# Instalar Python a través del símbolo del sistema
& $outFile /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

# Establecer la ubicación de Python
$pythonPath = 'C:\Program Files\Python310'
setx /M PATH "$env:PATH;$pythonPath"

$env:PATH = "$env:PATH;$pythonPath"

# Eliminar el archivo descargado
Remove-Item -Path $outFile -Force
