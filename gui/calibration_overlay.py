"""
Gartic AutoDraw Pro - Canvas Calibration & Screen Selector Overlay
Allows interactive selection of Gartic canvas bounds, full 2K screen presets,
and visual boundary verification with mouse tracing.
"""

import tkinter as tk
from typing import Tuple, Optional, Callable
import time
import threading
import win32api
import win32con

from core.win32_mouse import Win32MouseController


class CanvasCalibrator:
    """
    Handles screen canvas calibration, area testing, and multi-monitor coordinates.
    """

    def __init__(self, mouse_ctrl: Win32MouseController):
        self.mouse_ctrl = mouse_ctrl
        # Full edge-to-edge canvas for 2K Gartic Phone (2560x1440)
        self.canvas_x = 220
        self.canvas_y = 240
        self.canvas_w = 2120
        self.canvas_h = 1120

    def set_bounds(self, x: int, y: int, w: int, h: int):
        self.canvas_x = int(x)
        self.canvas_y = int(y)
        self.canvas_w = max(50, int(w))
        self.canvas_h = max(50, int(h))

    def get_bounds(self) -> Tuple[int, int, int, int]:
        return (self.canvas_x, self.canvas_y, self.canvas_w, self.canvas_h)

    def set_2k_preset(self):
        """Sets true centered Gartic Phone notebook canvas bounds on 2560x1440 2K display."""
        self.set_bounds(490, 220, 1560, 1050)

    def set_1080p_preset(self):
        """Sets standard Gartic Phone canvas position for maximized browser on 1920x1080 display."""
        self.set_bounds(368, 165, 1170, 788)

    def test_canvas_bounds_visual(self, speed_delay: float = 0.003):
        """
        Visually traces the perimeter of the canvas with the mouse cursor WITHOUT clicking.
        Allows the player to confirm canvas bounds on Gartic.io or Gartic Phone.
        """
        def _worker():
            x0 = self.canvas_x
            y0 = self.canvas_y
            x1 = self.canvas_x + self.canvas_w
            y1 = self.canvas_y + self.canvas_h

            corners = [
                (x0, y0),
                (x1, y0),
                (x1, y1),
                (x0, y1),
                (x0, y0),
            ]

            for i in range(len(corners) - 1):
                start_x, start_y = corners[i]
                end_x, end_y = corners[i + 1]

                steps = 60
                for s in range(steps + 1):
                    t = s / float(steps)
                    cx = int(start_x + (end_x - start_x) * t)
                    cy = int(start_y + (end_y - start_y) * t)
                    self.mouse_ctrl.set_cursor_pos(cx, cy)
                    time.sleep(speed_delay)

        threading.Thread(target=_worker, daemon=True).start()


class InteractiveScreenSelector:
    """
    Transparent fullscreen overlay across all monitors for drag-selecting the Gartic canvas.
    """

    def __init__(self, on_selected_callback: Callable[[int, int, int, int], None]):
        self.on_selected_callback = on_selected_callback
        self.start_x: Optional[int] = None
        self.start_y: Optional[int] = None
        self.rect_id = None
        self.root: Optional[tk.Toplevel] = None

    def start_selection(self, parent):
        vx = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
        vy = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
        vw = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
        vh = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)

        self.root = tk.Toplevel(parent)
        self.root.geometry(f"{vw}x{vh}+{vx}+{vy}")
        self.root.overrideredirect(True)
        self.root.attributes("-alpha", 0.35)
        self.root.attributes("-topmost", True)
        self.root.config(cursor="cross")

        self.canvas = tk.Canvas(
            self.root,
            width=vw,
            height=vh,
            bg="#0f172a",
            highlightthickness=0,
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.create_text(
            vw // 2,
            70,
            text="🎯 Gartic Tuvalinin Sol-Üst Köşesinden Sağ-Alt Köşesine Doğru Fareyle Sürükleyin\n(İptal etmek için ESC tuşuna basın)",
            fill="#38bdf8",
            font=("Segoe UI", 18, "bold"),
            justify=tk.CENTER,
        )

        self.canvas.bind("<ButtonPress-1>", self._on_button_press)
        self.canvas.bind("<B1-Motion>", self._on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self._on_button_release)
        self.root.bind("<Escape>", lambda e: self._cancel())

        self.vx = vx
        self.vy = vy

    def _on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.rect_id = self.canvas.create_rectangle(
            self.start_x,
            self.start_y,
            self.start_x,
            self.start_y,
            outline="#38bdf8",
            width=3,
            fill="#0284c7",
            stipple="gray25",
        )

    def _on_move_press(self, event):
        if self.start_x is not None and self.start_y is not None:
            self.canvas.coords(self.rect_id, self.start_x, self.start_y, event.x, event.y)

    def _on_button_release(self, event):
        if self.start_x is None or self.start_y is None:
            self._cancel()
            return

        end_x = event.x
        end_y = event.y

        abs_x1 = self.vx + min(self.start_x, end_x)
        abs_y1 = self.vy + min(self.start_y, end_y)
        abs_x2 = self.vx + max(self.start_x, end_x)
        abs_y2 = self.vy + max(self.start_y, end_y)

        w = abs_x2 - abs_x1
        h = abs_y2 - abs_y1

        if self.root:
            self.root.destroy()
            self.root = None

        if w > 30 and h > 30:
            self.on_selected_callback(abs_x1, abs_y1, w, h)

    def _cancel(self):
        if self.root:
            self.root.destroy()
            self.root = None
