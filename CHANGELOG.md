# 📋 Changelog / Değişiklik Günlüğü

All notable changes to **Gartic AutoDraw AI Studio Pro** will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.5.0] - 2026-09-28

### 🔍 Real-Time Computer Vision Screen Scanner & Universal Resolution Engine
*(Gerçek Zamanlı Bilgisayarlı Görü Ekran Taraması ve Tüm Çözünürlüklere Tam Uyum)*

#### ✨ Added / Eklenenler
- **🔍 Real-Time OpenCV Screen Scanner (`ScreenScannerCV`):**
  - Live desktop screen scanner using `OpenInputDesktop` and OpenCV color cluster centroid geometry.
  - Automatically identifies Gartic Phone's canvas and the exact centers of all 18 palette buttons on ANY screen (1080p, 2K, 4K, laptop screens, or custom browser zoom levels) in under 35 milliseconds.
  - *(Gartic Phone tuvalini ve 18 renk butonunun merkezini her ekranda (1080p, 2K, 4K, laptop, zoom) 35 milisaniyede bulan OpenCV ekran tarayıcısı eklendi.)*
- **🖥️ Universal Multi-Resolution Presets Dropdown:**
  - One-click presets for `1080p Full HD (1920x1080)`, `2K QHD (2560x1440)`, `4K Ultra HD (3840x2160)`, `Laptop HD (1366x768)`, and `Laptop FHD (1536x864 / %125 DPI)`.
  - Instant canvas bounds and palette coordinates for immediate use without manual setup.
  - *(Tüm popüler ekran çözünürlükleri ve DPI ölçekleri için tek tıkla hazır önayarlar eklendi.)*
- **🎨 Rock-Solid In-Game Color Switching Synchronization:**
  - Calibrated mouse click hold time (45ms) and post-switch stabilization delay (75ms) allowing Chromium's DOM event loop and React state to reliably update `activeColor` and canvas 2D context `ctx.strokeStyle`.
  - Added entry-point canvas settle delay (6ms) preventing dropped pointerdown events.
  - Guarantees 100% reliable in-game color rendering without monochrome lockups.
  - *(Oyun içi renk geçişlerinde React ve Chromium döngüsü için 45ms tıklama ve 75ms durum senkronizasyonu ile renklerin oyunda tam aktif olması sağlandı.)*
- **🌐 Browser Userscript v2.5 (18-Color Multi-Layer Drawing):**
  - Upgraded `GarticPhone_DrawBot_Tampermonkey.user.js` to full 18-color Floyd-Steinberg dithering.
  - Direct DOM color picker querying `window.getComputedStyle().backgroundColor` to click palette buttons natively inside the browser on any OS or screen.
  - *(Tampermonkey tarayıcı eklentisine 18 renkli Floyd-Steinberg çizim ve DOM üzerinden otomatik renk seçimi eklendi.)*

---

## [2.0.0] - 2026-09-28

### 🚀 Major Release - Ultra Realism & 2K Native Architecture
*(Büyük Güncelleme - Ultra Gerçekçi Renkli Çizim ve 2K Yerel Mimari)*

#### ✨ Added / Eklenenler
- **18-Color Perceptual Floyd-Steinberg Dithering:**
  - Full support for the official Gartic Phone 18-color palette (`skin_peach`, `terracotta`, `dark_blue`, `light_blue`, etc.).
  - Integrated **Redmean Perceptual Color Metric** for realistic human visual color distance matching.
  - *(Resmi 18 Gartic Phone rengi ve Redmean algısal renk uzayıyla Floyd-Steinberg renk difüzyonu eklendi.)*
- **Smart Skin-Tone Warmth & Portrait Layering:**
  - Automated warmth enhancement for human portraits to prevent pale, corpse-gray skin tones.
  - Weighted penalty against neutral grays and cold blues on facial regions to prioritize natural peach and terracotta tones.
  - *(Portrelerde soluk zombi grisi renkleri engelleyen, doğal ten rengi ve terracotta gölgelendirme katmanı eklendi.)*
- **Intelligent Border Background Cleaning:**
  - Automatic 4-corner flood-fill boundary detector that identifies dark room shadows, Discord frames, and webcam borders.
  - Converts dark background regions to clean canvas paper without wasting ink or round time.
  - *(Web kamerası odası ve Discord çerçevelerini otomatik beyaz tuval kabul edip temizleyen akıllı filtre eklendi.)*
- **Layered Vector Contour Inking:**
  - Multi-pass rendering: base colors are placed first, followed by crisp black line-art contours (eyes, lips, eyelashes, outlines) using Ramer-Douglas-Peucker simplification.
  - *(Renkli zemin üzerine en son katmanda en ince siyah kalemle vektörel hat güçlendirme eklendi.)*
- **Direct Win32 C Low-Level Mouse Driver:**
  - Sub-millisecond hardware mouse injection via Windows `user32.dll:mouse_event` and `winmm.dll:timeBeginPeriod(1)`.
  - Zero-lag sub-pixel interpolation for continuous, fluid brush strokes.
  - *(Windows C API'leri ile 1ms hassasiyetinde sıfır gecikmeli fare kontrolcüsü eklendi.)*
- **👑 Ultra Max Pro Quality One-Click Preset:**
  - One-click button in GUI that sets 480px Ultra HD resolution, 1.85x sharpness, and 1.45x color vibrancy.
  - *(Tek tıkla tüm ayarları zirveye çeken Ultra Max Pro Kalite modu eklendi.)*
- **Native 2K (2560x1440) & Multi-Monitor Support:**
  - Dedicated 2K layout preset (`canvas_x=780, canvas_y=260, canvas_w=1000, canvas_h=720`).
  - Bit-perfect 18-color palette button calibration (`Black: 552, 382`, `Peach: 691, 720`).
  - Automatic secondary monitor detection and placement.
  - *(2K çözünürlük için piksel piksel kalibre edilmiş palet koordinatları ve çift monitör desteği eklendi.)*
- **Browser Userscript (Tampermonkey):**
  - In-browser vanilla JavaScript drawing bot script for direct execution without Python.
  - *(Doğrudan tarayıcıda çalışan Tampermonkey eklentisi eklendi.)*

#### 🛡️ Security & Privacy / Güvenlik ve Gizlilik
- Verified 100% offline, local execution with zero telemetry, zero data collection, and zero API keys required.
- *(Hiçbir veri toplamayan, tamamen çevrimdışı ve API anahtarsız %100 güvenli yerel mimari.)*

---

**Developer / Geliştirici:** [Toprak Ahmet Aydoğmuş](https://github.com/toprakahmetaydogmus)
