// ==UserScript==
// @name         Gartic Phone Ultra AutoDraw Pro (2K & 4K Destekli)
// @namespace    https://garticphone.com/
// @version      2.0
// @description  Gartic Phone (https://garticphone.com/) için doğrudan tarayıcı içi çalışan, çözünürlükten bağımsız çalışan otomatik çizim aracı! Resmi sürükleyip bırakın, saniyeler içinde çizsin!
// @author       Toprak Ahmet Aydoğmuş
// @match        https://garticphone.com/*
// @match        https://*.garticphone.com/*
// @grant        none
// ==/UserScript==

(function () {
    'use strict';

    console.log("⚡ Gartic Phone Ultra AutoDraw Yüklendi!");

    // Gartic Phone official 18 colors palette
    const PALETTE = [
        { name: "black", rgb: [0, 0, 0] },
        { name: "dark_gray", rgb: [102, 102, 102] },
        { name: "gray", rgb: [170, 170, 170] },
        { name: "white", rgb: [255, 255, 255] },
        { name: "dark_blue", rgb: [0, 80, 205] },
        { name: "blue", rgb: [38, 201, 255] },
        { name: "dark_green", rgb: [1, 116, 32] },
        { name: "green", rgb: [105, 208, 37] },
        { name: "dark_red", rgb: [153, 0, 0] },
        { name: "red", rgb: [255, 0, 0] },
        { name: "dark_orange", rgb: [176, 75, 0] },
        { name: "orange", rgb: [255, 120, 41] },
        { name: "dark_yellow", rgb: [185, 140, 0] },
        { name: "yellow", rgb: [255, 204, 0] },
        { name: "brown", rgb: [102, 51, 0] },
        { name: "light_brown", rgb: [153, 102, 51] },
        { name: "dark_purple", rgb: [102, 0, 153] },
        { name: "purple", rgb: [153, 0, 255] },
        { name: "pink", rgb: [255, 153, 204] }
    ];

    let isDrawing = false;
    let shouldAbort = false;

    // Create In-Browser UI Container
    function createUI() {
        if (document.getElementById("gartic-autodraw-panel")) return;

        const panel = document.createElement("div");
        panel.id = "gartic-autodraw-panel";
        panel.style.cssText = `
            position: fixed;
            top: 15px;
            right: 15px;
            width: 280px;
            background: rgba(15, 23, 42, 0.95);
            backdrop-filter: blur(10px);
            border: 2px solid #38bdf8;
            border-radius: 12px;
            padding: 14px;
            z-index: 999999;
            box-shadow: 0 10px 25px rgba(0,0,0,0.7);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #fff;
            font-size: 13px;
        `;

        panel.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                <b style="color:#38bdf8; font-size:14px;">⚡ AutoDraw Pro</b>
                <span id="ad-status" style="font-size:11px; color:#10b981;">Hazır</span>
            </div>
            <div id="ad-dropzone" style="
                border: 2px dashed #0284c7;
                border-radius: 8px;
                padding: 12px;
                text-align: center;
                background: rgba(2, 132, 199, 0.1);
                cursor: pointer;
                margin-bottom: 10px;
            ">
                <span style="font-size:20px;">🖼️</span><br>
                <b>Resmi Buraya Sürükleyin</b><br>
                <small style="color:#94a3b8;">veya tıklayıp seçin</small>
                <input type="file" id="ad-file-input" accept="image/*" style="display:none;">
            </div>
            <div style="margin-bottom:8px;">
                <label style="font-size:11px; color:#94a3b8;">Çizim Modu:</label>
                <select id="ad-mode" style="width:100%; background:#1e293b; color:#fff; border:1px solid #334155; border-radius:6px; padding:4px;">
                    <option value="atkinson">Atkinson Fotogerçekçi</option>
                    <option value="edge">Kenar Çizgileri (Lineart)</option>
                </select>
            </div>
            <div style="display:flex; gap:6px;">
                <button id="ad-start-btn" style="flex:2; background:#10b981; color:#fff; border:none; border-radius:6px; padding:8px; font-weight:bold; cursor:pointer;">
                    🚀 ÇİZ (F8)
                </button>
                <button id="ad-stop-btn" style="flex:1; background:#ef4444; color:#fff; border:none; border-radius:6px; padding:8px; font-weight:bold; cursor:pointer;">
                    🛑 DUR
                </button>
            </div>
            <div id="ad-progress" style="margin-top:8px; height:6px; background:#1e293b; border-radius:3px; overflow:hidden;">
                <div id="ad-progress-bar" style="width:0%; height:100%; background:#38bdf8; transition:width 0.1s;"></div>
            </div>
        `;

        document.body.appendChild(panel);

        // Bind events
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
            dropzone.style.background = "rgba(2, 132, 199, 0.1)";
        });

        dropzone.addEventListener("drop", (e) => {
            e.preventDefault();
            dropzone.style.background = "rgba(2, 132, 199, 0.1)";
            if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                handleImageFile(e.dataTransfer.files[0]);
            }
        });

        // Clipboard paste (Ctrl+V) listener inside browser
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

    let loadedImage = null;

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
            alert("Lütfen önce bir resim yükleyin veya yapıştırın!");
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

        // Atkinson Dithering in JS
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
                if (newVal === 0) dithered[idx] = 1; // ink

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

        // Group into horizontal stroke runs
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

        // Fit into game canvas
        const pad = 15;
        const targetScale = Math.min((cw - 2 * pad) / tw, (ch - 2 * pad) / th);
        const offsetX = canvasRect.left + pad + (cw - 2 * pad - tw * targetScale) / 2;
        const offsetY = canvasRect.top + pad + (ch - 2 * pad - th * targetScale) / 2;

        const totalStrokes = strokes.length;
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

        for (let i = 0; i < totalStrokes; i++) {
            if (shouldAbort) break;

            const s = strokes[i];
            const px0 = offsetX + s.x0 * targetScale;
            const px1 = offsetX + s.x1 * targetScale;
            const py = offsetY + s.y * targetScale;

            dispatchPointer("pointerdown", px0, py);
            dispatchPointer("pointermove", px1, py);
            dispatchPointer("pointerup", px1, py);

            if (i % 25 === 0) {
                progressBar.style.width = Math.floor((i / totalStrokes) * 100) + "%";
                await new Promise(r => setTimeout(r, 2));
            }
        }

        progressBar.style.width = "100%";
        isDrawing = false;
        document.getElementById("ad-status").innerText = shouldAbort ? "Durduruldu" : "Tamamlandı! 🎉";
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
