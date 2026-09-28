"""
Gartic AutoDraw Pro - Win32 High Performance Mouse Controller
Supports Windows Per-Monitor V2 DPI Awareness, Virtual Desktop Multi-Monitor mapping,
sub-millisecond hardware timers, and robust HTML5 Canvas stroke delivery.
"""

import ctypes
from ctypes import wintypes
import time
import math
import threading
from typing import List, Tuple, Optional, Callable

# Initialize Windows User32 and WinMM libraries
user32 = ctypes.windll.user32
winmm = ctypes.windll.winmm

# Win32 Virtual Desktop Metrics
SM_XVIRTUALSCREEN = 76
SM_YVIRTUALSCREEN = 77
SM_CXVIRTUALSCREEN = 78
SM_CYVIRTUALSCREEN = 79

# Win32 Mouse Flags
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_VIRTUALDESK = 0x4000


class Win32MouseController:
    """
    Direct Win32 mouse controller optimized for drawing in web canvas games like Gartic.io and Gartic Phone.
    Uses MOUSEEVENTF_VIRTUALDESK | MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_MOVE for pixel-perfect 2K/4K multi-monitor support.
    """

    def __init__(self):
        self.is_drawing = False
        self.is_paused = False
        self.should_abort = False
        self.is_mouse_down = False
        self._lock = threading.Lock()
        self.on_progress: Optional[Callable[[int, int, str], None]] = None
        self.on_state_change: Optional[Callable[[str], None]] = None

        # Cache virtual desktop bounds
        self.update_virtual_desktop_bounds()

        # Enable 1ms timer resolution on Windows
        try:
            winmm.timeBeginPeriod(1)
        except Exception:
            pass

    def __del__(self):
        try:
            winmm.timeEndPeriod(1)
        except Exception:
            pass

    def update_virtual_desktop_bounds(self):
        """Updates virtual desktop coordinate boundaries."""
        self.v_left = user32.GetSystemMetrics(SM_XVIRTUALSCREEN)
        self.v_top = user32.GetSystemMetrics(SM_YVIRTUALSCREEN)
        self.v_width = max(1, user32.GetSystemMetrics(SM_CXVIRTUALSCREEN))
        self.v_height = max(1, user32.GetSystemMetrics(SM_CYVIRTUALSCREEN))

    def get_cursor_pos(self) -> Tuple[int, int]:
        """Returns current cursor position (x, y) on virtual desktop."""
        pt = wintypes.POINT()
        user32.GetCursorPos(ctypes.byref(pt))
        return (pt.x, pt.y)

    def set_cursor_pos(self, x: int, y: int):
        """
        Moves cursor directly to virtual desktop coordinates (x, y).
        Uses both SetCursorPos and mouse_event(MOUSEEVENTF_MOVE) to guarantee Chromium receives WM_MOUSEMOVE.
        """
        user32.SetCursorPos(int(x), int(y))

        # Also emit native hardware mouse move event
        norm_x = int((x - self.v_left) * 65536 / self.v_width)
        norm_y = int((y - self.v_top) * 65536 / self.v_height)
        user32.mouse_event(
            MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_VIRTUALDESK,
            norm_x,
            norm_y,
            0,
            0,
        )

    def mouse_down(self, x: Optional[int] = None, y: Optional[int] = None):
        """Presses and holds left mouse button with DOM dispatch delay."""
        if x is not None and y is not None:
            self.set_cursor_pos(x, y)
        user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        self.is_mouse_down = True
        # Essential 3ms delay for browser HTML5 pointerdown / context initialization
        time.sleep(0.003)

    def mouse_up(self, x: Optional[int] = None, y: Optional[int] = None):
        """Releases left mouse button with DOM dispatch delay."""
        if x is not None and y is not None:
            self.set_cursor_pos(x, y)
        time.sleep(0.001)
        user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        self.is_mouse_down = False
        time.sleep(0.002)

    def click(self, x: int, y: int, delay: float = 0.02):
        """Performs a single click at (x, y)."""
        self.set_cursor_pos(x, y)
        time.sleep(delay)
        self.mouse_down()
        time.sleep(delay)
        self.mouse_up()
        time.sleep(delay)

    def emergency_release(self):
        """Emergency killswitch: immediately aborts drawing and releases mouse."""
        self.should_abort = True
        self.is_drawing = False
        self.is_paused = False
        try:
            user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            user32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
        except Exception:
            pass
        self.is_mouse_down = False
        if self.on_state_change:
            self.on_state_change("Durduruldu (Acil)")

    def pause(self):
        """Pauses drawing and lifts pen."""
        if self.is_drawing and not self.is_paused:
            self.is_paused = True
            if self.is_mouse_down:
                self.mouse_up()
            if self.on_state_change:
                self.on_state_change("Duraklatıldı")

    def resume(self):
        """Resumes drawing."""
        if self.is_drawing and self.is_paused:
            self.is_paused = False
            if self.on_state_change:
                self.on_state_change("Çiziliyor...")

    def toggle_pause(self):
        if self.is_paused:
            self.resume()
        else:
            self.pause()

    def draw_continuous_stroke(
        self,
        points: List[Tuple[int, int]],
        point_delay: float = 0.0015,
        interpolation_step: int = 3,
    ) -> bool:
        """
        Draws a continuous ink stroke through points.
        Interpolates between distant points so HTML5 canvas doesn't leave gaps.
        """
        if not points or len(points) == 0:
            return True

        if self.should_abort:
            return False

        # Move to start of stroke
        start_x, start_y = points[0]
        self.set_cursor_pos(start_x, start_y)
        time.sleep(0.002)

        self.mouse_down()

        prev_x, prev_y = start_x, start_y
        for i in range(1, len(points)):
            if self.should_abort:
                self.mouse_up()
                return False

            while self.is_paused:
                if self.is_mouse_down:
                    self.mouse_up()
                time.sleep(0.05)
                if self.should_abort:
                    return False

            if not self.is_mouse_down:
                self.set_cursor_pos(prev_x, prev_y)
                self.mouse_down()

            curr_x, curr_y = points[i]
            dx = curr_x - prev_x
            dy = curr_y - prev_y
            dist = math.hypot(dx, dy)

            if dist > interpolation_step and interpolation_step > 0:
                steps = max(1, int(dist / interpolation_step))
                for s in range(1, steps + 1):
                    t = s / float(steps)
                    ix = int(prev_x + dx * t)
                    iy = int(prev_y + dy * t)
                    self.set_cursor_pos(ix, iy)
                    if point_delay > 0:
                        time.sleep(point_delay)
            else:
                self.set_cursor_pos(curr_x, curr_y)
                if point_delay > 0:
                    time.sleep(point_delay)

            prev_x, prev_y = curr_x, curr_y

        self.mouse_up()
        return True

    def draw_stroke_batches(
        self,
        strokes: List[List[Tuple[int, int]]],
        point_delay: float = 0.0015,
        stroke_delay: float = 0.004,
        interpolation_step: int = 3,
        color_selector_cb: Optional[Callable[[str], None]] = None,
        stroke_colors: Optional[List[str]] = None,
    ) -> bool:
        """
        Executes a sequence of strokes.
        Handles pause, abort, progress reporting, and optional color switching.
        """
        self.is_drawing = True
        self.is_paused = False
        self.should_abort = False
        self.update_virtual_desktop_bounds()

        if self.on_state_change:
            self.on_state_change("Çiziliyor...")

        total_strokes = len(strokes)
        current_color = None

        try:
            for idx, stroke in enumerate(strokes):
                if self.should_abort:
                    break

                while self.is_paused:
                    time.sleep(0.05)
                    if self.should_abort:
                        break

                if self.should_abort:
                    break

                # Handle color switching if provided
                if stroke_colors and idx < len(stroke_colors):
                    col = stroke_colors[idx]
                    if col != current_color:
                        current_color = col
                        if color_selector_cb:
                            color_selector_cb(col)
                            time.sleep(0.04)

                success = self.draw_continuous_stroke(
                    stroke,
                    point_delay=point_delay,
                    interpolation_step=interpolation_step,
                )

                if not success or self.should_abort:
                    break

                if self.on_progress:
                    self.on_progress(idx + 1, total_strokes, current_color or "Siyah")

                if stroke_delay > 0:
                    time.sleep(stroke_delay)

        finally:
            # Safely release mouse button if held down, without triggering emergency_release abort flag
            if self.is_mouse_down:
                try:
                    user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                except Exception:
                    pass
                self.is_mouse_down = False
            self.is_drawing = False

        if self.should_abort:
            if self.on_state_change:
                self.on_state_change("İptal Edildi")
            return False

        if self.on_state_change:
            self.on_state_change("Çizim Tamamlandı! 🎉")
        return True
