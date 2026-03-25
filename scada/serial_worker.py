import queue
import threading
from typing import Optional

import serial
from serial import SerialException
from serial.tools import list_ports


class SerialWorker:
    """Manages non-blocking serial communication with a background thread."""

    def __init__(self, baudrate: int = 115200, timeout: float = 0.2) -> None:
        self.baudrate = baudrate
        self.timeout = timeout
        self._serial: Optional[serial.Serial] = None
        self._stop_event = threading.Event()
        self._reader_thread: Optional[threading.Thread] = None
        self._rx_queue: "queue.Queue[str]" = queue.Queue()
        self._tx_lock = threading.Lock()

    @staticmethod
    def list_available_ports() -> list[str]:
        return [port.device for port in list_ports.comports()]

    @property
    def is_connected(self) -> bool:
        return self._serial is not None and self._serial.is_open

    def connect(self, port: str) -> None:
        if self.is_connected:
            return

        self._serial = serial.Serial(port=port, baudrate=self.baudrate, timeout=self.timeout)
        self._stop_event.clear()
        self._reader_thread = threading.Thread(target=self._read_loop, daemon=True)
        self._reader_thread.start()

    def disconnect(self) -> None:
        self._stop_event.set()

        if self._reader_thread and self._reader_thread.is_alive():
            self._reader_thread.join(timeout=1.0)

        if self._serial:
            try:
                if self._serial.is_open:
                    self._serial.close()
            finally:
                self._serial = None

    def send(self, command: str) -> None:
        if not self.is_connected or not self._serial:
            raise SerialException("Serial port is not connected")

        payload = command if command.endswith("\n") else f"{command}\n"
        with self._tx_lock:
            self._serial.write(payload.encode("ascii", errors="ignore"))

    def get_message_nowait(self) -> Optional[str]:
        try:
            return self._rx_queue.get_nowait()
        except queue.Empty:
            return None

    def _read_loop(self) -> None:
        while not self._stop_event.is_set():
            if not self._serial or not self._serial.is_open:
                break

            try:
                raw = self._serial.readline()
                if not raw:
                    continue

                text = raw.decode("ascii", errors="ignore").strip()
                if text:
                    self._rx_queue.put(text)
            except SerialException:
                break
            except OSError:
                break

        self._stop_event.set()
