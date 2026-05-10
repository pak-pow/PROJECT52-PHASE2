const productGrid = document.getElementById('product-grid');
const resultCount = document.getElementById('result-count');

const API_URL = 'http://127.0.0.1:5000/api/products';
let allProducts = []; // We will store the fetched products here

async function fetchProducts() {
    try {
        const response = await fetch(API_URL);
        const data = await response.json();
        
        allProducts = data.products;
        renderProducts(allProducts);
        
    } catch (error) {
        console.error("Failed to fetch products:", error);
        productGrid.innerHTML = `<p style="color: var(--danger-red); grid-column: 1/-1;">Error loading products. Is your Python server running?</p>`;
    }
}

function renderProducts(products) {
    productGrid.innerHTML = '';
    resultCount.textContent = `${products.length} Results`;

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