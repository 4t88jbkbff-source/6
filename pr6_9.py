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

SIGNAL_COL = "#89b4fa"
ENVELOPE_COL = "#f38ba8"


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

    def update_val(self, x):
        w = self.winfo_width()
        if w < 10: w = self.width
        x = max(8, min(w - 8, x))
        ratio = (x - 8) / (w - 16)
        self.val = self.min_val + ratio * (self.max_val - self.min_val)
        self.draw()
        if self.cmd:
            self.cmd(str(round(self.val, 2)))


class AMApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Амплитудная модуляция (АМ)")
        self.root.configure(bg=BG)
        self.root.geometry("1200x750")
        self.root.minsize(1000, 650)

        self.a_carrier = 1.0
        self.f_carrier = 20.0
        self.f_mod = 2.0
        self.m = 0.5
        self.zoom_x = 1.0

        self.panel = tk.Frame(self.root, bg=PANEL, width=320)
        self.panel.pack(side="left", fill="y")
        self.panel.pack_propagate(False)
        self._build_panel()

        self.canvas = tk.Canvas(self.root, bg=BG, highlightthickness=0)
        self.canvas.pack(side="right", fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda e: self.full_redraw())

        self.root.after(100, self.full_redraw)

    def _build_panel(self):
        tk.Label(self.panel, text="ПАРАМЕТРЫ АМ", font=("Segoe UI", 16, "bold"), fg=ACCENT, bg=PANEL).pack(
            pady=(20, 15))

        self._add_label("Масштаб (Время)")
        self.lbl_zoom = self._add_value_label(f"{self.zoom_x:.1f}x")
        self.sld_zoom = CustomSlider(self.panel, 0.5, 5.0, self.zoom_x, self.update_zoom, "#cba6f7")
        self.sld_zoom.pack(padx=20, pady=(0, 15))

        self._add_label("Амплитуда несущей (Uн)")
        self.lbl_a = self._add_value_label(f"{self.a_carrier:.2f}")
        self.sld_a = CustomSlider(self.panel, 0.1, 3.0, self.a_carrier, self.update_a, ACCENT)
        self.sld_a.pack(padx=20, pady=(0, 15))

        self._add_label("Частота несущей (fн)")
        self.lbl_fc = self._add_value_label(f"{self.f_carrier:.1f}")
        self.sld_fc = CustomSlider(self.panel, 5.0, 50.0, self.f_carrier, self.update_fc, ACCENT)
        self.sld_fc.pack(padx=20, pady=(0, 15))

        self._add_label("Частота модуляции (Fм)")
        self.lbl_fm = self._add_value_label(f"{self.f_mod:.1f}")
        self.sld_fm = CustomSlider(self.panel, 0.5, 10.0, self.f_mod, self.update_fm, ACCENT)
        self.sld_fm.pack(padx=20, pady=(0, 15))

        self._add_label("Глубина модуляции (m)")
        self.lbl_m = self._add_value_label(f"{self.m:.2f}")
        self.sld_m = CustomSlider(self.panel, 0.0, 1.5, self.m, self.update_m, "#f38ba8")
        self.sld_m.pack(padx=20, pady=(0, 15))

        btn = tk.Button(self.panel, text="СБРОС", command=self.reset_values,
                        font=("Segoe UI", 11, "bold"), bg="#313244", fg=TEXT,
                        activebackground="#45475a", relief="flat", pady=8, cursor="hand2")
        btn.pack(side="bottom", fill="x", padx=20, pady=15)

    def _add_label(self, text):
        tk.Label(self.panel, text=text, font=("Segoe UI", 10, "bold"), fg=SUBTLE, bg=PANEL).pack(anchor="w", padx=20,
                                                                                                 pady=(5, 0))

    def _add_value_label(self, text):
        lbl = tk.Label(self.panel, text=text, font=("Consolas", 14, "bold"), fg=TEXT, bg=PANEL)
        lbl.pack(anchor="w", padx=20, pady=(0, 5))
        return lbl

    # --- Обновление параметров ---
    def update_zoom(self, val):
        self.zoom_x = float(val)
        self.lbl_zoom.config(text=f"{self.zoom_x:.1f}x")
        self.full_redraw()  # Зум меняет сетку, поэтому перерисовываем всё один раз

    def update_a(self, val):
        self.a_carrier = float(val)
        self.lbl_a.config(text=f"{self.a_carrier:.2f}")
        self.update_lines()

    def update_fc(self, val):
        self.f_carrier = float(val)
        self.lbl_fc.config(text=f"{self.f_carrier:.1f}")
        self.update_lines()

    def update_fm(self, val):
        self.f_mod = float(val)
        self.lbl_fm.config(text=f"{self.f_mod:.1f}")
        self.update_lines()

    def update_m(self, val):
        self.m = float(val)
        self.lbl_m.config(text=f"{self.m:.2f}")
        self.update_lines()

    def reset_values(self):
        self.a_carrier = 1.0
        self.f_carrier = 20.0
        self.f_mod = 2.0
        self.m = 0.5
        self.zoom_x = 1.0

        for sld, val in [(self.sld_a, 1.0), (self.sld_fc, 20.0), (self.sld_fm, 2.0), (self.sld_m, 0.5),
                         (self.sld_zoom, 1.0)]:
            sld.val = val
            sld.draw()

        self.lbl_a.config(text="1.00")
        self.lbl_fc.config(text="20.0")
        self.lbl_fm.config(text="2.0")
        self.lbl_m.config(text="0.50")
        self.lbl_zoom.config(text="1.0x")
        self.full_redraw()

    # --- Отрисовка ---
    def full_redraw(self, event=None):
        # Полная перерисовка (только при старте, ресайзе или зуме)
        self.canvas.delete("all")
        self.root.update_idletasks()

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 100 or h < 100: return

        self.pad_l, self.pad_r, self.pad_t, self.pad_b = 60, 40, 40, 60
        self.plot_w = w - self.pad_l - self.pad_r
        self.plot_h = h - self.pad_t - self.pad_b

        self.x_range = 2.0 / self.zoom_x
        self.y_max = max(1.5, self.a_carrier * (1 + self.m) * 1.2)
        self.y_min = -self.y_max
        self.y_range = self.y_max - self.y_min

        # Сетка
        step_x = self.x_range / 10.0
        x_val = 0
        while x_val <= self.x_range + 0.001:
            px = self.get_px(x_val)
            self.canvas.create_line(px, self.pad_t, px, self.pad_t + self.plot_h, fill=GRID_COL)
            self.canvas.create_text(px, self.pad_t + self.plot_h + 20, text=f"{x_val:.2f}", font=("Consolas", 10),
                                    fill=SUBTLE)
            x_val += step_x

        step_y = max(0.5, round(self.y_max / 4 * 2) / 2)
        y_val = int(self.y_min / step_y) * step_y
        while y_val <= self.y_max + 0.01:
            py = self.get_py(y_val)
            self.canvas.create_line(self.pad_l, py, self.pad_l + self.plot_w, py, fill=GRID_COL)
            if abs(y_val) > 1e-3:
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

        # Создаем линии (пока пустые)
        self.env_top_line = self.canvas.create_line(0, 0, 0, 0, fill=ENVELOPE_COL, width=2, dash=(5, 4))
        self.env_bot_line = self.canvas.create_line(0, 0, 0, 0, fill=ENVELOPE_COL, width=2, dash=(5, 4))
        self.signal_line = self.canvas.create_line(0, 0, 0, 0, fill=SIGNAL_COL, width=2)

        # Заполняем их
        self.update_lines()

    def update_lines(self):
        # Быстрое обновление только координат линий
        if not hasattr(self, 'signal_line') or not self.signal_line:
            return

        points_sig = []
        points_env_top = []
        points_env_bot = []

        # Если амплитуда изменилась, границы Y могли выйти за экран
        current_ymax = max(1.5, self.a_carrier * (1 + self.m) * 1.2)

        for px in range(int(self.pad_l), int(self.pad_l + self.plot_w) + 1, 2):
            t = (px - self.pad_l) / self.plot_w * self.x_range
            envelope = self.a_carrier * (1 + self.m * math.cos(2 * math.pi * self.f_mod * t))
            y_val = envelope * math.cos(2 * math.pi * self.f_carrier * t)

            # Обрезаем по текущим границам (чтобы не рисовало за пределами)
            py_sig = self.pad_t + (self.y_max - max(self.y_min, min(self.y_max, y_val))) / self.y_range * self.plot_h
            points_sig.extend([px, py_sig])

            if px % 4 == 0:
                py_env_top = self.pad_t + (
                            self.y_max - max(self.y_min, min(self.y_max, envelope))) / self.y_range * self.plot_h
                py_env_bot = self.pad_t + (
                            self.y_max - max(self.y_min, min(self.y_max, -envelope))) / self.y_range * self.plot_h
                points_env_top.extend([px, py_env_top])
                points_env_bot.extend([px, py_env_bot])

        if len(points_sig) >= 4:
            self.canvas.coords(self.signal_line, *points_sig)
            self.canvas.coords(self.env_top_line, *points_env_top)
            self.canvas.coords(self.env_bot_line, *points_env_bot)

    def get_px(self, x_val):
        return self.pad_l + x_val / self.x_range * self.plot_w

    def get_py(self, y_val):
        return self.pad_t + (self.y_max - y_val) / self.y_range * self.plot_h


if __name__ == "__main__":
    root = tk.Tk()
    app = AMApp(root)
    root.mainloop()