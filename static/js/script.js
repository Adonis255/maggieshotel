let allDishes = [];
let allCategories = [];

// Open/Closed Logic (6am - 10pm)
const statusBadge = document.getElementById('statusBadgeTop');
const hours = new Date().getHours();
if (hours >= 6 && hours < 22) {
    statusBadge.style.background = "#00cc66";
} else {
    statusBadge.style.background = "#e74c3c";
}

async function fetchMenu() {
    try {
        const [menuRes, catRes] = await Promise.all([
            fetch('/api/menu'),
            fetch('/api/categories')
        ]);
        allDishes = await menuRes.json();
        allCategories = await catRes.json();
        renderCategories();
        renderDishes(allDishes);
    } catch (err) { console.error("Error loading menu:", err); }
}

function renderCategories() {
    const container = document.getElementById('categoryFilter');
    const select = document.getElementById('mobileCatSelect');
    
    // Reset both
    container.innerHTML = `<button class="cat-btn active" onclick="filterDishes('All')">All Dishes</button>`;
    select.innerHTML = `<option value="All">All Dishes</option>`;
    
    allCategories.forEach(cat => {
        container.innerHTML += `<button class="cat-btn" onclick="filterDishes(${cat.id})">${cat.name}</button>`;
        select.innerHTML += `<option value="${cat.id}">${cat.name}</option>`;
    });
}

// Event listener for the Mobile Dropdown
document.getElementById('mobileCatSelect').addEventListener('change', function() {
    filterDishes(this.value);
});

function renderDishes(dishes) {
    const grid = document.getElementById('menuGrid');
    grid.innerHTML = '';
    
    // FIX EMPTY STATE
    if (dishes.length === 0) {
        grid.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; color: #ccc; padding: 50px; font-size: 1.2rem;">
                No menu items available yet.<br> 
                <span style="font-size: 0.9rem; color: #888;">Add categories and dishes from the Admin Panel!</span>
            </div>
        `;
        return;
    }

    dishes.forEach(d => {
        grid.innerHTML += `
            <div class="dish-card">
                <img src="${d.image_url || 'https://via.placeholder.com/300x200?text=No+Image'}" alt="${d.name}" loading="lazy">
                <div class="dish-content">
                    <div class="dish-title">${d.name}</div>
                    <div class="dish-desc">${d.description || 'Delicious local meal served fresh.'}</div>
                    <div class="dish-price">Ksh ${d.price}</div>
                </div>
            </div>
        `;
    });
}

document.getElementById('searchInput').addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase();
    const filtered = allDishes.filter(d => d.name.toLowerCase().includes(query));
    renderDishes(filtered);
});

function filterDishes(categoryId) {
    document.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('active'));
    // Update the visual states for both desktop and mobile
    if(event && event.target && event.target.tagName === 'BUTTON') {
        event.target.classList.add('active');
    }
    // Sync the select dropdown if category is passed
    if(categoryId !== 'All') {
        document.getElementById('mobileCatSelect').value = categoryId;
    } else {
        document.getElementById('mobileCatSelect').value = 'All';
    }
    
    if (categoryId === 'All') renderDishes(allDishes);
    else renderDishes(allDishes.filter(d => d.category_id == categoryId));
}

fetchMenu();