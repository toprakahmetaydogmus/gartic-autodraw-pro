# 🤝 Katkıda Bulunma Rehberi / Contributing Guide

[English](#english) • [Türkçe](#türkçe)

---

## English

Thank you for your interest in contributing to **Gartic AutoDraw AI Studio Pro**! We welcome bug reports, feature suggestions, and pull requests.

### 📌 How to Contribute
1. **Fork the Repository:** Click the "Fork" button at the top right of the GitHub page.
2. **Clone your Fork:**
   ```bash
   git clone https://github.com/<your-username>/gartic-autodraw-pro.git
   cd gartic-autodraw-pro
   ```
3. **Create a Feature Branch:**
   ```bash
   git checkout -b feature/amazing-feature
   ```
4. **Make Your Changes:**
   - Adhere to PEP 8 standards.
   - Ensure Win32 mouse safety checks (`emergency_stop`, `should_abort`) remain intact.
5. **Commit Your Changes:**
   ```bash
   git commit -m "feat(module): description of feature"
   ```
6. **Push to Your Fork & Open a PR:**
   ```bash
   git push origin feature/amazing-feature
   ```

### 🐛 Reporting Bugs
Please use the GitHub Issue tracker and include:
- Your screen resolution and DPI scale (e.g. 2560x1440 @ 100%).
- Python version.
- Exact steps to reproduce the issue.

---

## Türkçe

**Gartic AutoDraw AI Studio Pro** projesine katkıda bulunmak istediğiniz için teşekkür ederiz! Hata bildirimleri, yeni özellik fikirleri ve Pull Request'lerinizi bekliyoruz.

### 📌 Nasıl Katkıda Bulunabilirsiniz?
1. **Repoyu Fork'layın:** Sağ üstteki "Fork" butonuna tıklayın.
2. **Kendi Fork'unuzu Klonlayın:**
   ```bash
   git clone https://github.com/<kullanici-adiniz>/gartic-autodraw-pro.git
   cd gartic-autodraw-pro
   ```
3. **Yeni Bir Dal (Branch) Açın:**
   ```bash
   git checkout -b ozellik/yeni-ozellik
   ```
4. **Değişikliklerinizi Yapın:**
   - PEP 8 Python standartlarına uyun.
   - Fare güvenlik kontrollerinin (`emergency_stop`, `F10 / ESC`) bozulmadığından emin olun.
5. **Değişiklikleri Commit'leyin:**
   ```bash
   git commit -m "feat: yeni özellik açıklaması"
   ```
6. **Fork'unuza Pushlayıp PR Açın:**
   ```bash
   git push origin ozellik/yeni-ozellik
   ```

### 🐛 Hata Bildirimi (Bug Report)
GitHub "Issues" sekmesini kullanarak hata bildirirken lütfen:
- Ekran çözünürlüğünüzü ve Windows ölçeklemenizi (Örn: 2560x1440, %100 DPI),
- Python sürümünüzü,
- Hatayı yeniden oluşturmak için izlenen adımları belirtiniz.

---

**Developer / Geliştirici:** [Toprak Ahmet Aydoğmuş](https://github.com/toprakahmetaydogmus)
