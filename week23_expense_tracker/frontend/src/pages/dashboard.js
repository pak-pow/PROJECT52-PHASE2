import { AuthService } from '../api/auth.js';
import { ExpenseService } from '../api/expenses.js';

document.addEventListener('DOMContentLoaded', async () => {
    if (!AuthService.isAuthenticated()) {
        window.location.href = '/public/login.html';
        return;
    }

    const welcomeMessage = document.getElementById('welcomeMessage');
    const logoutBtn = document.getElementById('logoutBtn');
    const expenseTableBody = document.getElementById('expenseTableBody');
    const addExpenseForm = document.getElementById('addExpenseForm');

    logoutBtn.addEventListener('click', () => {
        AuthService.logout();
    });

    try {
        const user = await AuthService.getMe();
        welcomeMessage.textContent = `Welcome, ${user.username}`;
    } catch (error) {
        console.error("Failed to load user profile");
    }

    const loadExpenses = async () => {
        try {
            expenseTableBody.innerHTML = '<tr><td colspan="4">Loading...</td></tr>';
            const expenses = await ExpenseService.getAll();
            
            expenseTableBody.innerHTML = ''; 
            
            if (expenses.length === 0) {
                expenseTableBody.innerHTML = '<tr><td colspan="4">No expenses found. Add one!</td></tr>';
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