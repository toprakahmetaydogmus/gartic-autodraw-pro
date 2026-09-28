"""
Gartic AutoDraw AI Studio Pro - Master Launcher
High-performance auto-drawing system for Gartic.io and Gartic Phone (https://garticphone.com/).
"""

import sys
import os
import io
import ctypes

# Fix Turkish Windows console encoding (CP1254 -> UTF-8)
if sys.platform.startswith("win"):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Enable Windows High DPI Awareness to guarantee pixel-perfect multi-monitor coordinate alignment
try:
    ctypes.windll.user32.SetProcessDPIAware()
except Exception:
    pass

from gui.app import GarticAutoDrawApp


def main():
    print("=" * 60)
    print("[*] GARTIC AUTODRAW AI STUDIO PRO BASLATILIYOR...")
    print("[*] Hedef Platformlar: Gartic Phone (garticphone.com) & Gartic.io")
    print("[*] Kisayol Tuslari:")
    print("   [F6]        : Tuval Alanini Sec (Ekranda surukleyin)")
    print("   [F7]        : Tuval Sinirlarini Test Et (Fare cizer)")
    print("   [F8]        : Otomatik Cizimi Baslat")
    print("   [F9]        : Duraklat / Devam Et")
    print("   [F10 / ESC] : ACIL DURDUR (Fareyi aninda birakir)")
    print("=" * 60)

    app = GarticAutoDrawApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()


if __name__ == "__main__":
    main()
