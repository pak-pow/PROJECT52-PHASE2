import { renderNavbar } from "../components/navbar.js";
import { renderToolbar } from "../components/toolbar.js";
import { CanvasEngine } from "../engine/canvasEngine.js";
import { getQueryParam, showToast } from "../utils/helpers.js";

document.addEventListener("DOMContentLoaded", () => {
    const roomCode = getQueryParam("room") || "CANVAS-DEMO";
    renderNavbar(roomCode);

    const canvasElement = document.getElementById("drawing-canvas");
    if (!canvasElement) return;

    // Initialize Canvas Engine
    const canvasEngine = new CanvasEngine(canvasElement, (strokeData) => {
        // Local stroke drawn
        showToast("Stroke drawn locally.", "info");
    });

    // Render Floating Toolbar
    renderToolbar(
        (tool) => {
            canvasEngine.setTool(tool);
            showToast(`Switched tool to ${tool.toUpperCase()}`, "info");
        },
        (color) => {
            canvasEngine.setColor(color);
        },
        (size) => {
            canvasEngine.setSize(size);
        },
        () => {
            canvasEngine.clear();
            showToast("Canvas cleared.", "info");
        }
    );
});
