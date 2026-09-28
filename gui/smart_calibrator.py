"""
Gartic AutoDraw Pro - Smart Visual Calibrator
Features transparent border highlight overlay, 2-Click canvas point picker,
and 2-Click 18-color palette calibrator.
"""

import tkinter as tk
from typing import Callable, Optional, Tuple
import winsound
from pynput import keyboard

from core.win32_mouse import Win32MouseController
from core.gartic_palette import GarticPaletteManager


class VisualCanvasBorderOverlay:
    """
    Renders a click-through, transparent neon-green rectangular border
    directly over the calibrated canvas on screen so the user can visually verify it.
    """

    def __init__(self, parent):
        self.parent = parent
        self.top: Optional[tk.Toplevel] = None

    def show_border(self, x: int, y: int, w: int, h: int, duration_sec: float = 3.5):
        """Displays neon green border at (x, y, w, h) for duration_sec seconds."""
        self.hide_border()

        try:
            self.top = tk.Toplevel(self.parent)
            self.top.geometry(f"{w}x{h}+{x}+{y}")
            self.top.overrideredirect(True)
            self.top.attributes("-topmost", True)
            self.top.attributes("-transparentcolor", "#000001")

            canvas = tk.Canvas(self.top, width=w, height=h, bg="#000001", highlightthickness=0)
            canvas.pack(fill="both", expand=True)

            canvas.create_rectangle(2, 2, w - 2, h - 2, outline="#10b981", width=4)
            canvas.create_text(
                w // 2,
                26,
                text=f"🎯 GARTIC PHONE ÇİZİM TUVALİ ({w}x{h} px)",
                fill="#10b981",
                font=("Segoe UI", 15, "bold"),
            )

            if duration_sec > 0:
                self.parent.after(int(duration_sec * 1000), self.hide_border)
        except Exception as e:
            print(f"Border overlay error: {e}")

    def hide_border(self):
        if self.top:
            try:
                self.top.destroy()
            except Exception:
                pass
            self.top = None


class TwoClickCalibrator:
    """
    Guides user through 2 simple steps:
    1. Move mouse to Canvas Top-Left -> press F6 or SPACE.
    2. Move mouse to Canvas Bottom-Right -> press F6 or SPACE.
    """

    def __init__(
        self,
        parent,
        mouse_ctrl: Win32MouseController,
        on_success: Callable[[int, int, int, int], None],
        on_cancel: Optional[Callable[[], None]] = None,
    ):
        self.parent = parent
        self.mouse_ctrl = mouse_ctrl
        self.on_success = on_success
        self.on_cancel = on_cancel

        self.step = 0
        self.point1 = None
        self.point2 = None
        self.banner: Optional[tk.Toplevel] = None
        self.lbl_text = None
        self.listener: Optional[keyboard.Listener] = None

    def start(self):
        self.step = 1
        self.point1 = None
        self.point2 = None

        self.banner = tk.Toplevel(self.parent)
        self.banner.geometry("740x70+400+20")
        self.banner.overrideredirect(True)
        self.banner.attributes("-topmost", True)
        self.banner.config(bg="#0f172a")

        frame = tk.Frame(self.banner, bg="#0f172a", highlightthickness=2, highlightbackground="#38bdf8")
        frame.pack(fill="both", expand=True)

        self.lbl_text = tk.Label(
            frame,
            text="📍 1. ADIM: Farenizi Gartic beyaz tuvalinin SOL-ÜST köşesine getirin ve F6 veya BOŞLUK'a basın!",
            fg="#38bdf8",
            bg="#0f172a",
            font=("Segoe UI", 12, "bold"),
        )
        self.lbl_text.pack(expand=True, pady=10)

        try:
            winsound.Beep(1000, 100)
        except Exception:
            pass

        self._start_listener()

    def _start_listener(self):
        def _on_press(key):
            try:
                if key == keyboard.Key.f6 or key == keyboard.Key.space:
                    self.parent.after(0, self._handle_click_step)
                elif key == keyboard.Key.esc:
                    self.parent.after(0, self._abort)
            except Exception:
                pass

        self.listener = keyboard.Listener(on_press=_on_press)
        self.listener.daemon = True
        self.listener.start()

    def _handle_click_step(self):
        pt = self.mouse_ctrl.get_cursor_pos()

        if self.step == 1:
            self.point1 = pt
            self.step = 2
            try:
                winsound.Beep(1200, 120)
            except Exception:
                pass
            if self.lbl_text:
                self.lbl_text.config(
                    text=f"✅ Sol-Üst ({pt[0]}, {pt[1]}) Alındı! Şimdi SAĞ-ALT köşeye gidip F6 veya BOŞLUK'a basın!",
                    fg="#10b981",
                )
        elif self.step == 2:
            self.point2 = pt
            try:
                winsound.Beep(1600, 180)
            except Exception:
                pass
            self._finish()

    def _finish(self):
        if self.listener:
            try:
                self.listener.stop()
            except Exception:
                pass
            self.listener = None

        if self.banner:
            try:
                self.banner.destroy()
            except Exception:
                pass
            self.banner = None

        if self.point1 and self.point2:
            x1, y1 = self.point1
            x2, y2 = self.point2

            cx = min(x1, x2)
            cy = min(y1, y2)
            cw = abs(x2 - x1)
            ch = abs(y2 - y1)

            if cw > 50 and ch > 50:
                self.on_success(cx, cy, cw, ch)

    def _abort(self):
        if self.listener:
            try:
                self.listener.stop()
            except Exception:
                pass
            self.listener = None

        if self.banner:
            try:
                self.banner.destroy()
            except Exception:
                pass
            self.banner = None

        if self.on_cancel:
            self.on_cancel()


class PaletteTwoClickCalibrator:
    """
    Calibrates the entire 18-color palette with 2 clicks:
    1. Click Top-Left color (Black) -> Press F6 / Space
    2. Click Bottom-Right color (Peach) -> Press F6 / Space
    """

    def __init__(
        self,
        parent,
        mouse_ctrl: Win32MouseController,
        palette_mgr: GarticPaletteManager,
        on_success: Callable[[], None],
    ):
        self.parent = parent
        self.mouse_ctrl = mouse_ctrl
        self.palette_mgr = palette_mgr
        self.on_success = on_success

        self.step = 0
        self.pt_black = None
        self.pt_peach = None
        self.banner: Optional[tk.Toplevel] = None
        self.lbl_text = None
        self.listener: Optional[keyboard.Listener] = None

    def start(self):
        self.step = 1
        self.pt_black = None
        self.pt_peach = None

        self.banner = tk.Toplevel(self.parent)
        self.banner.geometry("740x70+400+20")
        self.banner.overrideredirect(True)
        self.banner.attributes("-topmost", True)
        self.banner.config(bg="#0f172a")

        frame = tk.Frame(self.banner, bg="#0f172a", highlightthickness=2, highlightbackground="#8b5cf6")
        frame.pack(fill="both", expand=True)

        self.lbl_text = tk.Label(
            frame,
            text="🎨 1. ADIM: Farenizi Gartic'teki SİYAH kutucuğun üzerine getirin ve F6 veya BOŞLUK'a basın!",
            fg="#c084fc",
            bg="#0f172a",
            font=("Segoe UI", 12, "bold"),
        )
        self.lbl_text.pack(expand=True, pady=10)

        try:
            winsound.Beep(1100, 100)
        except Exception:
            pass

        def _on_press(key):
            try:
                if key == keyboard.Key.f6 or key == keyboard.Key.space:
                    self.parent.after(0, self._handle_step)
                elif key == keyboard.Key.esc:
                    self.parent.after(0, self._abort)
            except Exception:
                pass

        self.listener = keyboard.Listener(on_press=_on_press)
        self.listener.daemon = True
        self.listener.start()

    def _handle_step(self):
        pt = self.mouse_ctrl.get_cursor_pos()

        if self.step == 1:
            self.pt_black = pt
            self.step = 2
            try:
                winsound.Beep(1300, 120)
            except Exception:
                pass
            if self.lbl_text:
                self.lbl_text.config(
                    text=f"✅ Siyah ({pt[0]}, {pt[1]}) Alındı! Şimdi en sağ-alttaki TEN RENGİ (Şeftali) üzerine gidip F6 veya BOŞLUK basın!",
                    fg="#10b981",
                )
        elif self.step == 2:
            self.pt_peach = pt
            try:
                winsound.Beep(1700, 200)
            except Exception:
                pass
            self._finish()

    def _finish(self):
        if self.listener:
            try:
                self.listener.stop()
            except Exception:
                pass
            self.listener = None

        if self.banner:
            try:
                self.banner.destroy()
            except Exception:
                pass
            self.banner = None

        if self.pt_black and self.pt_peach:
            self.palette_mgr.calibrate_from_two_corners(
                self.pt_black[0], self.pt_black[1],
                self.pt_peach[0], self.pt_peach[1],
            )
            self.on_success()

    def _abort(self):
        if self.listener:
            try:
                self.listener.stop()
            except Exception:
                pass
            self.listener = None

        if self.banner:
            try:
                self.banner.destroy()
            except Exception:
                pass
            self.banner = None
