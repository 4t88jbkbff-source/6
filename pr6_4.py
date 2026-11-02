import random
import tkinter as tk
from tkinter import ttk

# ---------- Палитра (Осциллограф) ----------
BG = "#121212"
PANEL = "#1e1e1e"
GRAPH_BG = "#0a0a0a"
GRID_COLOR = "#2a2a2a"
TEXT = "#e0e0e0"
SUBTLE = "#888888"
ACCENT = "#007acc"

C_NRZ = "#00ff88"
C_MAN = "#00ccff"
C_AMI = "#ff00ff"
C_MLT = "#ffaa00"
C_RZ = "#ff3333"


class LineCodingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Анализатор физического кодирования")
        self.root.configure(bg=BG)
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)

        self.bits = [0] * 32
        self.bit_buttons = []

        self._setup_styles()
        self._build_ui()
        self.generate_random()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('default')
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=PANEL, foreground=SUBTLE,
                        padding=[20, 8], font=("Segoe UI", 11, "bold"), borderwidth=0)
        style.map("TNotebook.Tab", background=[("selected", GRAPH_BG)],
                  foreground=[("selected", ACCENT)])

    def _build_ui(self):
        # ----- Верхняя панель управления -----
        top = tk.Frame(self.root, bg=BG)
        top.pack(fill="x", padx=20, pady=15)

        tk.Label(top, text="SIGNAL ANALYZER", font=("Segoe UI", 20, "bold"), fg=TEXT, bg=BG).pack(side="left")

        self._button(top, "GENERATE RANDOM", self.generate_random, ACCENT, "#ffffff").pack(side="right", padx=(10, 0))
        self._button(top, "CLEAR (0)", self.clear_bits, "#333333", TEXT).pack(side="right", padx=(10, 0))
        self._button(top, "INVERT ALL", self.invert_bits, "#333333", TEXT).pack(side="right")

        # ----- Панель интерактивных битов (Кнопок-переключателей) -----
        bit_panel = tk.Frame(self.root, bg=PANEL, pady=10, padx=10)
        bit_panel.pack(fill="x", padx=20, pady=(0, 15))

        for i in range(32):
            # Создаем кнопку для каждого бита
            btn = tk.Button(bit_panel, text="0", font=("Consolas", 12, "bold"),
                            width=2, relief="flat", bd=0, cursor="hand2",
                            command=lambda idx=i: self.toggle_bit(idx))
            btn.pack(side="left", padx=2, expand=True, fill="x")
            self.bit_buttons.append(btn)

            # Добавляем визуальный отступ между байтами (каждые 8 бит)
            if (i + 1) % 8 == 0 and i != 31:
                tk.Frame(bit_panel, bg=PANEL, width=15).pack(side="left")

        # ----- Вкладки (Tab Control) -----
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.tabs = {
            "NRZ": {"color": C_NRZ, "canvas": None, "title": "NRZ (Non-Return to Zero)"},
            "Manchester": {"color": C_MAN, "canvas": None, "title": "Manchester (Манчестерское)"},
            "AMI": {"color": C_AMI, "canvas": None, "title": "AMI (Alternate Mark Inversion)"},
            "MLT-3": {"color": C_MLT, "canvas": None, "title": "MLT-3 (Multi-Level Transmit)"},
            "RZ": {"color": C_RZ, "canvas": None, "title": "RZ (Return to Zero / Импульсное)"}
        }

        for key, data in self.tabs.items():
            frame = tk.Frame(self.notebook, bg=GRAPH_BG)
            self.notebook.add(frame, text=f"  {key}  ")

            canvas = tk.Canvas(frame, bg=GRAPH_BG, highlightthickness=0)
            canvas.pack(fill="both", expand=True, padx=10, pady=10)
            data["canvas"] = canvas
            canvas.bind("<Configure>", lambda e, k=key: self._draw_single_graph(k))

    def _button(self, parent, text, cmd, bg_color, fg_color):
        return tk.Button(parent, text=text, command=cmd, font=("Segoe UI", 10, "bold"),
                         bg=bg_color, fg=fg_color, activebackground=bg_color, activeforeground=fg_color,
                         relief="flat", bd=0, padx=15, pady=8, cursor="hand2")

    # ------------------- Логика -------------------
    def generate_random(self):
        self.bits = [random.choice([0, 1]) for _ in range(32)]
        self._update_ui()

    def clear_bits(self):
        self.bits = [0] * 32
        self._update_ui()

    def invert_bits(self):
        self.bits = [1 - b for b in self.bits]
        self._update_ui()

    def toggle_bit(self, idx):
        # Инвертируем конкретный бит
        self.bits[idx] = 1 - self.bits[idx]
        self._update_ui()

    def _update_ui(self):
        # Обновляем цвета и текст на кнопках-переключателях
        for i, bit in enumerate(self.bits):
            btn = self.bit_buttons[i]
            btn.config(text=str(bit))
            if bit == 1:
                btn.config(bg="#00ff88", fg="#121212", activebackground="#00cc66")  # Зеленый
            else:
                btn.config(bg="#2a2a2a", fg="#888888", activebackground="#444444")  # Серый

        # Перерисовываем графики
        for key in self.tabs.keys():
            self._draw_single_graph(key)

    # ------------------- Отрисовка Графиков -------------------
    def _draw_single_graph(self, mode):
        canvas = self.tabs[mode]["canvas"]
        color = self.tabs[mode]["color"]
        title = self.tabs[mode]["title"]

        canvas.delete("all")
        self.root.update_idletasks()

        w = canvas.winfo_width()
        h = canvas.winfo_height()
        if w < 50 or h < 50: return

        pad_l, pad_r, pad_t, pad_b = 60, 40, 40, 40
        plot_w = w - pad_l - pad_r
        plot_h = h - pad_t - pad_b
        mid_y = pad_t + plot_h / 2
        step_x = plot_w / 32

        canvas.create_text(pad_l, pad_t - 20, text=title, fill=color, anchor="w", font=("Segoe UI", 14, "bold"))

        for i in range(33):
            x = pad_l + i * step_x
            canvas.create_line(x, pad_t, x, pad_t + plot_h, fill=GRID_COLOR, width=1 if i % 8 != 0 else 2)

        canvas.create_line(pad_l, pad_t, pad_l + plot_w, pad_t, fill=GRID_COLOR)
        canvas.create_line(pad_l, mid_y, pad_l + plot_w, mid_y, fill=GRID_COLOR)
        canvas.create_line(pad_l, pad_t + plot_h, pad_l + plot_w, pad_t + plot_h, fill=GRID_COLOR)

        canvas.create_text(pad_l - 15, pad_t + 5, text="+1", fill=SUBTLE, anchor="e", font=("Consolas", 12))
        canvas.create_text(pad_l - 15, mid_y, text="0", fill=SUBTLE, anchor="e", font=("Consolas", 12))
        canvas.create_text(pad_l - 15, pad_t + plot_h - 5, text="-1", fill=SUBTLE, anchor="e", font=("Consolas", 12))

        # Подписи битов под графиком
        for i in range(32):
            x = pad_l + i * step_x + step_x / 2
            canvas.create_text(x, pad_t + plot_h + 15, text=str(self.bits[i]),
                               fill=ACCENT if self.bits[i] == 1 else SUBTLE, font=("Consolas", 10, "bold"))

        def get_y(val):
            if val == 1: return pad_t + 10
            if val == -1: return pad_t + plot_h - 10
            return mid_y

        def draw_line(points):
            pts = []
            for pt in points:
                pts.extend([pad_l + pt[0] * step_x, get_y(pt[1])])
            if len(pts) >= 4:
                canvas.create_line(*pts, fill=color, width=4, joinstyle="miter")
                canvas.create_line(*pts, fill="#ffffff", width=1.5, joinstyle="miter")

        x, y = [], []
        if mode == "NRZ":
            for i, bit in enumerate(self.bits):
                level = 1 if bit == 1 else -1
                x.extend([i, i + 1]);
                y.extend([level, level])

        elif mode == "Manchester":
            for i, bit in enumerate(self.bits):
                if bit == 0:
                    x.extend([i, i + 0.5, i + 0.5, i + 1]);
                    y.extend([-1, -1, 1, 1])
                else:
                    x.extend([i, i + 0.5, i + 0.5, i + 1]);
                    y.extend([1, 1, -1, -1])

        elif mode == "AMI":
            polarity = 1
            for i, bit in enumerate(self.bits):
                level = 0
                if bit == 1:
                    level = polarity
                    polarity *= -1
                x.extend([i, i + 1]);
                y.extend([level, level])

        elif mode == "MLT-3":
            state = 1
            for i, bit in enumerate(self.bits):
                if bit == 1:
                    if state == 1:
                        state = 0
                    elif state == 0:
                        state = -1
                    elif state == -1:
                        state = 1
                x.extend([i, i + 1]);
                y.extend([state, state])

        elif mode == "RZ":
            for i, bit in enumerate(self.bits):
                if bit == 1:
                    x.extend([i, i + 0.5, i + 0.5, i + 1]);
                    y.extend([1, 1, 0, 0])
                else:
                    x.extend([i, i + 1]);
                    y.extend([0, 0])

        draw_line(list(zip(x, y)))


if __name__ == "__main__":
    root = tk.Tk()
    app = LineCodingApp(root)
    root.mainloop()