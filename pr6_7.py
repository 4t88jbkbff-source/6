import tkinter as tk
import math

# ---------- Палитра ----------
BG = "#1e1e2e"
PANEL = "#181825"
CARD = "#313244"
TEXT = "#cdd6f4"
SUBTLE = "#a6adc8"
ACCENT = "#89b4fa"
WAVE_COL = "#a6e3a1"
AXIS_COL = "#585b70"
GRID_COL = "#313244"


class CustomSlider(tk.Canvas):
    def __init__(self, parent, min_val, max_val, init_val, cmd, release_cmd=None, width=220):
        super().__init__(parent, width=width, height=30, bg=PANEL, highlightthickness=0, cursor="hand2")
        self.min_val = min_val
        self.max_val = max_val
        self.cmd = cmd
        self.release_cmd = release_cmd
        self.width = width

        self.val = init_val
        self.dragging = False

        self.bind("<Configure>", self.draw)
        self.bind("<Button-1>", self.on_click)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<ButtonRelease-1>", self.on_release)

    def set(self, val):
        self.val = max(self.min_val, min(self.max_val, val))
        self.draw()
        if self.cmd:
            self.cmd(str(self.val))

    def get(self):
        return self.val

    def draw(self, event=None):
        self.delete("all")
        w = self.winfo_width()
        if w < 10: w = self.width
        h = 30

        track_y = h // 2
        self.create_line(10, track_y, w - 10, track_y, fill=CARD, width=6, capstyle="round")

        ratio = (self.val - self.min_val) / (self.max_val - self.min_val)
        fill_x = 10 + ratio * (w - 20)
        if ratio > 0:
            self.create_line(10, track_y, fill_x, track_y, fill=ACCENT, width=6, capstyle="round")

        self.create_oval(fill_x - 8, track_y - 8, fill_x + 8, track_y + 8, fill="#ffffff", outline=ACCENT, width=3)

    def on_click(self, event):
        self.update_val(event.x)
        self.dragging = True

    def on_drag(self, event):
        if self.dragging:
            self.update_val(event.x)

    def on_release(self, event):
        self.dragging = False
        if self.release_cmd:
            self.release_cmd()

    def update_val(self, x):
        w = self.winfo_width()
        if w < 10: w = self.width
        x = max(10, min(w - 10, x))
        ratio = (x - 10) / (w - 20)
        self.val = self.min_val + ratio * (self.max_val - self.min_val)
        self.draw()
        if self.cmd:
            self.cmd(str(round(self.val, 1)))


class HarmonicApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Гармоническое колебание")
        self.root.configure(bg=BG)
        self.root.geometry("1100x650")
        self.root.minsize(900, 550)

        # Переменные
        self.amplitude = 1.0
        self.frequency = 1.0
        self.scale_factor = 1.0

        # Панель управления
        self.panel = tk.Frame(self.root, bg=PANEL, width=280)
        self.panel.pack(side="left", fill="y")
        self.panel.pack_propagate(False)
        self._build_panel()

        # Холст
        self.canvas = tk.Canvas(self.root, bg=BG, highlightthickness=0)
        self.canvas.pack(side="right", fill="both", expand=True)
        self.canvas.bind("<Configure>", self.full_redraw)

        # Флаг, чтобы при изменении размера окна не сбрасывался ползунок
        self.need_full_redraw = True

        # Запускаем первую отрисовку
        self.root.after(100, self.full_redraw)

    def _build_panel(self):
        tk.Label(self.panel, text="УПРАВЛЕНИЕ", font=("Segoe UI", 16, "bold"), fg=ACCENT, bg=PANEL).pack(pady=(25, 20))

        self._add_label("АМПЛИТУДА")
        self.amp_val_lbl = self._add_value_label(f"{self.amplitude:.1f}")
        self.amp_slider = CustomSlider(self.panel, 0.1, 5.0, self.amplitude, self.update_amplitude, self.full_redraw)
        self.amp_slider.pack(padx=20, pady=(0, 15))

        self._add_label("ЧАСТОТА")
        self.freq_val_lbl = self._add_value_label(f"{self.frequency:.1f}")
        self.freq_slider = CustomSlider(self.panel, 0.1, 5.0, self.frequency, self.update_frequency, self.full_redraw)
        self.freq_slider.pack(padx=20, pady=(0, 15))

        self._add_label("МАСШТАБ")
        self.scale_val_lbl = self._add_value_label(f"{self.scale_factor:.1f}x")
        self.scale_slider = CustomSlider(self.panel, 0.1, 5.0, self.scale_factor, self.update_scale, self.full_redraw)
        self.scale_slider.pack(padx=20, pady=(0, 15))

        tk.Label(self.panel, text="Тяните кружки,\nчтобы изменить график", font=("Segoe UI", 10, "italic"), fg=SUBTLE,
                 bg=PANEL, justify="center").pack(side="bottom", pady=20)

    def _add_label(self, text):
        tk.Label(self.panel, text=text, font=("Segoe UI", 10, "bold"), fg=SUBTLE, bg=PANEL).pack(anchor="w", padx=20,
                                                                                                 pady=(10, 0))

    def _add_value_label(self, text):
        lbl = tk.Label(self.panel, text=text, font=("Consolas", 16, "bold"), fg=ACCENT, bg=PANEL)
        lbl.pack(anchor="w", padx=20, pady=(0, 5))
        return lbl

    def update_amplitude(self, val):
        self.amplitude = float(val)
        self.amp_val_lbl.config(text=f"{self.amplitude:.1f}")
        self.update_graph_fast()  # Быстрое обновление

    def update_frequency(self, val):
        self.frequency = float(val)
        self.freq_val_lbl.config(text=f"{self.frequency:.1f}")
        self.update_graph_fast()

    def update_scale(self, val):
        self.scale_factor = float(val)
        self.scale_val_lbl.config(text=f"{self.scale_factor:.1f}x")
        self.update_graph_fast()

    def update_graph_fast(self):
        # Вместо удаления всего холста, мы обновляем только координаты линии
        if not hasattr(self, 'wave_line') or not self.wave_line:
            self.full_redraw()
            return

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 100 or h < 100: return

        pad_l, pad_r, pad_t, pad_b = 60, 40, 40, 60
        plot_w = w - pad_l - pad_r
        plot_h = h - pad_t - pad_b

        x_base = 4 * math.pi
        x_range = x_base / self.scale_factor
        x_min = -x_range / 2

        y_max = max(5.0, self.amplitude * 1.5)
        y_min = -y_max
        y_range = y_max - y_min

        def get_py(y_val):
            return pad_t + (y_max - y_val) / y_range * plot_h

        # Обновляем только точки линии
        points = []
        for px in range(int(pad_l) - 10, int(pad_l + plot_w) + 10, 2):
            t_val = x_min + (px - pad_l) / plot_w * x_range
            y_val = self.amplitude * math.sin(self.frequency * t_val)
            py = get_py(y_val)
            points.extend([px, py])

        if len(points) >= 4:
            self.canvas.coords(self.wave_line, *points)

    def full_redraw(self, event=None):
        # Полная перерисовка (сетка, оси, график)
        self.canvas.delete("all")
        self.root.update_idletasks()

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 100 or h < 100: return

        pad_l, pad_r, pad_t, pad_b = 60, 40, 40, 60
        plot_w = w - pad_l - pad_r
        plot_h = h - pad_t - pad_b

        x_base = 4 * math.pi
        x_range = x_base / self.scale_factor
        x_min = -x_range / 2
        x_max = x_range / 2

        y_max = max(5.0, self.amplitude * 1.5)
        y_min = -y_max
        y_range = y_max - y_min

        def get_px(x_val):
            return pad_l + (x_val - x_min) / x_range * plot_w

        def get_py(y_val):
            return pad_t + (y_max - y_val) / y_range * plot_h

        # Сетка
        step_x = self._nice_step(x_range)
        x_val = math.ceil(x_min / step_x) * step_x
        while x_val <= x_max:
            px = get_px(x_val)
            self.canvas.create_line(px, pad_t, px, pad_t + plot_h, fill=GRID_COL)

            if abs(x_val) < 1e-5:
                label = "0"
            else:
                coef = x_val / math.pi
                if abs(coef - round(coef)) < 1e-5:
                    label = f"{int(round(coef))}π"
                elif abs(coef * 2 - round(coef * 2)) < 1e-5:
                    label = f"{int(round(coef * 2))}π/2"
                else:
                    label = f"{coef:.1f}π"

            self.canvas.create_text(px, pad_t + plot_h + 20, text=label, font=("Consolas", 10), fill=SUBTLE)
            x_val += step_x

        step_y = self._nice_step(y_range)
        y_val = math.ceil(y_min / step_y) * step_y
        while y_val <= y_max:
            py = get_py(y_val)
            self.canvas.create_line(pad_l, py, pad_l + plot_w, py, fill=GRID_COL)
            if abs(y_val) > 1e-5:
                label = f"{y_val:.1f}".rstrip('0').rstrip('.')
                self.canvas.create_text(pad_l - 15, py, text=label, anchor="e", font=("Consolas", 10), fill=SUBTLE)
            y_val += step_y

        # Оси
        if y_min <= 0 <= y_max:
            py0 = get_py(0)
            self.canvas.create_line(pad_l, py0, pad_l + plot_w + 20, py0, fill=AXIS_COL, arrow=tk.LAST, width=2)
            self.canvas.create_text(pad_l + plot_w + 30, py0, text="t", font=("Times New Roman", 16, "italic"),
                                    fill=AXIS_COL)

        if x_min <= 0 <= x_max:
            px0 = get_px(0)
            self.canvas.create_line(px0, pad_t + plot_h + 20, px0, pad_t - 20, fill=AXIS_COL, arrow=tk.LAST, width=2)
            self.canvas.create_text(px0, pad_t - 30, text="y", font=("Times New Roman", 16, "italic"), fill=AXIS_COL)

        # График (создаем один раз, потом будем двигать через coords)
        points = []
        for px in range(int(pad_l) - 10, int(pad_l + plot_w) + 10, 2):
            t_val = x_min + (px - pad_l) / plot_w * x_range
            y_val = self.amplitude * math.sin(self.frequency * t_val)
            py = get_py(y_val)
            points.extend([px, py])

        if len(points) >= 4:
            self.wave_line = self.canvas.create_line(points, fill=WAVE_COL, width=3, smooth=True, capstyle="round",
                                                     joinstyle="round")
        else:
            self.wave_line = None

    def _nice_step(self, rng):
        if rng < 0.001: return 0.0001
        raw = rng / 10.0
        exp = math.floor(math.log10(raw))
        frac = raw / 10 ** exp
        if frac < 1.5:
            nice_frac = 1
        elif frac < 3:
            nice_frac = 2
        elif frac < 7:
            nice_frac = 5
        else:
            nice_frac = 10
        return nice_frac * 10 ** exp


if __name__ == "__main__":
    root = tk.Tk()
    app = HarmonicApp(root)
    root.mainloop()