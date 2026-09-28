// ==UserScript==
// @name         Gartic Phone Ultra AutoDraw Pro (18 Renk & Her Ekrana Tam Uyumlu)
// @namespace    https://garticphone.com/
// @version      2.5
// @description  Gartic Phone (https://garticphone.com/) için doğrudan tarayıcı içi çalışan, 18 renk paleti ve Floyd-Steinberg renkli çizim destekli otomatik çizim aracı! Çözünürlük ve ekrandan bağımsız %100 uyumlu.
// @author       Toprak Ahmet Aydoğmuş
// @match        https://garticphone.com/*
// @match        https://*.garticphone.com/*
// @grant        none
// ==/UserScript==

(function () {
    'use strict';

    console.log("⚡ Gartic Phone Ultra AutoDraw Pro v2.5 by Toprak Ahmet Aydoğmuş Yüklendi!");

    // Gartic Phone official 18 colors palette (Exact Hex & RGB)
    const GARTIC_PALETTE = [
        { name: "black", rgb: [0, 0, 0] },
        { name: "gray", rgb: [102, 102, 102] },
        { name: "dark_blue", rgb: [0, 80, 205] },
        { name: "white", rgb: [255, 255, 255] },
        { name: "light_gray", rgb: [170, 170, 170] },
        { name: "light_blue", rgb: [38, 201, 255] },
        { name: "dark_green", rgb: [1, 116, 32] },
        { name: "dark_red", rgb: [153, 0, 0] },
        { name: "brown", rgb: [150, 65, 18] },
        { name: "light_green", rgb: [17, 176, 60] },
        { name: "red", rgb: [255, 0, 19] },
        { name: "orange", rgb: [255, 120, 41] },
        { name: "dark_yellow", rgb: [176, 112, 28] },
        { name: "magenta", rgb: [153, 0, 78] },
        { name: "terracotta", rgb: [203, 90, 87] },
        { name: "yellow", rgb: [255, 193, 38] },
        { name: "hot_pink", rgb: [255, 0, 143] },
        { name: "skin_peach", rgb: [254, 175, 168] }
    ];

    let isDrawing = false;
    let shouldAbort = false;
    let loadedImage = null;

    // Helper: Selects color directly in Gartic Phone's web DOM
    function selectColorInDOM(targetRgb) {
        const elements = document.querySelectorAll('button, div[style*="background"], [class*="color"], [class*="item"]');
        let bestElem = null;
        let minDiff = 999999;

        for (let el of elements) {
            const bg = window.getComputedStyle(el).backgroundColor;
            const match = bg.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
            if (match) {
                const r = parseInt(match[1]);
                const g = parseInt(match[2]);
                const b = parseInt(match[3]);
                const diff = Math.abs(r - targetRgb[0]) + Math.abs(g - targetRgb[1]) + Math.abs(b - targetRgb[2]);
                if (diff < minDiff && diff < 35) {
                    minDiff = diff;
                    bestElem = el;
                }
            }
        }

        if (bestElem) {
            bestElem.dispatchEvent(new MouseEvent("mousedown", { bubbles: true, cancelable: true }));
            bestElem.dispatchEvent(new MouseEvent("mouseup", { bubbles: true, cancelable: true }));
            bestElem.click();
            return true;
        }
        return false;
    }

    // Perceptual color matching using Redmean distance
    function matchNearestColorIndex(r, g, b) {
        let bestIdx = 0;
        let minDist = Infinity;

        for (let i = 0; i < GARTIC_PALETTE.length; i++) {
            const p = GARTIC_PALETTE[i].rgb;
            const r_bar = (r + p[0]) / 2.0;
            const dr = r - p[0];
            const dg = g - p[1];
            const db = b - p[2];

            let dist = (2.0 + r_bar / 256.0) * (dr * dr) +
                       4.0 * (dg * dg) +
                       (2.0 + (255.0 - r_bar) / 256.0) * (db * db);

            // Skin warmth bias
            if (r > b + 5 && (r + g + b) / 3 > 50) {
                if (GARTIC_PALETTE[i].name === "skin_peach") dist *= 0.55;
                if (GARTIC_PALETTE[i].name === "terracotta") dist *= 0.65;
                if (GARTIC_PALETTE[i].name === "gray" || GARTIC_PALETTE[i].name === "dark_blue") dist *= 4.0;
            }

            if (dist < minDist) {
                minDist = dist;
                bestIdx = i;
            }
        }
        return bestIdx;
    }

    // Create In-Browser UI Container
    function createUI() {
        if (document.getElementById("gartic-autodraw-panel")) return;

        const panel = document.createElement("div");
        panel.id = "gartic-autodraw-panel";
        panel.style.cssText = `
            position: fixed;
            top: 15px;
            right: 15px;
            width: 290px;
            background: rgba(15, 23, 42, 0.95);
            backdrop-filter: blur(12px);
            border: 2px solid #38bdf8;
            border-radius: 12px;
            padding: 14px;
            z-index: 999999;
            box-shadow: 0 10px 30px rgba(0,0,0,0.8);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #fff;
            font-size: 13px;
        `;

        panel.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                <b style="color:#38bdf8; font-size:14px;">⚡ AutoDraw Pro v2.5</b>
                <span id="ad-status" style="font-size:11px; color:#10b981; font-weight:bold;">Hazır</span>
            </div>
            <div id="ad-dropzone" style="
                border: 2px dashed #0284c7;
                border-radius: 8px;
                padding: 12px;
                text-align: center;
                background: rgba(2, 132, 199, 0.12);
                cursor: pointer;
                margin-bottom: 10px;
                transition: background 0.2s;
            ">
                <span style="font-size:22px;">🖼️</span><br>
                <b>Resmi Buraya Sürükleyin</b><br>
                <small style="color:#94a3b8;">veya tıklayıp seçin (Ctrl+V)</small>
                <input type="file" id="ad-file-input" accept="image/*" style="display:none;">
            </div>
            <div style="margin-bottom:8px;">
                <label style="font-size:11px; color:#94a3b8; font-weight:bold;">Çizim Modu:</label>
                <select id="ad-mode" style="width:100%; background:#1e293b; color:#fff; border:1px solid #334155; border-radius:6px; padding:6px; font-weight:bold; margin-top:3px;">
                    <option value="color">🌈 18 Renk Ultra Gerçekçi (Önerilen)</option>
                    <option value="atkinson">✒️ Atkinson Fotogerçekçi (Siyah/Beyaz)</option>
                </select>
            </div>
            <div style="display:flex; gap:6px;">
                <button id="ad-start-btn" style="flex:2; background:#10b981; color:#fff; border:none; border-radius:6px; padding:9px; font-weight:bold; cursor:pointer; font-size:13px;">
                    🚀 ÇİZ (F8)
                </button>
                <button id="ad-stop-btn" style="flex:1; background:#ef4444; color:#fff; border:none; border-radius:6px; padding:9px; font-weight:bold; cursor:pointer; font-size:13px;">
                    🛑 DUR
                </button>
            </div>
            <div id="ad-progress" style="margin-top:10px; height:7px; background:#1e293b; border-radius:4px; overflow:hidden;">
                <div id="ad-progress-bar" style="width:0%; height:100%; background:#38bdf8; transition:width 0.1s;"></div>
            </div>
        `;

        document.body.appendChild(panel);

        const dropzone = document.getElementById("ad-dropzone");
        const fileInput = document.getElementById("ad-file-input");

        dropzone.addEventListener("click", () => fileInput.click());
        fileInput.addEventListener("change", (e) => {
            if (e.target.files && e.target.files[0]) {
                handleImageFile(e.target.files[0]);
            }
        });

        dropzone.addEventListener("dragover", (e) => {
            e.preventDefault();
            dropzone.style.background = "rgba(2, 132, 199, 0.3)";
        });

        dropzone.addEventListener("dragleave", () => {
            dropzone.style.background = "rgba(2, 132, 199, 0.12)";
        });

        dropzone.addEventListener("drop", (e) => {
            e.preventDefault();
            dropzone.style.background = "rgba(2, 132, 199, 0.12)";
            if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                handleImageFile(e.dataTransfer.files[0]);
            }
        });

        window.addEventListener("paste", (e) => {
            const items = (e.clipboardData || e.originalEvent.clipboardData).items;
            for (let item of items) {
                if (item.kind === "file" && item.type.startsWith("image/")) {
                    handleImageFile(item.getAsFile());
                    break;
                }
            }
        });

        document.getElementById("ad-start-btn").addEventListener("click", startDrawing);
        document.getElementById("ad-stop-btn").addEventListener("click", stopDrawing);

        window.addEventListener("keydown", (e) => {
            if (e.key === "F8") startDrawing();
            if (e.key === "Escape" || e.key === "F10") stopDrawing();
        });
    }

    function handleImageFile(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            const img = new Image();
            img.onload = () => {
                loadedImage = img;
                document.getElementById("ad-status").innerText = "Görsel Yüklendi! ✅";
                document.getElementById("ad-status").style.color = "#10b981";
            };
            img.src = e.target.result;
        };
        reader.readAsDataURL(file);
    }

    function getGameCanvas() {
        const canvases = document.querySelectorAll("canvas");
        for (let c of canvases) {
            const rect = c.getBoundingClientRect();
            if (rect.width > 300 && rect.height > 200) {
                return c;
            }
        }
        return canvases[0] || null;
    }

    async function startDrawing() {
        if (!loadedImage) {
            alert("Lütfen önce bir resim yükleyin veya Ctrl+V ile yapıştırın!");
            return;
        }

        const canvas = getGameCanvas();
        if (!canvas) {
            alert("Gartic Phone tuvali bulunamadı! Çizim sıranızda olduğunuza emin olun.");
            return;
        }

        if (isDrawing) return;
        isDrawing = true;
        shouldAbort = false;

        const mode = document.getElementById("ad-mode").value;
        document.getElementById("ad-status").innerText = "Çiziliyor... ⏳";
        document.getElementById("ad-status").style.color = "#38bdf8";

        const canvasRect = canvas.getBoundingClientRect();
        const cw = canvasRect.width;
        const ch = canvasRect.height;

        // Process image off-screen
        const offCanvas = document.createElement("canvas");
        const maxDim = 320;
        let scale = Math.min(maxDim / loadedImage.width, maxDim / loadedImage.height);
        let tw = Math.floor(loadedImage.width * scale);
        let th = Math.floor(loadedImage.height * scale);

        offCanvas.width = tw;
        offCanvas.height = th;
        const offCtx = offCanvas.getContext("2d");
        offCtx.fillStyle = "#ffffff";
        offCtx.fillRect(0, 0, tw, th);
        offCtx.drawImage(loadedImage, 0, 0, tw, th);

        const imgData = offCtx.getImageData(0, 0, tw, th);
        const data = imgData.data;

        const pad = 12;
        const targetScale = Math.min((cw - 2 * pad) / tw, (ch - 2 * pad) / th);
        const offsetX = canvasRect.left + pad + (cw - 2 * pad - tw * targetScale) / 2;
        const offsetY = canvasRect.top + pad + (ch - 2 * pad - th * targetScale) / 2;

        const progressBar = document.getElementById("ad-progress-bar");

        function dispatchPointer(type, cx, cy) {
            canvas.dispatchEvent(new PointerEvent(type, {
                clientX: cx,
                clientY: cy,
                bubbles: true,
                cancelable: true,
                pointerId: 1,
                pointerType: "mouse",
                isPrimary: true,
                pressure: 0.5,
                button: 0,
                buttons: type === "pointerup" ? 0 : 1
            }));
        }

        if (mode === "color") {
            // Multi-Color Floyd-Steinberg Error Diffusion
            const bufR = new Float32Array(tw * th);
            const bufG = new Float32Array(tw * th);
            const bufB = new Float32Array(tw * th);

            for (let i = 0; i < tw * th; i++) {
                bufR[i] = data[i * 4];
                bufG[i] = data[i * 4 + 1];
                bufB[i] = data[i * 4 + 2];
            }

            const quantized = new Uint8Array(tw * th);
            const whiteIdx = GARTIC_PALETTE.findIndex(p => p.name === "white");

            for (let y = 0; y < th; y++) {
                for (let x = 0; x < tw; x++) {
                    const idx = y * tw + x;
                    const oldR = bufR[idx];
                    const oldG = bufG[idx];
                    const oldB = bufB[idx];

                    const cIdx = matchNearestColorIndex(oldR, oldG, oldB);
                    quantized[idx] = cIdx;

                    const newR = GARTIC_PALETTE[cIdx].rgb[0];
                    const newG = GARTIC_PALETTE[cIdx].rgb[1];
                    const newB = GARTIC_PALETTE[cIdx].rgb[2];

                    const errR = (oldR - newR) * 0.75;
                    const errG = (oldG - newG) * 0.75;
                    const errB = (oldB - newB) * 0.75;

                    if (x + 1 < tw) {
                        bufR[idx + 1] += errR * (7 / 16);
                        bufG[idx + 1] += errG * (7 / 16);
                        bufB[idx + 1] += errB * (7 / 16);
                    }
                    if (y + 1 < th) {
                        if (x - 1 >= 0) {
                            bufR[(y + 1) * tw + (x - 1)] += errR * (3 / 16);
                            bufG[(y + 1) * tw + (x - 1)] += errG * (3 / 16);
                            bufB[(y + 1) * tw + (x - 1)] += errB * (3 / 16);
                        }
                        bufR[(y + 1) * tw + x] += errR * (5 / 16);
                        bufG[(y + 1) * tw + x] += errG * (5 / 16);
                        bufB[(y + 1) * tw + x] += errB * (5 / 16);
                        if (x + 1 < tw) {
                            bufR[(y + 1) * tw + (x + 1)] += errR * (1 / 16);
                            bufG[(y + 1) * tw + (x + 1)] += errG * (1 / 16);
                            bufB[(y + 1) * tw + (x + 1)] += errB * (1 / 16);
                        }
                    }
                }
            }

            // Layering order: skin/warm tones first, details, outlines LAST!
            const layerNames = [
                "skin_peach", "terracotta", "light_gray", "gray", "dark_yellow", "brown",
                "light_blue", "dark_blue", "light_green", "dark_green", "yellow", "orange",
                "red", "dark_red", "hot_pink", "magenta", "black"
            ];

            let totalLayersDrawn = 0;

            for (let layerName of layerNames) {
                if (shouldAbort) break;
                const cIdx = GARTIC_PALETTE.findIndex(p => p.name === layerName);
                if (cIdx === -1) continue;

                // Extract strokes for this color
                const layerStrokes = [];
                for (let y = 0; y < th; y++) {
                    let startX = -1;
                    for (let x = 0; x < tw; x++) {
                        if (quantized[y * tw + x] === cIdx) {
                            if (startX === -1) startX = x;
                        } else {
                            if (startX !== -1) {
                                layerStrokes.push({ x0: startX, x1: x - 1, y: y });
                                startX = -1;
                            }
                        }
                    }
                    if (startX !== -1) layerStrokes.push({ x0: startX, x1: tw - 1, y: y });
                }

                if (layerStrokes.length === 0) continue;

                // Select color in browser DOM
                selectColorInDOM(GARTIC_PALETTE[cIdx].rgb);
                await new Promise(r => setTimeout(r, 70));

                for (let s of layerStrokes) {
                    if (shouldAbort) break;
                    const px0 = offsetX + s.x0 * targetScale;
                    const px1 = offsetX + s.x1 * targetScale;
                    const py = offsetY + s.y * targetScale;

                    dispatchPointer("pointerdown", px0, py);
                    dispatchPointer("pointermove", px1, py);
                    dispatchPointer("pointerup", px1, py);
                }

                totalLayersDrawn++;
                progressBar.style.width = Math.floor((totalLayersDrawn / layerNames.length) * 100) + "%";
                await new Promise(r => setTimeout(r, 10));
            }

        } else {
            // Black and White Atkinson Dithering
            const grayBuf = new Float32Array(tw * th);
            for (let i = 0; i < tw * th; i++) {
                const r = data[i * 4];
                const g = data[i * 4 + 1];
                const b = data[i * 4 + 2];
                grayBuf[i] = (r * 0.299 + g * 0.587 + b * 0.114);
            }

            const dithered = new Uint8Array(tw * th);
            for (let y = 0; y < th; y++) {
                for (let x = 0; x < tw; x++) {
                    const idx = y * tw + x;
                    const oldVal = grayBuf[idx];
                    const newVal = oldVal < 128 ? 0 : 255;
                    grayBuf[idx] = newVal;
                    if (newVal === 0) dithered[idx] = 1;

                    const err = (oldVal - newVal) / 8;
                    if (x + 1 < tw) grayBuf[idx + 1] += err;
                    if (x + 2 < tw) grayBuf[idx + 2] += err;
                    if (y + 1 < th) {
                        if (x - 1 >= 0) grayBuf[(y + 1) * tw + (x - 1)] += err;
                        grayBuf[(y + 1) * tw + x] += err;
                        if (x + 1 < tw) grayBuf[(y + 1) * tw + (x + 1)] += err;
                    }
                    if (y + 2 < th) grayBuf[(y + 2) * tw + x] += err;
                }
            }

            const strokes = [];
            for (let y = 0; y < th; y++) {
                let startX = -1;
                for (let x = 0; x < tw; x++) {
                    if (dithered[y * tw + x] === 1) {
                        if (startX === -1) startX = x;
                    } else {
                        if (startX !== -1) {
                            strokes.push({ x0: startX, x1: x - 1, y: y });
                            startX = -1;
                        }
                    }
                }
                if (startX !== -1) strokes.push({ x0: startX, x1: tw - 1, y: y });
            }

            // Ensure Black color is selected
            selectColorInDOM([0, 0, 0]);
            await new Promise(r => setTimeout(r, 60));

            const total = strokes.length;
            for (let i = 0; i < total; i++) {
                if (shouldAbort) break;
                const s = strokes[i];
                const px0 = offsetX + s.x0 * targetScale;
                const px1 = offsetX + s.x1 * targetScale;
                const py = offsetY + s.y * targetScale;

                dispatchPointer("pointerdown", px0, py);
                dispatchPointer("pointermove", px1, py);
                dispatchPointer("pointerup", px1, py);

                if (i % 25 === 0) {
                    progressBar.style.width = Math.floor((i / total) * 100) + "%";
                    await new Promise(r => setTimeout(r, 2));
                }
            }
        }

        progressBar.style.width = "100%";
        isDrawing = false;
        document.getElementById("ad-status").innerText = shouldAbort ? "Durduruldu 🛑" : "Tamamlandı! 🎉";
        document.getElementById("ad-status").style.color = shouldAbort ? "#ef4444" : "#10b981";
    }

    function stopDrawing() {
        shouldAbort = true;
        isDrawing = false;
        document.getElementById("ad-status").innerText = "Durduruldu 🛑";
        document.getElementById("ad-status").style.color = "#ef4444";
    }

    // Auto-initialize UI
    setInterval(() => {
        if (!document.getElementById("gartic-autodraw-panel")) {
            createUI();
        }
    }, 1500);

})();
