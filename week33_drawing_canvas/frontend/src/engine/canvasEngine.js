export class CanvasEngine {
    /**
     * Core HTML5 Canvas 2D Engine with High-DPI scaling and smooth curve rendering.
     */
    constructor(canvasElement, onStrokeDrawn = null) {
        this.canvas = canvasElement;
        this.ctx = canvasElement.getContext("2d");
        this.onStrokeDrawn = onStrokeDrawn;

        // Current Brush State
        this.currentTool = "brush";      // 'brush' or 'eraser'
        this.currentColor = "#3b82f6";
        this.currentSize = 5;
        this.isDrawing = false;
        this.currentPoints = [];

        this._initCanvas();
        this._attachEventListeners();
    }

    _initCanvas() {
        this.resize();
        window.addEventListener("resize", () => this.resize());
    }

    resize() {
        const parent = this.canvas.parentElement;
        if (!parent) return;

        const dpr = window.devicePixelRatio || 1;
        const width = parent.clientWidth;
        const height = parent.clientHeight;

        // Scale canvas for High-DPI screens
        this.canvas.width = width * dpr;
        this.canvas.height = height * dpr;
        this.canvas.style.width = `${width}px`;
        this.canvas.style.height = `${height}px`;

        this.ctx.scale(dpr, dpr);
        this.ctx.lineCap = "round";
        this.ctx.lineJoin = "round";
    }

    setTool(tool) { this.currentTool = tool; }
    setColor(color) { this.currentColor = color; }
    setSize(size) { this.currentSize = size; }

    _getCanvasCoords(e) {
        const rect = this.canvas.getBoundingClientRect();
        let clientX = e.clientX;
        let clientY = e.clientY;

        if (e.touches && e.touches.length > 0) {
            clientX = e.touches[0].clientX;
            clientY = e.touches[0].clientY;
        }

        return {
            x: clientX - rect.left,
            y: clientY - rect.top
        };
    }

    _attachEventListeners() {
        // Mouse Events
        this.canvas.addEventListener("mousedown", (e) => this.startDrawing(e));
        this.canvas.addEventListener("mousemove", (e) => this.draw(e));
        this.canvas.addEventListener("mouseup", () => this.stopDrawing());
        this.canvas.addEventListener("mouseleave", () => this.stopDrawing());

        // Touch Events (Mobile Support)
        this.canvas.addEventListener("touchstart", (e) => {
            e.preventDefault();
            this.startDrawing(e);
        });
        this.canvas.addEventListener("touchmove", (e) => {
            e.preventDefault();
            this.draw(e);
        });
        this.canvas.addEventListener("touchend", () => this.stopDrawing());
    }

    startDrawing(e) {
        this.isDrawing = true;
        const coords = this._getCanvasCoords(e);
        this.currentPoints = [coords];

        // Capture canvas snapshot for shape live preview overlay
        if (["line", "rectangle", "circle"].includes(this.currentTool)) {
            const dpr = window.devicePixelRatio || 1;
            this.shapePreviewSnapshot = this.ctx.getImageData(0, 0, this.canvas.width, this.canvas.height);
        }
    }

    draw(e) {
        if (!this.isDrawing) return;

        const coords = this._getCanvasCoords(e);
        this.currentPoints.push(coords);

        const start = this.currentPoints[0];
        const end = coords;

        if (["line", "rectangle", "circle"].includes(this.currentTool)) {
            // Restore snapshot to clear previous drag preview frame
            if (this.shapePreviewSnapshot) {
                this.ctx.putImageData(this.shapePreviewSnapshot, 0, 0);
            }

            this.ctx.save();
            const dpr = window.devicePixelRatio || 1;
            this.ctx.scale(dpr, dpr);

            this.ctx.beginPath();
            this.ctx.lineCap = "round";
            this.ctx.lineJoin = "round";
            this.ctx.lineWidth = this.currentSize;
            this.ctx.strokeStyle = this.currentColor;
            this.ctx.globalCompositeOperation = "source-over";

            if (this.currentTool === "line") {
                this.ctx.moveTo(start.x, start.y);
                this.ctx.lineTo(end.x, end.y);
                this.ctx.stroke();
            } else if (this.currentTool === "rectangle") {
                this.ctx.strokeRect(start.x, start.y, end.x - start.x, end.y - start.y);
            } else if (this.currentTool === "circle") {
                const rx = Math.abs(end.x - start.x) / 2;
                const ry = Math.abs(end.y - start.y) / 2;
                const cx = Math.min(start.x, end.x) + rx;
                const cy = Math.min(start.y, end.y) + ry;
                this.ctx.ellipse(cx, cy, rx, ry, 0, 0, Math.PI * 2);
                this.ctx.stroke();
            }
            this.ctx.restore();
        } else {
            // Freehand Brush & Eraser
            this.ctx.save();
            this.ctx.beginPath();
            this.ctx.lineCap = "round";
            this.ctx.lineJoin = "round";
            this.ctx.lineWidth = this.currentSize;

            if (this.currentTool === "eraser") {
                this.ctx.globalCompositeOperation = "destination-out";
                this.ctx.strokeStyle = "rgba(0,0,0,1)";
            } else {
                this.ctx.globalCompositeOperation = "source-over";
                this.ctx.strokeStyle = this.currentColor;
            }

            const pts = this.currentPoints;

            if (pts.length < 2) {
                this.ctx.arc(coords.x, coords.y, this.currentSize / 2, 0, Math.PI * 2);
                if (this.currentTool === "eraser") {
                    this.ctx.fill();
                } else {
                    this.ctx.fillStyle = this.currentColor;
                    this.ctx.fill();
                }
            } else {
                this.ctx.moveTo(pts[0].x, pts[0].y);
                for (let i = 1; i < pts.length - 1; i++) {
                    const xc = (pts[i].x + pts[i + 1].x) / 2;
                    const yc = (pts[i].y + pts[i + 1].y) / 2;
                    this.ctx.quadraticCurveTo(pts[i].x, pts[i].y, xc, yc);
                }
                this.ctx.stroke();
            }
            this.ctx.restore();
        }
    }

    stopDrawing() {
        if (!this.isDrawing) return;
        this.isDrawing = false;

        let strokePoints = this.currentPoints;

        if (["line", "rectangle", "circle"].includes(this.currentTool) && this.currentPoints.length > 1) {
            // Shape tools take start point and final release point
            const start = this.currentPoints[0];
            const end = this.currentPoints[this.currentPoints.length - 1];
            strokePoints = [start, end];
        }

        if (strokePoints.length > 0) {
            const strokeData = {
                tool: this.currentTool,
                color: this.currentColor,
                size: this.currentSize,
                points: strokePoints
            };

            if (this.onStrokeDrawn) {
                this.onStrokeDrawn(strokeData);
            }
        }
        this.currentPoints = [];
        this.shapePreviewSnapshot = null;
    }

    renderExternalStroke(strokeData) {
        if (!strokeData || !strokeData.points || strokeData.points.length === 0) return;

        this.ctx.save();
        const dpr = window.devicePixelRatio || 1;
        this.ctx.scale(dpr, dpr);

        this.ctx.beginPath();
        this.ctx.lineCap = "round";
        this.ctx.lineJoin = "round";
        this.ctx.lineWidth = strokeData.size;

        if (strokeData.tool === "eraser") {
            this.ctx.globalCompositeOperation = "destination-out";
            this.ctx.strokeStyle = "rgba(0,0,0,1)";
        } else {
            this.ctx.globalCompositeOperation = "source-over";
            this.ctx.strokeStyle = strokeData.color || "#3b82f6";
        }

        const pts = strokeData.points;
        const start = pts[0];
        const end = pts[pts.length - 1];

        if (strokeData.tool === "line") {
            this.ctx.moveTo(start.x, start.y);
            this.ctx.lineTo(end.x, end.y);
            this.ctx.stroke();
        } else if (strokeData.tool === "rectangle") {
            this.ctx.strokeRect(start.x, start.y, end.x - start.x, end.y - start.y);
        } else if (strokeData.tool === "circle") {
            const rx = Math.abs(end.x - start.x) / 2;
            const ry = Math.abs(end.y - start.y) / 2;
            const cx = Math.min(start.x, end.x) + rx;
            const cy = Math.min(start.y, end.y) + ry;
            this.ctx.ellipse(cx, cy, rx, ry, 0, 0, Math.PI * 2);
            this.ctx.stroke();
        } else {
            if (pts.length < 2) {
                this.ctx.arc(pts[0].x, pts[0].y, strokeData.size / 2, 0, Math.PI * 2);
                if (strokeData.tool === "eraser") {
                    this.ctx.fill();
                } else {
                    this.ctx.fillStyle = strokeData.color || "#3b82f6";
                    this.ctx.fill();
                }
            } else {
                this.ctx.moveTo(pts[0].x, pts[0].y);
                for (let i = 1; i < pts.length - 1; i++) {
                    const xc = (pts[i].x + pts[i + 1].x) / 2;
                    const yc = (pts[i].y + pts[i + 1].y) / 2;
                    this.ctx.quadraticCurveTo(pts[i].x, pts[i].y, xc, yc);
                }
                this.ctx.stroke();
            }
        }
        this.ctx.restore();
    }

    clear() {
        const dpr = window.devicePixelRatio || 1;
        this.ctx.clearRect(0, 0, this.canvas.width / dpr, this.canvas.height / dpr);
    }
}
