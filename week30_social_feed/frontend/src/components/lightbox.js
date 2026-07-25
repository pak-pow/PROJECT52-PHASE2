/**
 * lightbox.js — Shared full-screen image lightbox modal component.
 */
export function openLightbox(src, alt = "Image preview") {
    let overlay = document.getElementById("lightbox-overlay");
    if (!overlay) {
        overlay = document.createElement("div");
        overlay.id = "lightbox-overlay";
        overlay.className = "lightbox-overlay hidden";
        overlay.innerHTML = `
            <div class="lightbox-content">
                <button class="lightbox-close" id="lightbox-close-btn">&times;</button>
                <img id="lightbox-img" src="" alt="" />
            </div>
        `;
        document.body.appendChild(overlay);

        const closeBtn = overlay.querySelector("#lightbox-close-btn");
        closeBtn.addEventListener("click", () => overlay.classList.add("hidden"));
        overlay.addEventListener("click", (e) => {
            if (e.target === overlay) overlay.classList.add("hidden");
        });
        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape" && !overlay.classList.contains("hidden")) {
                overlay.classList.add("hidden");
            }
        });
    }

    const img = overlay.querySelector("#lightbox-img");
    img.src = src;
    img.alt = alt;
    overlay.classList.remove("hidden");
}
