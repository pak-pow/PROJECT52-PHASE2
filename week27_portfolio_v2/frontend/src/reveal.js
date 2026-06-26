/**
 * reveal.js — Lightweight scroll-reveal for pages without contact.js
 * Immediately reveals sections already in the viewport;
 * uses IntersectionObserver for the rest.
 */

const revealEls = document.querySelectorAll(".section-reveal");

const observer = new IntersectionObserver(
    (entries) => {
        entries.forEach((e) => {
            if (e.isIntersecting) {
                e.target.classList.add("revealed");
                observer.unobserve(e.target);
            }
        });
    },
    { threshold: 0.08 }
);

revealEls.forEach((el) => {
    const rect = el.getBoundingClientRect();
    const alreadyVisible = rect.top < window.innerHeight && rect.bottom > 0;
    if (alreadyVisible) {
        el.classList.add("revealed");
    } else {
        observer.observe(el);
    }
});
