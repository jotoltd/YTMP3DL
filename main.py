import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import sys
import subprocess
import json
import re
import tempfile
import shutil
import ctypes
import time
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

VERSION = "1.1.7"
GITHUB_REPO = "jotoltd/YTMP3DL"

# Resolve ffmpeg location: PyInstaller bundle OR local ffmpeg\bin folder
if getattr(sys, "frozen", False):
    # Running as a PyInstaller .exe — ffmpeg was bundled alongside binaries
    _ffmpeg_dir = Path(sys._MEIPASS)
else:
    _ffmpeg_dir = Path(__file__).parent / "ffmpeg" / "bin"

if _ffmpeg_dir.exists() and str(_ffmpeg_dir) not in os.environ.get("PATH", ""):
    os.environ["PATH"] = str(_ffmpeg_dir) + os.pathsep + os.environ.get("PATH", "")

try:
    import yt_dlp
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
    import yt_dlp


ACCENT = "#e94560"
ACCENT_HOVER = "#c73652"

THEMES = {
    "dark": {
        "bg":              "#1a1a2e",
        "panel":           "#16213e",
        "card":            "#0f3460",
        "text":            "#eaeaea",
        "text_dim":        "#a0a0b0",
        "success":         "#4caf50",
        "warning":         "#ff9800",
        "log_bg":          "#0d2137",
        "entry_bg":        "#16213e",
        "progress_trough": "#0d2137",
    },
    "light": {
        "bg":              "#f0f2f5",
        "panel":           "#ffffff",
        "card":            "#e2e8f4",
        "text":            "#1a1a2e",
        "text_dim":        "#6b6b8a",
        "success":         "#2e7d32",
        "warning":         "#bf360c",
        "log_bg":          "#dde3ee",
        "entry_bg":        "#ffffff",
        "progress_trough": "#b8c4d8",
    },
    "ocean": {
        "bg":              "#0a192f",
        "panel":           "#112240",
        "card":            "#1d3a6e",
        "text":            "#ccd6f6",
        "text_dim":        "#8892b0",
        "success":         "#64ffda",
        "warning":         "#ffa07a",
        "log_bg":          "#071424",
        "entry_bg":        "#112240",
        "progress_trough": "#071424",
    },
    "sunset": {
        "bg":              "#1c0f1e",
        "panel":           "#2e1430",
        "card":            "#4a1f4e",
        "text":            "#f5d0d0",
        "text_dim":        "#c08090",
        "success":         "#ff9f43",
        "warning":         "#ff6b6b",
        "log_bg":          "#130a14",
        "entry_bg":        "#2e1430",
        "progress_trough": "#130a14",
    },
    "forest": {
        "bg":              "#0b1a0d",
        "panel":           "#112b14",
        "card":            "#1a4a20",
        "text":            "#d4edda",
        "text_dim":        "#7db87d",
        "success":         "#69db7c",
        "warning":         "#ffd43b",
        "log_bg":          "#071409",
        "entry_bg":        "#112b14",
        "progress_trough": "#071409",
    },
    "midnight": {
        "bg":              "#0d0d1a",
        "panel":           "#14142b",
        "card":            "#1e1e40",
        "text":            "#e0e0ff",
        "text_dim":        "#8888cc",
        "success":         "#a78bfa",
        "warning":         "#f59e0b",
        "log_bg":          "#08080f",
        "entry_bg":        "#14142b",
        "progress_trough": "#08080f",
    },
    "rose": {
        "bg":              "#1a0a12",
        "panel":           "#2d1120",
        "card":            "#4a1a32",
        "text":            "#f0d0e8",
        "text_dim":        "#c07aaa",
        "success":         "#f48fb1",
        "warning":         "#ff8a65",
        "log_bg":          "#12070e",
        "entry_bg":        "#2d1120",
        "progress_trough": "#12070e",
    },
    "neon": {
        "bg":              "#090909",
        "panel":           "#101010",
        "card":            "#1a1a1a",
        "text":            "#e0ffe0",
        "text_dim":        "#55bb55",
        "success":         "#00ff88",
        "warning":         "#ffaa00",
        "log_bg":          "#050505",
        "entry_bg":        "#101010",
        "progress_trough": "#050505",
    },
    "dracula": {
        "bg":              "#282a36",
        "panel":           "#1e1f29",
        "card":            "#44475a",
        "text":            "#f8f8f2",
        "text_dim":        "#6272a4",
        "success":         "#50fa7b",
        "warning":         "#ffb86c",
        "log_bg":          "#191a23",
        "entry_bg":        "#1e1f29",
        "progress_trough": "#191a23",
    },
    "nord": {
        "bg":              "#2e3440",
        "panel":           "#3b4252",
        "card":            "#434c5e",
        "text":            "#eceff4",
        "text_dim":        "#9099aa",
        "success":         "#a3be8c",
        "warning":         "#ebcb8b",
        "log_bg":          "#242933",
        "entry_bg":        "#3b4252",
        "progress_trough": "#242933",
    },
    "slate": {
        "bg":              "#1e2126",
        "panel":           "#282c34",
        "card":            "#3a3f4b",
        "text":            "#abb2bf",
        "text_dim":        "#5c6370",
        "success":         "#98c379",
        "warning":         "#e5c07b",
        "log_bg":          "#171a1f",
        "entry_bg":        "#282c34",
        "progress_trough": "#171a1f",
    },
    "amber": {
        "bg":              "#1a1200",
        "panel":           "#2a1e00",
        "card":            "#3d2c00",
        "text":            "#ffe599",
        "text_dim":        "#cc9933",
        "success":         "#ffcc00",
        "warning":         "#ff6600",
        "log_bg":          "#120d00",
        "entry_bg":        "#2a1e00",
        "progress_trough": "#120d00",
    },
    "coffee": {
        "bg":              "#1a0f07",
        "panel":           "#2b1a0a",
        "card":            "#3d2610",
        "text":            "#f0d8b0",
        "text_dim":        "#a07840",
        "success":         "#c8a46e",
        "warning":         "#ff8c42",
        "log_bg":          "#120b05",
        "entry_bg":        "#2b1a0a",
        "progress_trough": "#120b05",
    },
}

_PREFS_FILE = Path.home() / ".ytmp3dl_prefs.json"

# Legacy aliases (dark theme defaults used at widget-creation time)
DARK_BG = THEMES["dark"]["bg"]
PANEL_BG = THEMES["dark"]["panel"]
CARD_BG = THEMES["dark"]["card"]
TEXT_PRIMARY = THEMES["dark"]["text"]
TEXT_SECONDARY = THEMES["dark"]["text_dim"]
SUCCESS = THEMES["dark"]["success"]
WARNING = THEMES["dark"]["warning"]
PROGRESS_BG = THEMES["dark"]["log_bg"]


class DownloadItem:
    def __init__(self, url, title="Fetching info...", status="Queued", progress=0):
        self.url = url
        self.title = title
        self.status = status
        self.progress = progress
        self.error = None
        self._file_path = None


class WindowsAudioPlayer:
    """MP3 playback via Windows MCI (winmm). Zero extra dependencies."""
    _ALIAS = "ytmp3dl_player"

    def __init__(self):
        self._mci = ctypes.windll.winmm
        self._open = False

    def _send(self, cmd: str) -> int:
        return self._mci.mciSendStringW(cmd, None, 0, 0)

    def _query(self, cmd: str) -> str:
        buf = ctypes.create_unicode_buffer(256)
        self._mci.mciSendStringW(cmd, buf, 256, 0)
        return buf.value.strip()

    def load(self, path: str) -> bool:
        self.close()
        r = self._send(f'open "{path}" alias {self._ALIAS}')
        self._open = (r == 0)
        return self._open

    def play(self):
        if self._open:
            self._send(f'play {self._ALIAS}')

    def pause(self):
        if self._open:
            self._send(f'pause {self._ALIAS}')

    def resume(self):
        if self._open:
            self._send(f'resume {self._ALIAS}')

    def stop(self):
        if self._open:
            self._send(f'stop {self._ALIAS}')

    def close(self):
        if self._open:
            self._send(f'close {self._ALIAS}')
            self._open = False

    def seek(self, ms: int):
        if self._open:
            self._send(f'seek {self._ALIAS} to {ms}')
            self._send(f'play {self._ALIAS}')

    def get_position_ms(self) -> int:
        try:
            return int(self._query(f'status {self._ALIAS} position'))
        except (ValueError, OSError):
            return 0

    def get_length_ms(self) -> int:
        try:
            return int(self._query(f'status {self._ALIAS} length'))
        except (ValueError, OSError):
            return 0

    def mode(self) -> str:
        return self._query(f'status {self._ALIAS} mode')

    def set_volume(self, vol: int):  # 0-1000
        self._send(f'setaudio {self._ALIAS} volume to {vol}')


_THEME_LABELS = {
    "dark":     "Dark",
    "light":    "Light",
    "ocean":    "Ocean",
    "sunset":   "Sunset",
    "forest":   "Forest",
    "midnight": "Midnight",
    "rose":     "Rose",
    "neon":     "Neon",
    "dracula":  "Dracula",
    "nord":     "Nord",
    "slate":    "Slate",
    "amber":    "Amber",
    "coffee":   "Coffee",
}


class ThemePickerDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self._app = parent
        self.title("Choose Theme")
        self.resizable(False, False)
        self.grab_set()

        t = parent.T
        self.configure(bg=t["bg"])

        tk.Label(
            self, text="Choose a Theme",
            font=("Helvetica", 14, "bold"), fg=ACCENT, bg=t["bg"],
        ).pack(pady=(18, 2))
        tk.Label(
            self, text="Click any swatch to apply instantly",
            font=("Helvetica", 10), fg=t["text_dim"], bg=t["bg"],
        ).pack(pady=(0, 14))

        grid = tk.Frame(self, bg=t["bg"])
        grid.pack(padx=20, pady=(0, 6))

        for idx, name in enumerate(THEMES):
            row, col = divmod(idx, 3)
            self._make_swatch(grid, name, row, col)

        tk.Button(
            self, text="Close",
            font=("Helvetica", 10), bg=t["card"], fg=t["text"],
            activebackground=t["panel"], relief=tk.FLAT, cursor="hand2",
            padx=18, pady=6, command=self.destroy,
        ).pack(pady=(8, 18))

        self.update_idletasks()
        pw, ph = parent.winfo_width(), parent.winfo_height()
        px, py = parent.winfo_x(), parent.winfo_y()
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"+{px + (pw - w) // 2}+{py + (ph - h) // 2}")

    def _make_swatch(self, grid, name, row, col):
        th = THEMES[name]
        t_app = self._app.T
        active = (name == self._app._theme_name)

        border = tk.Frame(grid, bg=ACCENT if active else t_app["card"], bd=0)
        border.grid(row=row, column=col, padx=8, pady=8)

        inner = tk.Frame(border, bg=th["panel"], cursor="hand2")
        inner.pack(padx=2 if active else 1, pady=2 if active else 1)

        c = tk.Canvas(inner, width=120, height=64, bg=th["bg"],
                      highlightthickness=0, cursor="hand2")
        c.pack()
        c.create_rectangle(0,  0, 120, 64, fill=th["bg"],    outline="")
        c.create_rectangle(0,  0, 120, 18, fill=th["panel"], outline="")
        c.create_rectangle(6, 24,  58, 58, fill=th["card"],  outline="")
        c.create_oval(     64, 24,  84, 44, fill=ACCENT,          outline="")
        c.create_oval(     88, 24, 108, 44, fill=th["success"],   outline="")

        lbl_f = tk.Frame(inner, bg=th["panel"])
        lbl_f.pack(fill=tk.X)
        tk.Label(
            lbl_f,
            text=("✔  " if active else "   ") + _THEME_LABELS.get(name, name.title()),
            font=("Helvetica", 9, "bold"), bg=th["panel"], fg=th["text"],
            pady=4,
        ).pack()

        for widget in (inner, c, lbl_f):
            widget.bind("<Button-1>", lambda e, n=name: self._apply(n))
        for child in lbl_f.winfo_children():
            child.bind("<Button-1>", lambda e, n=name: self._apply(n))

    def _apply(self, name: str):
        self._app._theme_name = name
        self._app._save_theme_pref()
        self._app._apply_theme()
        self.destroy()


class PlaylistSelectDialog(tk.Toplevel):
    def __init__(self, parent, playlist_title: str, items: list):
        super().__init__(parent)
        self._app = parent
        self.title("Select Tracks")
        self.resizable(True, True)
        self.grab_set()
        self.selected: list = []
        self._items = items
        self._vars: list[tk.BooleanVar] = []

        t = parent.T
        self.configure(bg=t["bg"])
        self.geometry("600x520")

        tk.Label(
            self, text=f"{playlist_title}",
            font=("Helvetica", 13, "bold"), fg=ACCENT, bg=t["bg"],
        ).pack(padx=20, pady=(16, 2))

        tk.Label(
            self, text=f"{len(items)} tracks found — choose which to add:",
            font=("Helvetica", 10), fg=t["text_dim"], bg=t["bg"],
        ).pack()

        btn_row = tk.Frame(self, bg=t["bg"])
        btn_row.pack(fill=tk.X, padx=20, pady=8)
        for label, fn in (("Select All", self._select_all), ("Deselect All", self._deselect_all)):
            tk.Button(
                btn_row, text=label, command=fn,
                font=("Helvetica", 10), bg=t["card"], fg=t["text"],
                activebackground=t["panel"], relief=tk.FLAT, cursor="hand2", padx=10, pady=3,
            ).pack(side=tk.LEFT, padx=(0, 6))

        list_frame = tk.Frame(self, bg=t["panel"], bd=0)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 8))

        canvas = tk.Canvas(list_frame, bg=t["panel"], highlightthickness=0)
        sb = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg=t["panel"])
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        for i, item in enumerate(items):
            var = tk.BooleanVar(value=True)
            self._vars.append(var)
            row_bg = t["card"] if i % 2 == 0 else t["panel"]
            row = tk.Frame(inner, bg=row_bg)
            row.pack(fill=tk.X)
            tk.Checkbutton(
                row, variable=var,
                text=f"  {i+1}.  {item.title[:72]}",
                font=("Helvetica", 10), bg=row_bg, fg=t["text"],
                activebackground=row_bg, selectcolor=t["card"],
                anchor="w", padx=6, pady=5,
            ).pack(fill=tk.X)

        self._count_var = tk.StringVar()
        self._update_count()
        for v in self._vars:
            v.trace_add("write", lambda *_: self._update_count())

        bottom = tk.Frame(self, bg=t["bg"])
        bottom.pack(fill=tk.X, padx=20, pady=(0, 16))
        tk.Button(
            bottom, text="Cancel", command=self.destroy,
            font=("Helvetica", 11), bg=t["card"], fg=t["text_dim"],
            activebackground=t["panel"], relief=tk.FLAT, cursor="hand2", padx=12, pady=6,
        ).pack(side=tk.RIGHT, padx=(8, 0))
        tk.Button(
            bottom, textvariable=self._count_var, command=self._confirm,
            font=("Helvetica", 11, "bold"), bg=ACCENT, fg="white",
            activebackground=ACCENT_HOVER, relief=tk.FLAT, cursor="hand2", padx=12, pady=6,
        ).pack(side=tk.RIGHT)

        self.update_idletasks()
        pw, ph = parent.winfo_width(), parent.winfo_height()
        px, py = parent.winfo_x(), parent.winfo_y()
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"+{px + (pw-w)//2}+{py + (ph-h)//2}")
        self.wait_window()

    def _select_all(self):
        for v in self._vars: v.set(True)

    def _deselect_all(self):
        for v in self._vars: v.set(False)

    def _update_count(self):
        n = sum(1 for v in self._vars if v.get())
        self._count_var.set(f"Add {n} track{'s' if n != 1 else ''}" if n else "Nothing selected")

    def _confirm(self):
        self.selected = [item for item, var in zip(self._items, self._vars) if var.get()]
        self.destroy()


class YouTubeMP3Downloader(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("YouTube MP3 Downloader")
        self.geometry("820x680")
        self.minsize(700, 560)
        self.configure(bg=DARK_BG)

        self._theme_name = self._load_theme_pref()
        self._tw: dict = {}  # widget registry for theme updates

        self.download_path = tk.StringVar(value=str(Path.home() / "Downloads"))
        self.url_var = tk.StringVar()
        self.queue: list[DownloadItem] = []
        self.is_downloading = False
        self._stop_flag = threading.Event()
        self._active_thread = None
        self._update_available = None
        self._audio = None
        self._player_paused = False
        self._player_duration_ms = 0
        self._player_update_id = None

        self._cleanup_old_exe()
        self._build_ui()
        self._init_audio()
        self._apply_theme()
        self._check_ffmpeg()
        threading.Thread(target=self._check_for_updates, daemon=True).start()
        self.after(300, lambda: self._update_status("Checking for updates..."))

    @property
    def T(self) -> dict:
        return THEMES[self._theme_name]

    def _check_ffmpeg(self):
        try:
            subprocess.run(
                ["ffmpeg", "-version"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )
        except (FileNotFoundError, subprocess.CalledProcessError):
            self.after(500, self._warn_ffmpeg)

    def _warn_ffmpeg(self):
        if sys.platform == "win32":
            hint = "Re-run install_and_run.bat to install ffmpeg automatically."
        elif sys.platform == "darwin":
            hint = "Install via Homebrew:\n  brew install ffmpeg"
        else:
            hint = "Install ffmpeg via your package manager (e.g. apt install ffmpeg)."
        messagebox.showwarning(
            "ffmpeg not found",
            "ffmpeg is required for MP3 conversion and was not found.\n\n"
            + hint +
            "\n\nDownloads will fall back to best available audio format without it.",
        )

    def _build_ui(self):
        self._build_header()
        self._build_update_banner()
        self._build_input_section()
        self._build_queue_section()
        self._build_log_section()
        self._build_audio_player()
        self._build_status_bar()

    def _init_audio(self):
        if sys.platform == "win32":
            try:
                self._audio = WindowsAudioPlayer()
            except Exception:
                self._audio = None

    def _build_audio_player(self):
        self._player_frame = tk.Frame(self, bg=PANEL_BG, pady=6, padx=10)
        self._tw["player_frame"] = self._player_frame

        self._play_pause_btn = tk.Button(
            self._player_frame, text="⏸", font=("Helvetica", 15), width=2,
            bg=PANEL_BG, fg=ACCENT,
            activebackground=CARD_BG, activeforeground=ACCENT,
            relief=tk.FLAT, cursor="hand2", bd=0,
            command=self._player_toggle_pause,
        )
        self._play_pause_btn.pack(side=tk.LEFT, padx=(0, 2))

        stop_btn = tk.Button(
            self._player_frame, text="⏹", font=("Helvetica", 13), width=2,
            bg=PANEL_BG, fg=TEXT_SECONDARY,
            activebackground=CARD_BG,
            relief=tk.FLAT, cursor="hand2", bd=0,
            command=self._player_stop,
        )
        stop_btn.pack(side=tk.LEFT, padx=(0, 10))
        self._tw["player_stop_btn"] = stop_btn

        self._player_title_var = tk.StringVar(value="")
        title_lbl = tk.Label(
            self._player_frame, textvariable=self._player_title_var,
            font=("Helvetica", 10, "bold"), fg=TEXT_PRIMARY, bg=PANEL_BG,
            width=30, anchor="w",
        )
        title_lbl.pack(side=tk.LEFT)
        self._tw["player_title"] = title_lbl

        self._player_time_var = tk.StringVar(value="0:00 / 0:00")
        time_lbl = tk.Label(
            self._player_frame, textvariable=self._player_time_var,
            font=("Helvetica", 9), fg=TEXT_SECONDARY, bg=PANEL_BG, width=13,
        )
        time_lbl.pack(side=tk.LEFT, padx=(4, 6))
        self._tw["player_time"] = time_lbl

        self._player_canvas = tk.Canvas(
            self._player_frame, height=8, bg=PANEL_BG,
            highlightthickness=0, cursor="hand2",
        )
        self._player_canvas.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        self._player_canvas.bind("<Button-1>", self._player_seek_click)
        self._tw["player_canvas"] = self._player_canvas

        vol_lbl = tk.Label(
            self._player_frame, text="🔊", font=("Helvetica", 10),
            bg=PANEL_BG, fg=TEXT_SECONDARY,
        )
        vol_lbl.pack(side=tk.LEFT)
        self._tw["player_vol_lbl"] = vol_lbl

        self._volume_var = tk.IntVar(value=80)
        self._vol_slider = tk.Scale(
            self._player_frame, from_=0, to=100,
            orient=tk.HORIZONTAL, variable=self._volume_var,
            command=self._player_set_volume,
            length=75, showvalue=False,
            bg=PANEL_BG, fg=TEXT_SECONDARY,
            troughcolor=CARD_BG, activebackground=ACCENT,
            highlightthickness=0, bd=0, sliderlength=12,
        )
        self._vol_slider.pack(side=tk.LEFT, padx=(2, 8))
        self._tw["player_vol_slider"] = self._vol_slider

        close_btn = tk.Button(
            self._player_frame, text="✕",
            font=("Helvetica", 9), bg=PANEL_BG, fg=TEXT_SECONDARY,
            activebackground=CARD_BG, relief=tk.FLAT, cursor="hand2",
            command=self._player_stop,
        )
        close_btn.pack(side=tk.LEFT)
        self._tw["player_close_btn"] = close_btn

    def _build_header(self):
        header = tk.Frame(self, bg=PANEL_BG, height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        self._tw["header"] = header

        inner = tk.Frame(header, bg=PANEL_BG)
        inner.place(relx=0.5, rely=0.5, anchor="center")
        self._tw["header_inner"] = inner

        lbl_title = tk.Label(
            inner, text="▶  YouTube MP3 Downloader",
            font=("Helvetica", 22, "bold"), fg=ACCENT, bg=PANEL_BG,
        )
        lbl_title.pack(side=tk.LEFT)
        self._tw["title"] = lbl_title

        lbl_quality = tk.Label(
            inner, text="  320 kbps", font=("Helvetica", 11),
            fg=SUCCESS, bg=PANEL_BG,
        )
        lbl_quality.pack(side=tk.LEFT, pady=(8, 0))
        self._tw["quality"] = lbl_quality

        lbl_version = tk.Label(
            inner, text=f"  v{VERSION}", font=("Helvetica", 9),
            fg=TEXT_SECONDARY, bg=PANEL_BG,
        )
        lbl_version.pack(side=tk.LEFT, pady=(10, 0))
        self._tw["version"] = lbl_version

        right = tk.Frame(header, bg=PANEL_BG)
        right.place(relx=1.0, rely=0.5, anchor="e", x=-12)
        self._tw["header_right"] = right

        self._theme_btn = tk.Button(
            right,
            text="🎨  Theme",
            command=self._open_theme_picker,
            font=("Helvetica", 9),
            bg=PANEL_BG, fg=TEXT_SECONDARY,
            activebackground=CARD_BG, activeforeground=TEXT_PRIMARY,
            relief=tk.FLAT, cursor="hand2",
            padx=8, pady=4, bd=0,
        )
        self._theme_btn.pack(side=tk.LEFT, padx=(0, 6))

        self._update_check_btn = tk.Button(
            right,
            text="⟳  Check for Updates",
            command=self._manual_update_check,
            font=("Helvetica", 9),
            bg=PANEL_BG, fg=TEXT_SECONDARY,
            activebackground=CARD_BG, activeforeground=TEXT_PRIMARY,
            relief=tk.FLAT, cursor="hand2",
            padx=10, pady=4, bd=0,
        )
        self._update_check_btn.pack(side=tk.LEFT)

    def _build_input_section(self):
        frame = tk.Frame(self, bg=DARK_BG, padx=20, pady=14)
        frame.pack(fill=tk.X)
        self._tw["input_frame"] = frame

        lbl_url = tk.Label(
            frame, text="YouTube URL", font=("Helvetica", 10, "bold"),
            fg=TEXT_SECONDARY, bg=DARK_BG,
        )
        lbl_url.grid(row=0, column=0, sticky="w", pady=(0, 4))
        self._tw["url_label"] = lbl_url

        url_row = tk.Frame(frame, bg=DARK_BG)
        url_row.grid(row=1, column=0, sticky="ew")
        frame.columnconfigure(0, weight=1)
        self._tw["url_row"] = url_row

        self.url_entry = tk.Entry(
            url_row,
            textvariable=self.url_var,
            font=("Helvetica", 12),
            bg=PANEL_BG,
            fg=TEXT_PRIMARY,
            insertbackground=TEXT_PRIMARY,
            relief=tk.FLAT,
            bd=0,
        )
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, ipadx=10)
        self.url_entry.bind("<Return>", lambda e: self._add_to_queue())
        self.url_entry.bind("<Button-3>", self._show_entry_context_menu)
        self._tw["url_entry"] = self.url_entry

        self._add_btn = tk.Button(
            url_row,
            text="Add to Queue",
            command=self._add_to_queue,
            font=("Helvetica", 11, "bold"),
            bg=ACCENT,
            fg="white",
            activebackground=ACCENT_HOVER,
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            padx=16,
            pady=8,
        )
        self._add_btn.pack(side=tk.LEFT, padx=(8, 0))

        dir_row = tk.Frame(frame, bg=DARK_BG)
        dir_row.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        self._tw["dir_row"] = dir_row

        lbl_save = tk.Label(
            dir_row, text="Save to:", font=("Helvetica", 10),
            fg=TEXT_SECONDARY, bg=DARK_BG,
        )
        lbl_save.pack(side=tk.LEFT)
        self._tw["save_label"] = lbl_save

        self.dir_label = tk.Label(
            dir_row,
            textvariable=self.download_path,
            font=("Helvetica", 10),
            fg=TEXT_PRIMARY,
            bg=DARK_BG,
            anchor="w",
        )
        self.dir_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 0))
        self._tw["dir_label"] = self.dir_label

        browse_btn = tk.Button(
            dir_row,
            text="Browse",
            command=self._browse_dir,
            font=("Helvetica", 10),
            bg=CARD_BG,
            fg=TEXT_PRIMARY,
            activebackground=ACCENT,
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            padx=10,
            pady=4,
        )
        browse_btn.pack(side=tk.RIGHT)
        self._tw["browse_btn"] = browse_btn

    def _build_queue_section(self):
        outer = tk.Frame(self, bg=DARK_BG, padx=20)
        outer.pack(fill=tk.BOTH, expand=True)
        self._tw["queue_outer"] = outer

        header_row = tk.Frame(outer, bg=DARK_BG)
        header_row.pack(fill=tk.X, pady=(6, 6))
        self._tw["queue_header_row"] = header_row

        lbl_queue = tk.Label(
            header_row, text="Download Queue",
            font=("Helvetica", 11, "bold"), fg=TEXT_PRIMARY, bg=DARK_BG,
        )
        lbl_queue.pack(side=tk.LEFT)
        self._tw["queue_title"] = lbl_queue

        self.download_btn = tk.Button(
            header_row,
            text="⬇  Download All",
            command=self._start_downloads,
            font=("Helvetica", 11, "bold"),
            bg=SUCCESS,
            fg="white",
            activebackground="#388e3c",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            padx=14,
            pady=5,
            state=tk.DISABLED,
        )
        self.download_btn.pack(side=tk.RIGHT)

        self._stop_btn = tk.Button(
            header_row,
            text="⬛  Stop",
            command=self._stop_downloads,
            font=("Helvetica", 10, "bold"),
            bg="#7b1a1a",
            fg="#ffcccc",
            activebackground="#a02020",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            padx=10,
            pady=5,
            state=tk.DISABLED,
        )
        self._stop_btn.pack(side=tk.RIGHT, padx=(0, 8))

        clear_btn = tk.Button(
            header_row,
            text="Clear Queue",
            command=self._clear_queue,
            font=("Helvetica", 10),
            bg=CARD_BG,
            fg=TEXT_SECONDARY,
            activebackground=ACCENT,
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            padx=10,
            pady=5,
        )
        clear_btn.pack(side=tk.RIGHT, padx=(0, 8))
        self._tw["clear_btn"] = clear_btn

        list_frame = tk.Frame(outer, bg=PANEL_BG)
        list_frame.pack(fill=tk.BOTH, expand=True)
        self._tw["list_frame"] = list_frame

        self.queue_canvas = tk.Canvas(list_frame, bg=PANEL_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.queue_canvas.yview)
        self.queue_inner = tk.Frame(self.queue_canvas, bg=PANEL_BG)

        self.queue_inner.bind(
            "<Configure>",
            lambda e: self.queue_canvas.configure(scrollregion=self.queue_canvas.bbox("all")),
        )
        self.queue_canvas.create_window((0, 0), window=self.queue_inner, anchor="nw")
        self.queue_canvas.configure(yscrollcommand=scrollbar.set)

        self.queue_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.queue_canvas.bind("<MouseWheel>", self._on_mousewheel)

        self._empty_label = tk.Label(
            self.queue_inner,
            text="No items in queue. Paste a YouTube URL above and click 'Add to Queue'.",
            font=("Helvetica", 11),
            fg=TEXT_SECONDARY,
            bg=PANEL_BG,
            pady=30,
        )
        self._empty_label.pack()

        self._item_frames: list[tk.Frame] = []

    def _build_log_section(self):
        frame = tk.Frame(self, bg=DARK_BG, padx=20)
        frame.pack(fill=tk.X, pady=(0, 6))
        self._tw["log_frame"] = frame

        lbl_log = tk.Label(
            frame, text="Log", font=("Helvetica", 10, "bold"),
            fg=TEXT_SECONDARY, bg=DARK_BG,
        )
        lbl_log.pack(anchor="w")
        self._tw["log_label"] = lbl_log

        self.log_text = tk.Text(
            frame,
            height=5,
            font=("Courier", 10),
            bg=PROGRESS_BG,
            fg=TEXT_SECONDARY,
            insertbackground=TEXT_PRIMARY,
            relief=tk.FLAT,
            state=tk.DISABLED,
            wrap=tk.WORD,
        )
        self.log_text.pack(fill=tk.X, pady=(4, 0))

    def _build_status_bar(self):
        self.status_var = tk.StringVar(value="Ready")
        bar = tk.Frame(self, bg=PANEL_BG, height=26)
        bar.pack(fill=tk.X, side=tk.BOTTOM)
        bar.pack_propagate(False)
        self._tw["status_bar"] = bar

        lbl_status = tk.Label(
            bar, textvariable=self.status_var,
            font=("Helvetica", 10), fg=TEXT_SECONDARY, bg=PANEL_BG, anchor="w", padx=12,
        )
        lbl_status.pack(fill=tk.X, pady=4)
        self._tw["status_lbl"] = lbl_status

    def _build_update_banner(self):
        self._update_frame = tk.Frame(self, bg="#2d4a1e", pady=8)

        dismiss_btn = tk.Button(
            self._update_frame, text="✕",
            font=("Helvetica", 9), bg="#2d4a1e", fg="#a5d6a7",
            activebackground="#1b3a12", relief=tk.FLAT, cursor="hand2",
            command=lambda: self._update_frame.pack_forget(),
        )
        dismiss_btn.pack(side=tk.RIGHT, padx=(0, 10))

        self._update_btn = tk.Button(
            self._update_frame,
            text="⬇  Install Update",
            font=("Helvetica", 10, "bold"),
            bg="#66bb6a", fg="#0a1f0a",
            activebackground="#81c784", activeforeground="#0a1f0a",
            relief=tk.FLAT, cursor="hand2",
            padx=14, pady=4,
            command=self._apply_update,
        )
        self._update_btn.pack(side=tk.RIGHT, padx=(0, 8))

        self._update_label = tk.Label(
            self._update_frame, text="",
            font=("Helvetica", 10), fg="#c8e6c9", bg="#2d4a1e",
        )
        self._update_label.pack(side=tk.LEFT, padx=(16, 8))

    def _manual_update_check(self):
        self._set_update_btn("⟳  Checking...", TEXT_SECONDARY, state=tk.DISABLED)
        self._update_status("Checking for updates...")
        threading.Thread(target=self._check_for_updates, args=(True,), daemon=True).start()

    def _set_update_btn(self, text: str, color: str, state=tk.NORMAL):
        self.after(0, lambda: self._update_check_btn.config(text=text, fg=color, state=state))

    def _check_for_updates(self, manual: bool = False):
        if "YOUR_USERNAME" in GITHUB_REPO:
            return
        try:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
            req = urllib.request.Request(url, headers={"User-Agent": "YT-MP3-Downloader"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode())
            latest_tag = data.get("tag_name", "").lstrip("v")
            if not latest_tag:
                self._set_update_btn("⟳  Check for Updates", TEXT_SECONDARY)
                return
            if self._version_tuple(latest_tag) > self._version_tuple(VERSION):
                assets = data.get("assets", [])
                dl_url = next(
                    (a["browser_download_url"] for a in assets if a["name"].endswith(".exe")),
                    None,
                )
                self._update_available = {"version": latest_tag, "url": dl_url}
                self._set_update_btn(f"⬆  Update to v{latest_tag}", "#ffca28")
                self.after(0, lambda: self._show_update_banner(latest_tag))
            else:
                self._set_update_btn("✓  Up to date", SUCCESS)
                self._update_status(f"v{VERSION} is up to date.")
                if manual:
                    self.after(0, lambda: messagebox.showinfo(
                        "Up to Date", f"You're running the latest version (v{VERSION})."
                    ))
                self.after(4000, lambda: self._set_update_btn("⟳  Check for Updates", TEXT_SECONDARY))
        except Exception:
            self._set_update_btn("⟳  Check for Updates", TEXT_SECONDARY)
            if manual:
                self.after(0, lambda: messagebox.showwarning(
                    "Update Check Failed", "Could not reach GitHub. Check your internet connection."
                ))
            self._update_status("Ready")

    @staticmethod
    def _version_tuple(v: str):
        try:
            return tuple(int(x) for x in v.split("."))
        except ValueError:
            return (0,)

    def _show_update_banner(self, version: str):
        has_url = bool(self._update_available and self._update_available.get("url"))
        self._update_label.config(
            text=f"🔔  v{version} is available  —  "
                 + ("the app will restart automatically after installing." if has_url
                    else "click to open the download page.")
        )
        self._update_btn.config(text="⬇  Install Update" if has_url else "🌐  Download Page")
        self._update_frame.pack(fill=tk.X)
        self._log(f"Update available: v{version}")

    def _apply_update(self):
        import webbrowser
        if not self._update_available or not self._update_available.get("url"):
            webbrowser.open(f"https://github.com/{GITHUB_REPO}/releases/latest")
            return
        if not getattr(sys, "frozen", False):
            webbrowser.open(f"https://github.com/{GITHUB_REPO}/releases/latest")
            return
        self._update_btn.config(state=tk.DISABLED, text="⏳  Downloading...")
        threading.Thread(target=self._download_and_replace, daemon=True).start()

    def _cleanup_old_exe(self):
        if not getattr(sys, "frozen", False):
            return
        try:
            old = sys.executable + ".old"
            if os.path.exists(old):
                os.remove(old)
        except Exception:
            pass

    def _download_and_replace(self):
        try:
            dl_url = self._update_available["url"]
            tmp_dir = tempfile.mkdtemp()
            tmp_exe = os.path.join(tmp_dir, "update.exe")
            current_exe = sys.executable

            def _reporthook(count, block, total):
                if total > 0:
                    pct = min(100, int(count * block * 100 / total))
                    self._update_status(f"Downloading update... {pct}%")

            urllib.request.urlretrieve(dl_url, tmp_exe, _reporthook)

            if os.path.getsize(tmp_exe) < 500_000:
                raise Exception("Download appears corrupted (file too small).")

            self._update_status("Installing update...")

            backup_exe = current_exe + ".old"

            # Remove stale backup if present
            try:
                if os.path.exists(backup_exe):
                    os.remove(backup_exe)
            except Exception:
                pass

            # Rename the running exe — Windows allows this via FILE_SHARE_DELETE.
            # The process keeps running because it holds an internal handle to the
            # original file object, not to the path.
            os.rename(current_exe, backup_exe)

            try:
                # Copy the downloaded exe to the now-vacant original path.
                # This creates a brand-new file; no write-lock issue.
                shutil.copy2(tmp_exe, current_exe)
            except Exception as copy_err:
                # Restore original if copy failed
                try:
                    os.rename(backup_exe, current_exe)
                except Exception:
                    pass
                raise copy_err

            # Launch the updated exe in its own process group so it is fully
            # independent before we exit.  Once Popen() returns, CreateProcess
            # has already created the new process — we can exit immediately.
            subprocess.Popen(
                [current_exe],
                creationflags=(
                    subprocess.DETACHED_PROCESS
                    | subprocess.CREATE_NEW_PROCESS_GROUP
                ),
                close_fds=True,
            )
            # os._exit terminates every thread in this process instantly from
            # any thread — no Tk event loop needed, no sleep required.
            os._exit(0)

        except Exception as e:
            self._log(f"Update failed: {e}")
            self.after(0, lambda: self._update_btn.config(state=tk.NORMAL, text="⬇  Install Update"))

    def _show_entry_context_menu(self, event):
        menu = tk.Menu(self, tearoff=0)
        t = self.T
        menu.configure(bg=t["card"], fg=t["text"], activebackground=ACCENT, activeforeground="white")
        menu.add_command(label="Cut",        command=lambda: self.url_entry.event_generate("<<Cut>>"))
        menu.add_command(label="Copy",       command=lambda: self.url_entry.event_generate("<<Copy>>"))
        menu.add_command(label="Paste",      command=lambda: self.url_entry.event_generate("<<Paste>>"))
        menu.add_separator()
        menu.add_command(label="Select All", command=lambda: self.url_entry.select_range(0, tk.END))
        menu.add_command(label="Clear",      command=lambda: self.url_var.set(""))
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _on_mousewheel(self, event):
        self.queue_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _browse_dir(self):
        path = filedialog.askdirectory(initialdir=self.download_path.get())
        if path:
            self.download_path.set(path)

    def _is_playlist_url(self, url: str) -> bool:
        return "list=" in url and ("youtube.com" in url or "youtu.be" in url)

    def _expand_playlist(self, url: str):
        try:
            self.after(0, lambda: self._update_status("Fetching playlist info..."))
            ydl_opts = {"extract_flat": "in_playlist", "quiet": True, "no_warnings": True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
            entries = info.get("entries") or []
            playlist_title = info.get("title", "Playlist")
            items_to_add = []
            for e in entries:
                if not e:
                    continue
                vid_id = e.get("id", "")
                vid_url = e.get("url") or (f"https://www.youtube.com/watch?v={vid_id}" if vid_id else None)
                if not vid_url:
                    continue
                if not vid_url.startswith("http"):
                    vid_url = f"https://www.youtube.com/watch?v={vid_id}"
                items_to_add.append(DownloadItem(url=vid_url, title=e.get("title", "Unknown")))

            def _add_all():
                if not items_to_add:
                    self._log("Playlist had no downloadable tracks.")
                    return
                dlg = PlaylistSelectDialog(self, playlist_title, items_to_add)
                selected = dlg.selected
                if not selected:
                    self._update_status("No tracks selected.")
                    return
                for item in selected:
                    self.queue.append(item)
                    self._add_queue_item_widget(item)
                self._update_empty_label()
                self.download_btn.config(state=tk.NORMAL)
                self._log(f"Added {len(selected)}/{len(items_to_add)} tracks from: {playlist_title}")
                self._update_status(f"Added {len(selected)} track(s) to queue")
            self.after(0, _add_all)
        except Exception as e:
            self._log(f"Playlist error: {e}")
            self.after(0, lambda: self._update_status("Ready"))

    def _add_to_queue(self):
        raw = self.url_var.get().strip()
        if not raw:
            return

        urls = [u.strip() for u in raw.splitlines() if u.strip()]
        if not urls:
            urls = [raw]

        added = 0
        for url in urls:
            if not re.match(r"https?://", url):
                self._log(f"Invalid URL skipped: {url}")
                continue
            if self._is_playlist_url(url):
                self.url_var.set("")
                self._log(f"Playlist detected — fetching track list...")
                threading.Thread(target=self._expand_playlist, args=(url,), daemon=True).start()
                continue
            item = DownloadItem(url=url)
            self.queue.append(item)
            self._add_queue_item_widget(item)
            added += 1

        if added:
            self.url_var.set("")
            self._update_empty_label()
            self.download_btn.config(state=tk.NORMAL)
            self._log(f"Added {added} item(s) to queue.")

    def _add_queue_item_widget(self, item: DownloadItem):
        idx = len(self.queue) - 1
        frame = tk.Frame(self.queue_inner, bg=CARD_BG, pady=8, padx=12)
        frame.pack(fill=tk.X, padx=6, pady=4)
        frame.grid_columnconfigure(1, weight=1)

        num_label = tk.Label(
            frame, text=f"{idx + 1}.", font=("Helvetica", 10, "bold"),
            fg=TEXT_SECONDARY, bg=CARD_BG, width=3, anchor="e",
        )
        num_label.grid(row=0, column=0, rowspan=2, padx=(0, 10))

        title_label = tk.Label(
            frame, text=item.title, font=("Helvetica", 11, "bold"),
            fg=TEXT_PRIMARY, bg=CARD_BG, anchor="w",
        )
        title_label.grid(row=0, column=1, sticky="ew")

        url_label = tk.Label(
            frame,
            text=item.url[:80] + ("..." if len(item.url) > 80 else ""),
            font=("Helvetica", 9),
            fg=TEXT_SECONDARY,
            bg=CARD_BG,
            anchor="w",
        )
        url_label.grid(row=1, column=1, sticky="ew")

        status_label = tk.Label(
            frame, text=item.status, font=("Helvetica", 10),
            fg=TEXT_SECONDARY, bg=CARD_BG, anchor="e",
        )
        status_label.grid(row=0, column=2, padx=(10, 0))

        progress_bar = ttk.Progressbar(
            frame, length=200, mode="determinate", maximum=100
        )
        progress_bar.grid(row=1, column=2, padx=(10, 0), pady=(2, 0))
        progress_bar["value"] = 0
        progress_bar.configure(style="Themed.Horizontal.TProgressbar")

        play_btn = tk.Button(
            frame, text="▶  Play",
            font=("Helvetica", 9, "bold"),
            bg=CARD_BG, fg=SUCCESS,
            activebackground=SUCCESS, activeforeground="white",
            relief=tk.FLAT, cursor="hand2",
            padx=8, pady=2,
        )
        play_btn.grid(row=2, column=1, columnspan=2, sticky="e", padx=(10, 0), pady=(3, 0))
        play_btn.grid_remove()
        play_btn.config(command=lambda i=item: self._play_file(i._file_path))

        item._card_frame = frame
        item._num_label = num_label
        item._title_label = title_label
        item._url_label_widget = url_label
        item._status_label = status_label
        item._progress_bar = progress_bar
        item._play_btn = play_btn

        self._item_frames.append(frame)
        self._apply_card_theme(item)

    def _update_empty_label(self):
        if self.queue:
            self._empty_label.pack_forget()
        else:
            self._empty_label.pack()

    def _clear_queue(self):
        if self.is_downloading:
            messagebox.showwarning("Downloading", "Cannot clear queue while downloading.")
            return
        self.queue.clear()
        for f in self._item_frames:
            f.destroy()
        self._item_frames.clear()
        self._update_empty_label()
        self.download_btn.config(state=tk.DISABLED)
        self._log("Queue cleared.")

    def _stop_downloads(self):
        self._stop_flag.set()
        self._stop_btn.config(state=tk.DISABLED, text="Stopping...")
        self._update_status("Stopping after current track...")

    def _start_downloads(self):
        if self.is_downloading:
            return
        pending = [item for item in self.queue if item.status in ("Queued", "Error")]
        if not pending:
            messagebox.showinfo("Nothing to download", "No pending items in the queue.")
            return
        self._stop_flag.clear()
        self.is_downloading = True
        self.download_btn.config(state=tk.DISABLED, text="Downloading...")
        self._stop_btn.config(state=tk.NORMAL, text="⬛  Stop")
        self._add_btn.config(state=tk.DISABLED)
        self._active_thread = threading.Thread(
            target=self._download_all, args=(pending,), daemon=True
        )
        self._active_thread.start()

    @staticmethod
    def _fmt_duration(seconds: int) -> str:
        if seconds < 0:
            return "?"
        if seconds < 60:
            return f"{seconds}s"
        m, s = divmod(seconds, 60)
        if m < 60:
            return f"{m}:{s:02d}"
        h, m2 = divmod(m, 60)
        return f"{h}:{m2:02d}:{s:02d}"

    def _download_all(self, items: list[DownloadItem]):
        total = len(items)
        self._dl_current_idx = 0
        self._dl_total = total
        self._dl_track_times: list[float] = []

        self._update_status(f"Starting {total} track{'s' if total > 1 else ''}...")

        for i, item in enumerate(items):
            if self._stop_flag.is_set():
                break
            self._dl_current_idx = i
            _track_start = time.monotonic()
            self._download_item(item)
            elapsed = time.monotonic() - _track_start
            if item.status.startswith("✓"):
                self._dl_track_times.append(elapsed)
            # Post-track playlist ETA
            remaining = total - (i + 1)
            if remaining > 0 and self._dl_track_times and not self._stop_flag.is_set():
                avg = sum(self._dl_track_times) / len(self._dl_track_times)
                eta_s = int(avg * remaining)
                self._update_status(
                    f"✓ {i + 1}/{total} done  —  {remaining} left  —  ~{self._fmt_duration(eta_s)} remaining"
                )

        self.is_downloading = False
        self.after(0, self._on_all_done)

    def _download_item(self, item: DownloadItem):
        self._set_item_status(item, "Downloading...", TEXT_PRIMARY)
        self._set_item_progress(item, 0)

        out_dir = self.download_path.get()
        os.makedirs(out_dir, exist_ok=True)

        def pp_hook(d):
            if d.get("status") == "finished":
                fp = (d.get("info_dict") or {}).get("filepath") or d.get("filename", "")
                if fp:
                    item._file_path = os.path.splitext(fp)[0] + ".mp3" if not fp.endswith(".mp3") else fp

        def progress_hook(d):
            if self._stop_flag.is_set():
                raise Exception("__stopped__")
            if d["status"] == "downloading":
                pct_str = d.get("_percent_str", "0%").strip().replace("%", "")
                try:
                    pct = float(pct_str)
                except ValueError:
                    pct = 0
                speed = d.get("_speed_str", "").strip()
                eta_secs = d.get("eta")

                i   = getattr(self, "_dl_current_idx", 0)
                tot = getattr(self, "_dl_total", 1)

                # Per-track ETA
                if isinstance(eta_secs, (int, float)) and eta_secs >= 0:
                    track_eta = self._fmt_duration(int(eta_secs))
                else:
                    track_eta = d.get("_eta_str", "").strip().lstrip("0:") or "?"

                # Playlist ETA estimate
                track_times = getattr(self, "_dl_track_times", [])
                playlist_part = ""
                if tot > 1:
                    remaining_tracks = tot - i - 1
                    if track_times:
                        avg = sum(track_times) / len(track_times)
                        # remaining tracks * avg + rest of this track
                        rest_this = int(eta_secs) if isinstance(eta_secs, (int, float)) else 0
                        rest_this += 30  # approx conversion time
                        playlist_eta_s = rest_this + int(avg * remaining_tracks)
                        playlist_part = f"  ·  Playlist ~{self._fmt_duration(playlist_eta_s)} left"
                    else:
                        playlist_part = f"  ·  Track {i + 1}/{tot}"

                speed_part = f"  ↓ {speed}" if speed else ""
                self._set_item_progress(item, pct)
                self._set_item_status(
                    item,
                    f"{pct:.0f}%  ETA {track_eta}",
                    TEXT_PRIMARY,
                )
                self._update_status(
                    f"Track {i + 1}/{tot}  |  {pct:.0f}%{speed_part}  —  ETA {track_eta}{playlist_part}"
                )
            elif d["status"] == "finished":
                self._set_item_progress(item, 100)
                self._set_item_status(item, "Converting...", WARNING)

        ydl_opts = {
            "format": "bestaudio/best",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "320",
                },
                {
                    "key": "FFmpegMetadata",
                    "add_metadata": True,
                },
                {
                    "key": "EmbedThumbnail",
                },
            ],
            "outtmpl": os.path.join(out_dir, "%(title)s.%(ext)s"),
            "progress_hooks": [progress_hook],
            "quiet": True,
            "no_warnings": True,
            "writethumbnail": True,
            "noplaylist": True,
            "postprocessor_hooks": [pp_hook],
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(item.url, download=False)
                title = info.get("title", item.url)
                self._set_item_title(item, title)
                self._log(f"Starting: {title}")
                ydl.download([item.url])
            self._set_item_status(item, "✓ Done", SUCCESS)
            self._log(f"Completed: {title}")
            self.after(0, lambda i=item: i._play_btn.grid() if hasattr(i, "_play_btn") else None)
        except Exception as e:
            if "__stopped__" in str(e) or self._stop_flag.is_set():
                self._set_item_status(item, "⬛ Stopped", TEXT_SECONDARY)
                self._set_item_progress(item, 0)
            else:
                item.error = str(e)
                self._set_item_status(item, "✗ Error", ACCENT)
                self._log(f"Error: {str(e)[:120]}")

    def _on_all_done(self):
        self.download_btn.config(state=tk.NORMAL, text="⬇  Download All")
        self._stop_btn.config(state=tk.DISABLED, text="⬛  Stop")
        self._add_btn.config(state=tk.NORMAL)
        done = sum(1 for i in self.queue if i.status == "✓ Done")
        errors = sum(1 for i in self.queue if i.status == "✗ Error")
        msg = f"Done — {done} succeeded"
        if errors:
            msg += f", {errors} failed"
        self._update_status(msg)
        self._log(f"All downloads finished. {msg}")
        if done:
            messagebox.showinfo(
                "Downloads Complete",
                f"{done} file(s) saved to:\n{self.download_path.get()}",
            )

    def _set_item_title(self, item: DownloadItem, title: str):
        item.title = title
        self.after(0, lambda: item._title_label.config(text=title[:90]))

    def _set_item_status(self, item: DownloadItem, status: str, color: str):
        item.status = status
        self.after(0, lambda: item._status_label.config(text=status, fg=color))

    def _set_item_progress(self, item: DownloadItem, value: float):
        item.progress = value
        self.after(0, lambda: item._progress_bar.config(value=value))

    def _update_status(self, msg: str):
        self.after(0, lambda: self.status_var.set(msg))

    def _log(self, msg: str):
        ts = datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}]  {msg}\n"

        def _append():
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, line)
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)

        self.after(0, _append)

    # ── Theming ──────────────────────────────────────────────────────────

    def _load_theme_pref(self) -> str:
        try:
            name = json.loads(_PREFS_FILE.read_text()).get("theme", "dark")
            return name if name in THEMES else "dark"
        except Exception:
            return "dark"

    def _save_theme_pref(self):
        try:
            _PREFS_FILE.write_text(json.dumps({"theme": self._theme_name}))
        except Exception:
            pass

    def _open_theme_picker(self):
        ThemePickerDialog(self)

    def _configure_ttk_style(self):
        style = ttk.Style()
        style.theme_use("default")
        t = self.T
        style.configure(
            "Themed.Horizontal.TProgressbar",
            troughcolor=t["progress_trough"],
            background=ACCENT,
            bordercolor=t["card"],
            lightcolor=ACCENT,
            darkcolor=ACCENT,
        )
        style.configure(
            "Vertical.TScrollbar",
            background=t["panel"],
            troughcolor=t["bg"],
            bordercolor=t["bg"],
            arrowcolor=t["text_dim"],
            darkcolor=t["panel"],
            lightcolor=t["panel"],
        )

    def _play_file(self, path: str):
        if not path or not os.path.exists(path):
            messagebox.showwarning("File Not Found", "Could not locate the file.\nIt may have been moved or deleted.")
            return
        if self._audio and self._audio.load(path):
            self._player_paused = False
            self._player_duration_ms = self._audio.get_length_ms()
            self._audio.set_volume(self._volume_var.get() * 10)
            self._audio.play()
            name = os.path.splitext(os.path.basename(path))[0]
            self._player_title_var.set(name[:50])
            self._player_time_var.set("0:00 / 0:00")
            self._play_pause_btn.config(text="⏸")
            self._player_frame.pack(fill=tk.X, side=tk.BOTTOM,
                                    before=self._tw.get("status_bar"))
            if self._player_update_id:
                self.after_cancel(self._player_update_id)
            self._schedule_player_update()
        else:
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])

    def _player_toggle_pause(self):
        if not self._audio or not self._audio._open:
            return
        if self._player_paused:
            self._audio.resume()
            self._player_paused = False
            self._play_pause_btn.config(text="⏸")
        else:
            self._audio.pause()
            self._player_paused = True
            self._play_pause_btn.config(text="▶")

    def _player_stop(self):
        if self._player_update_id:
            self.after_cancel(self._player_update_id)
            self._player_update_id = None
        if self._audio:
            self._audio.stop()
            self._audio.close()
        self._player_frame.pack_forget()
        self._player_paused = False

    def _player_seek_click(self, event):
        if not self._audio or not self._audio._open or not self._player_duration_ms:
            return
        w = self._player_canvas.winfo_width()
        if w < 2:
            return
        pct = max(0.0, min(1.0, event.x / w))
        self._audio.seek(int(pct * self._player_duration_ms))
        self._player_paused = False
        self._play_pause_btn.config(text="⏸")

    def _player_set_volume(self, val):
        if self._audio:
            self._audio.set_volume(int(float(val)) * 10)

    def _schedule_player_update(self):
        self._update_player_display()
        self._player_update_id = self.after(500, self._schedule_player_update)

    def _update_player_display(self):
        if not self._audio or not self._audio._open:
            return
        pos = self._audio.get_position_ms()
        dur = self._player_duration_ms or 1

        pos_s = pos // 1000
        dur_s = dur // 1000
        self._player_time_var.set(
            f"{pos_s // 60}:{pos_s % 60:02d} / {dur_s // 60}:{dur_s % 60:02d}"
        )

        pct = min(100.0, pos * 100.0 / dur)
        c = self._player_canvas
        c.delete("all")
        w = c.winfo_width()
        h = c.winfo_height()
        if w > 2:
            t = self.T
            c.create_rectangle(0, 1, w, h - 1, fill=t["card"], outline="")
            filled = int(w * pct / 100)
            if filled > 0:
                c.create_rectangle(0, 1, filled, h - 1, fill=ACCENT, outline="")

        mode = self._audio.mode()
        if mode == "stopped" and not self._player_paused:
            self._player_stop()

    def _apply_card_theme(self, item: DownloadItem):
        if not hasattr(item, "_card_frame"):
            return
        t = self.T
        item._card_frame.config(bg=t["card"])
        item._num_label.config(bg=t["card"], fg=t["text_dim"])
        item._title_label.config(bg=t["card"], fg=t["text"])
        item._url_label_widget.config(bg=t["card"], fg=t["text_dim"])
        item._status_label.config(bg=t["card"])
        if hasattr(item, "_play_btn"):
            item._play_btn.config(bg=t["card"], fg=t["success"], activebackground=t["success"])

    def _apply_theme(self):
        t = self.T
        self.configure(bg=t["bg"])
        w = self._tw

        # Header
        for k in ("header", "header_inner", "header_right"):
            if k in w:
                w[k].config(bg=t["panel"])
        if "title" in w:
            w["title"].config(bg=t["panel"])
        if "quality" in w:
            w["quality"].config(bg=t["panel"], fg=t["success"])
        if "version" in w:
            w["version"].config(bg=t["panel"], fg=t["text_dim"])

        self._theme_btn.config(
            text="🎨  Theme",
            bg=t["panel"], fg=t["text_dim"],
            activebackground=t["card"], activeforeground=t["text"],
        )
        self._update_check_btn.config(
            bg=t["panel"], fg=t["text_dim"],
            activebackground=t["card"], activeforeground=t["text"],
        )

        # Input section
        for k in ("input_frame", "url_row", "dir_row"):
            if k in w:
                w[k].config(bg=t["bg"])
        if "url_label" in w:
            w["url_label"].config(bg=t["bg"], fg=t["text_dim"])
        if "url_entry" in w:
            w["url_entry"].config(bg=t["entry_bg"], fg=t["text"], insertbackground=t["text"])
        if "save_label" in w:
            w["save_label"].config(bg=t["bg"], fg=t["text_dim"])
        if "dir_label" in w:
            w["dir_label"].config(bg=t["bg"], fg=t["text"])
        if "browse_btn" in w:
            w["browse_btn"].config(bg=t["card"], fg=t["text"])

        # Queue section
        for k in ("queue_outer", "queue_header_row"):
            if k in w:
                w[k].config(bg=t["bg"])
        if "queue_title" in w:
            w["queue_title"].config(bg=t["bg"], fg=t["text"])
        if "clear_btn" in w:
            w["clear_btn"].config(bg=t["card"], fg=t["text_dim"])
        if "list_frame" in w:
            w["list_frame"].config(bg=t["bg"])
        self.queue_canvas.config(bg=t["panel"])
        self.queue_inner.config(bg=t["panel"])
        self._empty_label.config(bg=t["panel"], fg=t["text_dim"])

        # Log
        if "log_frame" in w:
            w["log_frame"].config(bg=t["bg"])
        if "log_label" in w:
            w["log_label"].config(bg=t["bg"], fg=t["text_dim"])
        self.log_text.config(bg=t["log_bg"], fg=t["text_dim"])

        # Status bar
        if "status_bar" in w:
            w["status_bar"].config(bg=t["panel"])
        if "status_lbl" in w:
            w["status_lbl"].config(bg=t["panel"], fg=t["text_dim"])

        # Audio player bar
        if "player_frame" in w:
            w["player_frame"].config(bg=t["panel"])
        self._play_pause_btn.config(bg=t["panel"], activebackground=t["card"])
        for k in ("player_stop_btn", "player_vol_lbl", "player_close_btn"):
            if k in w:
                w[k].config(bg=t["panel"])
        for k in ("player_title", "player_time"):
            if k in w:
                w[k].config(bg=t["panel"], fg=t["text_dim"] if k == "player_time" else t["text"])
        if "player_canvas" in w:
            w["player_canvas"].config(bg=t["panel"])
        if "player_vol_slider" in w:
            w["player_vol_slider"].config(bg=t["panel"], troughcolor=t["card"])

        # Queue item cards
        for item in self.queue:
            self._apply_card_theme(item)

        self._configure_ttk_style()


if __name__ == "__main__":
    app = YouTubeMP3Downloader()
    app.mainloop()
