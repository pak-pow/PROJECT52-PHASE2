import { AuthService } from '../api/auth.js';
import { ExpenseService } from '../api/expenses.js';
import { CURRENCIES, getActiveCurrency, setActiveCurrency, formatAmount } from '../utils/currency.js';

document.addEventListener('DOMContentLoaded', async () => {
    if (!AuthService.isAuthenticated()) {
        window.location.href = 'login.html';
        return;
    }

    const welcomeMessage = document.getElementById('welcomeMessage');
    const logoutBtn = document.getElementById('logoutBtn');
    const expenseTableBody = document.getElementById('expenseTableBody');
    const addExpenseForm = document.getElementById('addExpenseForm');
    const currencySelect = document.getElementById('currencySelect');

    // ── 1. Populate the currency dropdown ────────────────────────────────────
    const active = getActiveCurrency();
    CURRENCIES.forEach(c => {
        const option = document.createElement('option');
        option.value = c.code;
        option.textContent = `${c.symbol} ${c.code} — ${c.label}`;
        if (c.code === active.code) option.selected = true;
        currencySelect.appendChild(option);
    });

    // When the user picks a different currency, save it and re-render
    currencySelect.addEventListener('change', () => {
        setActiveCurrency(currencySelect.value);
        loadExpenses();
    });

    // ── 2. Logout ─────────────────────────────────────────────────────────────
    logoutBtn.addEventListener('click', () => AuthService.logout());

    // ── 3. Load user profile ──────────────────────────────────────────────────
    try {
        const user = await AuthService.getMe();
        welcomeMessage.textContent = `Welcome, ${user.username}`;
    } catch {
        console.error('Failed to load user profile');
    }

    // ── 4. Chart setup ────────────────────────────────────────────────────────
    let expenseChart = null;

    function renderChart(summaryData) {
        const ctx = document.getElementById('expenseChart');
        if (!ctx) return;

        const labels = summaryData.map(row => row.category);
        const values = summaryData.map(row => row.total_amount);
        const palette = [
            '#3b82f6', '#f59e0b', '#10b981', '#ef4444',
            '#8b5cf6', '#ec4899', '#06b6d4', '#f97316',
            '#84cc16', '#6366f1',
        ];

        if (expenseChart) expenseChart.destroy();

        expenseChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels,
                datasets: [{
                    data: values,
                    backgroundColor: palette.slice(0, labels.length),
                    borderWidth: 2,
                    borderColor: '#ffffff',
                    hoverOffset: 6,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '65%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 16,
                            font: { size: 12 },
                            color: '#64748b',
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => {
                                const value = ctx.parsed;
                                return `  ${ctx.label}: ${formatAmount(value)}`;
                            }
                        }
                    }
                }
            }
        });
    }

    // ── 5. Load & render expenses ─────────────────────────────────────────────
    const loadExpenses = async () => {
        try {
            expenseTableBody.innerHTML = '<tr><td colspan="4" style="text-align:center;padding:2rem;color:#94a3b8;">Loading...</td></tr>';

            const [expenses, summary] = await Promise.all([
                ExpenseService.getAll(),
                ExpenseService.getSummary()
            ]);

            // Render table
            expenseTableBody.innerHTML = '';

            if (expenses.length === 0) {
                expenseTableBody.innerHTML = '<tr><td colspan="4" style="text-align:center;padding:2rem;color:#94a3b8;">No expenses yet. Add one above!</td></tr>';
            } else {
                expenses.forEach(exp => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${exp.date}</td>
                        <td>${exp.category}</td>
                        <td><strong>${formatAmount(exp.amount)}</strong></td>
                        <td><button class="delete-btn" data-id="${exp.id}">Delete</button></td>
                    `;
                    expenseTableBody.appendChild(row);
                });

                document.querySelectorAll('.delete-btn').forEach(btn => {
                    btn.addEventListener('click', async (e) => {
                        const id = e.target.getAttribute('data-id');
                        await ExpenseService.delete(id);
                        loadExpenses();
                    });
                });
            }

            // Render chart
            renderChart(summary);

        } catch (error) {
            expenseTableBody.innerHTML = '<tr><td colspan="4" style="text-align:center;padding:2rem;color:#ef4444;">Failed to load data. Is the backend running?</td></tr>';
        }
    };

    // ── 6. Add expense form ───────────────────────────────────────────────────
    addExpenseForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const submitBtn = addExpenseForm.querySelector('button[type="submit"]');
        submitBtn.textContent = 'Saving...';
        submitBtn.disabled = true;

        const expenseData = {
            amount: parseFloat(document.getElementById('amount').value),
            category: document.getElementById('category').value,
            date: document.getElementById('date').value,
            description: document.getElementById('description').value
        };

        try {
            await ExpenseService.create(expenseData);
            addExpenseForm.reset();
            loadExpenses();
        } catch (error) {
            alert(error.message || 'Failed to add expense.');
        } finally {
            submitBtn.textContent = 'Save Expense';
            submitBtn.disabled = false;
        }
    });

    // Initial load
    loadExpenses();
});