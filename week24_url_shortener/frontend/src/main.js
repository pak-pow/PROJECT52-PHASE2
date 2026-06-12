import { createShortLink, getStats } from './api/url_api.js';

// SVG Icons templates
const COPY_SVG = `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg" style="width: 14px; height: 14px;"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>`;
const CHECK_SVG = `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg" style="width: 14px; height: 14px;"><polyline points="20 6 9 17 4 12"></polyline></svg>`;
const LIGHTNING_SVG = `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg" style="width: 18px; height: 18px;"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>`;
const SPINNER_SVG = `<svg class="icon animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" xmlns="http://www.w3.org/2000/svg" style="width: 18px; height: 18px;"><circle cx="12" cy="12" r="10" stroke="rgba(255, 255, 255, 0.25)" fill="none"></circle><path d="M4 12a8 8 0 0 1 8-8" stroke="currentColor"></path></svg>`;

document.addEventListener('DOMContentLoaded', () => {

    // ── DOM refs ────────────────────────────────────────────────
    const form          = document.getElementById('shorten-form');
    const submitBtn     = document.getElementById('submit-btn');
    const submitBtnIcon = document.getElementById('submit-btn-icon');
    const submitBtnText = document.getElementById('submit-btn-text');
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
    function showError(msg, linkUrl = null) {
        // Warning SVG (styled via .error-message .icon-alert in components.css)
        const warningSvg = `<svg class="icon icon-alert" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>`;
        
        errorBox.innerHTML = warningSvg;

        const textSpan = document.createElement('span');
        textSpan.textContent = ' ' + msg;
        errorBox.appendChild(textSpan);

        if (linkUrl) {
            errorBox.appendChild(document.createTextNode(' '));
            const a = document.createElement('a');
            a.href = linkUrl;
            a.target = '_blank';
            a.textContent = linkUrl;
            errorBox.appendChild(a);
        }
        errorBox.classList.remove('hidden');
    }

    function clearError() {
        errorBox.textContent = '';
        errorBox.classList.add('hidden');
    }

    const statsBody = document.getElementById('stats-body');
    const refreshBtn = document.getElementById('refresh-stats');

    // Function to fetch and render the table
    async function loadStats() {
        try {
            const records = await getStats();
            statsBody.innerHTML = ''; // Clear current rows

            if (records.length === 0) {
                statsBody.innerHTML = `<tr><td colspan="4" class="empty-state">No links generated yet.</td></tr>`;
                return;
            }

            records.forEach(record => {
                const row = document.createElement('tr');
                
                // Format the created_at timestamp: keep only the date part
                let formattedDate = record.created_at || '—';
                const dateSep = formattedDate.includes('T') ? 'T' : ' ';
                if (formattedDate.includes(dateSep)) {
                    formattedDate = formattedDate.split(dateSep)[0];
                }

                row.innerHTML = `
                    <td class="col-code"><a href="http://127.0.0.1:5000/${record.short_code}" target="_blank" rel="noopener noreferrer">/${record.short_code}</a></td>
                    <td class="col-url" title="${record.original_url}">
                        <a href="${record.original_url}" target="_blank" rel="noopener noreferrer">${record.original_url}</a>
                    </td>
                    <td class="col-clicks">${record.clicks}</td>
                    <td class="col-date">${formattedDate}</td>
                `;
                statsBody.appendChild(row);
            });
        } catch (error) {
            console.error("Failed to load stats:", error);
            statsBody.innerHTML = `<tr><td colspan="4" class="table-error">Failed to load analytics data.</td></tr>`;
        }
    }

    // Initial load
    loadStats();

    // Wire up the refresh button
    refreshBtn.addEventListener('click', loadStats);

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
        copyIcon.innerHTML = COPY_SVG;
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
        copyIcon.innerHTML = CHECK_SVG;
        copyText.textContent = 'Copied!';
        copyBtn.classList.add('copied');
        setTimeout(() => {
            copyIcon.innerHTML = COPY_SVG;
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

        submitBtnIcon.innerHTML = SPINNER_SVG;
        submitBtnText.textContent = 'Generating…';
        submitBtn.disabled    = true;

        try {
            const data = await createShortLink(payload);
            form.reset();
            openModal(data, expiresInHours);
            loadStats(); // Refresh the analytics table to show the new link

        } catch (err) {
            if (err.message.includes('already taken') && aliasInput) {
                const baseRedirectUrl = 'http://127.0.0.1:5000';
                showError(err.message + ' View existing link:', `${baseRedirectUrl}/${aliasInput}`);
            } else {
                showError(err.message);
            }

        } finally {
            submitBtnIcon.innerHTML = LIGHTNING_SVG;
            submitBtnText.textContent = 'Generate Short Link';
            submitBtn.disabled    = false;
        }
    });
});