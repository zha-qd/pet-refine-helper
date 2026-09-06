"""
Auto Refine Helper - GUI Edition
Light-themed tkinter interface (zero extra UI dependencies)
"""

import os
import sys
import time
import re
import threading

# Skip PaddlePaddle's slow network check
os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"

# --- Show a splash window while heavy imports load ---
import tkinter as tk

splash = tk.Tk()
splash.overrideredirect(True)
splash.configure(bg="#f5f7fb")
sw, sh = 320, 100
splash.geometry(f"{sw}x{sh}+{(splash.winfo_screenwidth()-sw)//2}+{(splash.winfo_screenheight()-sh)//2}")
tk.Label(splash, text="自动洗炼助手", font=("Microsoft YaHei UI", 14, "bold"),
         bg="#f5f7fb", fg="#243047").pack(pady=(18, 4))
splash_label = tk.Label(splash, text="正在加载，请稍候...", font=("Microsoft YaHei UI", 9),
                        bg="#f5f7fb", fg="#7b89a3")
splash_label.pack()
splash.update()

def splash_msg(msg):
    try:
        splash_label.configure(text=msg)
        splash.update()
    except: pass

splash_msg("加载核心组件...")
import numpy as np
import cv2
from mss import mss
import pyautogui
import pygetwindow as gw
from pynput import keyboard
from tkinter import ttk, scrolledtext

splash_msg("加载 OCR 引擎...")
from paddleocr import PaddleOCR

splash_msg("初始化 OCR 模型...")
# Portable releases ship these official OCR models alongside the application.
_model_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
_model_options = {}
for _kind in ("det", "rec", "cls"):
    _path = os.path.join(_model_root, _kind)
    if os.path.isfile(os.path.join(_path, "inference.pdmodel")):
        _model_options[_kind + "_model_dir"] = _path
_shared_ocr = PaddleOCR(lang="en", use_textline_orientation=False, show_log=False, **_model_options)

splash.destroy()

pyautogui.FAILSAFE = True

# ========= Light Theme Colors =========
BG       = "#f5f7fb"
BG2      = "#ffffff"
FG       = "#243047"
FG_DIM   = "#7b89a3"
ACCENT   = "#4678f5"
GREEN    = "#2da57a"
RED      = "#dc5965"
YELLOW   = "#b57c23"
BORDER   = "#dfe6f1"


def apply_light_theme(root):
    style = ttk.Style()
    style.theme_use("clam")

    style.configure(".", background=BG, foreground=FG, fieldbackground=BG2,
                     bordercolor=BORDER, darkcolor=BG2, lightcolor=BG2,
                     troughcolor=BG2, selectbackground=ACCENT, selectforeground=BG,
                     font=("Microsoft YaHei UI", 9))
    style.configure("TLabel", background=BG2, foreground=FG)
    style.configure("TFrame", background=BG2)
    style.configure("TLabelframe", background=BG, foreground=ACCENT, bordercolor=BORDER)
    style.configure("TLabelframe.Label", background=BG, foreground=ACCENT,
                     font=("Microsoft YaHei UI", 9, "bold"))
    style.configure("TButton", background=BG2, foreground=FG, bordercolor=BORDER, padding=(12, 6))
    style.map("TButton",
              background=[("active", ACCENT), ("disabled", BG)],
              foreground=[("active", BG), ("disabled", FG_DIM)])
    style.configure("TCombobox", fieldbackground=BG2, background=BG2, foreground=FG,
                     arrowcolor=FG, bordercolor=BORDER, selectbackground=BG2,
                     selectforeground=FG)
    style.map("TCombobox",
              fieldbackground=[("readonly", BG2), ("focus", BG2)],
              foreground=[("readonly", FG), ("focus", FG), ("disabled", FG_DIM)],
              selectbackground=[("readonly", BG2), ("focus", BG2)],
              selectforeground=[("readonly", FG), ("focus", FG)])
    style.configure("TSpinbox", fieldbackground=BG2, background=BG2, foreground=FG,
                     arrowcolor=FG, bordercolor=BORDER)
    # Fix combobox dropdown list colors
    root.option_add("*TCombobox*Listbox.background", BG2)
    root.option_add("*TCombobox*Listbox.foreground", FG)
    root.option_add("*TCombobox*Listbox.selectBackground", ACCENT)
    root.option_add("*TCombobox*Listbox.selectForeground", BG)

    style.configure("Green.TButton", background="#4678f5", foreground="#ffffff", bordercolor="#4678f5")
    style.map("Green.TButton", background=[("active", GREEN)], foreground=[("active", BG)])

    style.configure("Red.TButton", background="#fff1f2", foreground=RED, bordercolor="#f5d7dc")
    style.map("Red.TButton", background=[("active", RED)], foreground=[("active", BG)])

    style.configure("Yellow.TButton", background="#f0f4fb", foreground=YELLOW, bordercolor="#dfe6f1")
    style.map("Yellow.TButton", background=[("active", YELLOW)], foreground=[("active", BG)])

    style.configure("Accent.TLabel", foreground=ACCENT)
    style.configure("Green.TLabel", foreground=GREEN)
    style.configure("Red.TLabel", foreground=RED)
    style.configure("Dim.TLabel", foreground=FG_DIM)
    style.configure("Title.TLabel", font=("Microsoft YaHei UI", 14, "bold"), foreground=FG)

    style.configure("TEntry", padding=7, fieldbackground="#f8faff", bordercolor=BORDER)
    style.configure("TCombobox", padding=7)
    style.configure("TSpinbox", padding=7)
    style.configure("TButton", font=("Microsoft YaHei UI", 10), padding=(14, 9))
    style.configure("Heading.TLabel", font=("Microsoft YaHei UI", 11, "bold"))
    style.configure("Page.TLabel", background=BG)
    style.configure("PageDim.TLabel", background=BG, foreground=FG_DIM)
    style.map("Green.TButton", background=[("disabled", "#dce7ff"), ("active", "#3466e3")],
              foreground=[("disabled", "#6485c9"), ("active", "#ffffff")])
    root.configure(bg=BG)


class RoundedCard(tk.Canvas):
    def __init__(self, parent, stretch=False):
        self.stretch = stretch
        super().__init__(parent, bg=BG, highlightthickness=0, bd=0, height=150)
        self.body = ttk.Frame(self, padding=(18, 10))
        self.window = self.create_window(1, 1, window=self.body, anchor="nw")
        self.bind("<Configure>", self._layout)
        self.body.bind("<Configure>", self._height)

    def _height(self, event):
        if not self.stretch:
            self.configure(height=self.body.winfo_reqheight() + 16)

    def _layout(self, event):
        w, h, r = event.width-1, event.height-1, 18
        self.delete("card")
        points = [r,1,w-r,1,w,1,w,r,w,h-r,w,h,w-r,h,r,h,1,h,1,h-r,1,r,1,1]
        self.create_polygon(points, smooth=True, splinesteps=24, fill=BG2,
                            outline=BORDER, tags="card")
        self.tag_lower("card")
        self.coords(self.window, 8, 8)
        self.itemconfigure(self.window, width=max(1,w-16))
        if self.stretch:
            self.itemconfigure(self.window, height=max(1,h-16))


class Toggle(tk.Canvas):
    def __init__(self, parent, variable, command):
        super().__init__(parent, width=48, height=28, bg=BG2, highlightthickness=0,
                         cursor="hand2", takefocus=True)
        self.variable, self.command = variable, command
        self.bind("<Button-1>", self._toggle)
        self.bind("<space>", self._toggle)
        self.bind("<FocusIn>", lambda e: self._draw())
        self.bind("<FocusOut>", lambda e: self._draw())
        variable.trace_add("write", lambda *args: self._draw())
        self._draw()

    def _toggle(self, event=None):
        self.variable.set(not self.variable.get())
        self.command()

    def _draw(self):
        self.delete("all")
        color = ACCENT if self.variable.get() else "#cbd4e3"
        self.create_line(14,14,34,14,fill=color,width=26,capstyle=tk.ROUND)
        x = 34 if self.variable.get() else 14
        self.create_oval(x-9,5,x+9,23,fill="white",outline="white")
        if self.focus_get() == self:
            self.create_rectangle(1,1,47,27,outline=ACCENT,dash=(2,2))


class RefineApp:

    REGIONS = {
        "盾兵生命": {"rx1": 540, "ry1": 573, "rx2": 670, "ry2": 618},
        "矛兵穿透": {"rx1": 545, "ry1": 668, "rx2": 675, "ry2": 704},
        "矛兵生命": {"rx1": 545, "ry1": 747, "rx2": 675, "ry2": 785},
        "射手穿透": {"rx1": 545, "ry1": 829, "rx2": 675, "ry2": 868},
        "射手生命": {"rx1": 545, "ry1": 909, "rx2": 675, "ry2": 953},
    }
    BUTTONS = {
        "refine":  (407, 1201),
        "replace": (555, 1200),
        "reroll":  (255, 1198),
        "confirm": (558, 878),
    }

    SINGLE_OPTIONS = ["盾兵生命", "射手穿透", "射手生命", "矛兵生命", "矛兵穿透"]
    DUAL_OPTIONS   = ["射手双洗 (盾生+射穿)", "矛兵双洗 (盾生+矛穿)"]
    TRIPLE_OPTIONS = ["射手三洗 (盾+射穿+射生)", "矛兵三洗 (盾+矛生+矛穿)"]

    def __init__(self, root):
        self.root = root
        self.root.title("宠物洗练助手")
        self.root.geometry("1100x680")
        self.root.resizable(False, False)

        apply_light_theme(self.root)

        self.running = False
        self.worker_thread = None
        self.ocr = _shared_ocr  # pre-loaded at startup
        self.sct = None  # created in worker thread (mss is thread-local)
        self.win_left = 0
        self.win_top = 0
        self.win_width = 0
        self.win_height = 0

        # Reference window size (coordinates were calibrated at this size)
        self.REF_WIDTH = 777
        self.REF_HEIGHT = 1396
        self.scale_x = 1.0
        self.scale_y = 1.0

        self.stat_total = 0
        self.stat_replaced = 0
        self.stat_rerolled = 0
        self.stat_ocr_fail = 0
        self.attribute_gains = {}

        self.var_window_title = tk.StringVar(value="")
        self.var_mode = tk.StringVar(value="单洗")
        self.var_sub = tk.StringVar(value=self.SINGLE_OPTIONS[0])
        self.var_click_delay = tk.DoubleVar(value=0.8)
        self.var_anim_delay = tk.DoubleVar(value=0.2)

        self._build_ui()
        self._setup_hotkeys()

    # ================================================================
    #  UI
    # ================================================================
    def _build_ui(self):
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill=tk.X, padx=26, pady=(14, 10))
        tk.Label(header, text="宠物洗练助手", bg=BG, fg=FG,
                 font=("Microsoft YaHei UI", 21, "bold")).pack(anchor="w")
        ttk.Label(header, text="选择属性，轻松洗练。", style="PageDim.TLabel").pack(anchor="w", pady=(4,0))

        columns = tk.Frame(self.root, bg=BG)
        columns.pack(fill=tk.X, padx=20, pady=(0,10))
        columns.columnconfigure(0, minsize=560)
        columns.columnconfigure(1, weight=1)
        left = tk.Frame(columns, bg=BG)
        left.grid(row=0, column=0, sticky="nsew", padx=(0,14))

        def card(title, subtitle=None):
            shell = RoundedCard(left)
            shell.pack(fill=tk.X, pady=(0,10) if title != "运行控制" else 0)
            body = shell.body
            ttk.Label(body, text=title, style="Heading.TLabel").pack(anchor="w")
            if subtitle:
                ttk.Label(body, text=subtitle, style="Dim.TLabel").pack(anchor="w", pady=(3,0))
            return body

        win = card("游戏窗口", "输入窗口标题，检测后即可开始")
        row = ttk.Frame(win)
        row.pack(fill=tk.X, pady=(10,0))
        ttk.Entry(row, textvariable=self.var_window_title, width=20).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(row, text="检测窗口", command=self._detect_window).pack(side=tk.LEFT, padx=(10,6))
        ttk.Button(row, text="校准", command=self._calibrate).pack(side=tk.LEFT)
        self.lbl_win_status = ttk.Label(win, text="未检测窗口", style="Dim.TLabel", wraplength=480)
        self.lbl_win_status.pack(anchor="w", pady=(8,0))

        mode = card("洗练设置")
        row = ttk.Frame(mode)
        row.pack(fill=tk.X, pady=(10,12))
        mode_cb = ttk.Combobox(row, textvariable=self.var_mode, width=7,
                              values=["单洗", "双洗", "三洗"], state="readonly")
        mode_cb.pack(side=tk.LEFT, padx=(0,10))
        mode_cb.bind("<<ComboboxSelected>>", self._on_mode_change)
        self.cb_sub = ttk.Combobox(row, textvariable=self.var_sub, state="readonly", values=self.SINGLE_OPTIONS)
        self.cb_sub.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Frame(mode, height=1, bg="#edf1f7").pack(fill=tk.X)
        row = ttk.Frame(mode)
        row.pack(fill=tk.X, pady=(12,0))
        ttk.Label(row, text="点击间隔", style="Dim.TLabel").pack(side=tk.LEFT)
        ttk.Spinbox(row, textvariable=self.var_click_delay, from_=0.3, to=2.0, increment=0.1, width=5).pack(side=tk.LEFT, padx=8)
        ttk.Label(row, text="秒", style="Dim.TLabel").pack(side=tk.LEFT)
        ttk.Label(row, text="动画等待", style="Dim.TLabel").pack(side=tk.LEFT, padx=(25,0))
        ttk.Spinbox(row, textvariable=self.var_anim_delay, from_=0.1, to=1.0, increment=0.05, width=5).pack(side=tk.LEFT, padx=8)
        ttk.Label(row, text="秒", style="Dim.TLabel").pack(side=tk.LEFT)

        controls = card("运行控制")
        row = ttk.Frame(controls)
        row.pack(fill=tk.X, pady=(10,12))
        self.btn_start = ttk.Button(row, text="开始洗炼  ·  F5", style="Green.TButton", command=self._toggle_run)
        self.btn_start.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,8))
        tk.Frame(controls, height=1, bg="#edf1f7").pack(fill=tk.X)
        row = ttk.Frame(controls)
        row.pack(fill=tk.X, pady=(10,0))
        labels = ttk.Frame(row)
        labels.pack(side=tk.LEFT)
        ttk.Label(labels, text="调试模式", font=("Microsoft YaHei UI",10,"bold")).pack(anchor="w")
        ttk.Label(labels, text="保存识别截图，方便排查问题", style="Dim.TLabel").pack(anchor="w", pady=(3,0))
        self.var_debug = tk.BooleanVar(value=False)
        self.debug = False
        self.debug_toggle = Toggle(row, self.var_debug, self._toggle_debug)
        self.debug_toggle.pack(side=tk.RIGHT)

        self.log_card = RoundedCard(columns, stretch=True)
        self.log_card.grid(row=0, column=1, sticky="nsew")
        log = self.log_card.body
        ttk.Label(log, text="运行日志", style="Heading.TLabel").pack(anchor="w")
        self.lbl_stat = ttk.Label(log, text="总计: 0  |  替换: 0  |  重洗: 0  |  OCR失败: 0  |  替换率: N/A", style="Dim.TLabel", wraplength=430)
        self.lbl_stat.pack(anchor="w", pady=(6,10))
        self.log_text = scrolledtext.ScrolledText(log, height=3, width=40, wrap=tk.WORD, state=tk.DISABLED,
            bg="#f8faff", fg=FG, insertbackground=FG, selectbackground=ACCENT, selectforeground="white",
            font=("Microsoft YaHei UI",9), borderwidth=0, highlightthickness=0, padx=10, pady=8)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        for tag, color in [("good",GREEN),("bad",RED),("warn",YELLOW),("info",ACCENT)]:
            self.log_text.tag_configure(tag, foreground=color)
        ttk.Label(self.root, text="F5 开始 / 停止",
                  style="PageDim.TLabel").pack(pady=(0,12))

    # ================================================================
    #  Mode switch
    # ================================================================
    def _on_mode_change(self, event=None):
        mode = self.var_mode.get()
        if mode == "单洗":
            opts = self.SINGLE_OPTIONS
        elif mode == "双洗":
            opts = self.DUAL_OPTIONS
        else:
            opts = self.TRIPLE_OPTIONS
        self.cb_sub.configure(values=opts)
        self.var_sub.set(opts[0])

    # ================================================================
    #  Logging & Stats
    # ================================================================
    def log(self, msg, tag=None):
        timestamp = time.strftime("%H:%M:%S")
        line = f"[{timestamp}] {msg}\n"
        self.root.after(0, self._append_log, line, tag)

    def _append_log(self, line, tag=None):
        self.log_text.configure(state=tk.NORMAL)
        if tag:
            self.log_text.insert(tk.END, line, tag)
        else:
            self.log_text.insert(tk.END, line)
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def _update_stats(self):
        total = self.stat_total
        rate = f"{self.stat_replaced / total * 100:.1f}%" if total > 0 else "N/A"
        text = (f"总计: {total}  |  替换: {self.stat_replaced}  |  "
                f"重洗: {self.stat_rerolled}  |  OCR失败: {self.stat_ocr_fail}  |  替换率: {rate}")
        self.root.after(0, self.lbl_stat.configure, {"text": text})

    # ================================================================
    #  Window detection & calibration
    # ================================================================
    def _detect_window(self):
        title = self.var_window_title.get().strip()
        if not title:
            self.lbl_win_status.configure(text="  请输入标题", style="Red.TLabel")
            return False
        windows = gw.getWindowsWithTitle(title)
        if not windows:
            self.lbl_win_status.configure(text=f"  未找到 '{title}'", style="Red.TLabel")
            self.log(f"未找到标题包含 '{title}' 的窗口", "bad")
            return False
        win = windows[0]
        self.win_left = win.left
        self.win_top = win.top
        self.win_width = win.width
        self.win_height = win.height
        self.scale_x = win.width / self.REF_WIDTH
        self.scale_y = win.height / self.REF_HEIGHT
        status = f"  ({win.left},{win.top}) {win.width}x{win.height} x{self.scale_x:.2f}"
        self.lbl_win_status.configure(text=status, style="Green.TLabel")
        self.log(f"窗口已定位: {status}", "good")
        return True

    def _calibrate(self):
        if not self._detect_window():
            return
        self.log("校准中: 鼠标将移到各关键位置...", "info")

        def _run():
            for name, pt in self.BUTTONS.items():
                ax, ay = self._abs_point(pt)
                self.log(f"  {name}: ({ax}, {ay})")
                pyautogui.moveTo(ax, ay)
                time.sleep(1.5)
            pyautogui.moveTo(100, 100)
            self.log("校准完成!", "good")

        threading.Thread(target=_run, daemon=True).start()

    # ================================================================
    #  Coordinate conversion & core OCR
    # ================================================================
    def _abs_region(self, name):
        r = self.REGIONS[name]
        sx, sy = self.scale_x, self.scale_y
        return {
            "x1": int(r["rx1"] * sx) + self.win_left,
            "y1": int(r["ry1"] * sy) + self.win_top,
            "x2": int(r["rx2"] * sx) + self.win_left,
            "y2": int(r["ry2"] * sy) + self.win_top,
        }

    def _abs_point(self, rel_pt):
        return (int(rel_pt[0] * self.scale_x) + self.win_left,
                int(rel_pt[1] * self.scale_y) + self.win_top)

    def _grab(self, abs_r):
        monitor = {"left": abs_r["x1"], "top": abs_r["y1"],
                    "width": abs_r["x2"] - abs_r["x1"], "height": abs_r["y2"] - abs_r["y1"]}
        return np.array(self.sct.grab(monitor))[:, :, :3]

    @staticmethod
    def _detect_sign(img):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        red = (cv2.inRange(hsv, (0, 80, 80), (10, 255, 255))
               | cv2.inRange(hsv, (160, 80, 80), (180, 255, 255)))
        green = cv2.inRange(hsv, (35, 80, 80), (85, 255, 255))
        r_p, g_p = cv2.countNonZero(red), cv2.countNonZero(green)
        if r_p < 20 and g_p < 20:
            return 0
        return -1 if r_p > g_p else 1

    @staticmethod
    def _clean_ocr_text(text):
        """Clean common OCR misreads for small percentage numbers."""
        # Remove spaces
        text = text.replace(" ", "")
        # Common misreads: / → digit, | → 1, O → 0, l → 1, I → 1
        text = text.replace("|", "1").replace("O", "0").replace("l", "1").replace("I", "1")
        # "/" between digits is usually a misread digit — remove it so "0.0/4" → "0.04"
        text = re.sub(r"(\d)\/(\d)", r"\1\2", text)
        # "," between digits often misread for "." → "0,04" → "0.04"
        text = re.sub(r"(\d),(\d)", r"\1.\2", text)
        return text

    def _ocr_number(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Scale up 3x for better small-text recognition
        gray = cv2.resize(gray, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
        # Apply adaptive thresholding for sharper text
        gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                      cv2.THRESH_BINARY, 11, 2)
        res = self.ocr.ocr(gray, cls=False)
        raw_text = "".join([l[1][0] for l in res[0]]) if res and res[0] else ""
        text = self._clean_ocr_text(raw_text)
        match = re.search(r"(\d+\.?\d*)\s*%?", text)
        return (float(match.group(1)), raw_text) if match else (None, raw_text)

    def _get_value(self, name):
        region = self._abs_region(name)
        img = self._grab(region)
        sign = self._detect_sign(img)

        if sign == 0:
            self.log(f"  {name}: 无变化")
            return 0.0, True

        num, raw = self._ocr_number(img)
        cleaned = self._clean_ocr_text(raw)

        # Debug: save screenshot for inspection (toggle with self.debug)
        if getattr(self, 'debug', False):
            debug_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "debug_img")
            os.makedirs(debug_dir, exist_ok=True)
            ts = time.strftime("%H%M%S")
            cv2.imwrite(os.path.join(debug_dir, f"{ts}_{name}.png"), img)
            # Also save the preprocessed image for debugging
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            gray = cv2.resize(gray, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
            gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                          cv2.THRESH_BINARY, 11, 2)
            cv2.imwrite(os.path.join(debug_dir, f"{ts}_{name}_proc.png"), gray)
            self.log(f"  [DEBUG] {name} 区域: {region}, OCR原文: '{raw}', 清理后: '{cleaned}', 数值: {num}, 符号: {sign}")

        if num is None:
            self.stat_ocr_fail += 1
            self.log(f"  OCR 失败 ({name}), 原文: '{raw}'", "warn")
            return 0.0, False

        return num * sign, True

    # Total-value regions use the supplied 762 x 1393 full-window screenshot.
    TOTAL_ROWS = {"盾兵生命": 590, "矛兵穿透": 674, "矛兵生命": 757,
                  "射手穿透": 840, "射手生命": 923}

    @staticmethod
    def _parse_total(raw):
        text = re.sub(r"\s+", "", raw).replace("％", "%")
        text = text.replace("O", "0").replace("o", "0").replace(",", ".")
        match = re.fullmatch(r"(\d{1,3}(?:\.\d{1,2})?)%/(\d{1,3}(?:\.\d{1,2})?)%", text)
        if not match:
            return None
        current, maximum = (int(round(float(x) * 100)) for x in match.groups())
        if maximum <= 0 or current > maximum:
            return None
        return current, maximum

    def _get_total(self, name):
        y = self.TOTAL_ROWS[name]
        sx, sy = self.win_width / 762, self.win_height / 1393
        region = {"x1": self.win_left + round(370 * sx),
                  "x2": self.win_left + round(548 * sx),
                  "y1": self.win_top + round(y * sy),
                  "y2": self.win_top + round((y + 28) * sy)}
        img = self._grab(region)
        img = cv2.resize(img, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
        img = cv2.copyMakeBorder(img, 12, 12, 12, 12, cv2.BORDER_REPLICATE)
        result = self.ocr.ocr(img, cls=False)
        lines = result[0] if result and result[0] else []
        if not lines or any(float(line[1][1]) < 0.80 for line in lines):
            return None
        raw = "".join(line[1][0] for line in lines)
        return self._parse_total(raw)

    def _read_totals(self, keys, expected=None, finish=False):
        # Require two consecutive matching reads; post-confirmation reads are bounded
        # even when F5 was pressed, so the completed transaction can be accounted for.
        previous = None
        for attempt in range(8 if finish else 4):
            if not finish and not self.running:
                return None
            snapshot = {name: self._get_total(name) for name in keys}
            valid = all(value is not None for value in snapshot.values())
            if valid and expected is not None:
                valid = snapshot == expected
            if valid and snapshot == previous:
                return snapshot
            previous = snapshot if valid else None
            if finish:
                time.sleep(0.35)
            elif not self._wait_running(0.35):
                return None
        return None

    @staticmethod
    def _expected_totals(before, keys, changes):
        return {name: (min(before[name][1], max(0, before[name][0] + int(round(value * 100)))),
                       before[name][1]) for name, value in zip(keys, changes)}

    def _wait_running(self, seconds):
        deadline = time.monotonic() + max(0, seconds)
        while self.running:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return True
            time.sleep(min(0.05, remaining))
        return False

    def _safe_click(self, btn_name, delay=None, finish_confirmation=False):
        if not self.running and not finish_confirmation:
            return False
        if delay is None:
            delay = self.var_click_delay.get()
        pt = self._abs_point(self.BUTTONS[btn_name])
        pyautogui.click(pt[0], pt[1])
        pyautogui.moveTo(100, 100)
        if finish_confirmation:
            time.sleep(delay)
        else:
            self._wait_running(delay)
        return True

    # ================================================================
    #  Controls
    # ================================================================
    def _toggle_run(self):
        if self.running:
            self._stop()
        else:
            self._start()

    def _start(self):
        if self.worker_thread is not None and self.worker_thread.is_alive():
            return
        if not self._detect_window():
            return

        self.running = True
        self.stat_total = 0
        self.stat_replaced = 0
        self.stat_rerolled = 0
        self.stat_ocr_fail = 0
        self.attribute_gains = {}

        self.btn_start.configure(text="停止洗炼  ·  F5", state=tk.NORMAL, style="Red.TButton")

        self.run_mode = self.var_mode.get()
        self.run_sub = self.var_sub.get()
        self.attribute_gains = dict.fromkeys(self._selected_attributes(self.run_mode, self.run_sub), 0.0)
        mode_desc = f"{self.run_mode} - {self.run_sub}"
        self.log("=" * 30, "info")
        self.log(f"开始洗炼  {mode_desc}", "info")

        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()

    def _stop(self):
        if not self.running:
            return
        self.running = False
        self.btn_start.configure(text="正在停止…", state=tk.DISABLED)
        self._finish_stop()

    def _finish_stop(self):
        # Wait for the current iteration so the summary includes its final counts.
        if self.worker_thread is not None and self.worker_thread.is_alive():
            self.root.after(100, self._finish_stop)
            return
        self.btn_start.configure(text="开始洗炼  ·  F5", state=tk.NORMAL, style="Green.TButton")
        self.log("已停止", "info")
        self._update_stats()
        self.log("本轮属性累计增加（仅计已替换结果的正值）", "info")
        for name, gain in self.attribute_gains.items():
            self.log(f"  {name}: +{gain:.2f} 个百分点", "good")

    @staticmethod
    def _selected_attributes(mode, sub):
        if mode == "单洗":
            return [sub]
        if mode == "双洗":
            return ["盾兵生命", "射手穿透" if "射手" in sub else "矛兵穿透"]
        return (["盾兵生命", "射手穿透", "射手生命"] if "射手" in sub
                else ["盾兵生命", "矛兵生命", "矛兵穿透"])

    def _record_gains(self, names, values):
        for name, value in zip(names, values):
            if value > 0:
                self.attribute_gains[name] += value

    def _toggle_debug(self):
        self.debug = self.var_debug.get()
        if self.debug:
            self.log("调试模式开启：截图将保存到 debug_img 文件夹", "info")
        else:
            self.log("调试模式关闭", "info")

    def _setup_hotkeys(self):
        held = set()
        def on_press(key):
            if key == keyboard.Key.f5 and key not in held:
                held.add(key)
                self.root.after(0, self._toggle_run)
        def on_release(key):
            held.discard(key)
        self.hotkey_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        self.hotkey_listener.start()

    # ================================================================
    #  Replace logic
    # ================================================================
    def _should_replace(self, values, names):
        total = sum(values)
        desc = "  ".join(f"{n}({v:+.2f}%)" for n, v in zip(names, values))
        self.log(f"  {desc}  合计: {total:+.2f}%")

        if total > 0:
            self.log("  -> 合计为正，替换!", "good")
            return True
        else:
            self.log("  -> 合计不为正，重洗", "bad")
            return False

    # ================================================================
    #  Worker thread
    # ================================================================
    def _worker(self):
        need_refine = True
        fail_streak = 0
        keys = self._selected_attributes(self.run_mode, self.run_sub)
        self.sct = None
        try:
            self.sct = mss()
            self.log("OCR 已就绪", "good")
            while self.running:
                before = self._read_totals(keys)
                if before is None:
                    if self.running:
                        self.log("当前属性数值未能稳定识别，已停止，不进行洗练", "bad")
                    break
                if self.run_mode == "单洗" and before[keys[0]][0] == before[keys[0]][1]:
                    self.log(f"{keys[0]}已满：{before[keys[0]][0] / 100:.2f}% / {before[keys[0]][1] / 100:.2f}%，自动停止", "good")
                    break
                if fail_streak == 0:
                    self.log(f"第 {self.stat_total + 1} 次洗炼", "info")
                else:
                    self.log(f"第 {self.stat_total + 1} 次洗炼：重新识别", "warn")
                if need_refine:
                    if not self._safe_click("refine"):
                        break
                    need_refine = False
                if not self._wait_running(self.var_anim_delay.get()):
                    break
                vals, oks = [], []
                for name in keys:
                    if not self.running:
                        break
                    value, ok = self._get_value(name)
                    vals.append(value)
                    oks.append(ok)
                    if ok and value != 0:
                        self.log(f"  {name}: {value:+.2f}%")
                if not self.running:
                    break
                if not all(oks):
                    fail_streak += 1
                    self.log("识别未确认，本轮不点击，等待重试", "warn")
                    if fail_streak >= 3:
                        self.log("连续 3 次识别失败，已停止；检查游戏画面后按 F5 重新开始", "bad")
                        break
                    if not self._wait_running(0.5):
                        break
                    continue
                fail_streak = 0
                if self.run_mode == "单洗":
                    do_replace = vals[0] > 0
                    self.log("  -> 属性增加，替换" if do_replace else "  -> 属性未增加，重洗",
                             "good" if do_replace else "warn")
                else:
                    do_replace = self._should_replace(vals, keys)
                if do_replace:
                    if not self._safe_click("replace"):
                        break
                    # Once replacement has opened its dialog, finish that transaction only.
                    time.sleep(0.5)
                    if not self.running:
                        self.log("正在完成已打开的替换确认，随后停止", "info")
                    self._safe_click("confirm", finish_confirmation=True)
                    expected = self._expected_totals(before, keys, vals)
                    verified = self._read_totals(keys, expected=expected, finish=True)
                    if verified is None:
                        self.log("替换结果未通过核验，可能画面延迟或识别不一致；已停止，本次不计入累计，请检查游戏", "bad")
                        break
                    self.stat_replaced += 1
                    actual_changes = [(verified[name][0] - before[name][0]) / 100 for name in keys]
                    self._record_gains(keys, actual_changes)
                    for name in keys:
                        self.log(f"替换已核验｜{name}: {before[name][0] / 100:.2f}% → {verified[name][0] / 100:.2f}%", "good")
                    need_refine = True
                    if self.run_mode == "单洗" and verified[keys[0]][0] == verified[keys[0]][1]:
                        self.stat_total += 1
                        self._update_stats()
                        self.log(f"{keys[0]}已达到上限 {verified[keys[0]][1] / 100:.2f}%，自动停止", "good")
                        break
                else:
                    if not self._safe_click("reroll"):
                        break
                    self.stat_rerolled += 1
                self.stat_total += 1
                self._update_stats()
        except Exception as e:
            self.log(f"运行异常，已停止: {type(e).__name__}: {e}", "bad")
        finally:
            if self.sct is not None:
                self.sct.close()
            self.log("洗炼结束", "info")
            self._update_stats()
            self.root.after(0, self._stop)


# ========= Launch =========
if __name__ == "__main__":
    root = tk.Tk()
    RefineApp(root)
    root.mainloop()
