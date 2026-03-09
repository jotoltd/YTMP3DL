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
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

VERSION = "1.0.0"
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


DARK_BG = "#1a1a2e"
PANEL_BG = "#16213e"
CARD_BG = "#0f3460"
ACCENT = "#e94560"
ACCENT_HOVER = "#c73652"
TEXT_PRIMARY = "#eaeaea"
TEXT_SECONDARY = "#a0a0b0"
SUCCESS = "#4caf50"
WARNING = "#ff9800"
PROGRESS_BG = "#0d2137"


class DownloadItem:
    def __init__(self, url, title="Fetching info...", status="Queued", progress=0):
        self.url = url
        self.title = title
        self.status = status
        self.progress = progress
        self.error = None


class YouTubeMP3Downloader(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("YouTube MP3 Downloader")
        self.geometry("820x680")
        self.minsize(700, 560)
        self.configure(bg=DARK_BG)

        self.download_path = tk.StringVar(value=str(Path.home() / "Downloads"))
        self.url_var = tk.StringVar()
        self.queue: list[DownloadItem] = []
        self.is_downloading = False
        self._active_thread = None

        self._update_available = None

        self._build_ui()
        self._check_ffmpeg()
        threading.Thread(target=self._check_for_updates, daemon=True).start()

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
        self._build_status_bar()

    def _build_header(self):
        header = tk.Frame(self, bg=PANEL_BG, height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        inner = tk.Frame(header, bg=PANEL_BG)
        inner.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            inner,
            text="▶  YouTube MP3 Downloader",
            font=("Helvetica", 22, "bold"),
            fg=ACCENT,
            bg=PANEL_BG,
        ).pack(side=tk.LEFT)

        tk.Label(
            inner,
            text="  320 kbps",
            font=("Helvetica", 11),
            fg=SUCCESS,
            bg=PANEL_BG,
        ).pack(side=tk.LEFT, pady=(8, 0))

        tk.Label(
            inner,
            text=f"  v{VERSION}",
            font=("Helvetica", 9),
            fg=TEXT_SECONDARY,
            bg=PANEL_BG,
        ).pack(side=tk.LEFT, pady=(10, 0))

    def _build_input_section(self):
        frame = tk.Frame(self, bg=DARK_BG, padx=20, pady=14)
        frame.pack(fill=tk.X)

        tk.Label(
            frame, text="YouTube URL", font=("Helvetica", 10, "bold"),
            fg=TEXT_SECONDARY, bg=DARK_BG,
        ).grid(row=0, column=0, sticky="w", pady=(0, 4))

        url_row = tk.Frame(frame, bg=DARK_BG)
        url_row.grid(row=1, column=0, sticky="ew")
        frame.columnconfigure(0, weight=1)

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

        tk.Label(
            dir_row, text="Save to:", font=("Helvetica", 10),
            fg=TEXT_SECONDARY, bg=DARK_BG,
        ).pack(side=tk.LEFT)

        self.dir_label = tk.Label(
            dir_row,
            textvariable=self.download_path,
            font=("Helvetica", 10),
            fg=TEXT_PRIMARY,
            bg=DARK_BG,
            anchor="w",
        )
        self.dir_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 0))

        tk.Button(
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
        ).pack(side=tk.RIGHT)

    def _build_queue_section(self):
        outer = tk.Frame(self, bg=DARK_BG, padx=20)
        outer.pack(fill=tk.BOTH, expand=True)

        header_row = tk.Frame(outer, bg=DARK_BG)
        header_row.pack(fill=tk.X, pady=(6, 6))

        tk.Label(
            header_row, text="Download Queue",
            font=("Helvetica", 11, "bold"), fg=TEXT_PRIMARY, bg=DARK_BG,
        ).pack(side=tk.LEFT)

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

        tk.Button(
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
        ).pack(side=tk.RIGHT, padx=(0, 8))

        list_frame = tk.Frame(outer, bg=PANEL_BG)
        list_frame.pack(fill=tk.BOTH, expand=True)

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

        tk.Label(
            frame, text="Log", font=("Helvetica", 10, "bold"),
            fg=TEXT_SECONDARY, bg=DARK_BG,
        ).pack(anchor="w")

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

        tk.Label(
            bar, textvariable=self.status_var,
            font=("Helvetica", 10), fg=TEXT_SECONDARY, bg=PANEL_BG, anchor="w", padx=12,
        ).pack(fill=tk.X, pady=4)

    def _build_update_banner(self):
        self._update_frame = tk.Frame(self, bg="#7b5e00", pady=6)
        self._update_label = tk.Label(
            self._update_frame,
            text="",
            font=("Helvetica", 10),
            fg="#ffe082",
            bg="#7b5e00",
        )
        self._update_label.pack(side=tk.LEFT, padx=(16, 8))
        self._update_btn = tk.Button(
            self._update_frame,
            text="Update Now",
            font=("Helvetica", 10, "bold"),
            bg="#ffca28",
            fg="#1a1a00",
            activebackground="#ffe082",
            relief=tk.FLAT,
            cursor="hand2",
            padx=10,
            pady=2,
            command=self._apply_update,
        )
        self._update_btn.pack(side=tk.LEFT)
        tk.Button(
            self._update_frame,
            text="✕",
            font=("Helvetica", 9),
            bg="#7b5e00",
            fg="#ffe082",
            activebackground="#5a4400",
            relief=tk.FLAT,
            cursor="hand2",
            command=lambda: self._update_frame.pack_forget(),
        ).pack(side=tk.RIGHT, padx=8)

    def _check_for_updates(self):
        if "YOUR_USERNAME" in GITHUB_REPO:
            return
        try:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
            req = urllib.request.Request(url, headers={"User-Agent": "YT-MP3-Downloader"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode())
            latest_tag = data.get("tag_name", "").lstrip("v")
            if not latest_tag:
                return
            if self._version_tuple(latest_tag) > self._version_tuple(VERSION):
                assets = data.get("assets", [])
                dl_url = next(
                    (a["browser_download_url"] for a in assets if a["name"].endswith(".exe")),
                    None,
                )
                self._update_available = {"version": latest_tag, "url": dl_url}
                self.after(0, lambda: self._show_update_banner(latest_tag))
        except Exception:
            pass

    @staticmethod
    def _version_tuple(v: str):
        try:
            return tuple(int(x) for x in v.split("."))
        except ValueError:
            return (0,)

    def _show_update_banner(self, version: str):
        self._update_label.config(text=f"Update available: v{version}  —  new version ready to download.")
        self._update_frame.pack(fill=tk.X, after=None)
        self._update_frame.lift()
        self._update_frame.pack(fill=tk.X)
        self._log(f"Update available: v{version}")

    def _apply_update(self):
        if not self._update_available or not self._update_available.get("url"):
            messagebox.showinfo("Update", f"Visit https://github.com/{GITHUB_REPO}/releases to download the latest version.")
            return
        if not getattr(sys, "frozen", False):
            import webbrowser
            webbrowser.open(f"https://github.com/{GITHUB_REPO}/releases/latest")
            return
        self._update_btn.config(state=tk.DISABLED, text="Downloading...")
        threading.Thread(target=self._download_and_replace, daemon=True).start()

    def _download_and_replace(self):
        try:
            dl_url = self._update_available["url"]
            new_ver = self._update_available["version"]
            tmp_dir = tempfile.mkdtemp()
            tmp_exe = os.path.join(tmp_dir, "YT-MP3-Downloader_new.exe")
            current_exe = sys.executable

            def _reporthook(count, block, total):
                if total > 0:
                    pct = min(100, int(count * block * 100 / total))
                    self._update_status(f"Downloading update... {pct}%")

            urllib.request.urlretrieve(dl_url, tmp_exe, _reporthook)

            helper = os.path.join(tmp_dir, "_updater.bat")
            with open(helper, "w") as f:
                f.write("@echo off\n")
                f.write("ping -n 3 localhost >nul\n")
                f.write(f'move /Y "{tmp_exe}" "{current_exe}"\n')
                f.write(f'start "" "{current_exe}"\n')
                f.write('del "%~f0"\n')

            subprocess.Popen(["cmd", "/c", helper], creationflags=subprocess.CREATE_NO_WINDOW)
            self.after(0, self.destroy)
        except Exception as e:
            self._log(f"Update failed: {e}")
            self.after(0, lambda: self._update_btn.config(state=tk.NORMAL, text="Update Now"))

    def _on_mousewheel(self, event):
        self.queue_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _browse_dir(self):
        path = filedialog.askdirectory(initialdir=self.download_path.get())
        if path:
            self.download_path.set(path)

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

        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "red.Horizontal.TProgressbar",
            troughcolor=PROGRESS_BG,
            background=ACCENT,
            bordercolor=CARD_BG,
            lightcolor=ACCENT,
            darkcolor=ACCENT,
        )
        progress_bar.configure(style="red.Horizontal.TProgressbar")

        item._title_label = title_label
        item._status_label = status_label
        item._progress_bar = progress_bar

        self._item_frames.append(frame)

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

    def _start_downloads(self):
        if self.is_downloading:
            return
        pending = [item for item in self.queue if item.status in ("Queued", "Error")]
        if not pending:
            messagebox.showinfo("Nothing to download", "No pending items in the queue.")
            return
        self.is_downloading = True
        self.download_btn.config(state=tk.DISABLED, text="Downloading...")
        self._add_btn.config(state=tk.DISABLED)
        self._active_thread = threading.Thread(
            target=self._download_all, args=(pending,), daemon=True
        )
        self._active_thread.start()

    def _download_all(self, items: list[DownloadItem]):
        for i, item in enumerate(items):
            self._update_status(f"Downloading {i + 1}/{len(items)}: {item.url[:60]}...")
            self._download_item(item)
        self.is_downloading = False
        self.after(0, self._on_all_done)

    def _download_item(self, item: DownloadItem):
        self._set_item_status(item, "Downloading...", TEXT_PRIMARY)
        self._set_item_progress(item, 0)

        out_dir = self.download_path.get()
        os.makedirs(out_dir, exist_ok=True)

        def progress_hook(d):
            if d["status"] == "downloading":
                pct_str = d.get("_percent_str", "0%").strip().replace("%", "")
                try:
                    pct = float(pct_str)
                except ValueError:
                    pct = 0
                speed = d.get("_speed_str", "")
                eta = d.get("_eta_str", "")
                self._set_item_progress(item, pct)
                self._update_status(
                    f"{item.title[:50]}  |  {pct:.1f}%  {speed}  ETA {eta}"
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
        except yt_dlp.utils.DownloadError as e:
            item.error = str(e)
            self._set_item_status(item, "✗ Error", ACCENT)
            self._log(f"Error: {str(e)[:120]}")
        except Exception as e:
            item.error = str(e)
            self._set_item_status(item, "✗ Error", ACCENT)
            self._log(f"Unexpected error: {str(e)[:120]}")

    def _on_all_done(self):
        self.download_btn.config(state=tk.NORMAL, text="⬇  Download All")
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


if __name__ == "__main__":
    app = YouTubeMP3Downloader()
    app.mainloop()
