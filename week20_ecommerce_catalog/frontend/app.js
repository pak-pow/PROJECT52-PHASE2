// --- DOM ELEMENTS ---
const productGrid = document.getElementById('product-grid');
const resultCount = document.getElementById('result-count');
const searchInput = document.getElementById('search-input');
const filterButtons = document.querySelectorAll('.filter-btn');

// Cart DOM Elements
const cartIconBtn = document.getElementById('cart-icon-btn');
const cartSidebar = document.getElementById('cart-sidebar');
const cartOverlay = document.getElementById('cart-overlay');
const closeCartBtn = document.getElementById('close-cart-btn');
const cartItemsContainer = document.getElementById('cart-items');
const cartTotalPrice = document.getElementById('cart-total-price');

// --- GLOBAL STATE ---
const API_URL = 'http://127.0.0.1:5000/api/products';
let allProducts = [];       
let activeCategory = 'All'; 
let searchQuery = '';       
let cart = [];

// --- API REQUEST ---
async function fetchProducts() {
    try {
        const response = await fetch(API_URL);
        const data = await response.json();
        
        allProducts = data.products; 
        applyFilters(); 
        
    } catch (error) {
        console.error("Failed to fetch products:", error);
        productGrid.innerHTML = `<p style="color: var(--danger-red); grid-column: 1/-1;">Error loading products. Is your Python server running?</p>`;
    }
}

function applyFilters() {
    let filteredProducts = allProducts;

    if (activeCategory !== 'All') {
        filteredProducts = filteredProducts.filter(product => product.category === activeCategory);
    }

    if (searchQuery !== '') {
        filteredProducts = filteredProducts.filter(product => 
            product.name.toLowerCase().includes(searchQuery)
        );
    }

    renderProducts(filteredProducts);
}

// --- CART ENGINE ---
function toggleCart() {
    cartSidebar.classList.toggle('active');
    cartOverlay.classList.toggle('active');
}

function addToCart(productId) {
    // 1. Find the product data from our global array
    const productToAdd = allProducts.find(p => p.id === productId);
    
    // 2. Check if this exact item is ALREADY in our cart
    const existingItem = cart.find(item => item.id === productId);
    
    if (existingItem) {
        // If it exists, just bump the quantity
        existingItem.quantity += 1;
    } else {
        // If it's new, add it to the cart and give it a quantity of 1
        cart.push({ ...productToAdd, quantity: 1 });
    }
    
    // 3. Update the UI and open the sidebar
    updateCartUI();
    cartSidebar.classList.add('active');
    cartOverlay.classList.add('active');
}

function removeFromCart(index) {
    cart.splice(index, 1); // Remove item at the specific index
    updateCartUI();
}

function updateCartUI() {
    // Calculate total items (e.g., 2 keyboards + 1 mouse = 3 items)
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
    cartIconBtn.textContent = `🛒 Cart (${totalItems})`;

    cartItemsContainer.innerHTML = '';
    let totalPrice = 0;

    if (cart.length === 0) {
        cartItemsContainer.innerHTML = '<p style="color: #6c757d;">Your cart is empty.</p>';
    } else {
        cart.forEach((item, index) => {
            // Calculate total price based on quantity
            const itemTotal = item.price * item.quantity;
            totalPrice += itemTotal;
            
            const cartItemDiv = document.createElement('div');
            cartItemDiv.classList.add('cart-item');
            
            // Note the PHP formatting and the (2x) quantity display!
            cartItemDiv.innerHTML = `
                <div class="cart-item-info">
                    <h4>${item.name}</h4>
                    <span class="cart-item-price">PHP ${itemTotal.toFixed(2)} (${item.quantity}x)</span>
                </div>
                <button class="remove-item-btn" onclick="removeFromCart(${index})">Remove</button>
            `;
            cartItemsContainer.appendChild(cartItemDiv);
        });
    }

    // Update the final total at the bottom
    cartTotalPrice.textContent = `PHP ${totalPrice.toFixed(2)}`;
}

// --- EVENT LISTENERS ---

// 1. Search & Filter Listeners
searchInput.addEventListener('input', (e) => {
    searchQuery = e.target.value.toLowerCase().trim();
    applyFilters();
});

filterButtons.forEach(button => {
    button.addEventListener('click', (e) => {
        filterButtons.forEach(btn => btn.classList.remove('active'));
        e.target.classList.add('active');
        activeCategory = e.target.getAttribute('data-category');
        applyFilters();
    });
});

// 2. Cart Toggle Listeners (Opens and closes the sidebar)
cartIconBtn.addEventListener('click', toggleCart);
closeCartBtn.addEventListener('click', toggleCart);
cartOverlay.addEventListener('click', toggleCart);

// 3. EVENT DELEGATION: Listen for clicks on dynamically created "Add" buttons
productGrid.addEventListener('click', (e) => {
    if (e.target.classList.contains('add-to-cart-btn')) {
        // Grab the ID we attached to the button
        const productId = parseInt(e.target.getAttribute('data-id'));
        addToCart(productId);
    }
});

// --- UI RENDERING ---
function renderProducts(products) {
    productGrid.innerHTML = '';
    resultCount.textContent = `${products.length} Result${products.length !== 1 ? 's' : ''}`;

    if (products.length === 0) {
        productGrid.innerHTML = `<p style="grid-column: 1/-1; color: #6c757d;">No products found.</p>`;
        return;
    }

    products.forEach(product => {
        const card = document.createElement('div');
        card.classList.add('product-card');
        
        // Formatted to PHP to match the cart UI
        card.innerHTML = `
            <div class="product-image">${product.image}</div>
            <div class="product-info">
                <span class="product-category">${product.category}</span>
                <h4 class="product-name">${product.name}</h4>
                <div class="product-footer">
                    <span class="product-price">PHP ${product.price.toFixed(2)}</span>
                    <button class="add-to-cart-btn" data-id="${product.id}">Add</button>
                </div>
            </div>
        `;
        productGrid.appendChild(card);
    });
}

// --- BOOT UP ---
fetchProducts();