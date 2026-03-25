# SCADA Cinta Transportadora (CustomTkinter + MSP430)

Interfaz SCADA en Python para supervisar y controlar una cinta transportadora industrial mediante comunicacion USB-Serial (UART) con un MSP430 a 9600 baudios.

## Funcionalidades

- Control de movimiento:
  - Boton `Avanzar` con velocidad configurable en cm/s.
  - Envio de comando al MSP430 con formato `V<valor>`.
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

## Protocolo de comunicacion

- PC -> MSP430 (comandos salientes):
  - `V<valor>` para establecer velocidad.
  - `S` para detener la cinta.
- MSP430 -> PC (mensajes entrantes, terminados en `\n`):
  - `DET:1` objeto detectado.
  - `DET:0` zona despejada.
  - Opcional: `VEL:<valor>` para reportar velocidad medida.

## Consideraciones de hardware

- Motor DC 24V accionado por puente H L293D.
- Sensor fotoelectrico GT-442N3 leido por polling en el MSP430.
- Verificar jumpers RXD/TXD en la placa MSP430 antes de conectar por UART.
- Baudrate esperado: 9600.

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
3. Crea y activa `venv`.
4. Instala dependencias con `pip install -r requirements.txt`.
5. Ejecuta `python main.py`.
6. Conecta el MSP430 y selecciona el puerto en la interfaz.
