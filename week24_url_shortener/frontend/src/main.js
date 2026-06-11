import { createShortLink } from './api/url_api.js';

document.addEventListener('DOMContentLoaded', () => {

    const form = document.getElementById('shorten-form');
    const errorContainer = document.getElementById('form-error');
    const resultCard = document.getElementById('result-card');
    const shortUrlResult = document.getElementById('short-url-result');
    const deathClockDisplay = document.getElementById('death-clock-display');
    const submitButton = form.querySelector('button[type="submit"]');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        errorContainer.classList.add('hidden');
        errorContainer.textContent = '';
        resultCard.classList.add('hidden');
        
        const originalButtonText = submitButton.textContent;
        submitButton.textContent = 'Generating...';
        submitButton.disabled = true;

        const urlInput = document.getElementById('url').value.trim();
        const aliasInput = document.getElementById('custom-alias').value.trim();
        const expiresInput = document.getElementById('expires-in').value;

        const payload = { url: urlInput };
        if (aliasInput) payload.custom_alias = aliasInput;
        if (expiresInput) payload.expires_in_hours = parseInt(expiresInput, 10);

        try {
            const data = await createShortLink(payload);

            shortUrlResult.href = data.short_url;
            shortUrlResult.textContent = data.short_url;

            if (payload.expires_in_hours) {
                deathClockDisplay.textContent = `⚠️ This link will self-destruct in ${payload.expires_in_hours} hours.`;
            } else {
                deathClockDisplay.textContent = ''; 
            }

            resultCard.classList.remove('hidden');
            form.reset();

        } catch (error) {
            errorContainer.textContent = error.message;
            errorContainer.classList.remove('hidden');
        } finally {
            submitButton.textContent = originalButtonText;
            submitButton.disabled = false;
        }
    });
});