import { createShortLink, getStats, checkHealth } from './api/url_api.js';

// ── SVG Icon Templates ──────────────────────────────────────────
const COPY_SVG      = `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg" style="width:14px;height:14px"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>`;
const CHECK_SVG     = `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg" style="width:14px;height:14px"><polyline points="20 6 9 17 4 12"></polyline></svg>`;
const LIGHTNING_SVG = `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg" style="width:18px;height:18px"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>`;
const SPINNER_SVG   = `<svg class="icon animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" xmlns="http://www.w3.org/2000/svg" style="width:18px;height:18px"><circle cx="12" cy="12" r="10" stroke="rgba(255,255,255,0.25)" fill="none"></circle><path d="M4 12a8 8 0 0 1 8-8" stroke="currentColor"></path></svg>`;

document.addEventListener('DOMContentLoaded', () => {

    // ── DOM refs ─────────────────────────────────────────────────
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

    const statsBody     = document.getElementById('stats-body');
    const refreshBtn    = document.getElementById('refresh-stats');

    // ── Offline Banner refs ───────────────────────────────────────
    const offlineBanner      = document.getElementById('offline-banner');
    const offlineBannerBody  = offlineBanner.querySelector('.offline-banner__body');
    const offlineRetryStatus = document.getElementById('offline-retry-status');

    // ── Helpers ───────────────────────────────────────────────────
    function showError(msg, linkUrl = null) {
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

    // ── Analytics Table ───────────────────────────────────────────
    async function loadStats() {
        try {
            const records = await getStats();
            statsBody.innerHTML = '';

            if (records.length === 0) {
                statsBody.innerHTML = `<tr><td colspan="4" class="empty-state">No links generated yet.</td></tr>`;
                return;
            }

            records.forEach(record => {
                const row = document.createElement('tr');

                // Keep only the date portion of the timestamp
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
            console.error('Failed to load stats:', error);
            statsBody.innerHTML = `<tr><td colspan="4" class="table-error">Failed to load analytics data.</td></tr>`;
        }
    }

    loadStats();
    refreshBtn.addEventListener('click', loadStats);

    // ── Connection Monitor ────────────────────────────────────────
    // On page load, pings /api/health. If unreachable: shows an amber
    // "Backend Offline" banner with a live countdown and disables the form.
    // Polls every 10 s; when the server comes back it flashes a green
    // "Back Online" banner for 3 s then dismisses itself automatically.
    const POLL_INTERVAL_MS = 10_000;
    let isOffline        = false;
    let pollTimer        = null;
    let countdownTimer   = null;
    let retrySecondsLeft = 0;

    function startCountdown(seconds) {
        retrySecondsLeft = seconds;
        clearInterval(countdownTimer);
        countdownTimer = setInterval(() => {
            retrySecondsLeft -= 1;
            if (retrySecondsLeft <= 0) {
                offlineRetryStatus.textContent = 'Retrying now…';
                clearInterval(countdownTimer);
            } else {
                offlineRetryStatus.textContent = `Retrying in ${retrySecondsLeft}s…`;
            }
        }, 1000);
    }

    function showOfflineBanner() {
        offlineBanner.classList.remove('hidden', 'offline-banner--reconnected');
        offlineBannerBody.querySelector('strong').textContent = 'Backend Offline';
        offlineBannerBody.querySelector('span').innerHTML =
            'Cannot reach the server at <code>127.0.0.1:5000</code>. Run <code>python run.py</code> to start it.';
        startCountdown(POLL_INTERVAL_MS / 1000);
    }

    function showReconnectedBanner() {
        offlineBanner.classList.remove('hidden');
        offlineBanner.classList.add('offline-banner--reconnected');
        offlineBannerBody.querySelector('strong').textContent = 'Back Online';
        offlineBannerBody.querySelector('span').innerHTML =
            'Connected to <code>127.0.0.1:5000</code>. Everything is working again.';
        offlineRetryStatus.textContent = '';
        clearInterval(countdownTimer);
        setTimeout(() => offlineBanner.classList.add('hidden'), 3000);
    }

    async function checkConnection() {
        const alive = await checkHealth();

        if (!alive && !isOffline) {
            // Just went offline
            isOffline = true;
            showOfflineBanner();
            submitBtn.disabled = true;

            pollTimer = setInterval(async () => {
                const back = await checkHealth();
                if (back) {
                    isOffline = false;
                    clearInterval(pollTimer);
                    showReconnectedBanner();
                    submitBtn.disabled = false;
                    loadStats();
                } else {
                    showOfflineBanner(); // resets the countdown
                }
            }, POLL_INTERVAL_MS);

        } else if (alive && isOffline) {
            // Edge-case: came back online between polls
            isOffline = false;
            clearInterval(pollTimer);
            showReconnectedBanner();
            submitBtn.disabled = false;
        }
        // alive && !isOffline → server is fine, do nothing
    }

    // Run immediately on load
    checkConnection();

    // ── Modal ─────────────────────────────────────────────────────
    // Guard: track when the modal was opened so accidental backdrop clicks
    // or stray keyboard events within the first 400 ms cannot close it.
    let modalOpenedAt = 0;

    function openModal(data, expiresInHours) {
        const shortUrl = data.short_url;
        shortUrlLink.href        = shortUrl;
        shortUrlLink.textContent = shortUrl;
        metaOriginal.textContent = data.original_url;
        metaOriginal.title       = data.original_url;
        metaClicks.textContent   = data.clicks ?? 0;

        if (expiresInHours) {
            expiryText.textContent = `Self-destructs in ${expiresInHours} hour${expiresInHours !== 1 ? 's' : ''}`;
            expiryBadge.classList.remove('hidden');
        } else {
            expiryBadge.classList.add('hidden');
        }

        copyIcon.innerHTML   = COPY_SVG;
        copyText.textContent = 'Copy';
        copyBtn.classList.remove('copied');
        modalOpenedAt = Date.now();
        modal.classList.add('open');
    }

    function closeModal() {
        // Ignore close requests that arrive within 400 ms of the modal opening.
        // This prevents stray events (queued clicks, focus events) from
        // instantly dismissing the modal right after a successful submission.
        if (Date.now() - modalOpenedAt < 400) return;
        modal.classList.remove('open');
        // Re-enable the submit button now that the user has dismissed the modal.
        submitBtn.disabled = false;
    }

    // ── Copy to clipboard ─────────────────────────────────────────
    copyBtn.addEventListener('click', async () => {
        const url = shortUrlLink.href;
        try {
            await navigator.clipboard.writeText(url);
        } catch {
            const ta = document.createElement('textarea');
            ta.value = url;
            document.body.appendChild(ta);
            ta.select();
            document.execCommand('copy');
            document.body.removeChild(ta);
        }
        copyIcon.innerHTML   = CHECK_SVG;
        copyText.textContent = 'Copied!';
        copyBtn.classList.add('copied');
        setTimeout(() => {
            copyIcon.innerHTML   = COPY_SVG;
            copyText.textContent = 'Copy';
            copyBtn.classList.remove('copied');
        }, 2500);
    });

    // ── Close modal ───────────────────────────────────────────────
    modalCloseBtn.addEventListener('click', closeModal);
    newLinkBtn.addEventListener('click', closeModal);
    modal.addEventListener('click', (e) => { if (e.target === modal) closeModal(); });
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.classList.contains('open')) closeModal();
    });

    // ── Form submit ───────────────────────────────────────────────
    let isSubmitting = false;  // guard against double-submission

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        if (isSubmitting) return;  // ignore re-entrant submissions
        isSubmitting = true;
        clearError();

        const urlInput       = document.getElementById('url').value.trim();
        const aliasInput     = document.getElementById('custom-alias').value.trim();
        const expiresRaw     = document.getElementById('expires-in').value.trim();
        const expiresInHours = expiresRaw !== '' ? parseInt(expiresRaw, 10) : null;

        if (!urlInput) {
            showError('Please enter a URL.');
            isSubmitting = false;
            return;
        }

        const payload = { url: urlInput };
        if (aliasInput)     payload.custom_alias    = aliasInput;
        if (expiresInHours) payload.expires_in_hours = expiresInHours;

        submitBtnIcon.innerHTML  = SPINNER_SVG;
        submitBtnText.textContent = 'Generating…';
        submitBtn.disabled = true;

        let succeeded = false;
        try {
            const data = await createShortLink(payload);
            succeeded = true;
            openModal(data, expiresInHours);
            form.reset();   // reset AFTER modal opens so focus moves to modal
            loadStats();
        } catch (err) {
            if (err.message.includes('already taken') && aliasInput) {
                showError(err.message + ' View existing link:', `http://127.0.0.1:5000/${aliasInput}`);
            } else {
                showError(err.message);
            }
        } finally {
            isSubmitting = false;
            submitBtnIcon.innerHTML  = LIGHTNING_SVG;
            submitBtnText.textContent = 'Generate Short Link';
            // Only re-enable the button if the modal is NOT showing.
            // When the modal IS open, the button will be re-enabled by closeModal
            // (via the "Shorten another link" button flow) so the form is ready
            // for the next entry without disrupting the modal.
            if (!succeeded) {
                submitBtn.disabled = false;
            }
        }
    });
});