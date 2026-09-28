"""
Gartic AutoDraw Pro - Gartic Color Palette & Quantizer
Contains exact 18-color Gartic Phone 3x6 palette definitions,
Redmean perceptual color matching, auto-canvas relative positioning,
and Floyd-Steinberg multi-color error diffusion.
"""

from typing import Dict, Tuple, List, Optional
import numpy as np

# Official Gartic Phone 3x6 Palette Grid (Exact Hex & RGB from Gartic Phone DOM/Screen):
# Row 0: Black, Gray, Dark Blue
# Row 1: White, Light Gray, Light Blue
# Row 2: Dark Green, Dark Red, Brown
# Row 3: Light Green, Red, Orange
# Row 4: Mustard/Dark Yellow, Magenta/Purple, Terracotta/Dark Skin
# Row 5: Yellow, Hot Pink, Peach/Skin Tone

GARTIC_PALETTE_GRID = [
    [("black", (0, 0, 0)), ("gray", (102, 102, 102)), ("dark_blue", (0, 80, 205))],
    [("white", (255, 255, 255)), ("light_gray", (170, 170, 170)), ("light_blue", (38, 201, 255))],
    [("dark_green", (1, 116, 32)), ("dark_red", (153, 0, 0)), ("brown", (150, 65, 18))],
    [("light_green", (17, 176, 60)), ("red", (255, 0, 19)), ("orange", (255, 120, 41))],
    [("dark_yellow", (176, 112, 28)), ("magenta", (153, 0, 78)), ("terracotta", (203, 90, 87))],
    [("yellow", (255, 193, 38)), ("hot_pink", (255, 0, 143)), ("skin_peach", (254, 175, 168))]
]

GARTIC_PALETTE_RGB: Dict[str, Tuple[int, int, int]] = {}
for row in GARTIC_PALETTE_GRID:
    for name, rgb in row:
        GARTIC_PALETTE_RGB[name] = rgb

GARTIC_COLOR_NAMES_TR: Dict[str, str] = {
    "black": "Siyah",
    "gray": "Koyu Gri",
    "dark_blue": "Lacivert",
    "white": "Beyaz",
    "light_gray": "Açık Gri",
    "light_blue": "Açık Mavi / Camgöbeği",
    "dark_green": "Koyu Yeşil",
    "dark_red": "Bordo",
    "brown": "Kahverengi",
    "light_green": "Açık Yeşil",
    "red": "Kırmızı",
    "orange": "Turuncu",
    "dark_yellow": "Hardal Sarısı / Toprak",
    "magenta": "Mor / Macenta",
    "terracotta": "Sıcak Ten Gölgesi / Terracotta",
    "yellow": "Parlak Sarı",
    "hot_pink": "Neon Pembe",
    "skin_peach": "Açık Ten Rengi (Şeftali)",
}

PALETTE_NAMES = list(GARTIC_PALETTE_RGB.keys())
PALETTE_RGB_ARRAY = np.array([GARTIC_PALETTE_RGB[k] for k in PALETTE_NAMES], dtype=np.float32)


class GarticPaletteManager:
    """
    Manages Gartic Phone 3x6 color quantization, multi-color dithering,
    and on-screen palette button coordinates.
    """

    def __init__(self):
        self.color_coords: Dict[str, Tuple[int, int]] = {}
        # Default canvas: 2K centered canvas (780, 260, 1000, 720)
        self.calibrate_relative_to_canvas(780, 260, 1000, 720)

    def calibrate_relative_to_canvas(self, cx: int, cy: int, cw: int, ch: int):
        """
        Positions the 3x6 color palette relative to the Gartic Phone canvas.
        Based on mathematically verified pixel ratios from official Gartic Phone UI:
        Canvas Left is at cx, Top is at cy.
        Black (Row 0, Col 0): (cx - int(cw * 0.1625), cy + int(ch * 0.2381)) -> (617, 431) on 2K
        Peach (Row 5, Col 2): (cx - int(cw * 0.0708), cy + int(ch * 0.8155)) -> (709, 847) on 2K
        """
        tl_x = int(round(cx - (cw * 0.1625)))
        tl_y = int(round(cy + (ch * 0.2381)))
        br_x = int(round(cx - (cw * 0.0708)))
        br_y = int(round(cy + (ch * 0.8155)))
        self.calibrate_from_two_corners(tl_x, tl_y, br_x, br_y)

    def calibrate_from_two_corners(self, tl_x: int, tl_y: int, br_x: int, br_y: int):
        """
        Calculates exact centers of all 18 color buttons in the 3x6 grid
        from just 2 points: Top-Left (Black) and Bottom-Right (Peach).
        """
        col_step = (br_x - tl_x) / 2.0
        row_step = (br_y - tl_y) / 5.0

        for r in range(6):
            for c in range(3):
                name, _ = GARTIC_PALETTE_GRID[r][c]
                btn_x = int(round(tl_x + c * col_step))
                btn_y = int(round(tl_y + r * row_step))
                self.color_coords[name] = (btn_x, btn_y)

    def get_color_coord(self, color_name: str) -> Optional[Tuple[int, int]]:
        return self.color_coords.get(color_name)

    @staticmethod
    def match_nearest_palette_color(rgb: Tuple[int, int, int]) -> Tuple[str, Tuple[int, int, int]]:
        """Finds closest color in Gartic Phone palette using Redmean perceptual distance."""
        r, g, b = rgb
        diff = PALETTE_RGB_ARRAY - np.array([r, g, b], dtype=np.float32)
        # Redmean perceptual weighting
        r_bar = (r + PALETTE_RGB_ARRAY[:, 0]) / 2.0
        weights = (2.0 + r_bar / 256.0) * (diff[:, 0] ** 2) + \
                  4.0 * (diff[:, 1] ** 2) + \
                  (2.0 + (255.0 - r_bar) / 256.0) * (diff[:, 2] ** 2)
        best_idx = int(np.argmin(weights))
        name = PALETTE_NAMES[best_idx]
        return name, GARTIC_PALETTE_RGB[name]

    @staticmethod
    def quantize_and_dither_image(
        img_rgb: np.ndarray,
        remove_dark_bg: bool = True,
        dark_thresh: int = 60,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Runs Floyd-Steinberg error diffusion across the 18 Gartic Phone colors
        with Smart Portrait warmth enhancement and gray/mud suppression on human skin.
        Returns:
            - color_indices: (H, W) array of palette indices (0..17, or white_idx for background)
            - quantized_rgb: (H, W, 3) full-color rendered image using Gartic palette
        """
        h, w, _ = img_rgb.shape
        buf = img_rgb.astype(np.float32).copy()
        indices = np.zeros((h, w), dtype=np.uint8)
        rendered_rgb = np.full((h, w, 3), 255, dtype=np.uint8)

        white_idx = PALETTE_NAMES.index("white")
        gray_idx = PALETTE_NAMES.index("gray")
        light_gray_idx = PALETTE_NAMES.index("light_gray")
        dark_blue_idx = PALETTE_NAMES.index("dark_blue")
        dark_green_idx = PALETTE_NAMES.index("dark_green")
        peach_idx = PALETTE_NAMES.index("skin_peach")
        terracotta_idx = PALETTE_NAMES.index("terracotta")
        brown_idx = PALETTE_NAMES.index("brown")

        # Smart Portrait Warmth Enhancement (prevents pale webcam faces from turning into zombie gray)
        r, g, b = buf[:, :, 0], buf[:, :, 1], buf[:, :, 2]
        brightness = (r + g + b) / 3.0
        warm_mask = (r > b - 5) & (brightness > 40) & (brightness < 240)
        buf[warm_mask, 0] = np.clip(buf[warm_mask, 0] * 1.20 + 12, 0, 255)
        buf[warm_mask, 1] = np.clip(buf[warm_mask, 1] * 1.08 + 6, 0, 255)
        buf[warm_mask, 2] = np.clip(buf[warm_mask, 2] * 0.85 - 8, 0, 255)

        for y in range(h):
            direction = 1 if y % 2 == 0 else -1
            x_range = range(w) if direction == 1 else range(w - 1, -1, -1)

            for x in x_range:
                old_p = buf[y, x]

                # If removing dark background (e.g. webcam room shadows / Discord black bars)
                if remove_dark_bg and np.mean(old_p) < dark_thresh:
                    indices[y, x] = white_idx
                    rendered_rgb[y, x] = [255, 255, 255]
                    # Do not diffuse background darkness into subject!
                    continue

                # Redmean perceptual color distance
                diff = PALETTE_RGB_ARRAY - old_p
                r_bar = (old_p[0] + PALETTE_RGB_ARRAY[:, 0]) / 2.0
                dist = (2.0 + r_bar / 256.0) * (diff[:, 0] ** 2) + \
                       4.0 * (diff[:, 1] ** 2) + \
                       (2.0 + (255.0 - r_bar) / 256.0) * (diff[:, 2] ** 2)

                # If pixel has warm/skin tones, heavily penalize cold neutral gray and dark blue:
                if old_p[0] > old_p[2] + 2:
                    dist[gray_idx] *= 4.5
                    dist[light_gray_idx] *= 3.5
                    dist[dark_blue_idx] *= 4.0
                    dist[dark_green_idx] *= 3.0
                    # Prioritize peach and terracotta
                    dist[peach_idx] *= 0.55
                    dist[terracotta_idx] *= 0.65
                    dist[brown_idx] *= 0.80

                best_idx = int(np.argmin(dist))
                new_p = PALETTE_RGB_ARRAY[best_idx]

                indices[y, x] = best_idx
                rendered_rgb[y, x] = new_p.astype(np.uint8)

                # Damped error diffusion (0.75 prevents noisy grain and blends skin smoothly)
                err = (old_p - new_p) * 0.75

                if direction == 1:
                    if x + 1 < w:
                        buf[y, x + 1] += err * (7.0 / 16.0)
                    if y + 1 < h:
                        if x - 1 >= 0:
                            buf[y + 1, x - 1] += err * (3.0 / 16.0)
                        buf[y + 1, x] += err * (5.0 / 16.0)
                        if x + 1 < w:
                            buf[y + 1, x + 1] += err * (1.0 / 16.0)
                else:
                    if x - 1 >= 0:
                        buf[y, x - 1] += err * (7.0 / 16.0)
                    if y + 1 < h:
                        if x + 1 < w:
                            buf[y + 1, x + 1] += err * (3.0 / 16.0)
                        buf[y + 1, x] += err * (5.0 / 16.0)
                        if x - 1 >= 0:
                            buf[y + 1, x - 1] += err * (1.0 / 16.0)

        return indices, rendered_rgb
