import tkinter as tk
import math

# ---------- Палитра ----------
BG = "#1e1e2e"
PANEL = "#181825"
CARD = "#313244"
TEXT = "#cdd6f4"
SUBTLE = "#a6adc8"
ACCENT = "#89b4fa"
AXIS_COL = "#585b70"
GRID_COL = "#313244"

SIGNAL_COL = "#a6e3a1"
MOD_COL = "#f38ba8"


class CustomSlider(tk.Canvas):
    def __init__(self, parent, min_val, max_val, init_val, cmd, color, width=250):
        super().__init__(parent, width=width, height=20, bg=PANEL, highlightthickness=0, cursor="hand2")
        self.min_val = min_val
        self.max_val = max_val
        self.cmd = cmd
        self.color = color
        self.width = width
        self.val = init_val
        self.dragging = False

        self.bind("<Configure>", self.draw)
        self.bind("<Button-1>", self.on_click)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<ButtonRelease-1>", self.on_release)

    def draw(self, event=None):
        self.delete("all")
        w = self.winfo_width()
        if w < 10: w = self.width
        h = 20
        track_y = h // 2

        self.create_line(8, track_y, w - 8, track_y, fill=CARD, width=6, capstyle="round")
        ratio = (self.val - self.min_val) / (self.max_val - self.min_val)
        fill_x = 8 + ratio * (w - 16)
        if ratio > 0:
            self.create_line(8, track_y, fill_x, track_y, fill=self.color, width=6, capstyle="round")
        self.create_oval(fill_x - 8, track_y - 8, fill_x + 8, track_y + 8, fill="#ffffff", outline=self.color, width=2)

    def on_click(self, event):
        self.update_val(event.x)
        self.dragging = True

    def on_drag(self, event):
        if self.dragging:
            self.update_val(event.x)

    def on_release(self, event):
        self.dragging = False
        self.cmd("release")

    def update_val(self, x):
        w = self.winfo_width()
        if w < 10: w = self.width
        x = max(8, min(w - 8, x))
        ratio = (x - 8) / (w - 16)
        self.val = self.min_val + ratio * (self.max_val - self.min_val)
        self.draw()
        if self.cmd:
            self.cmd(str(round(self.val, 2)))


class DigitalModApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Цифровая модуляция: ASK / FSK / PSK")
        self.root.configure(bg=BG)
        self.root.geometry("1250x800")
        self.root.minsize(1000, 700)

        self.mod_type = "ASK"
        self.bits = [1, 0, 1, 1, 0, 0, 1, 0]  # Начальные биты
        self.f_carrier = 20.0
        self.bit_rate = 1.0
        self.bit_buttons = []

        # Панель управления
        self.panel = tk.Frame(self.root, bg=PANEL, width=340)
        self.panel.pack(side="left", fill="y")
        self.panel.pack_propagate(False)
        self._build_panel()

        # Правая часть (График + Кнопки битов)
        self.right_frame = tk.Frame(self.root, bg=BG)
        self.right_frame.pack(side="right", fill="both", expand=True)

        # Холст для графика
        self.canvas = tk.Canvas(self.right_frame, bg=BG, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=10, pady=(10, 0))
        self.canvas.bind("<Configure>", lambda e: self.full_redraw())

        # Панель для интерактивных битов (внизу)
        self.bits_panel = tk.Frame(self.right_frame, bg=BG)
        self.bits_panel.pack(fill="x", padx=10, pady=10)
        self._build_bit_buttons()

        self.root.after(100, self.full_redraw)

    def _build_panel(self):
        tk.Label(self.panel, text="ЦИФРОВАЯ МОДУЛЯЦИЯ", font=("Segoe UI", 14, "bold"), fg=ACCENT, bg=PANEL).pack(
            pady=(20, 10))

        mod_frame = tk.Frame(self.panel, bg=PANEL)
        mod_frame.pack(fill="x", padx=20, pady=10)

        self.btn_ask = self._mod_button(mod_frame, "ASK", "ASK", 0)
        self.btn_fsk = self._mod_button(mod_frame, "FSK", "FSK", 1)
        self.btn_psk = self._mod_button(mod_frame, "PSK", "PSK", 2)

        self._add_label("Частота несущей (fн)")
        self.lbl_fc = self._add_value_label(f"{self.f_carrier:.1f}")
        self.sld_fc = CustomSlider(self.panel, 5.0, 60.0, self.f_carrier, self.update_fc, ACCENT)
        self.sld_fc.pack(padx=20, pady=(0, 15))

        self._add_label("Скорость (бит/сек)")
        self.lbl_br = self._add_value_label(f"{self.bit_rate:.1f}")
        self.sld_br = CustomSlider(self.panel, 0.5, 5.0, self.bit_rate, self.update_br, "#cba6f7")
        self.sld_br.pack(padx=20, pady=(0, 15))

        help_text = (
            "ASK: 1 = сигнал, 0 = тишина\n"
            "FSK: 1 = высокая частота,\n"
            "     0 = низкая частота\n"
            "PSK: 1 = фаза 0°,\n"
            "     0 = фаза 180°\n\n"
            "Нажимай на кнопки битов\nвнизу, чтобы менять сигнал!"
        )
        tk.Label(self.panel, text=help_text, font=("Consolas", 10), fg=SUBTLE, bg=PANEL, justify="left").pack(
            side="bottom", anchor="w", padx=20, pady=20)

    def _mod_button(self, parent, text, mode, col):
        btn = tk.Button(parent, text=text, command=lambda: self.set_mod(mode),
                        font=("Segoe UI", 11, "bold"), bg=CARD, fg=TEXT,
                        activebackground=ACCENT, activeforeground=BG, relief="flat", pady=6, cursor="hand2")
        btn.grid(row=0, column=col, padx=2, sticky="ew")
        parent.columnconfigure(col, weight=1)
        return btn

    def _add_label(self, text):
        tk.Label(self.panel, text=text, font=("Segoe UI", 10, "bold"), fg=SUBTLE, bg=PANEL).pack(anchor="w", padx=20,
                                                                                                 pady=(5, 0))

    def _add_value_label(self, text):
        lbl = tk.Label(self.panel, text=text, font=("Consolas", 14, "bold"), fg=TEXT, bg=PANEL)
        lbl.pack(anchor="w", padx=20, pady=(0, 5))
        return lbl

    def _build_bit_buttons(self):
        for w in self.bits_panel.winfo_children():
            w.destroy()
        self.bit_buttons = []

        for i, bit in enumerate(self.bits):
            btn = tk.Button(self.bits_panel, text=str(bit), font=("Consolas", 14, "bold"),
                            width=3, relief="flat", bd=0, cursor="hand2",
                            command=lambda idx=i: self.toggle_bit(idx))
            btn.pack(side="left", padx=2, expand=True, fill="x")
            self.bit_buttons.append(btn)
            self._update_bit_btn_color(btn, bit)

    def _update_bit_btn_color(self, btn, bit):
        if bit == 1:
            btn.config(bg=SIGNAL_COL, fg=BG, activebackground=SIGNAL_COL)
        else:
            btn.config(bg=CARD, fg=SUBTLE, activebackground="#45475a")

    def toggle_bit(self, idx):
        self.bits[idx] = 1 - self.bits[idx]
        self._update_bit_btn_color(self.bit_buttons[idx], self.bits[idx])
        self.update_signal_line()  # Мгновенно перерисовываем только линию

    # --- Логика ---
    def set_mod(self, mode):
        self.mod_type = mode
        for btn, m in [(self.btn_ask, "ASK"), (self.btn_fsk, "FSK"), (self.btn_psk, "PSK")]:
            if m == mode:
                btn.config(bg=ACCENT, fg=BG)
            else:
                btn.config(bg=CARD, fg=TEXT)
        self.full_redraw()

    def update_fc(self, val):
        if val == "release":
            self.full_redraw()
            return
        self.f_carrier = float(val)
        self.lbl_fc.config(text=f"{self.f_carrier:.1f}")
        self.update_signal_line()

    def update_br(self, val):
        if val == "release":
            self.full_redraw()
            return
        self.bit_rate = float(val)
        self.lbl_br.config(text=f"{self.bit_rate:.1f}")
        self.update_signal_line()

    # --- Отрисовка ---
    def full_redraw(self, event=None):
        self.canvas.delete("all")
        self.root.update_idletasks()

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 100 or h < 100: return

        self.pad_l, self.pad_r, self.pad_t, self.pad_b = 60, 40, 40, 60
        self.plot_w = w - self.pad_l - self.pad_r
        self.plot_h = h - self.pad_t - self.pad_b

        self.total_time = len(self.bits) / self.bit_rate
        self.x_range = self.total_time
        self.y_max = 1.2
        self.y_min = -1.2
        self.y_range = self.y_max - self.y_min

        # Сетка
        step_x = 1.0 / self.bit_rate
        t_val = 0
        while t_val <= self.x_range + 0.001:
            px = self.get_px(t_val)
            self.canvas.create_line(px, self.pad_t, px, self.pad_t + self.plot_h, fill=GRID_COL)
            t_val += step_x

        step_y = 0.5
        y_val = -1.0
        while y_val <= 1.0:
            py = self.get_py(y_val)
            self.canvas.create_line(self.pad_l, py, self.pad_l + self.plot_w, py, fill=GRID_COL)
            self.canvas.create_text(self.pad_l - 15, py, text=f"{y_val:.1f}", anchor="e", font=("Consolas", 10),
                                    fill=SUBTLE)
            y_val += step_y

        # Оси
        py0 = self.get_py(0)
        self.canvas.create_line(self.pad_l, py0, self.pad_l + self.plot_w + 20, py0, fill=AXIS_COL, arrow=tk.LAST,
                                width=2)
        self.canvas.create_text(self.pad_l + self.plot_w + 30, py0, text="t (c)",
                                font=("Times New Roman", 14, "italic"), fill=AXIS_COL)

        px0 = self.get_px(0)
        self.canvas.create_line(px0, self.pad_t + self.plot_h + 20, px0, self.pad_t - 20, fill=AXIS_COL, arrow=tk.LAST,
                                width=2)
        self.canvas.create_text(px0, self.pad_t - 30, text="U", font=("Times New Roman", 14, "italic"), fill=AXIS_COL)

        # Создаем линию и сразу заполняем
        self.signal_line = self.canvas.create_line(0, 0, 0, 0, fill=SIGNAL_COL, width=2)
        self.update_signal_line()

    def update_signal_line(self):
        if not hasattr(self, 'signal_line') or not self.signal_line:
            return

        points = []
        num_points = int(self.plot_w * 2)
        for i in range(num_points + 1):
            t = (i / num_points) * self.x_range
            bit_idx = int(t * self.bit_rate)
            if bit_idx >= len(self.bits): break

            bit = self.bits[bit_idx]
            phase = 2 * math.pi * self.f_carrier * t

            if self.mod_type == "ASK":
                y_val = (1.0 if bit == 1 else 0.0) * math.sin(phase)
            elif self.mod_type == "FSK":
                freq = self.f_carrier * 1.5 if bit == 1 else self.f_carrier * 0.5
                y_val = math.sin(2 * math.pi * freq * t)
            elif self.mod_type == "PSK":
                phase_offset = 0 if bit == 1 else math.pi
                y_val = math.sin(phase + phase_offset)

            points.extend([self.get_px(t), self.get_py(y_val)])

        if len(points) >= 4:
            self.canvas.coords(self.signal_line, *points)

    def get_px(self, t):
        return self.pad_l + t / self.x_range * self.plot_w

    def get_py(self, y_val):
        return self.pad_t + (self.y_max - y_val) / self.y_range * self.plot_h


if __name__ == "__main__":
    root = tk.Tk()
    app = DigitalModApp(root)
    root.mainloop()