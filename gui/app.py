"""
Gartic AutoDraw Pro - State of the Art Graphical User Interface
Ultra-responsive CustomTkinter GUI with Full 18-Color Palette Automation,
Skin Tone Layering, Background Shadow Cleaning, 2K Edge-to-Edge Canvas Alignment,
and Visual Transparent Overlays.
"""

import os
import json
import time
import threading
import winsound
from typing import Optional, List, Tuple
from PIL import Image
import customtkinter as ctk
import win32api
import win32con

from core.win32_mouse import Win32MouseController
from core.image_processor import ImageProcessingEngine, DrawingMode
from core.path_optimizer import PathOptimizer
from core.web_search import ImageSearchEngine
from core.hotkeys import GlobalHotkeyManager
from gui.calibration_overlay import CanvasCalibrator, InteractiveScreenSelector
from gui.smart_calibrator import (
    VisualCanvasBorderOverlay,
    TwoClickCalibrator,
    PaletteTwoClickCalibrator,
)


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "settings.json")


class GarticAutoDrawApp(ctk.CTk):
    """
    Main Application Window for Gartic AutoDraw Pro.
    """

    def __init__(self):
        super().__init__()

        self.title("⚡ Gartic AutoDraw AI Studio Pro - Ultra Gerçekçi Renkli Çizim (2K Uyumlu)")
        self.geometry("1420x920")
        self.minsize(1220, 800)

        # Core Engines
        self.mouse_ctrl = Win32MouseController()
        self.calibrator = CanvasCalibrator(self.mouse_ctrl)
        self.img_engine = ImageProcessingEngine()
        self.search_engine = ImageSearchEngine()
        self.visual_border = VisualCanvasBorderOverlay(self)

        # State Variables
        self.current_image: Optional[Image.Image] = None
        self.preview_image: Optional[Image.Image] = None
        self.processed_strokes: List[List[Tuple[int, int]]] = []
        self.stroke_colors: Optional[List[str]] = None
        self.is_processing = False
        self.is_counting_down = False
        self.draw_thread: Optional[threading.Thread] = None

        # Speed defaults (optimal for HTML5 canvas games)
        self.active_p_delay: float = 0.0018
        self.active_s_delay: float = 0.004

        # Load saved settings (default to 2K centered canvas 780x720)
        self.settings = self._load_settings()
        cx = self.settings.get("canvas_x", 780)
        cy = self.settings.get("canvas_y", 260)
        cw = self.settings.get("canvas_w", 1000)
        ch = self.settings.get("canvas_h", 720)
        self.calibrator.set_bounds(cx, cy, cw, ch)
        if "palette_black" in self.settings and "palette_peach" in self.settings:
            pt_b = self.settings["palette_black"]
            pt_p = self.settings["palette_peach"]
            self.img_engine.palette_mgr.calibrate_from_two_corners(pt_b[0], pt_b[1], pt_p[0], pt_p[1])
        else:
            self.img_engine.palette_mgr.calibrate_relative_to_canvas(cx, cy, cw, ch)

        # Build UI Components
        self._build_header_hud()
        self._build_main_layout()

        # Setup Mouse Callbacks
        self.mouse_ctrl.on_progress = self._on_draw_progress
        self.mouse_ctrl.on_state_change = self._on_draw_state_change

        # Setup Global Hotkeys
        self.hotkeys = GlobalHotkeyManager(
            on_start=self._start_drawing_with_countdown,
            on_pause_toggle=self.mouse_ctrl.toggle_pause,
            on_emergency_stop=self.emergency_stop,
            on_test_bounds=self.test_canvas_bounds,
            on_calibrate=self.open_two_click_calibration,
        )
        self.hotkeys.start()

        # Bind keyboard shortcuts
        self.bind("<Control-v>", lambda e: self.paste_from_clipboard())
        self.bind("<Escape>", lambda e: self.emergency_stop())

        # Load instant local default sketch
        default_img = self.search_engine.get_local_default()
        self.set_active_image(default_img)

        # Auto position on second monitor if available
        if self.settings.get("auto_second_monitor", True):
            self.after(400, self.toggle_monitor_placement)

    def _load_settings(self) -> dict:
        default_settings = {
            "canvas_x": 780,
            "canvas_y": 260,
            "canvas_w": 1000,
            "canvas_h": 720,
            "speed": "Gartic Phone Standart (1.8ms - Önerilen)",
            "mode": DrawingMode.REALISTIC_COLOR,
            "contrast": 1.30,
            "brightness": 1.05,
            "sharpness": 1.50,
            "saturation": 1.35,
            "invert": False,
            "max_dim": 360,
            "remove_dark_bg": True,
            "dark_thresh": 60,
            "enable_contour_reinforce": True,
            "auto_select_pen": True,
            "auto_second_monitor": True,
        }
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    default_settings.update(data)
            except Exception:
                pass
        return default_settings

    def _save_settings(self):
        cx, cy, cw, ch = self.calibrator.get_bounds()
        self.settings.update({
            "canvas_x": cx,
            "canvas_y": cy,
            "canvas_w": cw,
            "canvas_h": ch,
            "mode": self.mode_selector.get(),
            "contrast": float(self.slider_contrast.get()),
            "brightness": float(self.slider_brightness.get()),
            "sharpness": float(self.slider_sharpness.get()),
            "saturation": float(self.slider_saturation.get()) if hasattr(self, "slider_saturation") else 1.35,
            "invert": bool(self.switch_invert.get()),
            "max_dim": int(self.slider_max_dim.get()),
            "remove_dark_bg": bool(self.switch_clean_bg.get()),
            "dark_thresh": int(self.slider_dark_thresh.get()),
            "enable_contour_reinforce": bool(self.switch_reinforce.get()) if hasattr(self, "switch_reinforce") else True,
            "auto_select_pen": bool(self.switch_auto_pen.get()) if hasattr(self, "switch_auto_pen") else True,
        })
        coord_black = self.img_engine.palette_mgr.get_color_coord("black")
        coord_peach = self.img_engine.palette_mgr.get_color_coord("skin_peach")
        if coord_black and coord_peach:
            self.settings["palette_black"] = list(coord_black)
            self.settings["palette_peach"] = list(coord_peach)
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4)
        except Exception:
            pass

    # ================= UI BUILDERS =================

    def _build_header_hud(self):
        """Top bar with monitor routing, 2K auto-alignment, live canvas info, and quick actions."""
        self.header_frame = ctk.CTkFrame(self, height=65, corner_radius=0, fg_color="#0b1120")
        self.header_frame.pack(fill="x", side="top", padx=0, pady=0)

        # App Logo & Branding
        logo_label = ctk.CTkLabel(
            self.header_frame,
            text="⚡ GARTIC AUTODRAW PRO",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color="#38bdf8",
        )
        logo_label.pack(side="left", padx=12, pady=12)

        # Multi-Monitor Action Button
        self.btn_monitor2 = ctk.CTkButton(
            self.header_frame,
            text="🖥️ 2. Monitöre Taşı",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#334155",
            hover_color="#475569",
            command=self.toggle_monitor_placement,
            width=140,
            height=36,
        )
        self.btn_monitor2.pack(side="left", padx=4, pady=12)

        # 2K TAM AYARLA Button
        self.btn_auto_setup = ctk.CTkButton(
            self.header_frame,
            text="⚡ 2K TAM AYARLA",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#8b5cf6",
            hover_color="#7c3aed",
            command=self.one_click_2k_setup,
            width=145,
            height=36,
        )
        self.btn_auto_setup.pack(side="left", padx=4, pady=12)

        # Show Border Button
        self.btn_show_border = ctk.CTkButton(
            self.header_frame,
            text="👁️ Çerçeveyi Göster",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#10b981",
            hover_color="#059669",
            command=self.show_visual_border,
            width=135,
            height=36,
        )
        self.btn_show_border.pack(side="left", padx=4, pady=12)

        # Palette Calibrate Button
        self.btn_calib_palette = ctk.CTkButton(
            self.header_frame,
            text="🎨 Paleti Kalibre Et",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#d97706",
            hover_color="#b45309",
            command=self.open_palette_calibration,
            width=130,
            height=36,
        )
        self.btn_calib_palette.pack(side="left", padx=3, pady=12)

        # Palette Test Button
        self.btn_test_palette = ctk.CTkButton(
            self.header_frame,
            text="🎯 Paleti Test Et",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#475569",
            hover_color="#64748b",
            command=self.test_palette_buttons,
            width=120,
            height=36,
        )
        self.btn_test_palette.pack(side="left", padx=3, pady=12)

        # Canvas Info Badge
        cx, cy, cw, ch = self.calibrator.get_bounds()
        self.lbl_canvas_badge = ctk.CTkLabel(
            self.header_frame,
            text=f"🎯 Tuval: {cw}x{ch}px (X={cx}, Y={cy})",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#94a3b8",
        )
        self.lbl_canvas_badge.pack(side="left", padx=6, pady=12)

        # Quick Calibration Buttons
        self.btn_calib = ctk.CTkButton(
            self.header_frame,
            text="📍 2 Tıkla Seç (F6)",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#0284c7",
            hover_color="#0369a1",
            command=self.open_two_click_calibration,
            width=125,
            height=36,
        )
        self.btn_calib.pack(side="right", padx=10, pady=12)

        self.btn_test_bounds = ctk.CTkButton(
            self.header_frame,
            text="📐 Sınırları Gez (F7)",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color="#1e293b",
            hover_color="#334155",
            command=self.test_canvas_bounds,
            width=130,
            height=36,
        )
        self.btn_test_bounds.pack(side="right", padx=4, pady=12)

    def _build_main_layout(self):
        """Builds dual preview areas and left/right parameter panels."""
        self.main_container = ctk.CTkFrame(self, fg_color="#0f172a")
        self.main_container.pack(fill="both", expand=True, padx=15, pady=10)

        # Left Column: Image Input & Mode Tuning (Width: 410px)
        self.left_panel = ctk.CTkScrollableFrame(
            self.main_container, width=410, fg_color="#1e293b", corner_radius=12
        )
        self.left_panel.pack(side="left", fill="y", padx=5, pady=5)

        # Center Column: Previews & Visualizers
        self.center_panel = ctk.CTkFrame(self.main_container, fg_color="#0f172a")
        self.center_panel.pack(side="left", fill="both", expand=True, padx=10, pady=5)

        # Bottom Panel: Drawing Execution HUD
        self._build_drawing_hud()

        # Populate Left Panel
        self._build_input_tabs(self.left_panel)
        self._build_algorithm_controls(self.left_panel)

        # Populate Center Panel
        self._build_preview_canvas(self.center_panel)

    def _build_input_tabs(self, parent):
        """Tabs for loading images: File, Clipboard, Web Search, URL, Presets."""
        tabview = ctk.CTkTabview(parent, fg_color="#0f172a", corner_radius=10)
        tabview.pack(fill="x", padx=5, pady=5)

        tab_quick = tabview.add("⚡ Hızlı Giriş")
        tab_search = tabview.add("🌐 Web Arama")
        tab_presets = tabview.add("🎨 Şablonlar")

        btn_clipboard = ctk.CTkButton(
            tab_quick,
            text="📋 Panodan Yapıştır (Ctrl+V)",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            fg_color="#10b981",
            hover_color="#059669",
            command=self.paste_from_clipboard,
            height=40,
        )
        btn_clipboard.pack(fill="x", padx=10, pady=6)

        btn_file = ctk.CTkButton(
            tab_quick,
            text="📁 Bilgisayardan Resim Seç...",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            fg_color="#334155",
            hover_color="#475569",
            command=self.browse_file,
            height=36,
        )
        btn_file.pack(fill="x", padx=10, pady=4)

        url_frame = ctk.CTkFrame(tab_quick, fg_color="transparent")
        url_frame.pack(fill="x", padx=10, pady=6)

        self.entry_url = ctk.CTkEntry(
            url_frame, placeholder_text="Resim Web URL adresi..."
        )
        self.entry_url.pack(side="left", fill="x", expand=True, padx=(0, 5))

        btn_load_url = ctk.CTkButton(
            url_frame,
            text="İndir",
            width=60,
            command=self.load_from_url,
            fg_color="#0284c7",
        )
        btn_load_url.pack(side="left")

        search_frame = ctk.CTkFrame(tab_search, fg_color="transparent")
        search_frame.pack(fill="x", padx=10, pady=6)

        self.entry_search = ctk.CTkEntry(
            search_frame, placeholder_text="Örn: Pikachu, Mona Lisa, Ferrari..."
        )
        self.entry_search.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.entry_search.bind("<Return>", lambda e: self.execute_web_search())

        btn_do_search = ctk.CTkButton(
            search_frame,
            text="Ara",
            width=60,
            command=self.execute_web_search,
            fg_color="#0284c7",
        )
        btn_do_search.pack(side="left")

        self.search_results_frame = ctk.CTkScrollableFrame(
            tab_search, height=130, fg_color="#1e293b"
        )
        self.search_results_frame.pack(fill="x", padx=10, pady=5)

        for name in ImageSearchEngine.PRESETS.keys():
            b = ctk.CTkButton(
                tab_presets,
                text=name,
                fg_color="#1e293b",
                hover_color="#334155",
                anchor="w",
                command=lambda n=name: self.load_preset(n),
                height=32,
            )
            b.pack(fill="x", padx=10, pady=2)

    def _build_algorithm_controls(self, parent):
        """Controls for Drawing Modes, Contrast, Brightness, Background Cleaning, Speed."""
        box = ctk.CTkFrame(parent, fg_color="#0f172a", corner_radius=10)
        box.pack(fill="x", padx=5, pady=8)

        lbl = ctk.CTkLabel(
            box,
            text="⚙️ Çizim & Filtre Ayarları",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color="#38bdf8",
        )
        lbl.pack(anchor="w", padx=12, pady=(10, 5))

        # ONE-CLICK ULTRA MAX PRO QUALITY PRESET BUTTON
        btn_ultra_max = ctk.CTkButton(
            box,
            text="👑 ULTRA MAX PRO KALİTE (En İnce Hat & Canlı Ten)",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color="#8b5cf6",
            hover_color="#7c3aed",
            command=self.apply_ultra_max_quality,
            height=38,
        )
        btn_ultra_max.pack(fill="x", padx=12, pady=(6, 8))

        # Mode Selector (Default to REALISTIC_COLOR)
        ctk.CTkLabel(box, text="Çizim Modu / Algoritma:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=12, pady=(4, 2))
        self.mode_selector = ctk.CTkOptionMenu(
            box,
            values=[
                DrawingMode.REALISTIC_COLOR,
                DrawingMode.ATKINSON_PHOTOREAL,
                DrawingMode.FLOYD_STEINBERG,
                DrawingMode.VECTOR_CONTOUR,
                DrawingMode.CROSS_HATCH,
            ],
            command=lambda v: self.reprocess_image_async(),
            fg_color="#0284c7",
            button_color="#0369a1",
        )
        self.mode_selector.set(self.settings.get("mode", DrawingMode.REALISTIC_COLOR))
        self.mode_selector.pack(fill="x", padx=12, pady=4)

        # Clean Dark Background Switch (Key for dark room / Discord screenshots!)
        self.switch_clean_bg = ctk.CTkSwitch(
            box,
            text="🧹 Koyu Arka Planı Temizle (Yalnızca Yüz)",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#38bdf8",
            command=self.reprocess_image_async,
        )
        if self.settings.get("remove_dark_bg", True):
            self.switch_clean_bg.select()
        self.switch_clean_bg.pack(anchor="w", padx=12, pady=(8, 4))

        # Contour Reinforcement Switch (Vector Line-Art Details)
        self.switch_reinforce = ctk.CTkSwitch(
            box,
            text="✍️ Keskin Vektör Hatları Ekle (En İnce Kalem)",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#10b981",
            command=self.reprocess_image_async,
        )
        if self.settings.get("enable_contour_reinforce", True):
            self.switch_reinforce.select()
        self.switch_reinforce.pack(anchor="w", padx=12, pady=(4, 4))

        # Auto Select Pen Tool Switch
        self.switch_auto_pen = ctk.CTkSwitch(
            box,
            text="🖌️ Otomatik Kalem Aracını Seç (Gartic Pen)",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#f59e0b",
        )
        if self.settings.get("auto_select_pen", True):
            self.switch_auto_pen.select()
        self.switch_auto_pen.pack(anchor="w", padx=12, pady=(4, 6))

        # Dark Background Threshold Slider
        ctk.CTkLabel(box, text="Arka Plan Temizleme Eşiği:", font=ctk.CTkFont(size=11)).pack(anchor="w", padx=12, pady=(2, 0))
        self.slider_dark_thresh = ctk.CTkSlider(
            box, from_=10, to=80, number_of_steps=35, command=lambda v: self.reprocess_image_async()
        )
        self.slider_dark_thresh.set(self.settings.get("dark_thresh", 35))
        self.slider_dark_thresh.pack(fill="x", padx=12, pady=2)

        # Contrast Slider
        ctk.CTkLabel(box, text="Kontrast (Derinlik):", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=12, pady=(6, 0))
        self.slider_contrast = ctk.CTkSlider(
            box, from_=0.5, to=2.5, number_of_steps=20, command=lambda v: self.reprocess_image_async()
        )
        self.slider_contrast.set(self.settings.get("contrast", 1.30))
        self.slider_contrast.pack(fill="x", padx=12, pady=2)

        # Saturation Slider (Skin tone and vibrancy boost)
        ctk.CTkLabel(box, text="Doygunluk (Ten & Canlı Renkler):", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=12, pady=(4, 0))
        self.slider_saturation = ctk.CTkSlider(
            box, from_=0.5, to=2.5, number_of_steps=20, command=lambda v: self.reprocess_image_async()
        )
        self.slider_saturation.set(self.settings.get("saturation", 1.35))
        self.slider_saturation.pack(fill="x", padx=12, pady=2)

        # Brightness Slider
        ctk.CTkLabel(box, text="Parlaklık:", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=12, pady=(4, 0))
        self.slider_brightness = ctk.CTkSlider(
            box, from_=0.5, to=1.8, number_of_steps=20, command=lambda v: self.reprocess_image_async()
        )
        self.slider_brightness.set(self.settings.get("brightness", 1.05))
        self.slider_brightness.pack(fill="x", padx=12, pady=2)

        # Sharpness Slider
        ctk.CTkLabel(box, text="Keskinlik:", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=12, pady=(4, 0))
        self.slider_sharpness = ctk.CTkSlider(
            box, from_=0.5, to=3.0, number_of_steps=25, command=lambda v: self.reprocess_image_async()
        )
        self.slider_sharpness.set(self.settings.get("sharpness", 1.6))
        self.slider_sharpness.pack(fill="x", padx=12, pady=2)

        # Resolution / Detail Slider
        ctk.CTkLabel(box, text="Detay / Çözünürlük Ölçeği (px):", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=12, pady=(4, 0))
        self.slider_max_dim = ctk.CTkSlider(
            box, from_=180, to=500, number_of_steps=32, command=lambda v: self.reprocess_image_async()
        )
        self.slider_max_dim.set(self.settings.get("max_dim", 360))
        self.slider_max_dim.pack(fill="x", padx=12, pady=2)

        # Invert Switch
        self.switch_invert = ctk.CTkSwitch(
            box,
            text="Renkleri Ters Çevir (Negatif)",
            font=ctk.CTkFont(size=12),
            command=self.reprocess_image_async,
        )
        if self.settings.get("invert", False):
            self.switch_invert.select()
        self.switch_invert.pack(anchor="w", padx=12, pady=6)

        # Drawing Speed Option
        ctk.CTkLabel(box, text="Çizim Hızı:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=12, pady=(4, 2))
        self.speed_selector = ctk.CTkOptionMenu(
            box,
            values=[
                "Gartic Phone Standart (1.8ms - Önerilen)",
                "Ultra Hızlı (0.8ms)",
                "Güvenli & Yavaş (3.5ms)",
            ],
            command=lambda v: self._update_speed_settings(),
            fg_color="#334155",
            button_color="#475569",
        )
        self.speed_selector.set(self.settings.get("speed", "Gartic Phone Standart (1.8ms - Önerilen)"))
        self.speed_selector.pack(fill="x", padx=12, pady=4)
        self._update_speed_settings()

    def _update_speed_settings(self):
        speed_str = self.speed_selector.get()
        if "0.8ms" in speed_str:
            self.active_p_delay = 0.0008
            self.active_s_delay = 0.002
        elif "3.5ms" in speed_str:
            self.active_p_delay = 0.0035
            self.active_s_delay = 0.006
        else:
            self.active_p_delay = 0.0018
            self.active_s_delay = 0.004

    def _build_preview_canvas(self, parent):
        """Side-by-side or stacked dual previews: Original vs Gartic Render."""
        preview_container = ctk.CTkFrame(parent, fg_color="#1e293b", corner_radius=12)
        preview_container.pack(fill="both", expand=True, padx=5, pady=5)

        title_frame = ctk.CTkFrame(preview_container, fg_color="transparent")
        title_frame.pack(fill="x", padx=15, pady=8)

        lbl_orig = ctk.CTkLabel(
            title_frame,
            text="📷 Kaynak Görsel",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color="#94a3b8",
        )
        lbl_orig.pack(side="left", padx=10)

        lbl_sim = ctk.CTkLabel(
            title_frame,
            text="🎨 Gartic Phone Renkli Tuval Simülasyonu (Birebir Çizilecek Şekil)",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color="#38bdf8",
        )
        lbl_sim.pack(side="right", padx=10)

        self.preview_splits = ctk.CTkFrame(preview_container, fg_color="transparent")
        self.preview_splits.pack(fill="both", expand=True, padx=10, pady=5)

        self.canvas_orig = ctk.CTkLabel(
            self.preview_splits,
            text="Resim Yükleniyor...",
            fg_color="#0f172a",
            corner_radius=8,
        )
        self.canvas_orig.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.canvas_sim = ctk.CTkLabel(
            self.preview_splits,
            text="Önizleme Hesaplanıyor...",
            fg_color="#0f172a",
            corner_radius=8,
        )
        self.canvas_sim.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        self.stats_bar = ctk.CTkFrame(preview_container, fg_color="#0f172a", height=38, corner_radius=8)
        self.stats_bar.pack(fill="x", padx=10, pady=(5, 10))

        self.lbl_stats = ctk.CTkLabel(
            self.stats_bar,
            text="📊 Çizgi: 0 | Nokta: 0 | Tahmini Süre: 0.0 sn",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#38bdf8",
        )
        self.lbl_stats.pack(side="left", padx=15, pady=6)

        self.lbl_round_warn = ctk.CTkLabel(
            self.stats_bar,
            text="⚡ Gartic Phone için Hazır",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#10b981",
        )
        self.lbl_round_warn.pack(side="right", padx=15, pady=6)

    def _build_drawing_hud(self):
        """Bottom Control Bar with Large Start, Pause, Stop buttons & Progress bar."""
        self.hud_frame = ctk.CTkFrame(self, height=80, fg_color="#0b1120", corner_radius=0)
        self.hud_frame.pack(fill="x", side="bottom", padx=0, pady=0)

        self.btn_start = ctk.CTkButton(
            self.hud_frame,
            text="🚀 ÇİZMEYE BAŞLA (F8)",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            fg_color="#10b981",
            hover_color="#059669",
            command=self._start_drawing_with_countdown,
            width=220,
            height=50,
            corner_radius=10,
        )
        self.btn_start.pack(side="left", padx=20, pady=15)

        self.btn_pause = ctk.CTkButton(
            self.hud_frame,
            text="⏸️ DURAKLAT (F9)",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            fg_color="#f59e0b",
            hover_color="#d97706",
            command=self.mouse_ctrl.toggle_pause,
            width=160,
            height=50,
            corner_radius=10,
        )
        self.btn_pause.pack(side="left", padx=10, pady=15)

        self.btn_stop = ctk.CTkButton(
            self.hud_frame,
            text="🛑 ACİL DURDUR (F10 / ESC)",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            fg_color="#ef4444",
            hover_color="#dc2626",
            command=self.emergency_stop,
            width=220,
            height=50,
            corner_radius=10,
        )
        self.btn_stop.pack(side="left", padx=10, pady=15)

        prog_frame = ctk.CTkFrame(self.hud_frame, fg_color="transparent")
        prog_frame.pack(side="right", fill="both", expand=True, padx=20, pady=12)

        self.lbl_progress_status = ctk.CTkLabel(
            prog_frame,
            text="Hazır (F8 tuşuna basarak veya butona tıklayarak çizin)",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#94a3b8",
            anchor="w",
        )
        self.lbl_progress_status.pack(fill="x", pady=(2, 4))

        self.progress_bar = ctk.CTkProgressBar(
            prog_frame, height=14, progress_color="#38bdf8", fg_color="#1e293b"
        )
        self.progress_bar.set(0.0)
        self.progress_bar.pack(fill="x", pady=2)

    # ================= LOGIC & ACTIONS =================

    def one_click_2k_setup(self):
        """
        One-click complete setup: configures centered 2K canvas, realistic color mode,
        synchronizes 18 palette buttons, background cleaning, and displays the visual border.
        """
        self.calibrator.set_2k_preset()
        cx, cy, cw, ch = self.calibrator.get_bounds()
        self.lbl_canvas_badge.configure(text=f"🎯 Tuval: {cw}x{ch}px (X={cx}, Y={cy})")
        self.img_engine.palette_mgr.calibrate_relative_to_canvas(cx, cy, cw, ch)

        # Set best photoreal color settings
        self.mode_selector.set(DrawingMode.REALISTIC_COLOR)
        self.slider_contrast.set(1.30)
        self.slider_brightness.set(1.05)
        self.slider_sharpness.set(1.50)
        if hasattr(self, "slider_saturation"):
            self.slider_saturation.set(1.35)
        self.slider_max_dim.set(360)
        self.switch_clean_bg.select()
        self.slider_dark_thresh.set(40)
        self.speed_selector.set("Gartic Phone Standart (1.8ms - Önerilen)")
        self._update_speed_settings()
        self._save_settings()

        self.lbl_progress_status.configure(
            text="⚡ 2K Gartic Phone 18 Renk Paleti ve Tuval Kusursuz Ayarlandı!",
            text_color="#10b981",
        )
        self.reprocess_image_async()
        self.show_visual_border()

    def show_visual_border(self):
        """Displays floating neon-green rectangle directly over the canvas on screen."""
        cx, cy, cw, ch = self.calibrator.get_bounds()
        self.visual_border.show_border(cx, cy, cw, ch, duration_sec=4.0)

    def open_palette_calibration(self):
        """Guides user to calibrate the 18-color palette in 2 clicks (Black + Peach)."""
        self.lbl_progress_status.configure(
            text="🎨 Renk Paleti Kalibrasyonu: Siyah renge gidip F6 / Boşluk basın!",
            text_color="#c084fc",
        )
        calib = PaletteTwoClickCalibrator(
            self,
            self.mouse_ctrl,
            self.img_engine.palette_mgr,
            on_success=self._on_palette_calibrated,
        )
        calib.start()

    def _on_palette_calibrated(self):
        self._save_settings()
        self.lbl_progress_status.configure(
            text="✅ Gartic Phone 18 Renk Paleti Kusursuz Kalibre Edildi ve Kaydedildi!",
            text_color="#10b981",
        )
        try:
            winsound.Beep(2000, 250)
        except Exception:
            pass

    def test_palette_buttons(self):
        """
        Visually moves the mouse cursor over each of the 18 Gartic Phone palette buttons
        so the user can immediately see with their own eyes that the bot points directly
        to every single color button without clicking them!
        """
        from core.gartic_palette import GARTIC_PALETTE_GRID, GARTIC_COLOR_NAMES_TR

        def _worker():
            self.lbl_progress_status.configure(
                text="🎨 Palet düğmeleri test ediliyor... Fareyi izleyin!",
                text_color="#c084fc",
            )
            for r in range(6):
                for c in range(3):
                    name, _ = GARTIC_PALETTE_GRID[r][c]
                    coord = self.img_engine.palette_mgr.get_color_coord(name)
                    tr_name = GARTIC_COLOR_NAMES_TR.get(name, name)
                    if coord:
                        self.mouse_ctrl.set_cursor_pos(coord[0], coord[1])
                        self.lbl_progress_status.configure(
                            text=f"🎯 Düğme: {tr_name} -> ({coord[0]}, {coord[1]})",
                            text_color="#38bdf8",
                        )
                        time.sleep(0.2)
            self.lbl_progress_status.configure(
                text="✅ Palet testi tamamlandı! 18 düğmenin hepsi doğru noktada.",
                text_color="#10b981",
            )
        threading.Thread(target=_worker, daemon=True).start()

    def toggle_monitor_placement(self):
        """Switches window between Monitor 1 and Monitor 2 cleanly."""
        try:
            monitors = win32api.EnumDisplayMonitors()
            if len(monitors) <= 1:
                self.btn_monitor2.configure(text="ℹ️ Tek Monitör Algılandı")
                return

            primary_rect = None
            secondary_rect = None
            for h, d, rect in monitors:
                info = win32api.GetMonitorInfo(h)
                if info["Flags"] & win32con.MONITORINFOF_PRIMARY:
                    primary_rect = rect
                else:
                    secondary_rect = rect

            if not secondary_rect:
                secondary_rect = monitors[1][2]
            if not primary_rect:
                primary_rect = monitors[0][2]

            cur_x = self.winfo_x()

            if secondary_rect[0] <= cur_x <= secondary_rect[2]:
                target = primary_rect
                target_name = "1. Monitöre"
                btn_next = "🖥️ 2. Monitöre Taşı"
            else:
                target = secondary_rect
                target_name = "2. Monitöre"
                btn_next = "🖥️ 1. Monitöre Taşı"

            m_left, m_top, m_right, m_bottom = target
            m_width = m_right - m_left
            m_height = m_bottom - m_top

            w = min(1380, m_width - 60)
            h = min(880, m_height - 60)
            pos_x = m_left + (m_width - w) // 2
            pos_y = m_top + (m_height - h) // 2

            self.geometry(f"{w}x{h}+{pos_x}+{pos_y}")
            self.btn_monitor2.configure(text=btn_next)
            self.lbl_progress_status.configure(
                text=f"Pencere başarıyla {target_name} taşındı!", text_color="#10b981"
            )
        except Exception as e:
            print(f"Monitör taşıma hatası: {e}")

    def paste_from_clipboard(self):
        """Pastes image from Windows clipboard."""
        img = self.search_engine.get_from_clipboard()
        if img:
            self.set_active_image(img)
            self.lbl_progress_status.configure(
                text="📋 Panodan resim başarıyla yapıştırıldı!", text_color="#10b981"
            )
        else:
            self.lbl_progress_status.configure(
                text="⚠️ Panoda görsel bulunamadı. Önce bir resmi kopyalayın!",
                text_color="#f59e0b",
            )

    def browse_file(self):
        """Opens file dialog for local images."""
        from tkinter import filedialog

        path = filedialog.askopenfilename(
            title="Çizilecek Resmi Seçin",
            filetypes=[
                (
                    "Tüm Resim Formatları",
                    "*.png *.jpg *.jpeg *.webp *.bmp *.gif",
                ),
                ("PNG Dosyaları", "*.png"),
                ("JPEG Dosyaları", "*.jpg *.jpeg"),
            ],
        )
        if path:
            try:
                raw_img = Image.open(path)
                img = self.search_engine.ensure_rgb_white_bg(raw_img)
                self.set_active_image(img)
            except Exception as e:
                self.lbl_progress_status.configure(
                    text=f"Dosya açılamadı: {e}", text_color="#ef4444"
                )

    def load_from_url(self):
        """Downloads image from direct web URL."""
        url = self.entry_url.get().strip()
        if not url:
            return
        self.lbl_progress_status.configure(text="🌐 URL'den indiriliyor...", text_color="#38bdf8")

        def _worker():
            img = self.search_engine.download_from_url(url)
            if img:
                self.after(0, lambda: self.set_active_image(img))
                self.after(0, lambda: self.lbl_progress_status.configure(text="✅ Görsel yüklendi!", text_color="#10b981"))
            else:
                self.after(0, lambda: self.lbl_progress_status.configure(text="❌ İndirme başarısız oldu!", text_color="#ef4444"))

        threading.Thread(target=_worker, daemon=True).start()

    def execute_web_search(self):
        """Searches Wikimedia Commons for the query and presents thumbnail choices."""
        query = self.entry_search.get().strip()
        if not query:
            return

        for widget in self.search_results_frame.winfo_children():
            try:
                widget.destroy()
            except Exception:
                pass

        loading_lbl = ctk.CTkLabel(
            self.search_results_frame, text="🔍 Aranıyor...", text_color="#94a3b8"
        )
        loading_lbl.pack(pady=10)

        def _worker():
            results = self.search_engine.search_wikimedia(query, limit=6)

            def _populate():
                try:
                    loading_lbl.destroy()
                except Exception:
                    pass

                if not results:
                    ctk.CTkLabel(
                        self.search_results_frame, text="Sonuç bulunamadı."
                    ).pack(pady=5)
                    return

                for item in results:
                    btn = ctk.CTkButton(
                        self.search_results_frame,
                        text=f"🖼️ {item['title'][:28]}...",
                        fg_color="#0f172a",
                        hover_color="#334155",
                        anchor="w",
                        command=lambda u=item["url"]: self._download_and_set(u),
                        height=28,
                    )
                    btn.pack(fill="x", padx=2, pady=2)

            self.after(0, _populate)

        threading.Thread(target=_worker, daemon=True).start()

    def _download_and_set(self, url: str):
        def _worker():
            img = self.search_engine.download_from_url(url)
            if img:
                self.after(0, lambda: self.set_active_image(img))

        threading.Thread(target=_worker, daemon=True).start()

    def load_preset(self, name: str):
        url = ImageSearchEngine.PRESETS.get(name)
        if url:
            self._download_and_set(url)

    def set_active_image(self, image: Image.Image):
        """Sets current image and triggers async processing pipeline."""
        self.current_image = image
        self._update_original_preview(image)
        self.reprocess_image_async()

    def _update_original_preview(self, img: Image.Image):
        w, h = img.size
        scale = min(360 / float(w), 320 / float(h), 1.0)
        disp_w = max(1, int(w * scale))
        disp_h = max(1, int(h * scale))
        preview_thumb = img.resize((disp_w, disp_h), Image.Resampling.LANCZOS)
        ctk_img = ctk.CTkImage(light_image=preview_thumb, dark_image=preview_thumb, size=(disp_w, disp_h))
        self.canvas_orig.configure(image=ctk_img, text="")
        self.canvas_orig.image = ctk_img

    def apply_ultra_max_quality(self):
        """One-click applies the absolute best settings: ultra resolution, crisp lineart, radiant skin tones."""
        self.mode_selector.set(DrawingMode.REALISTIC_COLOR)
        self.slider_max_dim.set(480)
        self.slider_contrast.set(1.35)
        self.slider_saturation.set(1.45)
        self.slider_sharpness.set(1.85)
        self.slider_brightness.set(1.05)
        self.slider_dark_thresh.set(65)
        if not self.switch_clean_bg.get():
            self.switch_clean_bg.select()
        if hasattr(self, "switch_reinforce") and not self.switch_reinforce.get():
            self.switch_reinforce.select()
        self.reprocess_image_async()
        self.lbl_progress_status.configure(
            text="👑 ULTRA MAX PRO KALİTE AKTİF! 480px çözünürlük, en ince hatlar ve canlı ten renkleri ayarlandı.",
            text_color="#10b981",
        )

    def reprocess_image_async(self):
        """Runs the vision pipeline in a background thread without blocking UI."""
        if self.current_image is None or self.is_processing:
            return

        self.is_processing = True
        self.lbl_progress_status.configure(text="🔄 Görsel renklendiriliyor ve optimize ediliyor...", text_color="#38bdf8")

        mode = self.mode_selector.get()
        contrast = float(self.slider_contrast.get())
        brightness = float(self.slider_brightness.get())
        sharpness = float(self.slider_sharpness.get())
        saturation = float(self.slider_saturation.get()) if hasattr(self, "slider_saturation") else 1.35
        max_dim = int(self.slider_max_dim.get())
        invert = bool(self.switch_invert.get())
        remove_dark_bg = bool(self.switch_clean_bg.get())
        dark_thresh = int(self.slider_dark_thresh.get())
        reinforce = bool(self.switch_reinforce.get()) if hasattr(self, "switch_reinforce") else True

        p_delay = self.active_p_delay
        s_delay = self.active_s_delay

        def _worker():
            try:
                strokes, colors, preview_pil = self.img_engine.process_image(
                    self.current_image,
                    mode=mode,
                    contrast=contrast,
                    brightness=brightness,
                    sharpness=sharpness,
                    saturation=saturation,
                    invert=invert,
                    max_dim=max_dim,
                    remove_dark_bg=remove_dark_bg,
                    dark_thresh=dark_thresh,
                    enable_contour_reinforce=reinforce,
                )

                total_pts = sum(len(s) for s in strokes)
                est_time = ImageProcessingEngine.calculate_estimated_time(
                    len(strokes), total_pts, point_delay=p_delay, stroke_delay=s_delay
                )

                def _apply():
                    self.processed_strokes = strokes
                    self.stroke_colors = colors
                    self.preview_image = preview_pil

                    pw, ph = preview_pil.size
                    scale = min(360 / float(pw), 320 / float(ph), 1.0)
                    dw = max(1, int(pw * scale))
                    dh = max(1, int(ph * scale))
                    p_thumb = preview_pil.resize((dw, dh), Image.Resampling.LANCZOS)
                    ctk_p = ctk.CTkImage(light_image=p_thumb, dark_image=p_thumb, size=(dw, dh))
                    self.canvas_sim.configure(image=ctk_p, text="")
                    self.canvas_sim.image = ctk_p

                    # Count unique colors
                    unique_c = len(set(colors)) if colors else 1
                    self.lbl_stats.configure(
                        text=f"📊 Çizgi: {len(strokes):,} | Renk Sayısı: {unique_c} | Tahmini Süre: {est_time} sn"
                    )

                    if est_time <= 75.0:
                        self.lbl_round_warn.configure(
                            text=f"✅ Gartic Rounduna Uygun ({est_time}s < 80s)",
                            text_color="#10b981",
                        )
                    else:
                        self.lbl_round_warn.configure(
                            text=f"⚠️ Süre Biraz Uzun ({est_time}s) - Detayı düşürebilirsiniz",
                            text_color="#f59e0b",
                        )

                    self.lbl_progress_status.configure(
                        text=f"Hazır! Toplam {len(strokes):,} çizgi ({unique_c} renk) optimize edildi.",
                        text_color="#38bdf8",
                    )
                    self.is_processing = False

                self.after(0, _apply)
            except Exception as e:
                print(f"İşleme hatası: {e}")
                self.is_processing = False

        threading.Thread(target=_worker, daemon=True).start()

    # ================= CALIBRATION & DRAWING =================

    def open_two_click_calibration(self):
        """Starts 2-click guided calibration banner."""
        self.lbl_progress_status.configure(
            text="📍 2-Tık Tuval Kalibrasyonu: Sol-Üst köşeye gidip F6 / Boşluk basın!",
            text_color="#38bdf8",
        )
        picker = TwoClickCalibrator(self, self.mouse_ctrl, on_success=self._on_canvas_selected)
        picker.start()

    def _on_canvas_selected(self, x: int, y: int, w: int, h: int):
        self.calibrator.set_bounds(x, y, w, h)
        self.img_engine.palette_mgr.calibrate_relative_to_canvas(x, y, w, h)
        self.lbl_canvas_badge.configure(text=f"🎯 Tuval: {w}x{h}px (X={x}, Y={y})")
        self._save_settings()
        self.lbl_progress_status.configure(
            text=f"✅ Tuval & 18 Renk Paleti ayarlandı: {w}x{h} px (X={x}, Y={y})! Yeşil çerçeve gösteriliyor...",
            text_color="#10b981",
        )
        self.show_visual_border()

    def test_canvas_bounds(self):
        """Visually traces the boundary of the canvas with the mouse."""
        cx, cy, cw, ch = self.calibrator.get_bounds()
        self.lbl_progress_status.configure(
            text=f"📐 Tuval sınırları geziliyor ({cw}x{ch}px)... Fareyi izleyin!",
            text_color="#38bdf8",
        )
        self.calibrator.test_canvas_bounds_visual(speed_delay=0.003)

    def test_palette_buttons(self):
        """Visually hovers across all 18 color buttons to demonstrate exact calibration."""
        def _worker():
            self.lbl_progress_status.configure(
                text="🎨 18 Renk Paleti test ediliyor... Fareyi izleyin!",
                text_color="#38bdf8",
            )
            for name, coord in self.img_engine.palette_mgr.color_coords.items():
                if self.mouse_ctrl.should_abort:
                    break
                self.mouse_ctrl.set_cursor_pos(coord[0], coord[1])
                msg = f"🎨 Renk: {name} ({coord[0]}, {coord[1]})"
                self.after(0, lambda m=msg: self.lbl_progress_status.configure(text=m, text_color="#38bdf8"))
                time.sleep(0.18)
            self.after(0, lambda: self.lbl_progress_status.configure(
                text="✅ 18 Renk Paleti testi tamamlandı! Tüm butonlar tam merkezde.",
                text_color="#10b981",
            ))
        threading.Thread(target=_worker, daemon=True).start()

    def _start_drawing_with_countdown(self):
        """
        Provides a 3-second audible/visual countdown, activates browser focus, and starts drawing.
        """
        if not self.processed_strokes or len(self.processed_strokes) == 0:
            self.lbl_progress_status.configure(
                text="⚠️ Çizilecek resim bulunamadı! Önce bir görsel yükleyin.",
                text_color="#f59e0b",
            )
            return

        if self.mouse_ctrl.is_drawing or self.is_counting_down:
            return

        self.is_counting_down = True
        self.btn_start.configure(state="disabled")

        def _countdown_worker():
            for sec in [3, 2, 1]:
                if self.mouse_ctrl.should_abort:
                    self.is_counting_down = False
                    self.after(0, lambda: self.btn_start.configure(state="normal"))
                    return
                try:
                    winsound.Beep(900 + (3 - sec) * 200, 120)
                except Exception:
                    pass
                msg = f"⏳ {sec} SANİYE İÇİNDE BAŞLIYOR! (Gartic tuvaline bakın...)"
                self.after(0, lambda m=msg: self.lbl_progress_status.configure(text=m, text_color="#f59e0b"))
                time.sleep(1.0)

            # Final start sound
            try:
                winsound.Beep(1500, 200)
            except Exception:
                pass

            self.is_counting_down = False
            self._execute_drawing_now()

        threading.Thread(target=_countdown_worker, daemon=True).start()

    def _execute_drawing_now(self):
        """Executes actual stroke drawing on canvas with palette color switching."""
        cx, cy, cw, ch = self.calibrator.get_bounds()
        src_w, src_h = self.preview_image.size if self.preview_image else (400, 400)

        mapped_strokes = PathOptimizer.map_strokes_to_canvas(
            self.processed_strokes,
            src_w=src_w,
            src_h=src_h,
            canvas_x=cx,
            canvas_y=cy,
            canvas_w=cw,
            canvas_h=ch,
            preserve_aspect=True,
            padding=10,
        )

        self.progress_bar.set(0.0)

        # Color selector callback for Gartic Phone palette
        def _color_cb(color_name: str):
            coord = self.img_engine.palette_mgr.get_color_coord(color_name)
            if coord:
                self.mouse_ctrl.set_cursor_pos(coord[0], coord[1])
                time.sleep(0.02)
                self.mouse_ctrl.mouse_down()
                time.sleep(0.04)
                self.mouse_ctrl.mouse_up()
                time.sleep(0.05)

        # Auto-select Pen tool on Gartic Phone right toolbar if enabled
        if hasattr(self, "switch_auto_pen") and self.switch_auto_pen.get():
            pen_x = int(cx + cw + (ch * 0.52))
            pen_y = int(cy + (ch * 0.1694))
            self.mouse_ctrl.set_cursor_pos(pen_x, pen_y)
            time.sleep(0.02)
            self.mouse_ctrl.mouse_down()
            time.sleep(0.04)
            self.mouse_ctrl.mouse_up()
            time.sleep(0.04)

        # Pre-select first color (this also focuses browser window cleanly without marking the canvas)
        if self.stroke_colors and len(self.stroke_colors) > 0:
            _color_cb(self.stroke_colors[0])
            time.sleep(0.05)

        def _draw_worker():
            self.mouse_ctrl.draw_stroke_batches(
                mapped_strokes,
                point_delay=self.active_p_delay,
                stroke_delay=self.active_s_delay,
                interpolation_step=2,
                color_selector_cb=_color_cb,
                stroke_colors=self.stroke_colors,
            )
            self.after(0, lambda: self.btn_start.configure(state="normal"))

        self.draw_thread = threading.Thread(target=_draw_worker, daemon=True)
        self.draw_thread.start()

    def emergency_stop(self):
        """Emergency panic button: immediately aborts drawing and releases mouse."""
        self.is_counting_down = False
        self.mouse_ctrl.emergency_release()
        self.lbl_progress_status.configure(
            text="🛑 ACİL DURDURULDU! Fare serbest bırakıldı.", text_color="#ef4444"
        )
        self.btn_start.configure(state="normal")
        self.progress_bar.set(0.0)

    def _on_draw_progress(self, current: int, total: int, current_color: str):
        fraction = float(current) / float(total) if total > 0 else 0.0

        def _update():
            self.progress_bar.set(fraction)
            pct = int(fraction * 100)
            self.lbl_progress_status.configure(
                text=f"🎨 Çiziliyor (%{pct}) - Çizgi {current:,} / {total:,} [{current_color}]",
                text_color="#38bdf8",
            )

        self.after(0, _update)

    def _on_draw_state_change(self, state_text: str):
        def _update():
            if "Tamamlandı" in state_text:
                self.lbl_progress_status.configure(text=state_text, text_color="#10b981")
                self.btn_start.configure(state="normal")
                self.progress_bar.set(1.0)
            elif "Durduruldu" in state_text or "İptal" in state_text:
                self.lbl_progress_status.configure(text=state_text, text_color="#ef4444")
                self.btn_start.configure(state="normal")
            else:
                self.lbl_progress_status.configure(text=state_text, text_color="#f59e0b")

        self.after(0, _update)

    def on_closing(self):
        self._save_settings()
        self.hotkeys.stop()
        self.destroy()
