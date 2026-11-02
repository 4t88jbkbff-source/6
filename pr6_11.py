import tkinter as tk
import base64

# ---------- Палитра (Catppuccin) ----------
BG = "#1e1e2e"
PANEL = "#181825"
CARD = "#313244"
TEXT = "#cdd6f4"
SUBTLE = "#a6adc8"
ACCENT = "#89b4fa"
GREEN = "#a6e3a1"


class CodeCalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Калькулятор кодов")
        self.root.configure(bg=BG)
        self.root.geometry("1000x550")
        self.root.minsize(800, 450)

        self.mode = "encode"
        self.encoding = "UTF-8"
        self.format = "hex"

        self.enc_btns = {}
        self.fmt_btns = {}
        self.mode_btns = {}

        self._build_ui()
        self.update_ui_state()

        self.input_text.insert("1.0", "Привет, мир!")
        self.process()

    def _build_ui(self):
        # --- 1. Верхняя панель (Настройки) ---
        top = tk.Frame(self.root, bg=PANEL, padx=20, pady=15)
        top.pack(fill="x", padx=20, pady=(20, 15))

        # Настраиваем 3 колонки, чтобы они делили ширину поровну
        top.columnconfigure(0, weight=1)
        top.columnconfigure(1, weight=1)
        top.columnconfigure(2, weight=1)

        # === КОЛОНКА 1: РЕЖИМ ===
        col1 = tk.Frame(top, bg=PANEL)
        col1.grid(row=0, column=0, sticky="ew", padx=10)
        tk.Label(col1, text="РЕЖИМ:", font=("Segoe UI", 9, "bold"), fg=SUBTLE, bg=PANEL).pack(anchor="w", pady=(0, 5))

        mode_frame = tk.Frame(col1, bg=PANEL)
        mode_frame.pack(fill="x")

        self.mode_btns["encode"] = self._create_btn(mode_frame, "Текст ➔ Код", lambda: self.set_mode("encode"))
        self.mode_btns["encode"].pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.mode_btns["decode"] = self._create_btn(mode_frame, "Код ➔ Текст", lambda: self.set_mode("decode"))
        self.mode_btns["decode"].pack(side="left", fill="x", expand=True)

        # === КОЛОНКА 2: КОДИРОВКА ===
        col2 = tk.Frame(top, bg=PANEL)
        col2.grid(row=0, column=1, sticky="ew", padx=10)
        tk.Label(col2, text="КОДИРОВКА:", font=("Segoe UI", 9, "bold"), fg=SUBTLE, bg=PANEL).pack(anchor="w",
                                                                                                  pady=(0, 5))

        enc_frame = tk.Frame(col2, bg=PANEL)
        enc_frame.pack(fill="x")

        encodings = ["UTF-8", "Windows-1251", "KOI8-R", "ISO-8859-1", "ASCII", "Base64"]
        for i, enc in enumerate(encodings):
            btn = self._create_btn(enc_frame, enc, lambda e=enc: self.set_encoding(e))
            btn.grid(row=i // 3, column=i % 3, sticky="ew", padx=2, pady=2)
            self.enc_btns[enc] = btn

        for i in range(3):
            enc_frame.columnconfigure(i, weight=1)

        # === КОЛОНКА 3: ФОРМАТ ===
        col3 = tk.Frame(top, bg=PANEL)
        col3.grid(row=0, column=2, sticky="ew", padx=10)
        self.fmt_label = tk.Label(col3, text="ФОРМАТ:", font=("Segoe UI", 9, "bold"), fg=SUBTLE, bg=PANEL)
        self.fmt_label.pack(anchor="w", pady=(0, 5))

        self.fmt_frame = tk.Frame(col3, bg=PANEL)
        self.fmt_frame.pack(fill="x")

        for i, (name, val) in enumerate([("Hex", "hex"), ("Bin", "bin"), ("Dec", "dec")]):
            btn = self._create_btn(self.fmt_frame, name, lambda v=val: self.set_format(v))
            btn.grid(row=0, column=i, sticky="ew", padx=2)
            self.fmt_btns[val] = btn

        for i in range(3):
            self.fmt_frame.columnconfigure(i, weight=1)

        # --- 2. Рабочая область (Ввод/Вывод) ---
        work = tk.Frame(self.root, bg=BG)
        work.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        work.columnconfigure(0, weight=1)
        work.columnconfigure(1, weight=1)
        work.rowconfigure(1, weight=1)

        # Ввод
        tk.Label(work, text="ВВОД", font=("Segoe UI", 10, "bold"), fg=SUBTLE, bg=BG).grid(row=0, column=0, sticky="w",
                                                                                          pady=(0, 5))
        self.input_text = tk.Text(work, font=("Consolas", 13), bg=CARD, fg=TEXT,
                                  insertbackground=TEXT, relief="flat", padx=10, pady=10, wrap="word",
                                  highlightthickness=1, highlightbackground=CARD, highlightcolor=ACCENT)
        self.input_text.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        self.input_text.bind("<KeyRelease>", lambda e: self.process())

        # Вывод
        tk.Label(work, text="РЕЗУЛЬТАТ", font=("Segoe UI", 10, "bold"), fg=GREEN, bg=BG).grid(row=0, column=1,
                                                                                              sticky="w", pady=(0, 5),
                                                                                              padx=(10, 0))
        self.output_text = tk.Text(work, font=("Consolas", 13), bg=CARD, fg=GREEN,
                                   relief="flat", padx=10, pady=10, wrap="word",
                                   highlightthickness=1, highlightbackground=CARD, highlightcolor=ACCENT)
        self.output_text.grid(row=1, column=1, sticky="nsew", padx=(10, 0))

        # --- 3. Нижняя панель (Кнопка) ---
        bottom_frame = tk.Frame(self.root, bg=BG)
        bottom_frame.pack(fill="x", padx=20, pady=(0, 20))

        self.btn_copy = tk.Button(bottom_frame, text="📋 Скопировать результат", command=self.copy_result,
                                  font=("Segoe UI", 11, "bold"), bg=ACCENT, fg=BG,
                                  activebackground=ACCENT, activeforeground=BG,
                                  relief="flat", bd=0, cursor="hand2", pady=8, padx=30)
        self.btn_copy.pack(side="right")

    def _create_btn(self, parent, text, cmd, bg_color=PANEL, fg_color=TEXT):
        return tk.Button(parent, text=text, command=cmd, font=("Segoe UI", 10),
                         bg=bg_color, fg=fg_color, activebackground=ACCENT, activeforeground=BG,
                         relief="flat", bd=0, cursor="hand2", padx=5, pady=6)

    # --- Логика ---
    def set_mode(self, mode):
        self.mode = mode
        self.update_ui_state()
        self.process()

    def set_encoding(self, enc):
        self.encoding = enc
        self.update_ui_state()
        self.process()

    def set_format(self, fmt):
        self.format = fmt
        self.update_ui_state()
        self.process()

    def update_ui_state(self):
        for m, btn in self.mode_btns.items():
            btn.config(bg=ACCENT if m == self.mode else CARD, fg=BG if m == self.mode else TEXT)

        if self.mode == "encode":
            self.fmt_label.pack(anchor="w", pady=(0, 5))
            self.fmt_frame.pack(fill="x")
            self.output_text.config(fg=GREEN)
        else:
            self.fmt_label.pack_forget()
            self.fmt_frame.pack_forget()
            self.output_text.config(fg=ACCENT)

        for enc, btn in self.enc_btns.items():
            btn.config(bg=ACCENT if enc == self.encoding else CARD, fg=BG if enc == self.encoding else TEXT)

        for fmt, btn in self.fmt_btns.items():
            btn.config(bg=ACCENT if fmt == self.format else CARD, fg=BG if fmt == self.format else TEXT)

    def process(self):
        input_str = self.input_text.get("1.0", tk.END).strip()
        self.output_text.delete("1.0", tk.END)
        if not input_str: return

        try:
            if self.mode == "encode":
                self._encode(input_str)
            else:
                self._decode(input_str)
        except Exception as e:
            self.output_text.insert(tk.END, f"Ошибка:\n{str(e)}")

    def _encode(self, text):
        if self.encoding == "Base64":
            self.output_text.insert(tk.END, base64.b64encode(text.encode('utf-8')).decode('utf-8'))
            return
        py_enc = self.encoding.lower()
        if py_enc == "windows-1251": py_enc = "cp1251"

        try:
            b = text.encode(py_enc)
        except UnicodeEncodeError:
            self.output_text.insert(tk.END, f"Ошибка: Текст содержит символы, которых нет в {self.encoding}")
            return

        res_parts = []
        for byte in b:
            if self.format == "hex":
                res_parts.append(f"{byte:02X}")
            elif self.format == "bin":
                res_parts.append(f"{byte:08b}")
            elif self.format == "dec":
                res_parts.append(str(byte))
        self.output_text.insert(tk.END, " ".join(res_parts))

    def _decode(self, text):
        if self.encoding == "Base64":
            try:
                self.output_text.insert(tk.END,
                                        base64.b64decode(text.encode('utf-8')).decode('utf-8', errors='replace'))
            except Exception:
                self.output_text.insert(tk.END, "Ошибка Base64")
            return
        py_enc = self.encoding.lower()
        if py_enc == "windows-1251": py_enc = "cp1251"

        clean_text = text.replace('\n', ' ').replace('\r', ' ')
        parts = clean_text.split()
        bytes_list = []
        if len(parts) == 1 and len(clean_text) % 2 == 0 and all(c in "0123456789abcdefABCDEF" for c in clean_text):
            parts = [clean_text[i:i + 2] for i in range(0, len(clean_text), 2)]

        for p in parts:
            p = p.strip().replace("0x", "").replace("0X", "")
            if not p: continue
            try:
                if self.format == "hex" or (self.format != "bin" and self.format != "dec" and len(p) <= 2):
                    bytes_list.append(int(p, 16))
                elif self.format == "bin" or len(p) == 8:
                    bytes_list.append(int(p, 2))
                elif self.format == "dec":
                    bytes_list.append(int(p, 10))
            except ValueError:
                pass

        if not bytes_list:
            self.output_text.insert(tk.END, "Не удалось распознать коды.")
            return
        try:
            self.output_text.insert(tk.END, bytearray(bytes_list).decode(py_enc, errors='replace'))
        except Exception as e:
            self.output_text.insert(tk.END, f"Ошибка: {e}")

    def copy_result(self):
        res = self.output_text.get("1.0", tk.END).strip()
        if res:
            self.root.clipboard_clear()
            self.root.clipboard_append(res)
            self.btn_copy.config(text="✓ Скопировано!", bg=GREEN)
            self.root.after(1500, lambda: self.btn_copy.config(text="📋 Скопировать результат", bg=ACCENT))


if __name__ == "__main__":
    root = tk.Tk()
    app = CodeCalculatorApp(root)
    root.mainloop()