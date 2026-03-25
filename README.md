# SCADA Cinta Transportadora (CustomTkinter + MSP430)

Interfaz SCADA en Python para supervisar y controlar una cinta transportadora industrial mediante comunicacion USB-Serial (UART) con un MSP430 a 115200 baudios.

## Funcionalidades

- Control de movimiento:
  - Boton `Avanzar` con velocidad configurable en cm/s.
  - Envio de comando al MSP430 con formato `V<valor_d10>` (decimas de cm/s).
  - Boton `Parada de Emergencia` con envio inmediato del comando `S`.
- Visualizacion de estado:
  - LED virtual de sensor:
    - Rojo para `DET:1` (objeto detectado).
    - Verde para `DET:0` (despejado).
  - Barra de progreso y etiqueta numerica para velocidad actual de cinta.
- Registro de datos:
  - Caja de log con marcas de tiempo para eventos y tramas recibidas.
- Conectividad:
  - Selector de puerto serial.
  - Boton `Actualizar` para refrescar puertos.
  - Boton `Conectar/Desconectar`.
- Comunicacion no bloqueante:
  - Lectura serial en hilo dedicado (`threading`) para no congelar la interfaz.

## Estructura del proyecto

- `main.py`: punto de entrada.
- `scada/ui.py`: interfaz grafica y logica de supervision/control.
- `scada/serial_worker.py`: gestion de conexion UART y lectura en segundo plano.
- `scada_config.ini`: configuracion de baudios y protocolo.
- `requirements.txt`: dependencias Python.

## Requisitos previos

- Python 3.10 o superior.
- Sistema con acceso al puerto USB-Serial del MSP430.
- En Linux, permiso para usar puertos seriales (ejemplo: grupo `dialout`).

## Crear entorno virtual (venv)

En la carpeta del proyecto:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Ejecucion

Con el entorno virtual activo:

```bash
python main.py
```

En Windows, puedes usar el script automatizado desde la carpeta del proyecto:

```bat
setup_and_run_windows.bat
```

Este script crea `.venv` (si no existe), instala dependencias y ejecuta la aplicacion.

## Protocolo de comunicacion

- PC -> MSP430 (comandos salientes):
  - `V<valor_d10>` para establecer velocidad en decimas de cm/s.
  - Ejemplos: `V75` (7.5 cm/s), `V100` (10.0 cm/s).
  - `S` para detener la cinta.
- MSP430 -> PC (mensajes entrantes, terminados en `\n`):
  - `DET:1` objeto detectado.
  - `DET:0` zona despejada.
  - `VEL:<valor_d10>` para reportar velocidad en decimas de cm/s.
  - Ejemplos: `VEL:75`, `VEL:0`.

## Configuracion por archivo INI

La app carga parametros desde `scada_config.ini`:

```ini
[serial]
baudrate = 115200
timeout = 0.2

[protocol]
max_speed_d10 = 100
```

- `baudrate`: velocidad UART usada al conectar.
- `timeout`: timeout de lectura serial.
- `max_speed_d10`: limite de velocidad en decimas (100 = 10.0 cm/s).

## Consideraciones de hardware

- Motor DC 24V accionado por puente H L293D.
- Sensor fotoelectrico GT-442N3 leido por polling en el MSP430.
- Verificar jumpers RXD/TXD en la placa MSP430 antes de conectar por UART.
- Baudrate esperado: 115200.

## Solucion de problemas

- Si no aparece el puerto serial:
  - Presiona `Actualizar`.
  - Verifica cable USB y drivers del adaptador USB-Serial.
  - Revisa permisos de usuario para puertos seriales.
- Si no conecta:
  - Comprueba que otra aplicacion no este usando el mismo puerto.
  - Revisa que el MSP430 este configurado a 115200 baudios.
  - Confirma jumpers RXD/TXD correctos.
- Si no llegan eventos `DET`:
  - Verifica firmware del MSP430 y formato de tramas con `\n` al final.

## Preparar en otro ordenador

1. Copia la carpeta del proyecto.
2. Instala Python 3.10+.
3. En Windows: haz doble clic en `setup_and_run_windows.bat`.
4. Espera a que termine la instalacion y se abra la interfaz.
5. Conecta el MSP430 y selecciona el puerto en la interfaz.
