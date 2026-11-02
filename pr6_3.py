import random
import tkinter as tk

# ---------- Палитра ----------
BG = "#12121a"
PANEL = "#1c1c26"
CARD = "#242433"
CARD_EDGE = "#33334d"
TEXT = "#e2e2e9"
SUBTLE = "#8a8a9e"
ACCENT = "#7aa2f7"
GREEN = "#9ece6a"
GREEN_BG = "#2b3a2b"
RED = "#f7768e"
RED_BG = "#3d252b"
YELLOW = "#e0af68"
CYAN = "#7dcfff"
PINK = "#bb9af7"

FONT_MAIN = "Segoe UI"
FONT_MONO = "Consolas"


class BitStateApp:
    def __init__(self, root):
        self.root = root
        self.root.title("32-bit State Machine & Checksum")
        self.root.configure(bg=BG)

        # Устанавливаем минимальный размер, чтобы ничего не сжималось
        self.root.geometry("1150x650")
        self.root.minsize(950, 550)

        self.bytes_data = [0, 0, 0, 0]
        self.prev_checksum = 0

        self._build_ui()
        self.generate_random()

    def _build_ui(self):
        # Главный контейнер на весь экран с отступами
        self.main_frame = tk.Frame(self.root, bg=BG)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Распределяем место: верхняя панель, плашка инфо, карточки, нижняя панель
        self.main_frame.rowconfigure(0, weight=0)  # Заголовок и кнопки
        self.main_frame.rowconfigure(1, weight=0)  # HEX/DEC байтов
        self.main_frame.rowconfigure(2, weight=1)  # Карточки (растягиваются)
        self.main_frame.rowconfigure(3, weight=0)  # Контрольная сумма
        self.main_frame.columnconfigure(0, weight=1)

        # ----- 1. Верхняя панель -----
        top = tk.Frame(self.main_frame, bg=BG)
        top.grid(row=0, column=0, sticky="ew", pady=(0, 15))

        tk.Label(
            top, text="32-BIT STATE MACHINE",
            font=(FONT_MAIN, 18, "bold"),
            fg=ACCENT, bg=BG,
        ).pack(side="left")

        self._button(top, "RANDOM", self.generate_random, ACCENT).pack(side="right", padx=(10, 0))
        self._button(top, "CLEAR", self.clear_all, RED).pack(side="right", padx=(10, 0))
        self._button(top, "INVERT", self.invert_all, YELLOW).pack(side="right")

        # ----- 2. Плашка с байтами (HEX / DEC) -----
        info = tk.Frame(self.main_frame, bg=PANEL, highlightbackground=CARD_EDGE, highlightthickness=1)
        info.grid(row=1, column=0, sticky="ew", pady=(0, 15))

        self.hex_lbl = tk.Label(info, text="", font=(FONT_MONO, 14, "bold"), fg=CYAN, bg=PANEL, anchor="w", padx=15,
                                pady=12)
        self.hex_lbl.pack(side="left")

        self.dec_lbl = tk.Label(info, text="", font=(FONT_MONO, 14), fg=PINK, bg=PANEL, anchor="e", padx=15, pady=12)
        self.dec_lbl.pack(side="right")

        # ----- 3. Сетка для 4 карточек -----
        self.bytes_frame = tk.Frame(self.main_frame, bg=BG)
        self.bytes_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 15))

        for col in range(4):
            self.bytes_frame.columnconfigure(col, weight=1, uniform="byte")
        self.bytes_frame.rowconfigure(0, weight=1)

        # ----- 4. Нижняя панель: Контрольная сумма -----
        csum_frame = tk.Frame(self.main_frame, bg=PANEL, highlightbackground=CARD_EDGE, highlightthickness=2)
        csum_frame.grid(row=3, column=0, sticky="ew")

        # Индикатор изменения (кружок)
        self.indicator = tk.Canvas(csum_frame, width=20, height=20, bg=PANEL, highlightthickness=0)
        self.indicator.pack(side="left", padx=(20, 10), pady=15)
        self.ind_circle = self.indicator.create_oval(4, 4, 16, 16, fill=SUBTLE, outline="")

        tk.Label(csum_frame, text="CHECKSUM:", font=(FONT_MAIN, 14, "bold"), fg=TEXT, bg=PANEL).pack(side="left",
                                                                                                     pady=15)

        self.csum_lbl = tk.Label(csum_frame, text="", font=(FONT_MONO, 16, "bold"), fg=ACCENT, bg=PANEL)
        self.csum_lbl.pack(side="left", padx=20, pady=15)

        # Подсказка
        tk.Label(csum_frame, text="(измените любой бит для проверки)", font=(FONT_MAIN, 10), fg=SUBTLE, bg=PANEL).pack(
            side="right", padx=20, pady=15)

    def _button(self, parent, text, cmd, color):
        btn = tk.Button(
            parent, text=text, command=cmd,
            font=(FONT_MAIN, 10, "bold"),
            bg=color, fg=BG,
            activebackground="#ffffff", activeforeground=BG,
            relief="flat", bd=0, padx=18, pady=8,
            cursor="hand2",
        )
        btn.bind("<Enter>", lambda e: btn.config(bg="#ffffff"))
        btn.bind("<Leave>", lambda e: btn.config(bg=color))
        return btn

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
        # Пересоздаем карточки байтов
        for w in self.bytes_frame.winfo_children():
            w.destroy()

        for i, v in enumerate(self.bytes_data):
            self._render_byte(i, v)

        # Обновляем общую плашку
        self.hex_lbl.config(text="HEX   " + "    ".join(f"0x{b:02X}" for b in self.bytes_data))
        self.dec_lbl.config(text="    ".join(f"{b:>3}" for b in self.bytes_data) + "   DEC")

        # Вычисление контрольной суммы (сумма всех байтов)
        checksum = sum(self.bytes_data)

        # Форматирование: DEC и HEX
        csum_hex = f"0x{checksum:02X}"
        csum_dec = f"{checksum}"

        self.csum_lbl.config(text=f"{csum_dec}  ({csum_hex})")

        # Визуальная проверка изменения
        if checksum != self.prev_checksum:
            self.indicator.itemconfig(self.ind_circle, fill=GREEN)  # Зеленый - изменилась
        else:
            self.indicator.itemconfig(self.ind_circle, fill=SUBTLE)  # Серый - без изменений

        self.prev_checksum = checksum

    def _render_byte(self, idx, value):
        card = tk.Frame(self.bytes_frame, bg=CARD, highlightbackground=CARD_EDGE, highlightthickness=1)
        card.grid(row=0, column=idx, sticky="nsew", padx=8, pady=8)

        # Внутренний контейнер для центрирования контента
        inner = tk.Frame(card, bg=CARD)
        inner.pack(expand=True)

        head = tk.Frame(inner, bg=CARD)
        head.pack(fill="x", padx=15, pady=(15, 5))

        tk.Label(head, text=f"BYTE {idx + 1}", font=(FONT_MAIN, 12, "bold"), fg=ACCENT, bg=CARD).pack(side="left")

        # ДВОИЧНЫЙ ВИД (по заданию)
        bin_str = format(value, "08b")
        pretty = f"{bin_str[:4]} {bin_str[4:]}"
        tk.Label(inner, text=pretty, font=(FONT_MONO, 26, "bold"), fg=TEXT, bg=CARD).pack(pady=(5, 10))

        # Тумблеры
        row = tk.Frame(inner, bg=CARD)
        row.pack(pady=(0, 15))

        sw_frame = tk.Frame(row, bg=CARD)
        sw_frame.pack()

        for bit_pos in range(7, -1, -1):
            bit_val = (value >> bit_pos) & 1
            self._switch(sw_frame, idx, bit_pos, bit_val)

    def _switch(self, parent, byte_idx, bit_pos, bit_val):
        col = tk.Frame(parent, bg=CARD)
        col.pack(side="left", padx=4)

        tk.Label(col, text=f"b{bit_pos}", font=(FONT_MONO, 9), fg=SUBTLE, bg=CARD).pack()

        W, H = 28, 48
        cv = tk.Canvas(col, width=W, height=H, bg=CARD, highlightthickness=0, cursor="hand2")
        cv.pack(pady=2)

        if bit_val:
            cv.create_rectangle(2, 2, W - 2, H - 2, fill=GREEN_BG, outline=GREEN, width=2)
            cv.create_oval(6, 6, W - 6, 22, fill=GREEN, outline=GREEN)
        else:
            cv.create_rectangle(2, 2, W - 2, H - 2, fill=RED_BG, outline=RED, width=2)
            cv.create_oval(6, H - 22, W - 6, H - 6, fill=RED, outline=RED)

        lbl = tk.Label(col, text="1" if bit_val else "0", font=(FONT_MONO, 11, "bold"), fg=GREEN if bit_val else RED,
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