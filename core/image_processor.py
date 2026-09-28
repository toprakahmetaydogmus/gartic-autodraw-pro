"""
Gartic AutoDraw Pro - Hyper-Realistic Computer Vision & Image Processing Engine
Features Atkinson/Floyd-Steinberg Dithering, Auto-Canny Vector Contours,
Cross-Hatch Pencil Shading, and Full 18-Color Gartic Phone Palette Vectorization.
"""

from typing import List, Tuple, Dict, Optional
import numpy as np
import cv2
from PIL import Image, ImageEnhance

from core.gartic_palette import (
    GarticPaletteManager,
    GARTIC_PALETTE_RGB,
    PALETTE_NAMES,
)
from core.path_optimizer import PathOptimizer


class DrawingMode:
    REALISTIC_COLOR = "🌈 Ultra Gerçekçi Çok Renkli (Önerilen - Renkli Portre)"
    ANIME_COLOR = "🎌 Anime / Manga Renkli (Canlı Çizgi & Gölgelendirme)"
    CYBERPUNK_NEON = "🎭 Siber / Neon Pop-Art (Yüksek Kontrast & Parlak)"
    PIXEL_ART = "👾 Retro Piksel Sanatı (8-Bit Nostalji)"
    ATKINSON_PHOTOREAL = "✒️ Atkinson Fotogerçekçi (Siyah/Beyaz Eskiz)"
    FLOYD_STEINBERG = "🌫️ Floyd-Steinberg Detaylı Gölgelendirme"
    VECTOR_CONTOUR = "🖋️ Vektör Çizgi Sanatı (Anime/Logo/Karikatür)"
    CROSS_HATCH = "✏️ Sanatsal Karakalem Tarama"


class ImageProcessingEngine:
    """
    State-of-the-art vision processor tailored specifically for Gartic Phone and Gartic.io canvases.
    """

    def __init__(self):
        self.palette_mgr = GarticPaletteManager()

    @staticmethod
    def adjust_image_properties(
        image: Image.Image,
        contrast: float = 1.3,
        brightness: float = 1.0,
        sharpness: float = 1.5,
        saturation: float = 1.3,
        invert: bool = False,
    ) -> Image.Image:
        """Applies brightness, contrast, sharpness, saturation adjustments and optional inversion."""
        img = image.convert("RGB")

        if brightness != 1.0:
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(brightness)

        if contrast != 1.0:
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(contrast)

        if saturation != 1.0:
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(saturation)

        if sharpness != 1.0:
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(sharpness)

        if invert:
            np_img = 255 - np.array(img)
            img = Image.fromarray(np_img)

        return img

    @staticmethod
    def resize_for_canvas(
        image: Image.Image,
        max_dim: int = 360,
    ) -> Image.Image:
        """Resizes image keeping aspect ratio such that max(width, height) <= max_dim."""
        w, h = image.size
        if max(w, h) <= max_dim:
            return image

        scale = max_dim / float(max(w, h))
        new_w = max(1, int(w * scale))
        new_h = max(1, int(h * scale))
        return image.resize((new_w, new_h), Image.Resampling.LANCZOS)

    @staticmethod
    def atkinson_dither(gray_img: np.ndarray) -> np.ndarray:
        """
        Atkinson Dithering algorithm (used by original MacPaint).
        Diffuses only 6/8 (75%) of quantization error, preserving high contrast and sharp details.
        Output: Binary mask (255 = black ink pixel, 0 = white paper).
        """
        h, w = gray_img.shape
        buf = gray_img.astype(np.float32).copy()
        out_binary = np.zeros((h, w), dtype=np.uint8)

        for y in range(h):
            for x in range(w):
                old_val = buf[y, x]
                new_val = 0.0 if old_val < 128 else 255.0
                buf[y, x] = new_val

                if new_val == 0.0:
                    out_binary[y, x] = 255

                err = (old_val - new_val) / 8.0

                if x + 1 < w:
                    buf[y, x + 1] += err
                if x + 2 < w:
                    buf[y, x + 2] += err
                if y + 1 < h:
                    if x - 1 >= 0:
                        buf[y + 1, x - 1] += err
                    buf[y + 1, x] += err
                    if x + 1 < w:
                        buf[y + 1, x + 1] += err
                if y + 2 < h:
                    buf[y + 2, x] += err

        return out_binary

    @staticmethod
    def floyd_steinberg_dither(gray_img: np.ndarray) -> np.ndarray:
        """
        Floyd-Steinberg error diffusion dithering.
        Output: Binary mask (255 = black ink pixel, 0 = white paper).
        """
        h, w = gray_img.shape
        buf = gray_img.astype(np.float32).copy()
        out_binary = np.zeros((h, w), dtype=np.uint8)

        for y in range(h):
            direction = 1 if y % 2 == 0 else -1
            x_range = range(w) if direction == 1 else range(w - 1, -1, -1)

            for x in x_range:
                old_val = buf[y, x]
                new_val = 0.0 if old_val < 128 else 255.0
                buf[y, x] = new_val

                if new_val == 0.0:
                    out_binary[y, x] = 255

                err = old_val - new_val

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

        return out_binary

    @staticmethod
    def extract_vector_contours(
        gray_img: np.ndarray,
        canny_low: int = 50,
        canny_high: int = 150,
        bilateral_filter: bool = True,
    ) -> np.ndarray:
        """
        Applies Bilateral smoothing followed by Canny edge detection.
        Output: Binary edge mask (255 = edge, 0 = background).
        """
        if bilateral_filter:
            filtered = cv2.bilateralFilter(gray_img, d=7, sigmaColor=75, sigmaSpace=75)
        else:
            filtered = cv2.GaussianBlur(gray_img, (3, 3), 0)

        edges = cv2.Canny(filtered, canny_low, canny_high)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        dilated = cv2.dilate(edges, kernel, iterations=1)
        return dilated

    def process_image(
        self,
        image: Image.Image,
        mode: str = DrawingMode.REALISTIC_COLOR,
        contrast: float = 1.3,
        brightness: float = 1.0,
        sharpness: float = 1.5,
        saturation: float = 1.35,
        invert: bool = False,
        max_dim: int = 360,
        canny_low: int = 50,
        canny_high: int = 150,
        epsilon: float = 1.2,
        min_run_len: int = 2,
        max_strokes: int = 6000,
        remove_dark_bg: bool = True,
        dark_thresh: int = 60,
        enable_contour_reinforce: bool = True,
        target_round_time: float = 72.0,
    ) -> Tuple[List[List[Tuple[int, int]]], Optional[List[str]], Image.Image]:
        """
        Main processing pipeline.
        Returns:
            - strokes: List of point sequences [(x, y), ...]
            - colors: List of color names corresponding to each stroke
            - preview_image: High-fidelity rendered preview Image showing what will be drawn
        """
        # 1. Resize and enhance
        resized = self.resize_for_canvas(image, max_dim=max_dim)
        enhanced = self.adjust_image_properties(
            resized,
            contrast=contrast,
            brightness=brightness,
            sharpness=sharpness,
            saturation=saturation,
            invert=invert,
        )

        w, h = enhanced.size
        rgb_np = np.array(enhanced)

        # Smart Border Background Cleaner (removes webcam room shadows / Discord borders from flooding canvas)
        if remove_dark_bg:
            bg_mask = np.zeros((h + 2, w + 2), np.uint8)
            corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
            for cx_c, cy_c in corners:
                if np.mean(rgb_np[cy_c, cx_c]) < (dark_thresh + 20):
                    cv2.floodFill(
                        rgb_np.copy(),
                        bg_mask,
                        (cx_c, cy_c),
                        (255, 255, 255),
                        (28, 28, 28),
                        (28, 28, 28),
                        flags=cv2.FLOODFILL_MASK_ONLY,
                    )
            border_bg = bg_mask[1:-1, 1:-1] > 0
            rgb_np[border_bg] = [255, 255, 255]

        gray_np = cv2.cvtColor(rgb_np, cv2.COLOR_RGB2GRAY)
        if remove_dark_bg:
            gray_np[border_bg] = 255

        strokes: List[List[Tuple[int, int]]] = []
        stroke_colors: Optional[List[str]] = None

        if mode == DrawingMode.REALISTIC_COLOR:
            # 18-color Floyd-Steinberg error diffusion
            indices, rendered_rgb = self.palette_mgr.quantize_and_dither_image(
                rgb_np, remove_dark_bg=remove_dark_bg, dark_thresh=dark_thresh
            )

            all_strokes: List[List[Tuple[int, int]]] = []
            all_colors: List[str] = []

            # Color drawing priority order:
            # 1. Base / skin tones first
            # 2. Neutral midtones and hair
            # 3. Vibrant colors (clothes, glowing headphones)
            # 4. Black outlines and deep shadows LAST on top!
            drawing_order = [
                "skin_peach",
                "terracotta",
                "light_gray",
                "gray",
                "dark_yellow",
                "brown",
                "light_blue",
                "dark_blue",
                "light_green",
                "dark_green",
                "yellow",
                "orange",
                "red",
                "dark_red",
                "hot_pink",
                "magenta",
                "black",
            ]

            white_idx = PALETTE_NAMES.index("white")

            for col_name in drawing_order:
                col_idx = PALETTE_NAMES.index(col_name)
                # Binary mask for this color
                mask = (indices == col_idx).astype(np.uint8) * 255
                if np.sum(mask) == 0:
                    continue

                # Run-length strokes
                col_strokes = PathOptimizer.dither_to_run_length_strokes(
                    mask, min_run_length=min_run_len, max_gap_to_merge=1
                )
                if not col_strokes:
                    continue

                # Optimize within this color
                col_strokes_opt = PathOptimizer.optimize_stroke_order(col_strokes)

                for s in col_strokes_opt:
                    all_strokes.append(s)
                    all_colors.append(col_name)

            strokes = all_strokes
            stroke_colors = all_colors

            # Fine Vector Line Art Reinforcement (Inks prominent facial features on top in crisp black)
            if enable_contour_reinforce:
                subject_edges = cv2.Canny(gray_np, canny_low, canny_high)
                if remove_dark_bg:
                    subject_edges[border_bg] = 0
                contour_strokes = PathOptimizer.extract_contours_as_strokes(
                    subject_edges, epsilon=0.8, min_contour_len=3
                )
                if contour_strokes:
                    contour_opt = PathOptimizer.optimize_stroke_order(contour_strokes)
                    for cs in contour_opt:
                        strokes.append(cs)
                        stroke_colors.append("black")
                    rendered_rgb[subject_edges > 0] = [15, 15, 15]

            preview_pil = Image.fromarray(rendered_rgb)

        elif mode == DrawingMode.ANIME_COLOR:
            # 1. Bilateral filter for cell-shaded smooth color fields
            filtered_rgb = cv2.bilateralFilter(rgb_np, d=9, sigmaColor=75, sigmaSpace=75)
            # 2. Extract sharp lineart edges
            edges = cv2.Canny(gray_np, 40, 110)
            if remove_dark_bg:
                edges[border_bg] = 0

            # 3. Quantize color fields without heavy grain
            indices, rendered_rgb = self.palette_mgr.quantize_and_dither_image(
                filtered_rgb, remove_dark_bg=remove_dark_bg, dark_thresh=dark_thresh
            )

            all_strokes: List[List[Tuple[int, int]]] = []
            all_colors: List[str] = []

            for col_name in [
                "skin_peach", "terracotta", "light_gray", "gray", "dark_yellow", "brown",
                "light_blue", "dark_blue", "light_green", "dark_green", "yellow", "orange",
                "red", "dark_red", "hot_pink", "magenta", "black"
            ]:
                col_idx = PALETTE_NAMES.index(col_name)
                mask = (indices == col_idx).astype(np.uint8) * 255
                if np.sum(mask) == 0:
                    continue
                col_strokes = PathOptimizer.dither_to_run_length_strokes(mask, min_run_length=min_run_len, max_gap_to_merge=2)
                col_opt = PathOptimizer.optimize_stroke_order(col_strokes)
                for s in col_opt:
                    all_strokes.append(s)
                    all_colors.append(col_name)

            # Bold black inking contours on top
            contour_strokes = PathOptimizer.extract_contours_as_strokes(edges, epsilon=0.9, min_contour_len=3)
            if contour_strokes:
                contour_opt = PathOptimizer.optimize_stroke_order(contour_strokes)
                for cs in contour_opt:
                    all_strokes.append(cs)
                    all_colors.append("black")
                rendered_rgb[edges > 0] = [10, 10, 10]

            strokes = all_strokes
            stroke_colors = all_colors
            preview_pil = Image.fromarray(rendered_rgb)

        elif mode == DrawingMode.CYBERPUNK_NEON:
            # High-saturation neon pop art
            enhanced_neon = self.adjust_image_properties(resized, contrast=1.45, brightness=1.05, sharpness=1.8, saturation=1.65, invert=invert)
            neon_np = np.array(enhanced_neon)
            if remove_dark_bg:
                neon_np[border_bg] = [255, 255, 255]

            indices, rendered_rgb = self.palette_mgr.quantize_and_dither_image(
                neon_np, remove_dark_bg=remove_dark_bg, dark_thresh=dark_thresh
            )

            all_strokes: List[List[Tuple[int, int]]] = []
            all_colors: List[str] = []

            for col_name in [
                "hot_pink", "light_blue", "yellow", "magenta", "orange", "dark_blue", "light_green", "skin_peach", "black"
            ]:
                if col_name not in PALETTE_NAMES:
                    continue
                col_idx = PALETTE_NAMES.index(col_name)
                mask = (indices == col_idx).astype(np.uint8) * 255
                if np.sum(mask) == 0:
                    continue
                col_strokes = PathOptimizer.dither_to_run_length_strokes(mask, min_run_length=min_run_len, max_gap_to_merge=1)
                col_opt = PathOptimizer.optimize_stroke_order(col_strokes)
                for s in col_opt:
                    all_strokes.append(s)
                    all_colors.append(col_name)

            edges = cv2.Canny(gray_np, 45, 125)
            if remove_dark_bg:
                edges[border_bg] = 0
            contour_strokes = PathOptimizer.extract_contours_as_strokes(edges, epsilon=0.9)
            if contour_strokes:
                contour_opt = PathOptimizer.optimize_stroke_order(contour_strokes)
                for cs in contour_opt:
                    all_strokes.append(cs)
                    all_colors.append("black")
                rendered_rgb[edges > 0] = [10, 10, 10]

            strokes = all_strokes
            stroke_colors = all_colors
            preview_pil = Image.fromarray(rendered_rgb)

        elif mode == DrawingMode.PIXEL_ART:
            # 64px pixel block downsampling
            p_dim = 64
            scale = p_dim / float(max(w, h))
            pw, ph = max(1, int(w * scale)), max(1, int(h * scale))
            small = cv2.resize(rgb_np, (pw, ph), interpolation=cv2.INTER_AREA)

            # Quantize each pixel to nearest Gartic color
            pixel_indices = np.zeros((ph, pw), dtype=np.uint8)
            rendered_pixels = np.full((ph, pw, 3), 255, dtype=np.uint8)

            for py in range(ph):
                for px in range(pw):
                    cname, crgb = GarticPaletteManager.match_nearest_palette_color(tuple(small[py, px]))
                    cidx = PALETTE_NAMES.index(cname)
                    pixel_indices[py, px] = cidx
                    rendered_pixels[py, px] = crgb

            # Scale up to canvas size
            scale_x = w / float(pw)
            scale_y = h / float(ph)

            # Group by color and merge contiguous horizontal runs for ultra-fast drawing
            all_strokes: List[List[Tuple[int, int]]] = []
            all_colors: List[str] = []

            for col_name in PALETTE_NAMES:
                if col_name == "white":
                    continue
                col_idx = PALETTE_NAMES.index(col_name)
                col_runs: List[List[Tuple[int, int]]] = []
                for py in range(ph):
                    px = 0
                    while px < pw:
                        if pixel_indices[py, px] == col_idx:
                            run_start = px
                            while px < pw and pixel_indices[py, px] == col_idx:
                                px += 1
                            run_end = px
                            rx0 = int(round(run_start * scale_x))
                            rx1 = int(round(run_end * scale_x))
                            ry = int(round((py + 0.5) * scale_y))
                            col_runs.append([(rx0, ry), (rx1, ry)])
                        else:
                            px += 1

                if col_runs:
                    opt_runs = PathOptimizer.optimize_stroke_order(col_runs)
                    for r in opt_runs:
                        all_strokes.append(r)
                        all_colors.append(col_name)

            strokes = all_strokes
            stroke_colors = all_colors
            preview_upscaled = cv2.resize(rendered_pixels, (w, h), interpolation=cv2.INTER_NEAREST)
            preview_pil = Image.fromarray(preview_upscaled)

        elif mode == DrawingMode.ATKINSON_PHOTOREAL:
            binary = self.atkinson_dither(gray_np)
            raw_strokes = PathOptimizer.dither_to_run_length_strokes(
                binary, min_run_length=min_run_len, max_gap_to_merge=1
            )
            strokes = PathOptimizer.optimize_stroke_order(raw_strokes)
            stroke_colors = ["black"] * len(strokes)
            preview_canvas = np.full((h, w, 3), 255, dtype=np.uint8)
            preview_canvas[binary > 0] = [20, 20, 20]
            preview_pil = Image.fromarray(preview_canvas)

        elif mode == DrawingMode.FLOYD_STEINBERG:
            binary = self.floyd_steinberg_dither(gray_np)
            raw_strokes = PathOptimizer.dither_to_run_length_strokes(
                binary, min_run_length=min_run_len, max_gap_to_merge=1
            )
            strokes = PathOptimizer.optimize_stroke_order(raw_strokes)
            stroke_colors = ["black"] * len(strokes)
            preview_canvas = np.full((h, w, 3), 255, dtype=np.uint8)
            preview_canvas[binary > 0] = [20, 20, 20]
            preview_pil = Image.fromarray(preview_canvas)

        elif mode == DrawingMode.VECTOR_CONTOUR:
            edges = self.extract_vector_contours(
                gray_np, canny_low=canny_low, canny_high=canny_high
            )
            raw_strokes = PathOptimizer.extract_contours_as_strokes(
                edges, epsilon=epsilon, min_contour_len=3
            )
            strokes = PathOptimizer.optimize_stroke_order(raw_strokes)
            stroke_colors = ["black"] * len(strokes)
            preview_canvas = np.full((h, w, 3), 255, dtype=np.uint8)
            preview_canvas[edges > 0] = [20, 20, 20]
            preview_pil = Image.fromarray(preview_canvas)

        else: # Cross-hatch
            edges = self.extract_vector_contours(gray_np, canny_low=80, canny_high=180)
            edge_strokes = PathOptimizer.extract_contours_as_strokes(edges, epsilon=1.5)
            hatch_strokes = PathOptimizer.dither_to_run_length_strokes(
                (gray_np < 120).astype(np.uint8) * 255, min_run_length=2, max_gap_to_merge=1
            )
            raw_strokes = edge_strokes + hatch_strokes[::2]
            strokes = PathOptimizer.optimize_stroke_order(raw_strokes)
            stroke_colors = ["black"] * len(strokes)
            preview_canvas = np.full((h, w, 3), 255, dtype=np.uint8)
            preview_pil = Image.fromarray(preview_canvas)

        # Apply stroke limit if necessary
        if max_strokes > 0 and len(strokes) > max_strokes:
            strokes = strokes[:max_strokes]
            if stroke_colors:
                stroke_colors = stroke_colors[:max_strokes]

        # Adaptive Time Budget Compression (Guarantee round completion within target time)
        if target_round_time > 0 and strokes:
            strokes, stroke_colors = PathOptimizer.fit_strokes_to_time_budget(
                strokes, stroke_colors, target_time_sec=target_round_time
            )

        return strokes, stroke_colors, preview_pil

    @staticmethod
    def calculate_estimated_time(
        num_strokes: int,
        total_points: int,
        point_delay: float = 0.0018,
        stroke_delay: float = 0.004,
    ) -> float:
        """Calculates realistic drawing time in seconds."""
        time_sec = (total_points * point_delay) + (num_strokes * stroke_delay)
        return round(time_sec, 1)
