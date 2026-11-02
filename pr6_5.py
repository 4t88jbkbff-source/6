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
RED = "#f7768e"
YELLOW = "#e0af68"
CYAN = "#7dcfff"
PINK = "#bb9af7"


class KeyCodeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Коды клавиш")
        self.root.configure(bg=BG)

        # Теперь окно можно разворачивать на весь экран и растягивать
        self.root.geometry("750x550")
        self.root.minsize(600, 400)

        self._build_ui()
        self.root.bind("<KeyPress>", self.on_key_press)
        self.root.focus_set()

    def _build_ui(self):
        # Настраиваем главную сетку так, чтобы все строки и колонки растягивались
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=0)  # Заголовок
        self.root.rowconfigure(1, weight=1)  # Дисплей символа (растягивается)
        self.root.rowconfigure(2, weight=2)  # Таблица (растягивается сильнее)

        # ----- Заголовок -----
        tk.Label(
            self.root, text="Нажмите любую клавишу",
            font=("Segoe UI", 16, "bold"), fg=ACCENT, bg=BG,
        ).grid(row=0, column=0, pady=(15, 5))

        # ----- Дисплей символа (растягивается) -----
        display = tk.Frame(self.root, bg=PANEL, highlightbackground=CARD_EDGE, highlightthickness=1)
        display.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)

        display.rowconfigure(0, weight=1)
        display.rowconfigure(1, weight=0)
        display.columnconfigure(0, weight=1)

        self.char_lbl = tk.Label(display, text="—", font=("Consolas", 70, "bold"), fg=GREEN, bg=PANEL)
        self.char_lbl.grid(row=0, column=0, sticky="nsew")

        self.key_name_lbl = tk.Label(display, text="Ожидание ввода...", font=("Consolas", 12), fg=SUBTLE, bg=PANEL)
        self.key_name_lbl.grid(row=1, column=0, pady=(0, 15))

        # ----- Таблица (растягивается) -----
        table = tk.Frame(self.root, bg=BG)
        table.grid(row=2, column=0, sticky="nsew", padx=20, pady=(5, 20))

        # Настраиваем колонки и строки таблицы
        table.columnconfigure(0, weight=2)  # Название системы
        table.columnconfigure(1, weight=1)  # DEC
        table.columnconfigure(2, weight=1)  # HEX
        table.columnconfigure(3, weight=1)  # Символ

        table.rowconfigure(0, weight=0)  # Заголовки
        for i in range(1, 5):
            table.rowconfigure(i, weight=1)  # Строки с данными (растягиваются поровну)

        # Заголовки
        headers = ["Система", "Код (DEC)", "Код (HEX)", "Символ"]
        for col, text in enumerate(headers):
            tk.Label(
                table, text=text, font=("Segoe UI", 12, "bold"),
                fg=ACCENT, bg=BG,
            ).grid(row=0, column=col, pady=(0, 8), sticky="nsew")

        self.row_labels = {}
        encodings = [
            ("ASCII", "ascii"),
            ("Unicode", "unicode"),
            ("Windows-1251", "cp1251"),
            ("CP866 (DOS)", "cp866"),
        ]

        for row, (title, key) in enumerate(encodings, start=1):
            tk.Label(
                table, text=title, font=("Consolas", 13, "bold"),
                fg=TEXT, bg=CARD, relief="flat",
            ).grid(row=row, column=0, padx=2, pady=2, sticky="nsew")

            dec_lbl = tk.Label(table, text="—", font=("Consolas", 14, "bold"), fg=CYAN, bg=CARD)
            hex_lbl = tk.Label(table, text="—", font=("Consolas", 14, "bold"), fg=PINK, bg=CARD)
            sym_lbl = tk.Label(table, text="—", font=("Consolas", 16, "bold"), fg=YELLOW, bg=CARD)

            dec_lbl.grid(row=row, column=1, padx=2, pady=2, sticky="nsew")
            hex_lbl.grid(row=row, column=2, padx=2, pady=2, sticky="nsew")
            sym_lbl.grid(row=row, column=3, padx=2, pady=2, sticky="nsew")

            self.row_labels[key] = (dec_lbl, hex_lbl, sym_lbl)

    # ------------------- Логика -------------------
    def on_key_press(self, event):
        char = event.char
        key_sym = event.keysym

        special_keys = {
            "Escape": "ESC", "Return": "ENTER", "space": "SPACE",
            "Tab": "TAB", "BackSpace": "BACKSPACE", "Delete": "DELETE",
            "Left": "←", "Right": "→", "Up": "↑", "Down": "↓",
            "Shift_L": "SHIFT", "Shift_R": "SHIFT", "Control_L": "CTRL",
            "Control_R": "CTRL", "Alt_L": "ALT", "Alt_R": "ALT",
            "Caps_Lock": "CAPS", "F1": "F1", "F2": "F2", "F3": "F3",
            "F4": "F4", "F5": "F5", "F6": "F6", "F7": "F7",
            "F8": "F8", "F9": "F9", "F10": "F10", "F11": "F11", "F12": "F12",
        }

        if key_sym in special_keys:
            self._show_special(special_keys[key_sym], key_sym)
            return

        if not char or len(char) != 1:
            return

        self.char_lbl.config(text=char, fg=GREEN)
        self.key_name_lbl.config(text=f"Клавиша: {key_sym}   |   Символ: «{char}»")

        unicode_code = ord(char)
        ascii_code = unicode_code if unicode_code < 128 else None

        try:
            cp1251_code = char.encode("cp1251")[0]
        except UnicodeEncodeError:
            cp1251_code = None

        try:
            cp866_code = char.encode("cp866")[0]
        except UnicodeEncodeError:
            cp866_code = None

        self._update_row("unicode", unicode_code, char)
        self._update_row("ascii", ascii_code, char)
        self._update_row("cp1251", cp1251_code, char)
        self._update_row("cp866", cp866_code, char)

    def _update_row(self, key, code, char):
        dec_lbl, hex_lbl, sym_lbl = self.row_labels[key]
        if code is None:
            dec_lbl.config(text="—", fg=RED)
            hex_lbl.config(text="—", fg=RED)
            sym_lbl.config(text="N/A", fg=RED)
        else:
            dec_lbl.config(text=str(code), fg=CYAN)
            hex_lbl.config(text=f"0x{code:02X}", fg=PINK)
            try:
                decoded = bytes([code]).decode(key if key != "unicode" else "utf-8", errors="replace")
            except Exception:
                decoded = "?"
            sym_lbl.config(text=decoded, fg=YELLOW)

    def _show_special(self, display_name, key_sym):
        self.char_lbl.config(text=display_name, fg=YELLOW)
        self.key_name_lbl.config(text=f"Служебная клавиша: {key_sym}")

        for key in self.row_labels:
            dec_lbl, hex_lbl, sym_lbl = self.row_labels[key]
            dec_lbl.config(text="—", fg=SUBTLE)
            hex_lbl.config(text="—", fg=SUBTLE)
            sym_lbl.config(text="N/A", fg=SUBTLE)


if __name__ == "__main__":
    root = tk.Tk()
    app = KeyCodeApp(root)
    root.mainloop()