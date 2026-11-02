#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Задание 12. Влияние битовых искажений на читаемость текста (v2).

Только стандартная библиотека (tkinter).
"""

import difflib
import random
import threading
import tkinter as tk
from tkinter import ttk

# --------------------------------------------------------------------------
# Данные и цвета
# --------------------------------------------------------------------------
ENCODINGS = {
    "UTF-8": "utf-8",
    "Windows-1251": "cp1251",
    "KOI8-R": "koi8-r",
    "ISO-8859-1": "iso-8859-1",
    "ASCII": "ascii",
}
ENC_COLORS = {
    "UTF-8": "#ff6b8b",
    "Windows-1251": "#22d3ee",
    "KOI8-R": "#fbbf24",
    "ISO-8859-1": "#a78bfa",
    "ASCII": "#34d399",
}
MODE_RANDOM, MODE_BURST = "random", "burst"

PRESETS = {
    "Русский": "Привет, мир! Это проверка влияния битовых искажений на читаемость текста.",
    "English": "The quick brown fox jumps over the lazy dog. Bits flip, text breaks.",
    "Смешанный": "Привет, мир! Hello, World! Один бит может испортить всё.",
}

FONT = "Segoe UI"
MONO = "Consolas"

BG = "#0d0f16"
CARD = "#161925"
CARD2 = "#1f2336"
FIELD = "#10121b"
BORDER = "#262b3e"
FG = "#eef0f8"
MUTED = "#7d86a3"
ACCENT = "#7c5cff"
ACCENT_H = "#9479ff"
CYAN = "#22d3ee"
BAD = "#ff4d6d"
GOOD = "#34d399"
WARN = "#fbbf24"
ORANGE = "#fb923c"


# --------------------------------------------------------------------------
# Логика
# --------------------------------------------------------------------------
def to_bytes(text, enc):
    return text.encode(enc, errors="replace")


def from_bytes(data, enc):
    return data.decode(enc, errors="replace")


def flip_bits(data, positions):
    buf = bytearray(data)
    for p in positions:
        buf[p >> 3] ^= 0x80 >> (p & 7)
    return bytes(buf)


def choose_positions(total_bits, k, mode, seed):
    """Детерминированно: при том же seed рост k только добавляет новые биты."""
    k = max(0, min(k, total_bits))
    if k == 0:
        return set()
    rng = random.Random(seed)
    if mode == MODE_RANDOM:
        idx = list(range(total_bits))
        rng.shuffle(idx)
        return set(idx[:k])
    start = int(rng.random() * (total_bits - k + 1))
    return set(range(start, start + k))


def compare_texts(reference, damaged):
    sm = difflib.SequenceMatcher(None, reference, damaged, autojunk=False)
    good, matched = set(), 0
    for block in sm.get_matching_blocks():
        matched += block.size
        good.update(range(block.b, block.b + block.size))
    bad = {i for i in range(len(damaged)) if i not in good}
    return bad, 100.0 * matched / max(len(reference), 1)


def quick_readability(reference, damaged):
    if len(reference) == len(damaged):
        same = sum(1 for a, b in zip(reference, damaged) if a == b)
        return 100.0 * same / max(len(reference), 1)
    return compare_texts(reference, damaged)[1]


def verdict(r):
    if r >= 95:
        return "Читается без проблем", GOOD
    if r >= 80:
        return "Есть опечатки, но понятно", "#a3e635"
    if r >= 55:
        return "Местами понятно", WARN
    if r >= 30:
        return "Читать очень трудно", ORANGE
    return "Нечитаемый мусор", BAD


def run_experiment(text, mode, trials=15, cap=48):
    """Считает кривые читаемости для всех кодировок. Работает в потоке."""
    datas = {n: to_bytes(text, e) for n, e in ENCODINGS.items()}
    maxk = min(cap, min(len(d) * 8 for d in datas.values()))
    rng = random.Random(2024)
    out = {}
    for name, data in datas.items():
        enc = ENCODINGS[name]
        ref = from_bytes(data, enc)
        total = len(data) * 8
        curve = [100.0]
        for k in range(1, maxk + 1):
            acc = 0.0
            for _ in range(trials):
                pos = choose_positions(total, k, mode, rng.randrange(1 << 30))
                acc += quick_readability(ref, from_bytes(flip_bits(data, pos), enc))
            curve.append(acc / trials)
        out[name] = curve
    return maxk, out


# --------------------------------------------------------------------------
# Свои виджеты
# --------------------------------------------------------------------------
def make_button(parent, text, command, primary=False):
    bg = ACCENT if primary else CARD2
    hov = ACCENT_H if primary else "#2b3150"
    lb = tk.Label(parent, text=text, bg=bg, fg="white" if primary else FG,
                  font=(FONT, 10, "bold"), padx=14, pady=8, cursor="hand2")
    lb.bind("<Enter>", lambda e: lb.configure(bg=hov))
    lb.bind("<Leave>", lambda e: lb.configure(bg=bg))
    lb.bind("<Button-1>", lambda e: command())
    return lb


class Segmented(tk.Frame):
    """Переключатель-«таблетки»."""

    def __init__(self, parent, options, variable, command, columns=3):
        super().__init__(parent, bg=CARD)
        self.var, self.command, self.items = variable, command, {}
        for idx, (label, value) in enumerate(options):
            lb = tk.Label(self, text=label, font=(FONT, 10, "bold"), padx=8, pady=7,
                          cursor="hand2", bg=CARD2, fg=MUTED)
            lb.grid(row=idx // columns, column=idx % columns, sticky="ew", padx=2, pady=2)
            lb.bind("<Button-1>", lambda e, v=value: self.select(v))
            lb.bind("<Enter>", lambda e, v=value: self._hover(v, True))
            lb.bind("<Leave>", lambda e, v=value: self._hover(v, False))
            self.items[value] = lb
        for c in range(columns):
            self.columnconfigure(c, weight=1, uniform="seg")
        self.refresh()

    def _hover(self, value, on):
        if self.var.get() != value:
            self.items[value].configure(bg="#2b3150" if on else CARD2)

    def select(self, value):
        self.var.set(value)
        self.refresh()
        self.command()

    def refresh(self):
        for v, lb in self.items.items():
            sel = self.var.get() == v
            lb.configure(bg=ACCENT if sel else CARD2, fg="white" if sel else MUTED)


class Slider(tk.Canvas):
    PAD = 14

    def __init__(self, parent, command):
        super().__init__(parent, height=38, bg=CARD, highlightthickness=0)
        self.command, self.max, self.value = command, 1, 0
        self.bind("<Configure>", lambda e: self.redraw())
        self.bind("<Button-1>", self._drag)
        self.bind("<B1-Motion>", self._drag)
        self.configure(cursor="hand2")

    def _x(self, v):
        w = max(self.winfo_width(), 2 * self.PAD + 1)
        return self.PAD + (w - 2 * self.PAD) * (v / self.max if self.max else 0)

    def redraw(self):
        self.delete("all")
        w, cy = self.winfo_width(), 19
        self.create_line(self.PAD, cy, w - self.PAD, cy, fill=CARD2, width=8, capstyle="round")
        x = self._x(self.value)
        if x > self.PAD:
            self.create_line(self.PAD, cy, x, cy, fill=ACCENT, width=8, capstyle="round")
        self.create_oval(x - 11, cy - 11, x + 11, cy + 11, fill=FG, outline=ACCENT, width=4)

    def _drag(self, e):
        w = max(self.winfo_width(), 2 * self.PAD + 1)
        frac = min(1.0, max(0.0, (e.x - self.PAD) / (w - 2 * self.PAD)))
        v = round(frac * self.max)
        if v != self.value:
            self.value = v
            self.redraw()
            self.command(v)

    def set(self, v):
        self.value = v
        self.redraw()

    def set_max(self, m):
        self.max = max(1, m)
        self.value = min(self.value, self.max)
        self.redraw()


def card(parent, title, subtitle=None):
    """Карточка с тонкой рамкой. Возвращает (внешний, внутренний) фрейм."""
    outer = tk.Frame(parent, bg=BORDER)
    inner = tk.Frame(outer, bg=CARD, padx=16, pady=14)
    inner.pack(fill="both", expand=True, padx=1, pady=1)
    head = tk.Frame(inner, bg=CARD)
    head.pack(fill="x", pady=(0, 10))
    tk.Label(head, text=title, bg=CARD, fg=FG, font=(FONT, 12, "bold")).pack(side="left")
    if subtitle:
        tk.Label(head, text=subtitle, bg=CARD, fg=MUTED, font=(FONT, 9)).pack(side="left", padx=10)
    return outer, inner


# --------------------------------------------------------------------------
# Приложение
# --------------------------------------------------------------------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Битовые искажения · читаемость текста")
        self.geometry("1280x860")
        self.minsize(1120, 740)
        self.configure(bg=BG)

        self.seed = random.randrange(1 << 30)
        self.k = 3
        self.manual = set()
        self.enc_var = tk.StringVar(value="UTF-8")
        self.mode_var = tk.StringVar(value=MODE_RANDOM)

        self._bits_state = (b"", set())
        self.gauge_val = 0.0
        self.gauge_target = 0.0
        self._anim = None

        self.chart_data, self.chart_maxk = {}, 0
        self.chart_loading = False
        self._chart_job = self._poll_job = None
        self._token = 0
        self._pending = None

        self._style_scrollbar()
        self._build()
        self.input.insert("1.0", PRESETS["Смешанный"])
        self.update_all(reset_manual=True)
        self.schedule_chart(delay=200)

    # ------------------------------------------------------------------ UI
    def _style_scrollbar(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("Vertical.TScrollbar", background=CARD2, troughcolor=CARD,
                    bordercolor=CARD, arrowcolor=MUTED, lightcolor=CARD2, darkcolor=CARD2)

    def _build(self):
        root = tk.Frame(self, bg=BG)
        root.pack(fill="both", expand=True, padx=20, pady=16)
        root.columnconfigure(1, weight=1)
        root.rowconfigure(1, weight=1)

        # ---- шапка
        head = tk.Frame(root, bg=BG)
        head.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 14))
        tk.Label(head, text="Битовые искажения", bg=BG, fg=FG,
                 font=(FONT, 22, "bold")).pack(side="left")
        tk.Label(head, text="переворачиваем биты и смотрим, что остаётся от текста",
                 bg=BG, fg=MUTED, font=(FONT, 11)).pack(side="left", padx=14, pady=(8, 0))

        # ---- левая колонка
        left = tk.Frame(root, bg=BG, width=350)
        left.grid(row=1, column=0, sticky="ns", padx=(0, 14))
        left.pack_propagate(False)
        left.configure(width=350)

        c1, b1 = card(left, "Текст")
        c1.pack(fill="x")
        self.input = tk.Text(b1, height=6, wrap="word", bg=FIELD, fg=FG, insertbackground=FG,
                             relief="flat", font=(FONT, 12), padx=10, pady=8,
                             highlightthickness=1, highlightbackground=BORDER,
                             highlightcolor=ACCENT)
        self.input.pack(fill="x")
        self.input.bind("<KeyRelease>", lambda e: self.on_text_change())
        row = tk.Frame(b1, bg=CARD)
        row.pack(fill="x", pady=(10, 0))
        for name, txt in PRESETS.items():
            make_button(row, name, lambda t=txt: self.set_preset(t)).pack(side="left", padx=(0, 6))

        c2, b2 = card(left, "Параметры")
        c2.pack(fill="x", pady=(14, 0))
        self._label(b2, "Кодировка")
        Segmented(b2, [(n, n) for n in ENCODINGS], self.enc_var,
                  self.on_text_change, columns=3).pack(fill="x", pady=(4, 12))
        self._label(b2, "Тип искажений")
        Segmented(b2, [("Случайные биты", MODE_RANDOM), ("Пакет подряд", MODE_BURST)],
                  self.mode_var, self.on_mode_change, columns=2).pack(fill="x", pady=(4, 12))

        top = tk.Frame(b2, bg=CARD)
        top.pack(fill="x")
        self._label(top, "Сколько бит исказить", side="left")
        self.lbl_k = tk.Label(top, text="0", bg=CARD, fg=ACCENT, font=(FONT, 20, "bold"))
        self.lbl_k.pack(side="right")
        self.slider = Slider(b2, self.on_slider)
        self.slider.pack(fill="x", pady=(2, 8))

        btns = tk.Frame(b2, bg=CARD)
        btns.pack(fill="x")
        make_button(btns, "−1", lambda: self.step(-1)).pack(side="left")
        make_button(btns, "+1", lambda: self.step(1)).pack(side="left", padx=6)
        make_button(btns, "Другие биты", self.new_seed, primary=True).pack(side="left")
        make_button(btns, "Сброс", self.reset_manual).pack(side="right")

        # ---- правая колонка
        right = tk.Frame(root, bg=BG)
        right.grid(row=1, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=3)
        right.rowconfigure(2, weight=3)

        # результат
        c3, b3 = card(right, "Результат")
        c3.grid(row=0, column=0, sticky="ew")
        res = tk.Frame(b3, bg=CARD)
        res.pack(fill="x")
        res.columnconfigure(0, weight=1)
        txts = tk.Frame(res, bg=CARD)
        txts.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        tk.Label(txts, text="КАК ДОЛЖНО БЫТЬ", bg=CARD, fg=MUTED,
                 font=(FONT, 8, "bold")).pack(anchor="w")
        self.txt_ref = self._ro_text(txts, 2, MUTED, 12)
        self.txt_ref.pack(fill="x", pady=(2, 10))
        tk.Label(txts, text="ЧТО ПОЛУЧИЛОСЬ", bg=CARD, fg=MUTED,
                 font=(FONT, 8, "bold")).pack(anchor="w")
        self.txt_bad = self._ro_text(txts, 3, FG, 15)
        self.txt_bad.pack(fill="x", pady=(2, 0))
        self.txt_bad.tag_configure("bad", foreground="white", background=BAD)

        gbox = tk.Frame(res, bg=CARD)
        gbox.grid(row=0, column=1, sticky="ns")
        self.gauge = tk.Canvas(gbox, width=170, height=150, bg=CARD, highlightthickness=0)
        self.gauge.pack()
        self.lbl_verdict = tk.Label(gbox, text="", bg=CARD, fg=FG, font=(FONT, 11, "bold"))
        self.lbl_verdict.pack()
        self.lbl_chars = tk.Label(gbox, text="", bg=CARD, fg=MUTED, font=(FONT, 9))
        self.lbl_chars.pack()

        # биты
        c4, b4 = card(right, "Биты",
                      "● единица   ○ ноль   красные — перевёрнутые   клик по биту — перевернуть вручную")
        c4.grid(row=1, column=0, sticky="nsew", pady=(14, 0))
        wrap = tk.Frame(b4, bg=CARD)
        wrap.pack(fill="both", expand=True)
        self.bits_canvas = tk.Canvas(wrap, bg=FIELD, highlightthickness=0, height=120)
        sb = ttk.Scrollbar(wrap, orient="vertical", command=self.bits_canvas.yview)
        self.bits_canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.bits_canvas.pack(side="left", fill="both", expand=True)
        self.bits_canvas.bind("<Configure>", lambda e: self.draw_bits())
        self.bits_canvas.bind("<MouseWheel>",
                              lambda e: self.bits_canvas.yview_scroll(-1 if e.delta > 0 else 1, "units"))
        self.bits_canvas.bind("<Button-4>", lambda e: self.bits_canvas.yview_scroll(-1, "units"))
        self.bits_canvas.bind("<Button-5>", lambda e: self.bits_canvas.yview_scroll(1, "units"))
        self.bits_canvas.tag_bind("bit", "<Button-1>", self.on_bit_click)
        self.bits_canvas.tag_bind("bit", "<Enter>", lambda e: self.bits_canvas.configure(cursor="hand2"))
        self.bits_canvas.tag_bind("bit", "<Leave>", lambda e: self.bits_canvas.configure(cursor=""))

        # график
        c5, b5 = card(right, "Читаемость от числа искажённых бит",
                      "все кодировки, усреднение по 15 испытаниям")
        c5.grid(row=2, column=0, sticky="nsew", pady=(14, 0))
        self.chart = tk.Canvas(b5, bg=FIELD, highlightthickness=0, height=150)
        self.chart.pack(fill="both", expand=True)
        self.chart.bind("<Configure>", lambda e: self.draw_chart())

    @staticmethod
    def _label(parent, text, side=None):
        lb = tk.Label(parent, text=text.upper(), bg=CARD, fg=MUTED, font=(FONT, 8, "bold"))
        if side:
            lb.pack(side=side)
        else:
            lb.pack(anchor="w")
        return lb

    @staticmethod
    def _ro_text(parent, height, fg, size):
        return tk.Text(parent, height=height, wrap="word", bg=FIELD, fg=fg, relief="flat",
                       font=(FONT, size), padx=10, pady=6, highlightthickness=1,
                       highlightbackground=BORDER, state="disabled", cursor="arrow")

    @staticmethod
    def _set_text(widget, chunks):
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        for s, tag in chunks:
            if tag:
                widget.insert("end", s, tag)
            else:
                widget.insert("end", s)
        widget.configure(state="disabled")

    # --------------------------------------------------------------- события
    def current_text(self):
        return self.input.get("1.0", "end-1c")

    def on_text_change(self):
        self.update_all(reset_manual=True)
        self.schedule_chart()

    def on_mode_change(self):
        self.update_all()
        self.schedule_chart()

    def on_slider(self, v):
        self.k = v
        self.update_all()

    def step(self, d):
        self.k = max(0, min(self.slider.max, self.k + d))
        self.slider.set(self.k)
        self.update_all()

    def new_seed(self):
        self.seed = random.randrange(1 << 30)
        self.update_all()

    def reset_manual(self):
        self.manual.clear()
        self.update_all()

    def set_preset(self, text):
        self.input.delete("1.0", "end")
        self.input.insert("1.0", text)
        self.on_text_change()

    def on_bit_click(self, event):
        c = self.bits_canvas
        item = c.find_withtag("current")
        if not item:
            return
        for tag in c.gettags(item[0]):
            if tag.startswith("p") and tag[1:].isdigit():
                self.manual ^= {int(tag[1:])}
                self.update_all()
                return

    # --------------------------------------------------------------- расчёт
    def update_all(self, reset_manual=False):
        if reset_manual:
            self.manual.clear()
        text = self.current_text()
        enc = ENCODINGS[self.enc_var.get()]
        data = to_bytes(text, enc)
        total = len(data) * 8

        self.slider.set_max(total)
        self.k = min(self.k, self.slider.max)
        self.slider.set(self.k)
        self.manual = {p for p in self.manual if p < total}

        auto = choose_positions(total, self.k, self.mode_var.get(), self.seed)
        positions = auto ^ self.manual
        damaged = flip_bits(data, positions)

        reference = from_bytes(data, enc)
        result = from_bytes(damaged, enc)
        bad_idx, readability = compare_texts(reference, result)

        self._set_text(self.txt_ref, [(reference, None)])
        self._set_text(self.txt_bad,
                       [(ch, "bad" if i in bad_idx else None) for i, ch in enumerate(result)])

        self.lbl_k.configure(text=f"{len(positions)}")
        msg, color = verdict(readability)
        self.lbl_verdict.configure(text=msg, fg=color)
        self.lbl_chars.configure(
            text=f"испорчено символов: {len(bad_idx)} из {len(result)}\n"
                 f"{len(data)} байт · {total} бит · {len(positions)} перевёрнуто")

        self._bits_state = (damaged, positions)
        self.draw_bits()
        self.animate_gauge(readability)
        self.draw_chart()

    # ---------------------------------------------------------------- биты
    def draw_bits(self):
        c = self.bits_canvas
        c.delete("all")
        w = c.winfo_width()
        damaged, positions = self._bits_state
        if w < 60 or not damaged:
            return
        R, step, pad = 6, 17, 5
        bw, bh, gap = 8 * step + 2 * pad, 48, 8
        per_row = max(1, (w - 12) // (bw + gap))
        changed = {p >> 3 for p in positions}

        for i, byte in enumerate(damaged):
            r, col = divmod(i, per_row)
            x0, y0 = 8 + col * (bw + gap), 8 + r * (bh + gap)
            c.create_rectangle(x0, y0, x0 + bw, y0 + bh, fill=CARD2,
                               outline=BAD if i in changed else BORDER, width=1)
            c.create_text(x0 + bw / 2, y0 + 10, text=f"{byte:02X}",
                          fill=BAD if i in changed else MUTED, font=(MONO, 9, "bold"))
            for j in range(8):
                pos = i * 8 + j
                bit = (byte >> (7 - j)) & 1
                cx, cy = x0 + pad + step / 2 + j * step, y0 + 31
                if pos in positions:
                    fill, outline, width = (BAD if bit else CARD2), BAD, 2
                else:
                    fill, outline, width = (CYAN if bit else CARD2), (CYAN if bit else "#3d4466"), 1
                c.create_oval(cx - R, cy - R, cx + R, cy + R, fill=fill, outline=outline,
                              width=width, tags=("bit", f"p{pos}"))
        rows = -(-len(damaged) // per_row)
        c.configure(scrollregion=(0, 0, w, 8 + rows * (bh + gap)))

    # ------------------------------------------------------------- индикатор
    def animate_gauge(self, target):
        self.gauge_target = target
        if self._anim is None:
            self._tick()

    def _tick(self):
        diff = self.gauge_target - self.gauge_val
        if abs(diff) < 0.4:
            self.gauge_val = self.gauge_target
            self._anim = None
        else:
            self.gauge_val += diff * 0.25
            self._anim = self.after(16, self._tick)
        self.draw_gauge(self.gauge_val)

    def draw_gauge(self, val):
        g = self.gauge
        g.delete("all")
        box = (22, 12, 148, 138)
        g.create_arc(*box, start=225, extent=-270, style="arc", outline=CARD2, width=14)
        if val > 0.5:
            g.create_arc(*box, start=225, extent=-270 * val / 100, style="arc",
                         outline=verdict(val)[1], width=14)
        g.create_text(85, 70, text=f"{val:.0f}%", fill=FG, font=(FONT, 28, "bold"))
        g.create_text(85, 100, text="читаемость", fill=MUTED, font=(FONT, 9))

    # ---------------------------------------------------------------- график
    def schedule_chart(self, delay=500):
        if self._chart_job:
            self.after_cancel(self._chart_job)
        self._chart_job = self.after(delay, self.start_experiment)

    def start_experiment(self):
        self._chart_job = None
        text = self.current_text()[:120]
        if not text:
            self.chart_data = {}
            self.draw_chart()
            return
        self._token += 1
        token, mode = self._token, self.mode_var.get()
        self.chart_loading = True
        self.draw_chart()

        def work():
            maxk, res = run_experiment(text, mode)
            self._pending = (token, maxk, res)

        threading.Thread(target=work, daemon=True).start()
        if self._poll_job:
            self.after_cancel(self._poll_job)
        self._poll_job = self.after(100, self._poll)

    def _poll(self):
        p = self._pending
        if p and p[0] == self._token:
            _, self.chart_maxk, self.chart_data = p
            self._pending = None
            self.chart_loading = False
            self._poll_job = None
            self.draw_chart()
        else:
            self._poll_job = self.after(100, self._poll)

    def draw_chart(self):
        c = self.chart
        c.delete("all")
        w, h = c.winfo_width(), c.winfo_height()
        if w < 120 or h < 80:
            return
        if not self.chart_data:
            msg = "считаю…" if self.chart_loading else "введите текст"
            c.create_text(w / 2, h / 2, text=msg, fill=MUTED, font=(FONT, 12))
            return

        l, r, t, b = 50, 16, 34, 28
        pw, ph = w - l - r, h - t - b
        maxk = max(self.chart_maxk, 1)
        X = lambda k: l + pw * k / maxk
        Y = lambda v: t + ph * (1 - v / 100.0)

        for v in range(0, 101, 25):
            c.create_line(l, Y(v), w - r, Y(v), fill=BORDER)
            c.create_text(l - 8, Y(v), text=f"{v}%", fill=MUTED, anchor="e", font=(FONT, 9))
        st = max(1, maxk // 8)
        for k in range(0, maxk + 1, st):
            c.create_text(X(k), t + ph + 14, text=str(k), fill=MUTED, font=(FONT, 9))
        c.create_text(w - r, h - 6, text="число искажённых бит", fill=MUTED,
                      anchor="se", font=(FONT, 8))

        k_now = min(self.k, maxk)
        c.create_line(X(k_now), t, X(k_now), t + ph, fill=ACCENT, dash=(4, 4), width=2)

        lx = l
        for name, curve in self.chart_data.items():
            col = ENC_COLORS[name]
            pts = []
            for k, v in enumerate(curve):
                pts += [X(k), Y(v)]
            c.create_line(*pts, fill=col, width=3, smooth=True)
            c.create_oval(X(k_now) - 5, Y(curve[k_now]) - 5, X(k_now) + 5, Y(curve[k_now]) + 5,
                          fill=col, outline=FIELD, width=2)
            c.create_oval(lx, 12, lx + 10, 22, fill=col, outline=col)
            c.create_text(lx + 15, 17, text=name, fill=FG, anchor="w", font=(FONT, 9, "bold"))
            lx += 36 + 7 * len(name)


if __name__ == "__main__":
    # DPI-awareness только на Windows, и только один раз
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    app = App()
    app.mainloop()