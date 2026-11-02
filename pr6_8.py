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

# Яркие цвета для 5 колебаний
COLORS = ["#ff7b72", "#79c0ff", "#d2a8ff", "#ffa657", "#7ee787"]
SUM_COL = "#ffffff"


class CustomSlider(tk.Canvas):
    def __init__(self, parent, min_val, max_val, init_val, cmd, color, width=150):
        super().__init__(parent, width=width, height=20, bg=CARD, highlightthickness=0, cursor="hand2")
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

        self.create_line(8, track_y, w - 8, track_y, fill=BG, width=4, capstyle="round")
        ratio = (self.val - self.min_val) / (self.max_val - self.min_val)
        fill_x = 8 + ratio * (w - 16)
        if ratio > 0:
            self.create_line(8, track_y, fill_x, track_y, fill=self.color, width=4, capstyle="round")
        self.create_oval(fill_x - 7, track_y - 7, fill_x + 7, track_y + 7, fill="#ffffff", outline=self.color, width=2)

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
            self.cmd(str(round(self.val, 1)))


class HarmonicsSumApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Сложение гармоник (Плавная визуализация)")
        self.root.configure(bg=BG)
        self.root.geometry("1250x800")
        self.root.minsize(1000, 700)

        self.harmonics = [
            [1.0, 1.0], [0.5, 2.0], [0.3, 3.0], [0.2, 4.5], [0.1, 6.0]
        ]
        self.zoom_level = 1.0

        # Флаг для оптимизации (чтобы не тормозило)
        self.needs_update = False

        self.panel = tk.Frame(self.root, bg=PANEL, width=320)
        self.panel.pack(side="left", fill="y")
        self.panel.pack_propagate(False)
        self._build_panel()

        self.canvas = tk.Canvas(self.root, bg=BG, highlightthickness=0)
        self.canvas.pack(side="right", fill="both", expand=True)
        self.canvas.bind("<Configure>", self.full_redraw)

        # Запускаем цикл плавной отрисовки (60 FPS)
        self.root.after(100, self.full_redraw)
        self.animate()

    def animate(self):
        # Этот метод вызывается каждые 16 мс (около 60 раз в секунду)
        if self.needs_update:
            self.update_graph_fast()
            self.needs_update = False
        self.root.after(16, self.animate)

    def _build_panel(self):
        tk.Label(self.panel, text="ГАРМОНИКИ", font=("Segoe UI", 16, "bold"), fg=ACCENT, bg=PANEL).pack(pady=(15, 5))

        zoom_frame = tk.Frame(self.panel, bg=BG, pady=10, padx=10)
        zoom_frame.pack(fill="x", padx=10, pady=(0, 10))
        tk.Label(zoom_frame, text="МАСШТАБ (X)", font=("Segoe UI", 10, "bold"), fg=ACCENT, bg=BG).pack(anchor="w")
        self.zoom_lbl = tk.Label(zoom_frame, text="1.0x", font=("Consolas", 12, "bold"), fg=TEXT, bg=BG)
        self.zoom_lbl.pack(anchor="e")
        self.zoom_sld = CustomSlider(zoom_frame, 0.1, 5.0, 1.0, self.update_zoom, ACCENT, width=280)
        self.zoom_sld.pack(fill="x", pady=5)

        canvas_scroll = tk.Canvas(self.panel, bg=PANEL, highlightthickness=0)
        scrollbar = tk.Scrollbar(self.panel, orient="vertical", command=canvas_scroll.yview)
        scroll_frame = tk.Frame(canvas_scroll, bg=PANEL)

        scroll_frame.bind("<Configure>", lambda e: canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all")))
        canvas_scroll.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas_scroll.configure(yscrollcommand=scrollbar.set)

        canvas_scroll.pack(side="left", fill="both", expand=True, padx=10)
        scrollbar.pack(side="right", fill="y")

        self.sliders = []
        for i in range(5):
            self._build_harmonic_block(scroll_frame, i)

        btn = tk.Button(self.panel, text="СБРОСИТЬ", command=self.reset_values,
                        font=("Segoe UI", 11, "bold"), bg="#f38ba8", fg="#ffffff",
                        activebackground="#f38ba8", relief="flat", pady=8, cursor="hand2")
        btn.pack(side="bottom", fill="x", padx=20, pady=15)

    def _build_harmonic_block(self, parent, idx):
        color = COLORS[idx]
        frame = tk.Frame(parent, bg=CARD, pady=8, padx=10)
        frame.pack(fill="x", pady=5, padx=5)

        head = tk.Frame(frame, bg=CARD)
        head.pack(fill="x", pady=(0, 5))
        tk.Label(head, text="●", font=("Segoe UI", 14), fg=color, bg=CARD).pack(side="left")
        tk.Label(head, text=f"Гармоника {idx + 1}", font=("Segoe UI", 10, "bold"), fg=TEXT, bg=CARD).pack(side="left",
                                                                                                          padx=5)

        row_amp = tk.Frame(frame, bg=CARD)
        row_amp.pack(fill="x", pady=2)
        tk.Label(row_amp, text="A =", font=("Consolas", 10), fg=SUBTLE, bg=CARD, width=3).pack(side="left")
        lbl_amp = tk.Label(row_amp, text="1.0", font=("Consolas", 10, "bold"), fg=color, bg=CARD, width=4)
        lbl_amp.pack(side="right")
        sld_amp = CustomSlider(row_amp, 0.1, 3.0, self.harmonics[idx][0], lambda v, i=idx: self.update_param(i, 0, v),
                               color)
        sld_amp.pack(side="left", fill="x", expand=True, padx=5)

        row_freq = tk.Frame(frame, bg=CARD)
        row_freq.pack(fill="x", pady=2)
        tk.Label(row_freq, text="ω =", font=("Consolas", 10), fg=SUBTLE, bg=CARD, width=3).pack(side="left")
        lbl_freq = tk.Label(row_freq, text="1.0", font=("Consolas", 10, "bold"), fg=color, bg=CARD, width=4)
        lbl_freq.pack(side="right")
        sld_freq = CustomSlider(row_freq, 0.1, 8.0, self.harmonics[idx][1], lambda v, i=idx: self.update_param(i, 1, v),
                                color)
        sld_freq.pack(side="left", fill="x", expand=True, padx=5)

        self.sliders.append({"amp_lbl": lbl_amp, "freq_lbl": lbl_freq, "amp_sld": sld_amp, "freq_sld": sld_freq})

    def update_param(self, idx, param_idx, val_str):
        val = float(val_str)
        self.harmonics[idx][param_idx] = val
        if param_idx == 0:
            self.sliders[idx]["amp_lbl"].config(text=f"{val:.1f}")
        else:
            self.sliders[idx]["freq_lbl"].config(text=f"{val:.1f}")

        # Вместо мгновенной перерисовки, просто ставим флаг
        self.needs_update = True

    def update_zoom(self, val):
        self.zoom_level = float(val)
        self.zoom_lbl.config(text=f"{self.zoom_level:.1f}x")
        self.needs_update = True

    def reset_values(self):
        defaults = [[1.0, 1.0], [0.5, 2.0], [0.3, 3.0], [0.2, 4.5], [0.1, 6.0]]
        self.zoom_level = 1.0
        self.zoom_sld.val = 1.0
        self.zoom_sld.draw()
        self.zoom_lbl.config(text="1.0x")

        for i in range(5):
            self.harmonics[i] = defaults[i][:]
            self.sliders[i]["amp_lbl"].config(text=f"{defaults[i][0]:.1f}")
            self.sliders[i]["freq_lbl"].config(text=f"{defaults[i][1]:.1f}")
            self.sliders[i]["amp_sld"].val = defaults[i][0]
            self.sliders[i]["amp_sld"].draw()
            self.sliders[i]["freq_sld"].val = defaults[i][1]
            self.sliders[i]["freq_sld"].draw()
        self.full_redraw()

    def update_graph_fast(self):
        if not hasattr(self, 'wave_lines') or len(self.wave_lines) != 6:
            self.full_redraw()
            return

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 100 or h < 100: return

        pad_l, pad_r, pad_t, pad_b = 60, 40, 40, 60
        plot_w = w - pad_l - pad_r
        plot_h = h - pad_t - pad_b

        x_range = 4 * math.pi / self.zoom_level
        x_min = -x_range / 2

        max_y = sum(amp for amp, _ in self.harmonics) + 0.5
        y_max = max(5.0, max_y)
        y_min = -y_max
        y_range = y_max - y_min

        def get_py(y_val):
            if y_val > y_max: y_val = y_max
            if y_val < y_min: y_val = y_min
            return pad_t + (y_max - y_val) / y_range * plot_h

        for idx in range(5):
            amp, freq = self.harmonics[idx]
            points = []
            for px in range(int(pad_l) - 10, int(pad_l + plot_w) + 10, 2):
                t_val = x_min + (px - pad_l) / plot_w * x_range
                y_val = amp * math.sin(freq * t_val)
                py = get_py(y_val)
                points.extend([px, py])
            if len(points) >= 4:
                self.canvas.coords(self.wave_lines[idx], *points)

        points_sum = []
        for px in range(int(pad_l) - 10, int(pad_l + plot_w) + 10, 2):
            t_val = x_min + (px - pad_l) / plot_w * x_range
            y_val = sum(amp * math.sin(freq * t_val) for amp, freq in self.harmonics)
            py = get_py(y_val)
            points_sum.extend([px, py])
        if len(points_sum) >= 4:
            self.canvas.coords(self.wave_lines[5], *points_sum)

    def full_redraw(self, event=None):
        self.canvas.delete("all")
        self.root.update_idletasks()

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 100 or h < 100: return

        pad_l, pad_r, pad_t, pad_b = 60, 40, 40, 60
        plot_w = w - pad_l - pad_r
        plot_h = h - pad_t - pad_b

        x_range = 4 * math.pi / self.zoom_level
        x_min = -x_range / 2
        x_max = x_range / 2

        max_y = sum(amp for amp, _ in self.harmonics) + 0.5
        y_max = max(5.0, max_y)
        y_min = -y_max
        y_range = y_max - y_min

        def get_px(x_val):
            return pad_l + (x_val - x_min) / x_range * plot_w

        def get_py(y_val):
            if y_val > y_max: y_val = y_max
            if y_val < y_min: y_val = y_min
            return pad_t + (y_max - y_val) / y_range * plot_h

        step_x = math.pi / (2 * max(1, round(self.zoom_level)))
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

        step_y = max(1, int(y_max / 5))
        y_val = int(y_min)
        while y_val <= y_max:
            py = get_py(y_val)
            self.canvas.create_line(pad_l, py, pad_l + plot_w, py, fill=GRID_COL)
            if y_val != 0:
                self.canvas.create_text(pad_l - 15, py, text=str(y_val), anchor="e", font=("Consolas", 10), fill=SUBTLE)
            y_val += step_y

        py0 = get_py(0)
        self.canvas.create_line(pad_l, py0, pad_l + plot_w + 20, py0, fill=AXIS_COL, arrow=tk.LAST, width=2)
        self.canvas.create_text(pad_l + plot_w + 30, py0, text="t", font=("Times New Roman", 16, "italic"),
                                fill=AXIS_COL)

        px0 = get_px(0)
        self.canvas.create_line(px0, pad_t + plot_h + 20, px0, pad_t - 20, fill=AXIS_COL, arrow=tk.LAST, width=2)
        self.canvas.create_text(px0, pad_t - 30, text="y", font=("Times New Roman", 16, "italic"), fill=AXIS_COL)

        self.wave_lines = []
        for idx in range(5):
            amp, freq = self.harmonics[idx]
            points = []
            for px in range(int(pad_l) - 10, int(pad_l + plot_w) + 10, 2):
                t_val = x_min + (px - pad_l) / plot_w * x_range
                y_val = amp * math.sin(freq * t_val)
                py = get_py(y_val)
                points.extend([px, py])
            line = self.canvas.create_line(points, fill=COLORS[idx], width=2)
            self.wave_lines.append(line)

        points_sum = []
        for px in range(int(pad_l) - 10, int(pad_l + plot_w) + 10, 2):
            t_val = x_min + (px - pad_l) / plot_w * x_range
            y_val = sum(amp * math.sin(freq * t_val) for amp, freq in self.harmonics)
            py = get_py(y_val)
            points_sum.extend([px, py])

        sum_line = self.canvas.create_line(points_sum, fill=SUM_COL, width=4, smooth=True, capstyle="round",
                                           joinstyle="round")
        self.wave_lines.append(sum_line)


if __name__ == "__main__":
    root = tk.Tk()
    app = HarmonicsSumApp(root)
    root.mainloop()