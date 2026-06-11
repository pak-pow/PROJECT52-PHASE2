import { createShortLink } from './api/url_api.js';

document.addEventListener('DOMContentLoaded', () => {

    // ── DOM refs ────────────────────────────────────────────────
    const form          = document.getElementById('shorten-form');
    const submitBtn     = document.getElementById('submit-btn');
    const errorBox      = document.getElementById('form-error');

    const modal         = document.getElementById('result-modal');
    const modalCloseBtn = document.getElementById('modal-close-btn');
    const newLinkBtn    = document.getElementById('new-link-btn');

    const shortUrlLink  = document.getElementById('short-url-link');
    const copyBtn       = document.getElementById('copy-btn');
    const copyIcon      = document.getElementById('copy-icon');
    const copyText      = document.getElementById('copy-text');

    const metaOriginal  = document.getElementById('meta-original');
    const metaClicks    = document.getElementById('meta-clicks');
    const expiryBadge   = document.getElementById('expiry-badge');
    const expiryText    = document.getElementById('expiry-text');

    // ── Helpers ─────────────────────────────────────────────────
    function showError(msg) {
        errorBox.textContent = msg;
        errorBox.classList.remove('hidden');
    }

    function clearError() {
        errorBox.textContent = '';
        errorBox.classList.add('hidden');
    }

    function openModal(data, expiresInHours) {
        const shortUrl = data.short_url;

        // Populate link
        shortUrlLink.href        = shortUrl;
        shortUrlLink.textContent = shortUrl;

        // Meta
        metaOriginal.textContent = data.original_url;
        metaOriginal.title       = data.original_url;
        metaClicks.textContent   = data.clicks ?? 0;

        // Expiry badge
        if (expiresInHours) {
            expiryText.textContent = `Self-destructs in ${expiresInHours} hour${expiresInHours !== 1 ? 's' : ''}`;
            expiryBadge.classList.remove('hidden');
        } else {
            expiryBadge.classList.add('hidden');
        }

        // Reset copy button state
        copyIcon.textContent = '📋';
        copyText.textContent = 'Copy';
        copyBtn.classList.remove('copied');

        modal.classList.add('open');
    }

    function closeModal() {
        modal.classList.remove('open');
    }

    // ── Copy to clipboard ────────────────────────────────────────
    copyBtn.addEventListener('click', async () => {
        const url = shortUrlLink.href;
        try {
            await navigator.clipboard.writeText(url);
        } catch {
            // Fallback for non-HTTPS contexts
            const ta = document.createElement('textarea');
            ta.value = url;
            document.body.appendChild(ta);
            ta.select();
            document.execCommand('copy');
            document.body.removeChild(ta);
        }
        copyIcon.textContent = '✅';
        copyText.textContent = 'Copied!';
        copyBtn.classList.add('copied');
        setTimeout(() => {
            copyIcon.textContent = '📋';
            copyText.textContent = 'Copy';
            copyBtn.classList.remove('copied');
        }, 2500);
    });

    // ── Close modal ──────────────────────────────────────────────
    modalCloseBtn.addEventListener('click', closeModal);
    newLinkBtn.addEventListener('click', closeModal);

    // Close when clicking backdrop (outside the modal box)
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });

    // Close on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.classList.contains('open')) closeModal();
    });

    // ── Form submit ──────────────────────────────────────────────
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        clearError();

        const urlInput     = document.getElementById('url').value.trim();
        const aliasInput   = document.getElementById('custom-alias').value.trim();
        const expiresRaw   = document.getElementById('expires-in').value.trim();

        // ── BUG FIX: only send expires_in_hours if the input is a valid number ──
        // parseInt("") → NaN, which fails the backend's isinstance(x, (int,float)) check
        // and returns a 400 error. Only include it when the field has a real value.
        const expiresInHours = expiresRaw !== '' ? parseInt(expiresRaw, 10) : null;

        if (!urlInput) {
            showError('Please enter a URL.');
            return;
        }

        const payload = { url: urlInput };
        if (aliasInput)         payload.custom_alias    = aliasInput;
        if (expiresInHours)     payload.expires_in_hours = expiresInHours;

        submitBtn.textContent = '⏳ Generating…';
        submitBtn.disabled    = true;

        try {
            const data = await createShortLink(payload);
            form.reset();
            openModal(data, expiresInHours);

        } catch (err) {
            showError(err.message);

        } finally {
            submitBtn.textContent = '⚡ Generate Short Link';
            submitBtn.disabled    = false;
        }
    });
});