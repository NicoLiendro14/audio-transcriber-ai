# Proyecto de Transcripción de Audio en Tiempo Real 👂📝

Este proyecto consiste en un sistema de transcripción de audio en tiempo real utilizando Whisper y websockets. El objetivo principal es permitir la transcripción automática de el audio de salida del sistema.

## Requisitos ⚙️

- Python 3.8 o superior.
- Windows 10.

## Instalación 🛠️

1. Clona este repositorio en tu máquina local.
2. Asegúrate de tener Python instalado en tu sistema.
3. Crea un entorno virtual:
```shell
python -m venv venv 
```

4. Instala las dependencias del proyecto ejecutando el siguiente comando en la terminal:

```shell
venv/Scripts/activate && pip install -r requirements.txt
```

## Ejecucion directa.

Para probar directamente la app se puede ejecutar el archivo **run.bat**

## Configuración ⚙️

Puedes personalizar la configuración del transcriptor de audio modificando los siguientes parámetros en el archivo main.py:

- model_size: El tamaño del modelo Whisper a utilizar.
- device: El dispositivo de cómputo a utilizar ("cpu" o "cuda").
- phrase_timeout: El tiempo máximo en segundos para considerar una frase completa.
- record_timeout: El tiempo máximo en segundos para cada grabación de audio.

## Issues y cosas a mejorar 📝
- Separar la ejecucion del script con la instalacion total. En la primera instancia que se ejecuta el script se instalan todas las dependencias y ademas se baja el modelo de Whisper a utilizar. Se debe separar la instalacion de las dependencias y el modelo de la ejecucion del script.
- Cuando en el front tarda en mostrar las lineas de texto se saltea muchas partes de el audio que escucha. Pareciera ser que es mas comun cuando hay un cambio de voces. Probar con el siguiente ejemplo: https://www.youtube.com/watch?v=TzutZgU83Ds
- Cuando el script escucha musica tambien tiene problemas.

## Features a agregar 🛠️
- Opcion para que siempre se mantenga por encima de todas las vetanas.
- Historial de la transcripcion.