"""Start the GUI and retain startup errors without a console window."""
from pathlib import Path
import contextlib
import runpy
import traceback

base = Path(__file__).resolve().parent
logs = base / "logs"
logs.mkdir(exist_ok=True)
with (logs / "startup.log").open("w", encoding="utf-8", buffering=1) as stream:
    with contextlib.redirect_stdout(stream), contextlib.redirect_stderr(stream):
        try:
            runpy.run_path(str(base / "auto_refine_gui.py"), run_name="__main__")
        except Exception:
            traceback.print_exc()
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("启动失败", "请查看 logs/startup.log，或运行 debug_run.bat 查看错误。")
            root.destroy()
