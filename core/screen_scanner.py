"""
Gartic AutoDraw Pro - Computer Vision Screen Scanner & Multi-Resolution Engine
Automatically detects Gartic Phone canvas, 18-color palette, and brush tools
across any screen resolution (1080p, 2K, 4K, laptop screens, or custom zooms)
using OpenCV color cluster centroid geometry.
Author: Toprak Ahmet Aydoğmuş
"""

import ctypes
from typing import Dict, Tuple, Optional, List
import numpy as np
import cv2
from PIL import ImageGrab
import win32api
import win32con

from core.gartic_palette import GARTIC_PALETTE_GRID, GARTIC_PALETTE_RGB


class ScreenResolutionPresets:
    """
    Standard calibrated presets for all major display resolutions and scaling modes.
    Ensures pixel-perfect drawing even before running auto-detection.
    """
    PRESETS = {
        "2K (2560x1440 - Önerilen)": {
            "canvas": (780, 260, 1000, 720),
            "palette_black": (552, 382),
            "palette_peach": (691, 720),
            "pen_thin": (1840, 382),
            "pen_medium": (1840, 448),
        },
        "1080p Full HD (1920x1080)": {
            "canvas": (585, 195, 750, 540),
            "palette_black": (414, 286),
            "palette_peach": (518, 540),
            "pen_thin": (1380, 286),
            "pen_medium": (1380, 336),
        },
        "4K Ultra HD (3840x2160)": {
            "canvas": (1170, 390, 1500, 1080),
            "palette_black": (828, 573),
            "palette_peach": (1036, 1080),
            "pen_thin": (2760, 573),
            "pen_medium": (2760, 672),
        },
        "Laptop HD (1366x768)": {
            "canvas": (416, 138, 534, 384),
            "palette_black": (294, 203),
            "palette_peach": (368, 384),
            "pen_thin": (981, 203),
            "pen_medium": (981, 239),
        },
        "Laptop FHD (1536x864 / %125 DPI)": {
            "canvas": (468, 156, 600, 432),
            "palette_black": (331, 229),
            "palette_peach": (414, 432),
            "pen_thin": (1104, 229),
            "pen_medium": (1104, 269),
        },
    }

    @classmethod
    def get_auto_preset_for_screen(cls) -> Tuple[str, dict]:
        """Detects current screen resolution and picks the best matching preset."""
        w = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        h = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)

        if w >= 3400:
            name = "4K Ultra HD (3840x2160)"
        elif w >= 2400:
            name = "2K (2560x1440 - Önerilen)"
        elif w >= 1800:
            name = "1080p Full HD (1920x1080)"
        elif w >= 1500:
            name = "Laptop FHD (1536x864 / %125 DPI)"
        else:
            name = "Laptop HD (1366x768)"

        return name, cls.PRESETS[name]


class ScreenScannerCV:
    """
    Real-time Computer Vision Screen Scanner.
    Captures live desktop and locates Gartic Phone canvas and 18-color palette buttons.
    """

    @staticmethod
    def capture_screen() -> Optional[np.ndarray]:
        """
        Safely captures the active Windows desktop image using Win32 OpenInputDesktop
        to bypass permission issues, returning an RGB numpy array.
        """
        user32 = ctypes.windll.user32
        hdesk = user32.OpenInputDesktop(0, False, 0x01FF)
        img = None
        if hdesk:
            user32.SetThreadDesktop(hdesk)
            try:
                img = ImageGrab.grab()
            except Exception:
                pass
            user32.CloseDesktop(hdesk)

        if img is None:
            try:
                img = ImageGrab.grab()
            except Exception:
                return None

        return np.array(img)

    @classmethod
    def scan_and_calibrate(cls) -> Tuple[bool, str, dict]:
        """
        Scans screen for Gartic Phone and returns detected coordinates:
        Returns:
            (success: bool, status_message: str, data: dict)
            data contains:
                'canvas': (cx, cy, cw, ch)
                'palette_black': (x, y)
                'palette_peach': (x, y)
                'palette_coords': dict of 18 color coords
                'pen_thin': (x, y)
                'pen_medium': (x, y)
        """
        screen_rgb = cls.capture_screen()
        if screen_rgb is None:
            preset_name, preset = ScreenResolutionPresets.get_auto_preset_for_screen()
            coords = cls.generate_all_palette_coords(preset["palette_black"], preset["palette_peach"])
            preset["palette_coords"] = coords
            return False, f"Ekran görüntüsü alınamadı, '{preset_name}' ayarı uygulandı.", preset

        return cls.detect_from_image_array(screen_rgb)

    @classmethod
    def detect_from_image_array(cls, screen_rgb: np.ndarray) -> Tuple[bool, str, dict]:
        """Runs computer vision detection on any given RGB numpy image."""
        screen_h, screen_w, _ = screen_rgb.shape

        # Helper to find centroid of a specific RGB color
        def find_cluster_center(rgb: List[int], tol: int = 24) -> Optional[Tuple[int, int]]:
            diff = np.abs(screen_rgb - np.array(rgb, dtype=np.int16))
            m = np.all(diff < tol, axis=2)
            ys, xs = np.where(m)
            if len(xs) >= 40:
                return int(np.median(xs)), int(np.median(ys))
            return None

        # Key distinct colors in Gartic Phone:
        # Col 0, Row 5: Yellow [255, 193, 38]
        # Col 1, Row 5: Hot Pink [255, 0, 143]
        # Col 2, Row 5: Peach [254, 175, 168]
        # Col 2, Row 0: Dark Blue [0, 80, 205]
        # Col 1, Row 3: Red [255, 0, 19]
        # Col 0, Row 2: Dark Green [1, 116, 32]
        c_yellow = find_cluster_center([255, 193, 38])
        c_pink = find_cluster_center([255, 0, 143])
        c_peach = find_cluster_center([254, 175, 168])
        c_dblue = find_cluster_center([0, 80, 205])
        c_red = find_cluster_center([255, 0, 19])
        c_dgreen = find_cluster_center([1, 116, 32])

        palette_found = False
        pt_black = None
        pt_peach = None
        col_step = 0.0
        row_step = 0.0

        if c_pink and (c_peach or c_yellow):
            palette_found = True

            # Calculate col_step
            if c_yellow and c_peach:
                col_step = (c_peach[0] - c_yellow[0]) / 2.0
            elif c_pink and c_peach:
                col_step = float(c_peach[0] - c_pink[0])
            else:
                col_step = float(c_pink[0] - c_yellow[0])

            # Calculate row_step
            if c_red and c_pink:
                row_step = (c_pink[1] - c_red[1]) / 2.0
            elif c_dblue and c_peach:
                row_step = (c_peach[1] - c_dblue[1]) / 5.0
            elif c_dgreen and c_yellow:
                row_step = (c_yellow[1] - c_dgreen[1]) / 3.0
            else:
                row_step = col_step * 1.09

            # Anchor from bottom row (Row 5)
            ref_x = c_yellow[0] if c_yellow else (c_pink[0] - col_step)
            ref_y = c_yellow[1] if c_yellow else c_pink[1]

            black_x = int(round(ref_x))
            black_y = int(round(ref_y - 5.0 * row_step))
            peach_x = int(round(ref_x + 2.0 * col_step))
            peach_y = int(round(ref_y))

            pt_black = (black_x, black_y)
            pt_peach = (peach_x, peach_y)

        # 2. Canvas Detection
        best_canvas = None

        if palette_found and pt_peach:
            # Search canvas strictly to the right of the palette
            sub_x = pt_peach[0] + 12
            if sub_x < screen_w:
                sub_img = screen_rgb[:, sub_x:]
                # Canvas has light / white background
                gray_sub = cv2.cvtColor(sub_img, cv2.COLOR_RGB2GRAY)
                # Threshold for canvas white surface (tolerant to user sketches on canvas)
                _, th = cv2.threshold(gray_sub, 215, 255, cv2.THRESH_BINARY)
                # Morphological close to merge drawing gaps
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
                closed = cv2.morphologyEx(th, cv2.MORPH_CLOSE, kernel)
                cnts, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                best_area = 0
                for c in cnts:
                    bx, by, bw, bh = cv2.boundingRect(c)
                    if bw > (screen_w * 0.20) and bh > (screen_h * 0.20):
                        area = bw * bh
                        if area > best_area:
                            best_area = area
                            best_canvas = (bx + sub_x, by, bw, bh)

        # If palette was found:
        if palette_found and pt_black and pt_peach:
            palette_coords = cls.generate_all_palette_coords(pt_black, pt_peach)

            # If canvas was found:
            if best_canvas:
                cx, cy, cw, ch = best_canvas
            else:
                # Estimate canvas from palette dimensions
                cx = pt_peach[0] + int(col_step * 1.6)
                cy = pt_black[1] - int(row_step * 0.4)
                cw = int(col_step * 24.0)
                ch = int(row_step * 17.5)
                best_canvas = (cx, cy, cw, ch)

            # Toolbar buttons (right side of canvas)
            pen_tool = (int(cx + cw + col_step * 0.8), int(cy + ch * 0.169))
            eraser_tool = (int(cx + cw + col_step * 0.8), int(cy + ch * 0.265))
            bucket_tool = (int(cx + cw + col_step * 0.8), int(cy + ch * 0.355))
            pen_thin = (int(cx + cw + col_step * 0.8), int(cy + ch * 0.650))
            pen_medium = (int(cx + cw + col_step * 0.8), int(cy + ch * 0.740))

            result = {
                "canvas": best_canvas,
                "palette_black": pt_black,
                "palette_peach": pt_peach,
                "palette_coords": palette_coords,
                "pen_tool": pen_tool,
                "eraser_tool": eraser_tool,
                "bucket_tool": bucket_tool,
                "pen_thin": pen_thin,
                "pen_medium": pen_medium,
            }
            msg = f"✅ Gartic Phone Algılandı! Tuval: {best_canvas[2]}x{best_canvas[3]}px, 18 Renk Paleti ve Araçlar tam kilitlendi."
            return True, msg, result

        # If palette was NOT found on screen:
        preset_name, preset = ScreenResolutionPresets.get_auto_preset_for_screen()
        palette_coords = cls.generate_all_palette_coords(preset["palette_black"], preset["palette_peach"])
        preset["palette_coords"] = palette_coords
        msg = f"⚠️ Gartic Phone penceresi görünürde bulunamadı. Ekran çözünürlüğünüze uygun '{preset_name}' ayarı uygulandı."
        return False, msg, preset

    @staticmethod
    def focus_gartic_browser_window() -> bool:
        """
        Finds open browser window running Gartic Phone and brings it cleanly to the foreground.
        """
        import win32gui
        target_hwnd = None

        def _enum_cb(hwnd, _):
            nonlocal target_hwnd
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd).lower()
                if "gartic" in title:
                    target_hwnd = hwnd
                elif target_hwnd is None and any(b in title for b in ["chrome", "edge", "opera", "brave", "firefox"]):
                    target_hwnd = hwnd

        try:
            win32gui.EnumWindows(_enum_cb, None)
            if target_hwnd:
                user32 = ctypes.windll.user32
                user32.ShowWindow(target_hwnd, 9)  # SW_RESTORE
                user32.SetForegroundWindow(target_hwnd)
                return True
        except Exception:
            pass
        return False

    @staticmethod
    def generate_all_palette_coords(pt_black: Tuple[int, int], pt_peach: Tuple[int, int]) -> Dict[str, Tuple[int, int]]:
        """Computes exact center coordinates for all 18 colors from Black and Peach corners."""
        tl_x, tl_y = pt_black
        br_x, br_y = pt_peach
        col_step = (br_x - tl_x) / 2.0
        row_step = (br_y - tl_y) / 5.0

        coords = {}
        for r in range(6):
            for c in range(3):
                name, _ = GARTIC_PALETTE_GRID[r][c]
                bx = int(round(tl_x + c * col_step))
                by = int(round(tl_y + r * row_step))
                coords[name] = (bx, by)
        return coords
