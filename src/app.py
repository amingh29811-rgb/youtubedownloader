from kivy.config import Config

# Window size is set via Config BEFORE any other kivy import
Config.set("graphics", "width", "420")
Config.set("graphics", "height", "700")

import os
import shutil
import threading

from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle, Line, Rectangle
from kivy.metrics import dp
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.textinput import TextInput


# -----------------------------
# Rounded background
# -----------------------------

class RoundedBox(BoxLayout):

    def __init__(self, bg_color=(0.07, 0.07, 0.09, 1),
                 radius=20, border_color=None, **kwargs):

        super().__init__(**kwargs)

        self.bg_color = bg_color
        self.radius = radius
        self.border_color = border_color

        with self.canvas.before:

            Color(*self.bg_color)

            self.background = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(self.radius)]
            )

            if self.border_color:
                Color(*self.border_color)

                self.border = Line(
                    rounded_rectangle=(
                        self.x,
                        self.y,
                        self.width,
                        self.height,
                        dp(self.radius)
                    ),
                    width=1
                )

        self.bind(
            pos=self.update_background,
            size=self.update_background
        )

    def update_background(self, *args):

        self.background.pos = self.pos
        self.background.size = self.size

        if self.border_color:

            self.border.rounded_rectangle = (
                self.x,
                self.y,
                self.width,
                self.height,
                dp(self.radius)
            )


# -----------------------------
# Quality Button
# -----------------------------

class QualityButton(Button):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)

        self.color = (0.85, 0.85, 0.88, 1)
        self.font_size = dp(15)
        self.bold = True

        self.size_hint_y = None
        self.height = dp(48)

        with self.canvas.before:

            self.bg_color = Color(0.10, 0.10, 0.13, 1)

            self.bg = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(14)]
            )

        self.bind(
            pos=self.update_background,
            size=self.update_background
        )

    def update_background(self, *args):

        self.bg.pos = self.pos
        self.bg.size = self.size

    def set_active(self, active):

        self.bg_color.rgba = (
            (0.92, 0.04, 0.08, 1) if active
            else (0.10, 0.10, 0.13, 1)
        )

        self.color = (
            (1, 1, 1, 1) if active
            else (0.85, 0.85, 0.88, 1)
        )


# -----------------------------
# Main UI
# -----------------------------

class DownloaderUI(BoxLayout):

    status_text = StringProperty("Ready to download")

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        # App background (replaces Window.clearcolor)
        with self.canvas.before:
            Color(0.035, 0.035, 0.045, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self.update_bg, size=self.update_bg)

        self.orientation = "vertical"

        self.padding = [dp(25), dp(25), dp(25), dp(25)]

        self.spacing = dp(18)

        # -------------------------
        # Header
        # -------------------------

        header = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(105),
            spacing=dp(3)
        )

        title = Label(
            text="[b]YD[/b]  DOWNLOADER",
            markup=True,
            font_size=dp(28),
            color=(1, 1, 1, 1),
            halign="left",
            valign="middle"
        )

        title.bind(
            size=lambda instance, value:
            setattr(instance, "text_size", value)
        )

        subtitle = Label(
            text="Fast • Simple • Private",
            font_size=dp(13),
            color=(0.55, 0.55, 0.60, 1),
            halign="left",
            valign="top"
        )

        subtitle.bind(
            size=lambda instance, value:
            setattr(instance, "text_size", value)
        )

        header.add_widget(title)
        header.add_widget(subtitle)

        self.add_widget(header)

        # -------------------------
        # URL Card
        # -------------------------

        url_card = RoundedBox(
            orientation="vertical",
            padding=dp(18),
            spacing=dp(10),
            size_hint_y=None,
            height=dp(130),
            bg_color=(0.075, 0.075, 0.095, 1)
        )

        url_title = Label(
            text="VIDEO URL",
            font_size=dp(12),
            color=(0.60, 0.60, 0.65, 1),
            bold=True,
            size_hint_y=None,
            height=dp(20),
            halign="left"
        )

        url_title.bind(
            size=lambda instance, value:
            setattr(instance, "text_size", value)
        )

        self.url_input = TextInput(
            hint_text="Paste YouTube link here...",
            multiline=False,
            font_size=dp(15),
            padding=[dp(15), dp(13)],
            foreground_color=(0.95, 0.95, 0.97, 1),
            hint_text_color=(0.42, 0.42, 0.47, 1),
            background_color=(0.045, 0.045, 0.06, 1),
            cursor_color=(1, 0.08, 0.12, 1)
        )

        url_card.add_widget(url_title)
        url_card.add_widget(self.url_input)

        self.add_widget(url_card)

        # -------------------------
        # Quality
        # -------------------------

        quality_title = Label(
            text="VIDEO QUALITY",
            font_size=dp(12),
            color=(0.60, 0.60, 0.65, 1),
            bold=True,
            size_hint_y=None,
            height=dp(20),
            halign="left"
        )

        quality_title.bind(
            size=lambda instance, value:
            setattr(instance, "text_size", value)
        )

        self.add_widget(quality_title)

        quality_row = BoxLayout(
            spacing=dp(10),
            size_hint_y=None,
            height=dp(48)
        )

        self.selected_quality = "720p"

        self.quality_buttons = []

        for quality in ["360p", "480p", "720p", "1080p"]:

            button = QualityButton(text=quality)

            button.bind(
                on_release=lambda instance:
                self.select_quality(instance)
            )

            self.quality_buttons.append(button)

            quality_row.add_widget(button)

        # 720p selected by default
        self.select_quality(self.quality_buttons[2])

        self.add_widget(quality_row)

        # -------------------------
        # Download Button
        # -------------------------

        self.download_button = Button(
            text="DOWNLOAD",
            font_size=dp(17),
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(58),
            background_normal="",
            background_down="",
            background_color=(0, 0, 0, 0)
        )

        with self.download_button.canvas.before:

            Color(0.92, 0.04, 0.08, 1)

            self.download_bg = RoundedRectangle(
                pos=self.download_button.pos,
                size=self.download_button.size,
                radius=[dp(17)]
            )

        self.download_button.bind(
            pos=self.update_download_button,
            size=self.update_download_button
        )

        self.download_button.bind(
            on_release=self.start_download
        )

        self.add_widget(self.download_button)

        # -------------------------
        # Status Card
        # -------------------------

        status_card = RoundedBox(
            orientation="vertical",
            padding=dp(18),
            spacing=dp(10),
            size_hint_y=None,
            height=dp(125),
            bg_color=(0.075, 0.075, 0.095, 1)
        )

        status_header = BoxLayout(
            size_hint_y=None,
            height=dp(25)
        )

        status_label = Label(
            text="DOWNLOAD STATUS",
            font_size=dp(12),
            color=(0.60, 0.60, 0.65, 1),
            bold=True,
            halign="left"
        )

        status_label.bind(
            size=lambda instance, value:
            setattr(instance, "text_size", value)
        )

        self.percent = Label(
            text="0%",
            font_size=dp(12),
            color=(0.95, 0.08, 0.12, 1),
            bold=True,
            halign="right"
        )

        self.percent.bind(
            size=lambda instance, value:
            setattr(instance, "text_size", value)
        )

        status_header.add_widget(status_label)
        status_header.add_widget(self.percent)

        status_card.add_widget(status_header)

        # Progress bar

        self.progress = ProgressBar(
            max=100,
            value=0,
            size_hint_y=None,
            height=dp(10)
        )

        status_card.add_widget(self.progress)

        self.status = Label(
            text="Ready to download",
            font_size=dp(13),
            color=(0.65, 0.65, 0.70, 1),
            halign="left"
        )

        self.status.bind(
            size=lambda instance, value:
            setattr(instance, "text_size", value)
        )

        status_card.add_widget(self.status)

        self.add_widget(status_card)

        # -------------------------
        # Footer
        # -------------------------

        footer = Label(
            text="YD Downloader  •  Built with Python",
            font_size=dp(11),
            color=(0.35, 0.35, 0.40, 1),
            size_hint_y=None,
            height=dp(30)
        )

        self.add_widget(footer)

    # -------------------------
    # Quality
    # -------------------------

    def select_quality(self, button):

        self.selected_quality = button.text

        for btn in self.quality_buttons:
            btn.set_active(btn == button)

    # -------------------------
    # Download
    # -------------------------

    def start_download(self, instance):

        url = self.url_input.text.strip()

        if not url:
            self.set_status("Please paste a YouTube URL first.")
            return

        self.download_button.disabled = True
        self.set_progress(0)
        self.set_status("Starting...")

        threading.Thread(
            target=self._download,
            args=(url, self.selected_quality),
            daemon=True
        ).start()

    # -------------------------
    # Thread-safe UI helpers
    # -------------------------

    def set_status(self, text):

        Clock.schedule_once(
            lambda dt: setattr(self.status, "text", text)
        )

    def set_progress(self, value):

        def update(dt):
            self.progress.value = value
            self.percent.text = f"{int(value)}%"

        Clock.schedule_once(update)

    def enable_button(self):

        Clock.schedule_once(
            lambda dt: setattr(self.download_button, "disabled", False)
        )

    # -------------------------
    # Real download (runs in a thread)
    # -------------------------

    def _download(self, url, quality):

        try:
            import yt_dlp
        except ImportError:
            self.set_status("Run: pip install yt-dlp")
            self.enable_button()
            return

        height = quality.replace("p", "")
        has_ffmpeg = shutil.which("ffmpeg") is not None

        if has_ffmpeg:
            fmt = f"bv*[height<={height}]+ba/b[height<={height}]/b"
        else:
            # Without ffmpeg only single-file formats work
            fmt = f"b[height<={height}]/b"

        out_dir = os.path.expanduser("~/YD_Downloads")
        os.makedirs(out_dir, exist_ok=True)

        def hook(d):

            if d["status"] == "downloading":

                total = (
                    d.get("total_bytes")
                    or d.get("total_bytes_estimate")
                )

                if total:
                    self.set_progress(d["downloaded_bytes"] / total * 100)

                self.set_status(f"Downloading • {quality}")

            elif d["status"] == "finished":

                self.set_progress(100)
                self.set_status("Processing...")

        opts = {
            "format": fmt,
            "outtmpl": os.path.join(out_dir, "%(title)s.%(ext)s"),
            "progress_hooks": [hook],
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
        }

        if has_ffmpeg:
            opts["merge_output_format"] = "mp4"

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)

            title = info.get("title", "video")
            self.set_status(f"Done: {title[:40]}")

        except Exception as e:
            msg = str(e).replace("ERROR: ", "")
            self.set_status(f"Error: {msg[:90]}")

        finally:
            self.enable_button()

    # -------------------------
    # Backgrounds
    # -------------------------

    def update_bg(self, *args):

        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def update_download_button(self, *args):

        self.download_bg.pos = self.download_button.pos
        self.download_bg.size = self.download_button.size


# -----------------------------
# App
# -----------------------------

class YouTubeDownloaderApp(App):

    def build(self):

        self.title = "YD Downloader"

        return DownloaderUI()


if __name__ == "__main__":

    YouTubeDownloaderApp().run()