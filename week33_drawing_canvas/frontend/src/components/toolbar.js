export function renderToolbar(onToolChange, onColorChange, onSizeChange, onClearCanvas) {
    const toolbarContainer = document.getElementById("toolbar-container");
    if (!toolbarContainer) return;

    const DEFAULT_COLORS = [
        "#ef4444", "#f97316", "#f59e0b", "#10b981", 
        "#06b6d4", "#3b82f6", "#8b5cf6", "#ec4899", 
        "#000000", "#ffffff"
    ];

    const swatchesHtml = DEFAULT_COLORS.map((color, i) => `
        <button class="swatch-btn ${i === 5 ? 'active' : ''}" data-color="${color}" style="background-color: ${color};"></button>
    `).join("");

    toolbarContainer.innerHTML = `
        <div class="floating-toolbar">
            <!-- Tool Selection Group -->
            <div class="tool-group">
                <button class="tool-btn active" data-tool="brush" title="Brush Tool">✏️</button>
                <button class="tool-btn" data-tool="eraser" title="Eraser Tool">🧹</button>
            </div>

            <div class="toolbar-divider"></div>

            <!-- Color Palette Swatches -->
            <div class="color-swatch-group">
                ${swatchesHtml}
                <input type="color" id="custom-color-picker" class="custom-color-input" value="#3b82f6" title="Custom Color">
            </div>

            <div class="toolbar-divider"></div>

            <!-- Brush Size Slider -->
            <div class="brush-size-group">
                <span style="font-size: 0.8rem; font-weight: 700; color: var(--text-muted);">SIZE</span>
                <input type="range" id="brush-size-slider" class="brush-size-slider" min="1" max="50" value="5">
                <div id="brush-size-preview" class="brush-preview-dot" style="width: 10px; height: 10px; background-color: #3b82f6;"></div>
            </div>

            <div class="toolbar-divider"></div>

            <!-- Clear Canvas Button -->
            <button id="clear-canvas-btn" class="btn-secondary" style="padding: 0.4rem 0.75rem; font-size: 0.85rem; color: var(--danger);">
                🗑️ Clear
            </button>
        </div>
    `;

    // Event Handlers
    toolbarContainer.querySelectorAll(".tool-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            toolbarContainer.querySelectorAll(".tool-btn").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            const tool = btn.getAttribute("data-tool");
            if (onToolChange) onToolChange(tool);
        });
    });

    toolbarContainer.querySelectorAll(".swatch-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            toolbarContainer.querySelectorAll(".swatch-btn").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            const color = btn.getAttribute("data-color");
            if (onColorChange) onColorChange(color);
        });
    });

    const colorPicker = document.getElementById("custom-color-picker");
    colorPicker?.addEventListener("input", (e) => {
        toolbarContainer.querySelectorAll(".swatch-btn").forEach(b => b.classList.remove("active"));
        if (onColorChange) onColorChange(e.target.value);
    });

    const sizeSlider = document.getElementById("brush-size-slider");
    const sizePreview = document.getElementById("brush-size-preview");
    sizeSlider?.addEventListener("input", (e) => {
        const val = parseInt(e.target.value);
        if (sizePreview) {
            sizePreview.style.width = `${Math.max(4, Math.min(24, val))}px`;
            sizePreview.style.height = `${Math.max(4, Math.min(24, val))}px`;
        }
        if (onSizeChange) onSizeChange(val);
    });

    document.getElementById("clear-canvas-btn")?.addEventListener("click", () => {
        if (onClearCanvas) onClearCanvas();
    });
}
