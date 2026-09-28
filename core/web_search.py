"""
Gartic AutoDraw Pro - Image Acquisition & Search Engine
Retrieves images from Windows Clipboard, direct URLs, Wikimedia Commons API, and bundled presets.
Guarantees clean RGB conversion with white background for transparent PNGs.
"""

import os
import io
from typing import List, Dict, Optional
import requests
from PIL import Image, ImageGrab


class ImageSearchEngine:
    """
    Acquires images from clipboard, direct URLs, Wikimedia Commons search, and local presets.
    """

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 GarticAutoDrawPro/1.0"
    }

    # High quality built-in preset images (royalty-free direct URLs for instant testing)
    PRESETS: Dict[str, str] = {
        "🐱 Sevimli Kedi Çizimi": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Cat03.jpg/500px-Cat03.jpg",
        "🎨 Mona Lisa Portresi": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg/500px-Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg",
        "⚡ Pikachu Anime Çizimi": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/98/International_Pok%C3%A9mon_logo.svg/500px-International_Pok%C3%A9mon_logo.svg.png",
        "🏎️ Spor Araba Silüeti": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Ferrari_F40_1.jpg/500px-Ferrari_F40_1.jpg",
        "🐺 Kurt Karakalem": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/Canis_lupus_laying.jpg/500px-Canis_lupus_laying.jpg",
        "🇹🇷 Türk Bayrağı": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b4/Flag_of_Turkey.svg/500px-Flag_of_Turkey.svg.png",
    }

    @staticmethod
    def ensure_rgb_white_bg(image: Image.Image) -> Image.Image:
        """
        Converts any PIL image (RGBA, LA, P with transparency) to RGB with a solid pure WHITE background.
        Prevents transparent PNGs from turning pitch black!
        """
        if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
            rgba = image.convert("RGBA")
            bg = Image.new("RGB", rgba.size, (255, 255, 255))
            bg.paste(rgba, mask=rgba.split()[3])
            return bg
        return image.convert("RGB")

    @staticmethod
    def get_from_clipboard() -> Optional[Image.Image]:
        """
        Grabs an image from the Windows clipboard if present.
        Supports standard bitmaps, screenshots, and copied browser images.
        """
        try:
            img = ImageGrab.grabclipboard()
            if isinstance(img, Image.Image):
                return ImageSearchEngine.ensure_rgb_white_bg(img)
            # If clipboard contains a list of file paths (e.g. copied from explorer)
            if isinstance(img, list) and len(img) > 0 and isinstance(img[0], str):
                return ImageSearchEngine.ensure_rgb_white_bg(Image.open(img[0]))
        except Exception as e:
            print(f"Pano okuma hatası: {e}")
        return None

    @staticmethod
    def download_from_url(url: str, timeout: int = 10) -> Optional[Image.Image]:
        """Downloads an image from a direct web URL."""
        try:
            resp = requests.get(url, headers=ImageSearchEngine.HEADERS, timeout=timeout)
            if resp.status_code == 200:
                img_bytes = io.BytesIO(resp.content)
                img = Image.open(img_bytes)
                return ImageSearchEngine.ensure_rgb_white_bg(img)
        except Exception as e:
            print(f"URL indirme hatası ({url}): {e}")
        return None

    @staticmethod
    def get_local_default() -> Image.Image:
        """Loads bundled local default sketch."""
        local_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "assets", "default_sketch.png"
        )
        if os.path.exists(local_path):
            try:
                return Image.open(local_path).convert("RGB")
            except Exception:
                pass
        # Fallback in-memory image
        return Image.new("RGB", (300, 300), (255, 255, 255))

    @staticmethod
    def search_wikimedia(query: str, limit: int = 6) -> List[Dict[str, str]]:
        """
        Searches Wikimedia Commons / Wikipedia for images matching query.
        Returns a list of dicts: [{"title": ..., "thumbnail": ..., "full": ...}, ...]
        No API key required!
        """
        if not query or len(query.strip()) == 0:
            return []

        url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "prop": "pageimages|extracts",
            "generator": "search",
            "gsrsearch": query.strip(),
            "gsrlimit": limit,
            "piprop": "thumbnail|original",
            "pithumbsize": 400,
        }

        results: List[Dict[str, str]] = []
        try:
            resp = requests.get(url, params=params, headers=ImageSearchEngine.HEADERS, timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                pages = data.get("query", {}).get("pages", {})
                for page in pages.values():
                    if "thumbnail" in page:
                        thumb_url = page["thumbnail"].get("source")
                        full_url = page.get("original", {}).get("source", thumb_url)
                        title = page.get("title", "Görsel")
                        results.append({
                            "title": title,
                            "thumbnail": thumb_url,
                            "url": full_url,
                        })
        except Exception as e:
            print(f"Wikimedia arama hatası: {e}")

        return results
