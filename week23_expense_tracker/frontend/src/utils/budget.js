/**
 * budget.js — Monthly budget limits utility
 * Stores per-category budget limits in localStorage.
 * No backend required — budgets are a user preference, not financial data.
 */

const STORAGE_KEY = 'expense_tracker_budgets';

/**
 * Returns all saved budgets as an object: { Food: 5000, Rent: 15000, ... }
 */
export const getBudgets = () => {
    try {
        return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {};
    } catch {
        return {};
    }
};

/**
 * Saves a budget for a specific category.
 * Pass amount = 0 or null to remove the limit.
 */
export const setBudget = (category, amount) => {
    const budgets = getBudgets();
    if (!amount || amount <= 0) {
        delete budgets[category];
    } else {
        budgets[category] = parseFloat(amount);
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(budgets));
};

/**
 * Compares current spending summary against saved budgets.
 * Returns an array of warning objects:
 * [{ category, spent, limit, percent, exceeded }]
 */
export const checkBudgets = (summary) => {
    const budgets = getBudgets();
    const warnings = [];

    summary.forEach(row => {
        const limit = budgets[row.category];
        if (!limit) return; // No budget set for this category

        const percent = (row.total_amount / limit) * 100;
        warnings.push({
            category: row.category,
            spent: row.total_amount,
            limit,
            percent: Math.round(percent),
            exceeded: percent >= 100
        });
    });

    // Sort: exceeded first, then by % descending
    return warnings.sort((a, b) => b.percent - a.percent);
};
