import { AuthService } from '../api/auth.js';
import { ExpenseService } from '../api/expenses.js';

document.addEventListener('DOMContentLoaded', async () => {
    if (!AuthService.isAuthenticated()) {
        window.location.href = 'login.html';
        return;
    }

    const welcomeMessage = document.getElementById('welcomeMessage');
    const logoutBtn = document.getElementById('logoutBtn');
    const expenseTableBody = document.getElementById('expenseTableBody');
    const addExpenseForm = document.getElementById('addExpenseForm');

    let expenseChartInstance = null;

    logoutBtn.addEventListener('click', () => {
        AuthService.logout();
    });

    try {
        const user = await AuthService.getMe();
        welcomeMessage.textContent = `Welcome, ${user.username}`;
    } catch (error) {
        console.error("Failed to load user profile");
    }

    const renderChart = async () => {
        try {
            const summaryData = await ExpenseService.getSummary();
            const ctx = document.getElementById('expenseChart').getContext('2d');

            if (expenseChartInstance) {
                expenseChartInstance.destroy();
            }

            const labels = summaryData.map(item => item.category);
            const data = summaryData.map(item => item.total_amount);

            expenseChartInstance = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        data: data,
                        backgroundColor: [
                            '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6'
                        ],
                        borderWidth: 0,
                        hoverOffset: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'right' }
                    }
                }
            });
        } catch (error) {
            console.error("Failed to render chart:", error);
        }
    };

    const loadExpenses = async () => {
        try {
            expenseTableBody.innerHTML = '<tr><td colspan="4">Loading...</td></tr>';
            const expenses = await ExpenseService.getAll();
            
            expenseTableBody.innerHTML = '';
            
            if (expenses.length === 0) {
                expenseTableBody.innerHTML = '<tr><td colspan="4">No expenses found. Add one!</td></tr>';
                renderChart(); 
                return;
            }

            expenses.forEach(exp => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${exp.date}</td>
                    <td>${exp.category}</td>
                    <td>$${parseFloat(exp.amount).toFixed(2)}</td>
                    <td><button class="text-red delete-btn" data-id="${exp.id}">Delete</button></td>
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

            renderChart(); 

        } catch (error) {
            expenseTableBody.innerHTML = '<tr><td colspan="4" style="color:red;">Failed to load data.</td></tr>';
        }
    };

    addExpenseForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
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
            alert(error.message || "Failed to add expense.");
        }
    });

    loadExpenses();
});