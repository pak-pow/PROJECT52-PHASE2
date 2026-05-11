const productGrid = document.getElementById('product-grid');
const resultCount = document.getElementById('result-count');
const searchInput = document.getElementById('search-input');
const filterButtons = document.querySelectorAll('.filter-btn');

const API_URL = 'http://127.0.0.1:5000/api/products';
let allProducts = [];       
let activeCategory = 'All'; 
let searchQuery = '';       

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

function renderProducts(products) {
    productGrid.innerHTML = '';

    resultCount.textContent = `${products.length} Result${products.length !== 1 ? 's' : ''}`;

    if (products.length === 0) {
        productGrid.innerHTML = `<p style="grid-column: 1/-1; color: #6c757d;">No products found matching your criteria.</p>`;
        return;
    }

    products.forEach(product => {
        const card = document.createElement('div');
        card.classList.add('product-card');
        const formattedPrice = `$${product.price.toFixed(2)}`;

        card.innerHTML = `
            <div class="product-image">${product.image}</div>
            <div class="product-info">
                <span class="product-category">${product.category}</span>
                <h4 class="product-name">${product.name}</h4>
                <div class="product-footer">
                    <span class="product-price">${formattedPrice}</span>
                    <button class="add-to-cart-btn">Add</button>
                </div>
            </div>
        `;
        
        productGrid.appendChild(card);
    });
}

// --- BOOT UP ---
fetchProducts();