import random
import tkinter as tk

# ---------- Палитра ----------
BG = "#1e1e2e"
PANEL = "#181825"
CARD = "#313244"
EDGE = "#45475a"
TEXT = "#cdd6f4"
SUBTLE = "#6c7086"
ACCENT = "#89b4fa"
GREEN = "#a6e3a1"
GREEN_BG = "#2d4a3e"
RED = "#f38ba8"
RED_BG = "#4a2d36"
YELLOW = "#f9e2af"
CYAN = "#89dceb"
PINK = "#f5c2e7"


class BitStateApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Моделирование битовых состояний — 32 переключателя")
        self.root.configure(bg=BG)

        # Размер окна, чтобы всё влезало
        self.root.geometry("1000x520")
        self.root.minsize(900, 480)  # Минимальный размер, чтобы не ломать верстку
        self.root.resizable(True, True)

        self.bytes_data = [0, 0, 0, 0]
        self._build_ui()
        self.generate_random()

    def _build_ui(self):
        # Главный контейнер
        self.main_frame = tk.Frame(self.root, bg=BG)
        self.main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # ----- Верхняя панель -----
        top = tk.Frame(self.main_frame, bg=BG)
        top.pack(fill="x", pady=(0, 15))

        tk.Label(
            top, text="◉  32-BIT STATE MACHINE",
            font=("Consolas", 18, "bold"),
            fg=ACCENT, bg=BG,
        ).pack(side="left")

        self._button(top, "🎲  RANDOM", self.generate_random, ACCENT).pack(side="right", padx=(8, 0))
        self._button(top, "⭘  CLEAR", self.clear_all, RED).pack(side="right", padx=(8, 0))
        self._button(top, "⇄  INVERT", self.invert_all, YELLOW).pack(side="right")

        # ----- Плашка HEX / DEC -----
        info = tk.Frame(self.main_frame, bg=PANEL, highlightbackground=EDGE, highlightthickness=1)
        info.pack(fill="x", pady=(0, 15))

        self.hex_lbl = tk.Label(info, text="", font=("Consolas", 13, "bold"), fg=CYAN, bg=PANEL, anchor="w", padx=15,
                                pady=10)
        self.hex_lbl.pack(side="left")

        self.dec_lbl = tk.Label(info, text="", font=("Consolas", 13), fg=PINK, bg=PANEL, anchor="e", padx=15, pady=10)
        self.dec_lbl.pack(side="right")

        # ----- Сетка для 4 карточек -----
        self.bytes_frame = tk.Frame(self.main_frame, bg=BG)
        self.bytes_frame.pack(fill="both", expand=True)

        # 4 колонки, одинаковый вес
        for col in range(4):
            self.bytes_frame.columnconfigure(col, weight=1, uniform="byte")
        self.bytes_frame.rowconfigure(0, weight=1)

    def _button(self, parent, text, cmd, color):
        return tk.Button(
            parent, text=text, command=cmd,
            font=("Consolas", 11, "bold"),
            bg=color, fg=BG,
            activebackground=color, activeforeground=BG,
            relief="flat", bd=0, padx=14, pady=8,
            cursor="hand2",
        )

    # ------------------- Логика -------------------
    def generate_random(self):
        self.bytes_data = [random.randint(0, 255) for _ in range(4)]
        self._refresh()

    def invert_all(self):
        self.bytes_data = [b ^ 0xFF for b in self.bytes_data]
        self._refresh()

    def clear_all(self):
        self.bytes_data = [0, 0, 0, 0]
        self._refresh()

    def toggle_bit(self, byte_idx, bit_pos):
        self.bytes_data[byte_idx] ^= (1 << bit_pos)
        self._refresh()

    # ------------------- Отрисовка -------------------
    def _refresh(self):
        for w in self.bytes_frame.winfo_children():
            w.destroy()

        for i, v in enumerate(self.bytes_data):
            self._render_byte(i, v)

        self.hex_lbl.config(text="HEX   " + "    ".join(f"0x{b:02X}" for b in self.bytes_data))
        self.dec_lbl.config(text="    ".join(f"{b:>3}" for b in self.bytes_data) + "   DEC")

    def _render_byte(self, idx, value):
        card = tk.Frame(self.bytes_frame, bg=CARD, highlightbackground=EDGE, highlightthickness=1)
        card.grid(row=0, column=idx, sticky="nsew", padx=6, pady=6)

        # Внутренний контейнер для центрирования
        inner = tk.Frame(card, bg=CARD)
        inner.pack(expand=True)

        head = tk.Frame(inner, bg=CARD)
        head.pack(fill="x", padx=12, pady=(12, 6))

        tk.Label(head, text=f"BYTE {idx + 1}", font=("Consolas", 12, "bold"), fg=ACCENT, bg=CARD).pack(side="left")
        tk.Label(head, text=f"0x{value:02X}", font=("Consolas", 12, "bold"), fg=SUBTLE, bg=CARD).pack(side="right")

        bin_str = format(value, "08b")
        pretty = f"{bin_str[:4]} {bin_str[4:]}"
        tk.Label(inner, text=pretty, font=("Consolas", 24, "bold"), fg=TEXT, bg=CARD).pack(pady=(6, 18))

        row = tk.Frame(inner, bg=CARD)
        row.pack(pady=(0, 20))

        sw_frame = tk.Frame(row, bg=CARD)
        sw_frame.pack()

        for bit_pos in range(7, -1, -1):
            bit_val = (value >> bit_pos) & 1
            self._switch(sw_frame, idx, bit_pos, bit_val)

    def _switch(self, parent, byte_idx, bit_pos, bit_val):
        col = tk.Frame(parent, bg=CARD)
        col.pack(side="left", padx=3)

        tk.Label(col, text=f"b{bit_pos}", font=("Consolas", 8), fg=SUBTLE, bg=CARD).pack()

        # Уменьшил размер тумблеров, чтобы точно влезали
        W, H = 26, 46
        cv = tk.Canvas(col, width=W, height=H, bg=CARD, highlightthickness=0, cursor="hand2")
        cv.pack(pady=2)

        if bit_val:
            cv.create_rectangle(2, 2, W - 2, H - 2, fill=GREEN_BG, outline=GREEN, width=2)
            cv.create_oval(6, 6, W - 6, 22, fill=GREEN, outline=GREEN)
        else:
            cv.create_rectangle(2, 2, W - 2, H - 2, fill=RED_BG, outline=RED, width=2)
            cv.create_oval(6, H - 22, W - 6, H - 6, fill=RED, outline=RED)

        lbl = tk.Label(col, text="1" if bit_val else "0", font=("Consolas", 10, "bold"), fg=GREEN if bit_val else RED,
                       bg=CARD)
        lbl.pack()

        def click(_e):
            self.toggle_bit(byte_idx, bit_pos)

        cv.bind("<Button-1>", click)
        lbl.bind("<Button-1>", click)


if __name__ == "__main__":
    root = tk.Tk()
    app = BitStateApp(root)
    root.mainloop()