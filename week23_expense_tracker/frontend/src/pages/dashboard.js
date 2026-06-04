import { AuthService } from '../api/auth.js';
import { ExpenseService } from '../api/expenses.js';
import { CURRENCIES, getActiveCurrency, setActiveCurrency, formatAmount } from '../utils/currency.js';
import { getBudgets, setBudget, checkBudgets } from '../utils/budget.js';

// ── Helpers ────────────────────────────────────────────────────────
const escapeHtml = (str) => {
    if (str === null || str === undefined) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
};

const sanitizeCsvField = (val) => {
    const str = String(val || '');
    // Prefix with single quote if it starts with a formula character
    return /^[=+\-@\t\r]/.test(str) ? `'${str}` : str;
};

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
    const categorySelect = document.getElementById('category');
    const customCategoryGroup = document.getElementById('customCategoryGroup');
    const customCategoryInput = document.getElementById('customCategory');

    const filterStartDate = document.getElementById('filterStartDate');
    const filterEndDate = document.getElementById('filterEndDate');
    const filterCategory = document.getElementById('filterCategory');
    const clearFilterBtn = document.getElementById('clearFilterBtn');
    const exportCsvBtn = document.getElementById('exportCsvBtn');

    const editModal = document.getElementById('editModal');
    const editExpenseForm = document.getElementById('editExpenseForm');
    const editCategory = document.getElementById('editCategory');
    const closeEditModal = document.getElementById('closeEditModal');
    const cancelEditBtn = document.getElementById('cancelEditBtn');

    const budgetForm = document.getElementById('budgetForm');
    const budgetCategorySelect = document.getElementById('budgetCategory');
    const budgetAmountInput = document.getElementById('budgetAmount');
    const budgetListEl = document.getElementById('budgetList');
    const budgetWarningsEl = document.getElementById('budgetWarnings');

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

    // ── 4. Category Dropdown Logic ────────────────────────────────────────────
    categorySelect.addEventListener('change', () => {
        if (categorySelect.value === '__new__') {
            customCategoryGroup.classList.remove('hidden');
            customCategoryInput.required = true;
            customCategoryInput.focus();
        } else {
            customCategoryGroup.classList.add('hidden');
            customCategoryInput.required = false;
        }
    });

    // Set of base categories already in the HTML to prevent duplicates
    const baseCategories = new Set(['Food', 'Rent', 'Utilities', 'Transport', 'Entertainment']);

    // ── 5. Chart setup ────────────────────────────────────────────────────────
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

    // ── 6. Load & render expenses ─────────────────────────────────────────────
    const loadExpenses = async (filters = {}) => {
        try {
            expenseTableBody.innerHTML = '<tr><td colspan="6" class="empty-state">Loading...</td></tr>';

            const [expenses, summary] = await Promise.all([
                ExpenseService.getAll(filters),
                ExpenseService.getSummary(filters)
            ]);

            // Calculate total spending
            const totalSpending = summary.reduce((sum, row) => sum + row.total_amount, 0);
            const totalBadge = document.getElementById('totalSpendingBadge');
            if (totalBadge) {
                totalBadge.textContent = `Total: ${formatAmount(totalSpending)}`;
            }

            // Dynamically populate new categories in both dropdowns
            summary.forEach(row => {
                if (!baseCategories.has(row.category)) {
                    baseCategories.add(row.category);

                    // Add form dropdown
                    const addNewOption = categorySelect.querySelector('option[value="__new__"]');
                    const newOption = document.createElement('option');
                    newOption.value = row.category;
                    newOption.textContent = row.category;
                    categorySelect.insertBefore(newOption, addNewOption);

                    // Edit modal dropdown
                    const editOption = document.createElement('option');
                    editOption.value = row.category;
                    editOption.textContent = row.category;
                    editCategory.appendChild(editOption);
                }
            });

            // Render table
            expenseTableBody.innerHTML = '';

            if (expenses.length === 0) {
                expenseTableBody.innerHTML = '<tr><td colspan="6" class="empty-state">No expenses yet. Add one above!</td></tr>';
            } else {
                expenses.forEach(exp => {
                    const row = document.createElement('tr');
                    const safeCategory = escapeHtml(exp.category);
                    const safeDesc = escapeHtml(exp.description);
                    const safeDate = escapeHtml(exp.date);
                    
                    row.innerHTML = `
                        <td>${safeDate}</td>
                        <td>${safeCategory}</td>
                        <td class="desc-cell">${safeDesc || '<span class="no-desc">No description</span>'}</td>
                        <td><strong>${formatAmount(exp.amount)}</strong></td>
                        <td><button class="edit-btn" data-id="${exp.id}"
                                    data-amount="${exp.amount}"
                                    data-category="${escapeHtml(exp.category)}"
                                    data-date="${escapeHtml(exp.date)}"
                                    data-description="${escapeHtml(exp.description || '')}">Edit</button></td>
                        <td><button class="delete-btn" data-id="${exp.id}">Delete</button></td>
                    `;
                    expenseTableBody.appendChild(row);
                });

                // Wire delete buttons
                document.querySelectorAll('.delete-btn').forEach(btn => {
                    btn.addEventListener('click', async (e) => {
                        if (!confirm("Are you sure you want to delete this expense? This action cannot be undone.")) return;
                        const id = e.target.getAttribute('data-id');
                        await ExpenseService.delete(id);
                        loadExpenses(currentFilters());
                    });
                });

                // Wire edit buttons
                document.querySelectorAll('.edit-btn').forEach(btn => {
                    btn.addEventListener('click', (e) => {
                        const b = e.target;
                        openEditModal({
                            id: b.dataset.id,
                            amount: b.dataset.amount,
                            category: b.dataset.category,
                            date: b.dataset.date,
                            description: b.dataset.description
                        });
                    });
                });
            }

            // Render chart
            renderChart(summary);
            
            // Update filter dropdown
            updateFilterDropdown(summary);

            // Check budgets and render warnings
            renderBudgetWarnings(summary);

        } catch (error) {
            expenseTableBody.innerHTML = '<tr><td colspan="6" class="error-state">Failed to load data. Is the backend running?</td></tr>';
        }
    };

    // Helper to read current filter state
    const currentFilters = () => {
        const f = {
            start_date: filterStartDate.value,
            end_date: filterEndDate.value,
            category: filterCategory.value
        };
        Object.keys(f).forEach(key => !f[key] && delete f[key]);
        return f;
    };

    // ── Edit Modal ──────────────────────────────────────────────────
    const openEditModal = (expense) => {
        document.getElementById('editExpenseId').value = expense.id;
        document.getElementById('editAmount').value = expense.amount;
        document.getElementById('editDate').value = expense.date;
        document.getElementById('editDescription').value = expense.description;
        editCategory.value = expense.category;
        editModal.showModal();
    };

    closeEditModal.addEventListener('click', () => editModal.close());
    cancelEditBtn.addEventListener('click', () => editModal.close());

    // Close modal if user clicks the backdrop
    editModal.addEventListener('click', (e) => {
        if (e.target === editModal) editModal.close();
    });

    editExpenseForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const submitBtn = editExpenseForm.querySelector('button[type="submit"]');
        submitBtn.textContent = 'Saving...';
        submitBtn.disabled = true;

        const id = document.getElementById('editExpenseId').value;
        const payload = {
            amount: parseFloat(document.getElementById('editAmount').value),
            category: editCategory.value,
            date: document.getElementById('editDate').value,
            description: document.getElementById('editDescription').value
        };

        try {
            await ExpenseService.update(id, payload);
            editModal.close();
            loadExpenses(currentFilters());
        } catch (err) {
            alert(err.message || 'Failed to update expense.');
        } finally {
            submitBtn.textContent = 'Save Changes';
            submitBtn.disabled = false;
        }
    });

    // ── 7. Add expense form ───────────────────────────────────────────────────
    addExpenseForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const submitBtn = addExpenseForm.querySelector('button[type="submit"]');
        submitBtn.textContent = 'Saving...';
        submitBtn.disabled = true;

        let finalCategory = categorySelect.value;
        if (finalCategory === '__new__') {
            finalCategory = customCategoryInput.value.trim();
        }

        const expenseData = {
            amount: parseFloat(document.getElementById('amount').value),
            category: finalCategory,
            date: document.getElementById('date').value,
            description: document.getElementById('description').value
        };

        try {
            await ExpenseService.create(expenseData);
            
            // Reset form but keep selected category unless it was a new one
            const currentCat = categorySelect.value;
            addExpenseForm.reset();
            
            if (currentCat !== '__new__') {
                categorySelect.value = currentCat;
            } else {
                categorySelect.value = '';
                customCategoryGroup.classList.add('hidden');
                customCategoryInput.required = false;
            }
            
            loadExpenses();
        } catch (error) {
            alert(error.message || 'Failed to add expense.');
        } finally {
            submitBtn.textContent = 'Save Expense';
            submitBtn.disabled = false;
        }
    });

    // ── Budget Limits ───────────────────────────────────────────────
    const renderBudgetList = () => {
        const budgets = getBudgets();
        const categories = Object.keys(budgets);
        if (categories.length === 0) {
            budgetListEl.innerHTML = '<p class="no-desc" style="font-size:0.8rem;margin-top:0.5rem;">No limits set yet.</p>';
            return;
        }
        budgetListEl.innerHTML = categories.map(cat => {
            const safeCat = escapeHtml(cat);
            return `
            <div class="budget-list-item">
                <span class="budget-cat">${safeCat}</span>
                <span class="budget-limit">${formatAmount(budgets[cat])}/mo</span>
                <button class="budget-remove-btn" data-cat="${safeCat}" title="Remove limit">&times;</button>
            </div>
            `;
        }).join('');

        budgetListEl.querySelectorAll('.budget-remove-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                setBudget(btn.dataset.cat, 0);
                renderBudgetList();
                loadExpenses(currentFilters());
            });
        });
    };

    const renderBudgetWarnings = (summary) => {
        const warnings = checkBudgets(summary);
        if (warnings.length === 0) {
            budgetWarningsEl.innerHTML = '';
            return;
        }
        budgetWarningsEl.innerHTML = warnings.map(w => {
            const clampedPct = Math.min(w.percent, 100);
            const icon = w.exceeded ? '🚨' : '⚠️';
            const cls = w.exceeded ? 'exceeded' : 'warning';
            const safeCat = escapeHtml(w.category);
            const label = w.exceeded
                ? `<strong>${safeCat}</strong>: over budget! Spent ${formatAmount(w.spent)} of ${formatAmount(w.limit)}`
                : `<strong>${safeCat}</strong>: ${w.percent}% used (${formatAmount(w.spent)} of ${formatAmount(w.limit)})`;
            return `
                <div class="budget-warning-banner ${cls}">
                    <span class="budget-icon">${icon}</span>
                    <span style="flex:1">${label}</span>
                    <div class="budget-progress-bar">
                        <div class="budget-progress-fill" style="width:${clampedPct}%"></div>
                    </div>
                </div>`;
        }).join('');
    };

    budgetForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const cat = budgetCategorySelect.value;
        const amount = parseFloat(budgetAmountInput.value);
        if (!cat || isNaN(amount) || amount <= 0) return;
        setBudget(cat, amount);
        budgetForm.reset();
        renderBudgetList();
        loadExpenses(currentFilters());
    });

    // Initial budget list render
    renderBudgetList();

    // ── 8. Filters & Export ───────────────────────────────────────────────────
    const updateFilterDropdown = (summaryData) => {
        const currentVal = filterCategory.value;
        filterCategory.innerHTML = '<option value="All">All Categories</option>';
        summaryData.forEach(item => {
            const opt = new Option(item.category, item.category);
            filterCategory.add(opt);
        });
        filterCategory.value = currentVal || 'All';
    };

    const applyFilters = () => {
        const filters = {
            start_date: filterStartDate.value,
            end_date: filterEndDate.value,
            category: filterCategory.value
        };
        Object.keys(filters).forEach(key => !filters[key] && delete filters[key]);
        loadExpenses(filters);
    };

    filterStartDate.addEventListener('change', applyFilters);
    filterEndDate.addEventListener('change', applyFilters);
    filterCategory.addEventListener('change', applyFilters);

    clearFilterBtn.addEventListener('click', () => {
        filterStartDate.value = '';
        filterEndDate.value = '';
        filterCategory.value = 'All';
        loadExpenses();
    });

    exportCsvBtn.addEventListener('click', async () => {
        try {
            exportCsvBtn.textContent = "Exporting...";
            
            const filters = {
                start_date: filterStartDate.value,
                end_date: filterEndDate.value,
                category: filterCategory.value
            };
            Object.keys(filters).forEach(key => !filters[key] && delete filters[key]);
            
            const expenses = await ExpenseService.getAll(filters);
            if (expenses.length === 0) return alert("No data to export!");

            const headers = ['Date', 'Category', 'Description', 'Amount'];
            const csvRows = [headers.join(',')];
            
            expenses.forEach(exp => {
                const row = [
                    exp.date, 
                    `"${sanitizeCsvField(exp.category)}"`, 
                    `"${sanitizeCsvField(exp.description)}"`, 
                    exp.amount
                ];
                csvRows.push(row.join(','));
            });
            const csvString = csvRows.join('\n');

            const blob = new Blob([csvString], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.setAttribute('hidden', '');
            a.setAttribute('href', url);
            a.setAttribute('download', `expenses_export_${new Date().toISOString().split('T')[0]}.csv`);
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);

        } catch (error) {
            alert("Export failed.");
        } finally {
            exportCsvBtn.textContent = "⬇ Download CSV";
        }
    });

    // Initial load
    loadExpenses();
});