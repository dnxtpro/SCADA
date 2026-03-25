# SCADA Cinta Transportadora (Python + CustomTkinter)

Interfaz SCADA para supervisar y controlar una cinta transportadora con MSP430 por UART (USB-Serial).

La aplicacion esta escrita en Python y usa:

- `customtkinter` para la interfaz.
- `pyserial` para comunicacion serie no bloqueante.

## Indice

- [Estado actual del sistema](#estado-actual-del-sistema)
- [Funcionalidades de la interfaz](#funcionalidades-de-la-interfaz)
- [Protocolo serial (compatible con tu firmware)](#protocolo-serial-compatible-con-tu-firmware)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Descargar la aplicacion](#descargar-la-aplicacion)
- [Requisitos previos](#requisitos-previos)
- [Instalacion y ejecucion](#instalacion-y-ejecucion)
- [Configuracion (`scada_config.ini`)](#configuracion-scada_configini)
- [Uso rapido](#uso-rapido)
- [Solucion de problemas](#solucion-de-problemas)

## Estado actual del sistema

- UART configurada por defecto a **115200 baudios**.
- Lectura serie en segundo plano con hilo dedicado (la interfaz no se bloquea).
- Entrada de velocidad en **cm/s** en la UI, pero envio al firmware en **decimas de cm/s**.

Ejemplo:

- Si escribes `7.5` en la UI, se envia `V75`.

## Funcionalidades de la interfaz

- Seleccion de puerto serial y boton de `Conectar/Desconectar`.
- Boton `Actualizar` para refrescar puertos.
- Boton `Avanzar` con velocidad ingresada por el usuario.
- Boton `Parada de Emergencia` (envia `S`).
- LED virtual de sensor:
  - Rojo cuando llega `DET:1`.
  - Verde cuando llega `DET:0`.
- Indicador de velocidad:
  - valor en cm/s,
  - porcentaje,
  - barra de progreso.
- Registro de eventos con timestamp y boton `Limpiar`.

## Protocolo serial (compatible con tu firmware)

Todos los mensajes son ASCII y terminan en salto de linea `\n`.

### PC -> MSP430

- `V<valor_d10>`
  - `valor_d10` en decimas de cm/s.
  - Ejemplos: `V75`, `V100`, `V0`.
- `S`
  - Stop inmediato.

### MSP430 -> PC

- `DET:1` objeto detectado.
- `DET:0` sensor despejado.
- `VEL:<valor_d10>`
  - Ejemplos: `VEL:75`, `VEL:0`.

Notas:

- La UI convierte `VEL:75` a `7.5 cm/s` para mostrarlo.
- Si llega una trama no reconocida, se registra como `RX: ...` en el log.

## Estructura del proyecto

- `main.py`: punto de entrada.
- `scada/ui.py`: interfaz y logica de control.
- `scada/serial_worker.py`: capa serial con hilo lector.
- `scada_config.ini`: configuracion editable.
- `requirements.txt`: dependencias Python.
- `setup_and_run_windows.bat`: instalacion + ejecucion automatica en Windows.
- `setup_and_run_linux.sh`: instalacion + ejecucion automatica en Linux.
- `setup_and_run_mac.sh`: instalacion + ejecucion automatica en macOS.

## Descargar la aplicacion

Puedes hacerlo de dos formas.

### Opcion 1: Descargar ZIP (recomendada para usuarios no tecnicos)

1. Abre el repositorio en GitHub.
2. Pulsa `Code` -> `Download ZIP`.
3. Extrae el ZIP en una carpeta local, por ejemplo `C:\SCADA` o `~/SCADA`.
4. Abre una terminal dentro de esa carpeta.

### Opcion 2: Clonar con Git

```bash
git clone <URL_DEL_REPOSITORIO>
cd SCADA
```

## Requisitos previos

- Python 3.10 o superior.
- Acceso al puerto USB-Serial del MSP430.
- En Linux, permisos de usuario sobre puertos serie (por ejemplo grupo `dialout`).

## Instalacion y ejecucion

### Windows (automatico)

En la carpeta del proyecto, ejecuta:

```bat
setup_and_run_windows.bat
```

Ese script realiza automaticamente:

1. Detecta Python (`py -3` o `python`).
2. Crea `.venv` si no existe.
3. Activa entorno virtual.
4. Actualiza `pip`.
5. Instala dependencias.
6. Inicia `main.py`.

### Linux (automatico)

En la carpeta del proyecto, ejecuta:

```bash
chmod +x setup_and_run_linux.sh
./setup_and_run_linux.sh
```

### macOS (automatico)

En la carpeta del proyecto, ejecuta:

```bash
chmod +x setup_and_run_mac.sh
./setup_and_run_mac.sh
```

### Windows (manual)

```bat
py -3 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

### Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

### macOS (manual)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

## Configuracion (`scada_config.ini`)

Archivo actual:

```ini
[serial]
baudrate = 115200
timeout = 0.2

[protocol]
# Velocidad maxima en decimas de cm/s (100 => 10.0 cm/s)
max_speed_d10 = 100
```

Significado:

- `baudrate`: velocidad UART.
- `timeout`: timeout de lectura serial (segundos).
- `max_speed_d10`: limite maximo de velocidad en decimas de cm/s.

## Uso rapido

1. Conecta el MSP430 por USB.
2. Abre la app.
3. Pulsa `Actualizar` y selecciona el puerto.
4. Pulsa `Conectar`.
5. Ingresa velocidad en cm/s (ejemplo `7.5`) y pulsa `Avanzar`.
6. Usa `Parada de Emergencia` para detener.

## Solucion de problemas

### Error: acceso denegado al puerto (PermissionError 13 en Windows)

Suele indicar que otro programa tiene el puerto abierto.

- Cierra Arduino IDE, monitores serie, PuTTY, TeraTerm, etc.
- Desconecta y reconecta el USB.
- Verifica el COM correcto en Administrador de dispositivos.
- Ejecuta la app una vez como administrador.

### En Linux no veo el puerto

Lista puertos detectados:

```bash
ls /dev/ttyS* /dev/ttyUSB* /dev/ttyACM* 2>/dev/null
```

Ver procesos usando puertos serie:

```bash
sudo lsof | grep -E "/dev/tty(USB|ACM|S)"
```

### No llegan mensajes del sensor

- Revisa jumpers RXD/TXD del MSP430.
- Verifica que el firmware envia lineas terminadas en `\n`.
- Comprueba que ambos lados usan el mismo baudrate (actualmente 115200).
