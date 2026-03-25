from __future__ import annotations

import configparser
import datetime as dt
import tkinter as tk
from tkinter import messagebox
from pathlib import Path

import customtkinter as ctk
from serial import SerialException

from scada.serial_worker import SerialWorker


class ScadaApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        self.config_path = Path(__file__).resolve().parent.parent / "scada_config.ini"
        self.app_config = self._load_config()
        self.serial_baudrate = self.app_config.getint("serial", "baudrate", fallback=115200)
        self.serial_timeout = self.app_config.getfloat("serial", "timeout", fallback=0.2)
        self.max_speed_d10 = self.app_config.getint("protocol", "max_speed_d10", fallback=100)
        self.max_speed = self.max_speed_d10 / 10.0

        self.title("SCADA Cinta Transportadora")
        self.geometry("1040x700")
        self.minsize(860, 560)

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        self.configure(fg_color="#e9eef2")

        self.font_title = ctk.CTkFont(family="Montserrat", size=25, weight="bold")
        self.font_subtitle = ctk.CTkFont(family="Montserrat", size=13)
        self.font_section = ctk.CTkFont(family="Montserrat", size=15, weight="bold")
        self.font_body = ctk.CTkFont(family="Montserrat", size=13)
        self.font_mono = ctk.CTkFont(family="Courier New", size=12)

        self.palette = {
            "card": "#fdfefe",
            "card_border": "#d3dbe3",
            "accent": "#0c7a6c",
            "accent_hover": "#0a6659",
            "danger": "#d32f2f",
            "danger_hover": "#9a1f1f",
            "ok": "#1f7a3d",
            "muted": "#526170",
            "title": "#0f1f2e",
            "surface": "#f4f7fb",
            "surface_dark": "#0f172a",
        }

        self.serial_worker = SerialWorker(baudrate=self.serial_baudrate, timeout=self.serial_timeout)
        self.current_speed = 0.0
        self.last_sensor_state: bool | None = None

        self._build_layout()
        self.refresh_ports()

        self.after(120, self._poll_messages)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _load_config(self) -> configparser.ConfigParser:
        config = configparser.ConfigParser()
        config.read_dict(
            {
                "serial": {
                    "baudrate": "115200",
                    "timeout": "0.2",
                },
                "protocol": {
                    "max_speed_d10": "100",
                },
            }
        )
        config.read(self.config_path, encoding="utf-8")
        return config

    def _build_layout(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 6))
        self.header_frame.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="Centro de Control - Cinta Transportadora",
            font=self.font_title,
            text_color=self.palette["title"],
        )
        self.title_label.grid(row=0, column=0, sticky="w")

        self.subtitle_label = ctk.CTkLabel(
            self.header_frame,
            text="Monitoreo en tiempo real y control por UART (MSP430)",
            font=self.font_subtitle,
            text_color=self.palette["muted"],
        )
        self.subtitle_label.grid(row=1, column=0, sticky="w", pady=(2, 0))

        self.badge_label = ctk.CTkLabel(
            self.header_frame,
            text="SCADA LIVE",
            font=ctk.CTkFont(family="Montserrat", size=11, weight="bold"),
            text_color="#ecfeff",
            fg_color="#155e75",
            corner_radius=10,
            padx=12,
            pady=5,
        )
        self.badge_label.grid(row=0, column=1, rowspan=2, sticky="e")

        self.connection_frame = ctk.CTkFrame(
            self,
            fg_color=self.palette["card"],
            corner_radius=16,
            border_width=1,
            border_color=self.palette["card_border"],
        )
        self.connection_frame.grid(row=1, column=0, sticky="ew", padx=16, pady=(8, 8))
        self.connection_frame.grid_columnconfigure(1, weight=1)

        self.port_label = ctk.CTkLabel(
            self.connection_frame,
            text="Puerto Serial",
            font=self.font_section,
        )
        self.port_label.grid(row=0, column=0, padx=(12, 8), pady=12)

        self.port_combobox = ctk.CTkComboBox(
            self.connection_frame,
            values=["No ports"],
            border_color="#9fb2c7",
            button_color="#2f4f6d",
            button_hover_color="#253f58",
            dropdown_font=self.font_body,
            font=self.font_body,
        )
        self.port_combobox.grid(row=0, column=1, sticky="ew", padx=8, pady=12)

        self.refresh_button = ctk.CTkButton(
            self.connection_frame,
            text="Actualizar",
            width=120,
            command=self.refresh_ports,
            fg_color=self.palette["accent"],
            hover_color=self.palette["accent_hover"],
            font=self.font_body,
            corner_radius=10,
        )
        self.refresh_button.grid(row=0, column=2, padx=8, pady=12)

        self.connect_button = ctk.CTkButton(
            self.connection_frame,
            text="Conectar",
            width=140,
            command=self.toggle_connection,
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            font=self.font_body,
            corner_radius=10,
        )
        self.connect_button.grid(row=0, column=3, padx=(8, 12), pady=12)

        self.connection_state = ctk.CTkLabel(
            self.connection_frame,
            text="Desconectado",
            text_color="#b22222",
            font=ctk.CTkFont(family="Montserrat", size=14, weight="bold"),
        )
        self.connection_state.grid(row=0, column=4, padx=(8, 12), pady=12)

        self.controls_frame = ctk.CTkFrame(
            self,
            fg_color=self.palette["card"],
            corner_radius=16,
            border_width=1,
            border_color=self.palette["card_border"],
        )
        self.controls_frame.grid(row=2, column=0, sticky="ew", padx=16, pady=8)
        self.controls_frame.grid_columnconfigure(0, weight=1)
        self.controls_frame.grid_columnconfigure(1, weight=0)

        self.speed_entry = ctk.CTkEntry(
            self.controls_frame,
            placeholder_text="Velocidad cm/s (ej: 7.5)",
            fg_color=self.palette["surface"],
            border_color="#9fb2c7",
            font=self.font_body,
            corner_radius=10,
        )
        self.speed_entry.grid(row=0, column=0, sticky="ew", padx=(12, 8), pady=12)

        self.forward_button = ctk.CTkButton(
            self.controls_frame,
            text="Avanzar",
            command=self.send_forward,
            fg_color=self.palette["accent"],
            hover_color=self.palette["accent_hover"],
            font=self.font_body,
            corner_radius=10,
        )
        self.forward_button.grid(row=0, column=1, padx=8, pady=12)

        self.stop_button = ctk.CTkButton(
            self.controls_frame,
            text="Parada de Emergencia",
            fg_color=self.palette["danger"],
            hover_color=self.palette["danger_hover"],
            command=self.send_stop,
            font=self.font_body,
            corner_radius=10,
        )
        self.stop_button.grid(row=0, column=2, padx=(8, 12), pady=12)

        self.status_frame = ctk.CTkFrame(
            self,
            fg_color=self.palette["card"],
            corner_radius=16,
            border_width=1,
            border_color=self.palette["card_border"],
        )
        self.status_frame.grid(row=3, column=0, sticky="nsew", padx=16, pady=8)
        self.status_frame.grid_columnconfigure(1, weight=1)
        self.status_frame.grid_rowconfigure(2, weight=1)

        self.sensor_title = ctk.CTkLabel(
            self.status_frame,
            text="Estado Sensor GT-442N3",
            font=self.font_section,
        )
        self.sensor_title.grid(row=0, column=0, padx=12, pady=(12, 6), sticky="w")

        self.sensor_canvas = tk.Canvas(self.status_frame, width=76, height=76, highlightthickness=0)
        self.sensor_canvas.grid(row=1, column=0, padx=16, pady=(0, 12), sticky="n")
        self.sensor_canvas.configure(bg=self.palette["card"])
        self.sensor_canvas.create_oval(6, 6, 70, 70, fill="#cbd5e1", outline="#94a3b8", width=1)
        self.led = self.sensor_canvas.create_oval(14, 14, 62, 62, fill="#2e7d32", outline="#1b5e20", width=3)

        self.sensor_state_label = ctk.CTkLabel(
            self.status_frame,
            text="Estado: Despejado",
            text_color=self.palette["ok"],
            font=ctk.CTkFont(family="Montserrat", size=13, weight="bold"),
        )
        self.sensor_state_label.grid(row=2, column=0, padx=12, pady=(0, 12), sticky="n")

        self.speed_title = ctk.CTkLabel(
            self.status_frame,
            text="Velocidad Cinta",
            font=self.font_section,
        )
        self.speed_title.grid(row=0, column=1, padx=12, pady=(12, 6), sticky="w")

        self.speed_progress = ctk.CTkProgressBar(
            self.status_frame,
            progress_color="#2563eb",
            fg_color="#dbe7ff",
            corner_radius=12,
            height=18,
        )
        self.speed_progress.grid(row=1, column=1, sticky="ew", padx=(12, 20), pady=(8, 0))
        self.speed_progress.set(0)

        self.speed_value_label = ctk.CTkLabel(self.status_frame, text="0.0 cm/s", font=self.font_body)
        self.speed_value_label.grid(row=2, column=1, padx=12, pady=(6, 12), sticky="w")

        self.speed_percent_label = ctk.CTkLabel(
            self.status_frame,
            text="0%",
            font=ctk.CTkFont(family="Montserrat", size=13, weight="bold"),
        )
        self.speed_percent_label.grid(row=2, column=1, padx=12, pady=(6, 12), sticky="e")

        self.log_frame = ctk.CTkFrame(
            self,
            fg_color=self.palette["card"],
            corner_radius=16,
            border_width=1,
            border_color=self.palette["card_border"],
        )
        self.log_frame.grid(row=4, column=0, sticky="nsew", padx=16, pady=(8, 16))
        self.log_frame.grid_columnconfigure(0, weight=1)
        self.log_frame.grid_rowconfigure(1, weight=1)

        self.log_title = ctk.CTkLabel(
            self.log_frame,
            text="Registro de Eventos",
            font=self.font_section,
        )
        self.log_title.grid(row=0, column=0, sticky="w", padx=12, pady=(12, 8))

        self.clear_log_button = ctk.CTkButton(
            self.log_frame,
            text="Limpiar",
            width=90,
            fg_color="#64748b",
            hover_color="#475569",
            command=self.clear_log,
            font=self.font_body,
            corner_radius=9,
        )
        self.clear_log_button.grid(row=0, column=1, padx=12, pady=(12, 8), sticky="e")

        self.log_box = ctk.CTkTextbox(
            self.log_frame,
            wrap="word",
            fg_color=self.palette["surface_dark"],
            text_color="#e2e8f0",
            border_width=1,
            border_color="#334155",
            font=self.font_mono,
            corner_radius=10,
        )
        self.log_box.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=12, pady=(0, 12))
        self.log_box.configure(state="disabled")

    def refresh_ports(self) -> None:
        ports = self.serial_worker.list_available_ports()
        if not ports:
            ports = ["No ports"]

        self.port_combobox.configure(values=ports)
        self.port_combobox.set(ports[0])

    def toggle_connection(self) -> None:
        if self.serial_worker.is_connected:
            self._disconnect_serial()
            return

        selected_port = self.port_combobox.get().strip()
        if not selected_port or selected_port == "No ports":
            messagebox.showerror("Error", "No hay puerto serial disponible")
            return

        try:
            self.serial_worker.connect(selected_port)
            self.connect_button.configure(text="Desconectar")
            self.connection_state.configure(text="Conectado", text_color="#1b5e20")
            self.log_event(f"Conectado al puerto {selected_port}")
        except (SerialException, OSError, ValueError) as exc:
            messagebox.showerror("Error de conexion", f"No se pudo abrir el puerto: {exc}")
            self.connection_state.configure(text="Desconectado", text_color="#b22222")

    def _disconnect_serial(self) -> None:
        self.serial_worker.disconnect()
        self.connect_button.configure(text="Conectar")
        self.connection_state.configure(text="Desconectado", text_color="#b22222")
        self.log_event("Puerto serial desconectado")

    def send_forward(self) -> None:
        if not self.serial_worker.is_connected:
            messagebox.showwarning("Aviso", "Primero conecta el puerto serial")
            return

        raw_speed = self.speed_entry.get().strip().replace(",", ".")
        try:
            speed = float(raw_speed)
            if speed <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Ingresa una velocidad valida en cm/s")
            return

        speed_d10 = int(round(speed * 10.0))
        if speed_d10 > self.max_speed_d10:
            speed_d10 = self.max_speed_d10

        command = f"V{speed_d10}"
        try:
            self.serial_worker.send(command)
            self._update_speed(speed_d10 / 10.0)
            self.log_event(f"Cinta iniciada a {speed_d10 / 10.0:.1f} cm/s (cmd {command})")
        except SerialException as exc:
            messagebox.showerror("Error serial", str(exc))

    def send_stop(self) -> None:
        if not self.serial_worker.is_connected:
            messagebox.showwarning("Aviso", "Primero conecta el puerto serial")
            return

        try:
            self.serial_worker.send("S")
            self._update_speed(0.0)
            self.log_event("Cinta detenida (parada de emergencia)")
        except SerialException as exc:
            messagebox.showerror("Error serial", str(exc))

    def _poll_messages(self) -> None:
        while True:
            message = self.serial_worker.get_message_nowait()
            if message is None:
                break
            self._process_message(message)

        self.after(120, self._poll_messages)

    def _process_message(self, message: str) -> None:
        if message.startswith("DET:"):
            value = message.split(":", maxsplit=1)[1].strip()
            if value == "1":
                self._set_sensor_state(True)
            elif value == "0":
                self._set_sensor_state(False)
            return

        if message.startswith("VEL:"):
            value = message.split(":", maxsplit=1)[1].strip()
            try:
                speed_d10 = int(value)
                speed = speed_d10 / 10.0
                self._update_speed(speed)
                self.log_event(f"Velocidad reportada: {speed:.1f} cm/s")
            except ValueError:
                self.log_event(f"Trama VEL invalida: {message}")
            return

        self.log_event(f"RX: {message}")

    def _set_sensor_state(self, detected: bool) -> None:
        if detected:
            self.sensor_canvas.itemconfig(self.led, fill="#d32f2f", outline="#8e0000")
            self.sensor_state_label.configure(text="Estado: Objeto detectado", text_color="#b91c1c")
            if self.last_sensor_state is not True:
                self.log_event("Objeto detectado al final de la cinta")
        else:
            self.sensor_canvas.itemconfig(self.led, fill="#2e7d32", outline="#1b5e20")
            self.sensor_state_label.configure(text="Estado: Despejado", text_color=self.palette["ok"])
            if self.last_sensor_state is not False:
                self.log_event("Sensor despejado")

        self.last_sensor_state = detected

    def _update_speed(self, speed: float) -> None:
        self.current_speed = max(0.0, speed)
        ratio = min(self.current_speed / self.max_speed, 1.0)
        self.speed_progress.set(ratio)
        self.speed_value_label.configure(text=f"{self.current_speed:.2f} cm/s")
        self.speed_percent_label.configure(text=f"{ratio * 100:.0f}%")

        if ratio >= 0.8:
            self.speed_progress.configure(progress_color="#dc2626")
        elif ratio >= 0.5:
            self.speed_progress.configure(progress_color="#d97706")
        else:
            self.speed_progress.configure(progress_color="#2563eb")

    def clear_log(self) -> None:
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")

    def log_event(self, text: str) -> None:
        timestamp = dt.datetime.now().strftime("%H:%M:%S")
        line = f"[{timestamp}] {text}\n"

        self.log_box.configure(state="normal")
        self.log_box.insert("end", line)
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def _on_close(self) -> None:
        if self.serial_worker.is_connected:
            self.serial_worker.disconnect()
        self.destroy()


def run_app() -> None:
    app = ScadaApp()
    app.mainloop()
