import tkinter as tk
import math

# ---------- Палитра ----------
BG = "#ffffff"
GRID_COL = "#e5e5e5"
AXIS_COL = "#000000"
TEXT_COL = "#000000"
SIN_COL = "#ff2222"
COS_COL = "#2222ff"
PANEL = "#f4f4f9"
ACCENT = "#3b82f6"


class MathGraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Интерактивные графики sin(x) и cos(x)")
        self.root.configure(bg=BG)
        self.root.geometry("1100x700")
        self.root.minsize(800, 500)

        # --- Верхняя панель ---
        top = tk.Frame(self.root, bg=PANEL, pady=12)
        top.pack(fill="x", side="top")

        tk.Label(top, text="Графики Sin и Cos", font=("Segoe UI", 16, "bold"), fg=TEXT_COL, bg=PANEL).pack(side="left",
                                                                                                           padx=20)

        legend = tk.Frame(top, bg=PANEL)
        legend.pack(side="right", padx=20)
        tk.Label(legend, text="sin(x)", font=("Segoe UI", 11, "bold"), fg=SIN_COL, bg=PANEL).pack(side="left", padx=10)
        tk.Label(legend, text="cos(x)", font=("Segoe UI", 11, "bold"), fg=COS_COL, bg=PANEL).pack(side="left", padx=10)

        btn_frame = tk.Frame(top, bg=PANEL)
        btn_frame.pack(side="top", pady=5)

        # Кнопки приближения и отдаления (без "Сброса")
        self._btn(btn_frame, "🔍 Приблизить", lambda: self.zoom(1.5)).pack(side="left", padx=5)
        self._btn(btn_frame, "🔎 Отдалить", lambda: self.zoom(0.67)).pack(side="left", padx=5)

        # Подсказка вместо кнопки сброса
        tk.Label(btn_frame, text="(Двойной клик по графику — сброс)", font=("Segoe UI", 10, "italic"), fg="#888888",
                 bg=PANEL).pack(side="left", padx=15)

        # --- Холст ---
        self.canvas = tk.Canvas(self.root, bg=BG, highlightthickness=0, cursor="fleur")
        self.canvas.pack(fill="both", expand=True)

        self.canvas.bind("<Configure>", self.draw_graphs)
        self.canvas.bind("<MouseWheel>", self.on_wheel_zoom)
        self.canvas.bind("<Button-4>", self.on_wheel_zoom)
        self.canvas.bind("<Button-5>", self.on_wheel_zoom)

        # Перетаскивание (ЛКМ)
        self.canvas.bind("<ButtonPress-1>", self.on_pan_start)
        self.canvas.bind("<B1-Motion>", self.on_pan_move)

        # Двойной клик для сброса
        self.canvas.bind("<Double-Button-1>", lambda e: self.reset_view())

        self.reset_view()

    def _btn(self, parent, text, cmd, bg="#e0e0e0", fg="#000000"):
        return tk.Button(parent, text=text, command=cmd, font=("Segoe UI", 11, "bold"),
                         bg=bg, fg=fg, activebackground=bg, relief="flat",
                         padx=20, pady=6, cursor="hand2")

    def reset_view(self):
        self.x_min = 0
        self.x_max = 2 * math.pi
        self.y_min = -1.2
        self.y_max = 1.2
        self.draw_graphs()

    def zoom(self, factor):
        cx = (self.x_min + self.x_max) / 2
        cy = (self.y_min + self.y_max) / 2
        hx = (self.x_max - self.x_min) / 2
        hy = (self.y_max - self.y_min) / 2

        self.x_min = cx - hx / factor
        self.x_max = cx + hx / factor
        self.y_min = cy - hy / factor
        self.y_max = cy + hy / factor
        self.draw_graphs()

    def on_wheel_zoom(self, event):
        if event.num == 4 or event.delta > 0:
            self.zoom(1.2)
        else:
            self.zoom(0.8)

    def on_pan_start(self, event):
        self.pan_x = event.x
        self.pan_y = event.y

    def on_pan_move(self, event):
        dx = event.x - self.pan_x
        dy = event.y - self.pan_y
        self.pan_x = event.x
        self.pan_y = event.y

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()

        shift_x = (dx / w) * (self.x_max - self.x_min)
        shift_y = (dy / h) * (self.y_max - self.y_min)

        self.x_min -= shift_x
        self.x_max -= shift_x
        self.y_min += shift_y
        self.y_max += shift_y
        self.draw_graphs()

    def draw_graphs(self, event=None):
        self.canvas.delete("all")
        self.root.update_idletasks()

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 100 or h < 100: return

        pad_l, pad_r, pad_t, pad_b = 60, 40, 40, 60
        plot_w = w - pad_l - pad_r
        plot_h = h - pad_t - pad_b

        x_range = self.x_max - self.x_min
        y_range = self.y_max - self.y_min

        def get_px(x_val):
            return pad_l + (x_val - self.x_min) / x_range * plot_w

        def get_py(y_val):
            return pad_t + (self.y_max - y_val) / y_range * plot_h

        # --- Сетка ---
        step_x = self._nice_step(x_range)
        step_y = self._nice_step(y_range)

        x_val = math.ceil(self.x_min / step_x) * step_x
        while x_val <= self.x_max:
            px = get_px(x_val)
            self.canvas.create_line(px, pad_t, px, pad_t + plot_h, fill=GRID_COL)

            if abs(x_val) < 1e-5:
                label = "0"
            else:
                if abs(x_range - 2 * math.pi) < 0.1:
                    coef = x_val / math.pi
                    if abs(coef - round(coef)) < 1e-5:
                        label = f"{int(round(coef))}π"
                    elif abs(coef * 2 - round(coef * 2)) < 1e-5:
                        label = f"{int(round(coef * 2))}π/2"
                    elif abs(coef * 4 - round(coef * 4)) < 1e-5:
                        label = f"{int(round(coef * 4))}π/4"
                    else:
                        label = f"{coef:.1f}π"
                else:
                    label = f"{x_val:.2f}".rstrip('0').rstrip('.')

            self.canvas.create_text(px, pad_t + plot_h + 20, text=label, font=("Segoe UI", 11), fill=TEXT_COL)
            x_val += step_x

        y_val = math.ceil(self.y_min / step_y) * step_y
        while y_val <= self.y_max:
            py = get_py(y_val)
            self.canvas.create_line(pad_l, py, pad_l + plot_w, py, fill=GRID_COL)
            if abs(y_val) > 1e-5:
                label = f"{y_val:.2f}".rstrip('0').rstrip('.')
                self.canvas.create_text(pad_l - 15, py, text=label, anchor="e", font=("Segoe UI", 11), fill=TEXT_COL)
            y_val += step_y

        # --- Оси ---
        if self.y_min <= 0 <= self.y_max:
            py0 = get_py(0)
            self.canvas.create_line(pad_l, py0, pad_l + plot_w + 20, py0, fill=AXIS_COL, arrow=tk.LAST, width=2)
            self.canvas.create_text(pad_l + plot_w + 30, py0, text="x", font=("Times New Roman", 16, "italic"),
                                    fill=TEXT_COL)

        if self.x_min <= 0 <= self.x_max:
            px0 = get_px(0)
            self.canvas.create_line(px0, pad_t + plot_h + 20, px0, pad_t - 20, fill=AXIS_COL, arrow=tk.LAST, width=2)
            self.canvas.create_text(px0, pad_t - 30, text="y", font=("Times New Roman", 16, "italic"), fill=TEXT_COL)

        # --- Графики ---
        def plot_function(func, color):
            points = []
            # Шаг 1 пиксель, с запасом за края, чтобы не было обрывов
            for px in range(int(pad_l) - 20, int(pad_l + plot_w) + 20, 1):
                x_val = self.x_min + (px - pad_l) / plot_w * x_range
                y_val = func(x_val)
                py = get_py(y_val)
                points.extend([px, py])

            # smooth=True делает линию идеально гладкой, без "рваных" пикселей
            self.canvas.create_line(points, fill=color, width=3, smooth=True, capstyle="round", joinstyle="round")

        plot_function(math.sin, SIN_COL)
        plot_function(math.cos, COS_COL)

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
    app = MathGraphApp(root)
    root.mainloop()