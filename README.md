<div align="center">

# ⚡ Gartic AutoDraw AI Studio Pro

### 🎨 Ultra-Gerçekçi, 18-Renk Palet Otomasyonlu, 2K/4K Uyumlu Gartic Phone & Gartic.io Çizim Botu

[![Python Version](https://img.shields.io/badge/Python-3.10%20|%203.11%20|%203.12%20|%203.14-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20|%2011-0078D4?style=for-the-badge&logo=windows&logoColor=white)](https://microsoft.com/windows)
[![Resolution](https://img.shields.io/badge/Display-2K%20|%204K%20|%201080p-8b5cf6?style=for-the-badge)](https://github.com/toprakahmetaydogmus)
[![License](https://img.shields.io/badge/License-MIT-10b981?style=for-the-badge)](LICENSE)
[![Author](https://img.shields.io/badge/Developer-Toprak%20Ahmet%20Aydoğmuş-f59e0b?style=for-the-badge&logo=github)](https://github.com/toprakahmetaydogmus)

<p align="center">
  <b>Gartic Phone</b> (<a href="https://garticphone.com/">garticphone.com</a>) ve <b>Gartic.io</b> için geliştirilmiş, insan eliyle çizilmiş gibi doğal katmanlı fırça darbeleri üreten, sıfır gecikmeli Win32 C sürücülü yeni nesil otomatik çizim stüdyosu.
</p>

</div>

---

## 🌟 Öne Çıkan Üstün Özellikler

* **🎨 Resmi 18 Renk Gartic Phone Paleti Desteği:**
  * Redmean algısal renk uzayında çalışan Floyd-Steinberg hata difüzyon algoritması.
  * Resmi 18 Gartic Phone rengini (`Ten Rengi #feafa8`, `Terracotta #cb5a57`, `Açık Mavi #26c9ff` vb.) kusursuz şekilde piksellerle eşleştirir.
* **👤 Akıllı Ten Rengi & Portre Katmanlama (Smart Skin Layering):**
  * Web kamerası veya soğuk ışık alan yüz fotoğraflarında soluk/gri zombi tonlarını engeller.
  * Ten bölgelerine otomatik sıcaklık katar, yanak ve burun kıvrımlarına doğal terracotta gölgeler yerleştirir.
* **🧹 Akıllı Kenarlık & Arka Plan Ayıklayıcı (Smart Background Cleaning):**
  * Web kamerası arka planındaki karanlık odayı veya Discord/ekran görüntüsü çerçevelerini otomatik saptar.
  * Tuvali gereksiz yere siyaha boyamak yerine saf beyaz tuval kağıdı kabul eder ve yalnızca kişiyi/nesneyi çizer.
* **✍️ Katmanlı Vektör Hat Güçlendirme (Line-Art & Inking):**
  * Önce zemin renkleri ve gölgeler serilir, ardından **en ince siyah kalemle** göz bebekleri, kirpikler, burun ve dudak kıvrımları vektörel olarak üzerine işlenir.
* **⚡ Sıfır Gecikmeli Win32 C Mouse Motoru:**
  * Standart hantal kütüphaneler yerine doğrudan Windows `user32.dll` ve `winmm.dll` C API'leri (`mouse_event`, `SetCursorPos`, `timeBeginPeriod(1)`) üzerinden 1ms hassasiyetle çizim yapar.
* **🖥️ 2K (2560x1440), 4K ve Çoklu Monitör Uyumlu:**
  * Windows High-DPI farkındalığıyla birincil 2K ekranda çizim yaparken stüdyo penceresini otomatik olarak 2. monitöre konumlandırabilir.
* **🎮 Tarayıcı İçi Tampermonkey Eklentisi:**
  * Python istemeyenler için doğrudan Chrome, Edge, Brave tarayıcısı içinde çalışan `GarticPhone_DrawBot_Tampermonkey.user.js` betiği dahildir.

---

## 🏛️ Mimari & Çalışma Prensibi

```mermaid
graph TD
    A[Kaynak Görsel: Pano / Dosya / Web] --> B[Görsel İyileştirme & Filtreler]
    B --> C{Arka Plan Temizleme?}
    C -->|Evet| D[Kenar Bağlantılı Karanlık Alanları Beyaz Tuvale Çevir]
    C -->|Hayır| E[Doğrudan Kuantizasyon]
    D --> F[18 Renk Floyd-Steinberg Hata Difüzyonu]
    E --> F
    F --> G[Sıcak Ten Rengi ve Gölgelendirme Takviyesi]
    G --> H[Vektörel Hat Çıkarımı: Canny + Ramer-Douglas-Peucker]
    H --> I[Greedy TSP Çizgi Sırası Optimizasyonu]
    I --> J[Win32 C Sürücüsü ile Gartic Phone Tuvaline Çizim]
```

---

## ⌨️ Global Kısayol Tuşları (Hotkeys)

| Tuş | İşlev | Açıklama |
| :---: | :--- | :--- |
| **`F6`** | **2-Tık Tuval Kalibrasyonu** | Sol-üst ve sağ-alt köşeleri tıklayarak tuvali anında tanımlar. |
| **`F7`** | **Tuval Sınırlarını Test Et** | Fareniz tuval sınırlarını görsel olarak çizerek hizalamayı gösterir. |
| **`F8`** | **Otomatik Çizimi Başlat** | 3 saniyelik sesli geri sayımdan sonra çizimi başlatır. |
| **`F9`** | **Duraklat / Devam Et** | Çizimi anlık olarak durdurur veya devam ettirir. |
| **`F10` / `ESC`** | **ACİL DURDUR (Panic)** | Farenin sol tıkını anında bırakır ve tüm işlemleri iptal eder. |

---

## 🚀 Hızlı Başlangıç

### 1. Gereksinimler
* Windows 10 veya Windows 11 (64-bit)
* Python 3.10+ (veya üstü)

### 2. Kurulum
Repoyu klonlayın ve bağımlılıkları yükleyin:

```bash
git clone https://github.com/toprakahmetaydogmus/gartic-autodraw-pro.git
cd gartic-autodraw-pro
pip install -r requirements.txt
```

### 3. Çalıştırma
İster tek tıkla başlatıcıyı kullanın:
```cmd
GarticAutoDraw_Baslat.bat
```
Veya komut satırından çalıştırın:
```bash
python main.py
```

---

## 🎨 Nasıl Çizim Yapılır?

1. **Görselinizi Yükleyin:**
   * İstediğiniz herhangi bir resmi kopyalayın ve stüdyoda **`Panodan Yapıştır (Ctrl+V)`** butonuna basın.
2. **Ultra Max Kaliteye Alın:**
   * Sol paneldeki mor **`👑 ULTRA MAX PRO KALİTE`** butonuna bir kez tıklayın. Çözünürlük, ten rengi ve en ince hatlar otomatik ayarlanır.
3. **Tuvali Hizalayın:**
   * Üst menüdeki **`⚡ 2K TAM AYARLA`** butonuna tıklayın (veya özel tuval boyutunuz varsa `F6` ile sol-üst ve sağ-alt köşeleri seçin).
4. **Çizimi Başlatın:**
   * Gartic Phone ekranına geçip **`F8`** tuşuna basın. Gerisini AutoDraw Pro halletsin!

---

## 🔒 Güvenlik & Gizlilik

* **%100 Yerel (Local):** Bilgisayarınızdan internete hiçbir kişisel veri, fotoğraf veya bilgi yüklenmez.
* **API Anahtarı Gerekmez:** Harici ücretli bulut servisleri veya yapay zeka API anahtarları içermez.
* **Açık Kaynak:** Tüm kodlar incelenebilir, şeffaf ve güvenlidir.

---

## 📜 Lisans

Bu proje **MIT Lisansı** altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına göz atabilirsiniz.

**Geliştirici:** [Toprak Ahmet Aydoğmuş](https://github.com/toprakahmetaydogmus)
