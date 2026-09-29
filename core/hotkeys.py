"""
Gartic AutoDraw Pro - Global Hotkey Listener
Provides background system-wide keyboard shortcuts for starting, pausing, and emergency-aborting.
"""

from typing import Callable, Optional
import threading
from pynput import keyboard


class GlobalHotkeyManager:
    """
    Listens for global hotkeys across all windows and monitors:
    - F6: Calibrate Canvas
    - F7: Test Canvas Outline
    - F8: Start Drawing
    - F9: Pause / Resume
    - F10 or ESC: Emergency Stop
    """

    def __init__(
        self,
        on_start: Optional[Callable[[], None]] = None,
        on_pause_toggle: Optional[Callable[[], None]] = None,
        on_emergency_stop: Optional[Callable[[], None]] = None,
        on_test_bounds: Optional[Callable[[], None]] = None,
        on_calibrate: Optional[Callable[[], None]] = None,
        on_test_pen: Optional[Callable[[], None]] = None,
    ):
        self.on_start = on_start
        self.on_pause_toggle = on_pause_toggle
        self.on_emergency_stop = on_emergency_stop
        self.on_test_bounds = on_test_bounds
        self.on_calibrate = on_calibrate
        self.on_test_pen = on_test_pen
        self.listener: Optional[keyboard.Listener] = None

    def start(self):
        """Starts global keyboard hook in background thread."""
        def _on_press(key):
            try:
                if key == keyboard.Key.f6:
                    if self.on_calibrate:
                        self.on_calibrate()
                elif key == keyboard.Key.f7:
                    if self.on_test_pen:
                        self.on_test_pen()
                    elif self.on_test_bounds:
                        self.on_test_bounds()
                elif key == keyboard.Key.f8:
                    if self.on_start:
                        self.on_start()
                elif key == keyboard.Key.f9:
                    if self.on_pause_toggle:
                        self.on_pause_toggle()
                elif key == keyboard.Key.f10 or key == keyboard.Key.esc:
                    if self.on_emergency_stop:
                        self.on_emergency_stop()
            except Exception as e:
                print(f"Hotkey handling error: {e}")

        self.listener = keyboard.Listener(on_press=_on_press)
        self.listener.daemon = True
        self.listener.start()

    def stop(self):
        """Stops the global keyboard listener."""
        if self.listener:
            try:
                self.listener.stop()
            except Exception:
                pass
            self.listener = None
