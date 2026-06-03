/**
 * currency.js — Currency display utility
 * Handles currency selection, formatting, and localStorage persistence.
 * Uses the browser's built-in Intl.NumberFormat — no external API needed.
 */

export const CURRENCIES = [
    { code: 'PHP', symbol: '₱', label: 'Philippine Peso',    locale: 'en-PH' },
    { code: 'USD', symbol: '$', label: 'US Dollar',           locale: 'en-US' },
    { code: 'EUR', symbol: '€', label: 'Euro',                locale: 'de-DE' },
    { code: 'GBP', symbol: '£', label: 'British Pound',       locale: 'en-GB' },
    { code: 'JPY', symbol: '¥', label: 'Japanese Yen',        locale: 'ja-JP' },
    { code: 'SGD', symbol: 'S$', label: 'Singapore Dollar',   locale: 'en-SG' },
    { code: 'AUD', symbol: 'A$', label: 'Australian Dollar',  locale: 'en-AU' },
    { code: 'CAD', symbol: 'C$', label: 'Canadian Dollar',    locale: 'en-CA' },
    { code: 'KRW', symbol: '₩', label: 'Korean Won',          locale: 'ko-KR' },
    { code: 'CNY', symbol: '¥', label: 'Chinese Yuan',        locale: 'zh-CN' },
];

const STORAGE_KEY = 'preferred_currency';
const DEFAULT_CODE = 'PHP';

/**
 * Get the currently selected currency object.
 */
export function getActiveCurrency() {
    const saved = localStorage.getItem(STORAGE_KEY) || DEFAULT_CODE;
    return CURRENCIES.find(c => c.code === saved) || CURRENCIES[0];
}

/**
 * Save a currency code to localStorage.
 * @param {string} code - e.g. 'PHP', 'USD'
 */
export function setActiveCurrency(code) {
    localStorage.setItem(STORAGE_KEY, code);
}

/**
 * Format a numeric amount in the currently active currency.
 * @param {number} amount
 * @returns {string} e.g. '₱ 1,200.00'
 */
export function formatAmount(amount) {
    const currency = getActiveCurrency();
    return new Intl.NumberFormat(currency.locale, {
        style: 'currency',
        currency: currency.code,
        minimumFractionDigits: currency.code === 'JPY' || currency.code === 'KRW' ? 0 : 2,
        maximumFractionDigits: currency.code === 'JPY' || currency.code === 'KRW' ? 0 : 2,
    }).format(amount);
}
