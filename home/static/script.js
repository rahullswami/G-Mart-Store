// const products = [
//     { id: 1, name: "The Great Gatsby", author: "F. Scott Fitzgerald", price: 499, img: "https://via.placeholder.com/200" },
//     { id: 2, name: "1984", author: "George Orwell", price: 399, img: "https://via.placeholder.com/200" },
//     { id: 3, name: "To Kill a Mockingbird", author: "Harper Lee", price: 299, img: "https://via.placeholder.com/200" }
// ];

// const productList = document.getElementById('product-list');

// // Load Products
// products.forEach(product => {
//     const productCard = `
//         <div class="col-md-4 mb-4">
//             <div class="card product-card">
//                 <img src="${product.img}" class="card-img-top" alt="${product.name}">
//                 <div class="card-body">
//                     <h5 class="card-title">${product.name}</h5>
//                     <p class="card-text">Author: ${product.author}</p>
//                     <p class="card-text"><strong>₹${product.price}</strong></p>
//                     <button class="btn btn-danger">Add to Cart</button>
//                 </div>
//             </div>
//         </div>
//     `;
//     productList.innerHTML += productCard;
// });



// //  cart coding startrin 

// const cart = [
//     { id: 1, name: "The Great Gatsby", price: 499, quantity: 1 },
//     { id: 2, name: "1984", price: 399, quantity: 2 },
//     { id: 3, name: "To Kill a Mockingbird", price: 299, quantity: 1 }
// ];

// const cartItems = document.getElementById('cart-items');
// const cartTotal = document.getElementById('cart-total');

// // Render Cart Items
// function renderCart() {
//     cartItems.innerHTML = '';
//     let total = 0;

//     cart.forEach(item => {
//         const itemTotal = item.price * item.quantity;
//         total += itemTotal;

//         const row = `
//             <tr>
//                 <td>${item.name}</td>
//                 <td>
//                     <input type="number" min="1" value="${item.quantity}" 
//                            class="form-control quantity-input" 
//                            data-id="${item.id}">
//                 </td>
//                 <td>₹${item.price}</td>
//                 <td>₹${itemTotal}</td>
//                 <td>
//                     <button class="btn btn-danger btn-sm" onclick="removeItem(${item.id})">Remove</button>
//                 </td>
//             </tr>
//         `;
//         cartItems.innerHTML += row;
//     });

//     cartTotal.textContent = `Grand Total: ₹${total}`;
// }

// // Update Quantity
// document.addEventListener('input', (e) => {
//     if (e.target.classList.contains('quantity-input')) {
//         const id = parseInt(e.target.dataset.id);
//         const newQuantity = parseInt(e.target.value);

//         const item = cart.find(item => item.id === id);
//         if (item) {
//             item.quantity = newQuantity;
//         }
//         renderCart();
//     }
// });

// // Remove Item
// function removeItem(id) {
//     const index = cart.findIndex(item => item.id === id);
//     if (index !== -1) {
//         cart.splice(index, 1);
//     }
//     renderCart();
// }

// // Initial Render
// renderCart();



// // order hitory 

// const orders = [
//     {
//         orderId: 101,
//         products: [
//             { name: "The Great Gatsby", quantity: 1 },
//             { name: "1984", quantity: 2 }
//         ],
//         totalPrice: 1297,
//         date: "2024-12-01"
//     },
//     {
//         orderId: 102,
//         products: [
//             { name: "To Kill a Mockingbird", quantity: 1 },
//             { name: "The Alchemist", quantity: 3 }
//         ],
//         totalPrice: 1696,
//         date: "2024-12-05"
//     }
// ];

// const orderHistory = document.getElementById('order-history');

// // Render Orders
// orders.forEach(order => {
//     const productDetails = order.products
//         .map(product => `${product.name} (x${product.quantity})`)
//         .join(", ");

//     const row = `
//         <tr>
//             <td>${order.orderId}</td>
//             <td>${productDetails}</td>
//             <td>${order.products.reduce((sum, p) => sum + p.quantity, 0)}</td>
//             <td>₹${order.totalPrice}</td>
//             <td>${order.date}</td>
//         </tr>
//     `;
//     orderHistory.innerHTML += row;
// });



// Get the current date and time
const now = new Date();

// Set the target date and time for Valentine's Day
const valentinesDay = new Date('February 14, 2024 00:00:00'); // Update year accordingly

// Calculate the difference in milliseconds
const diff = valentinesDay - now;

// Calculate days, hours, minutes, and seconds
const days = Math.floor(diff / (1000 * 60 * 60 * 24));
const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
const seconds = Math.floor((diff % (1000 * 60)) / 1000);

// Display the countdown on the page
document.getElementById('countdown').innerHTML = 
    `${days}d ${hours}h ${minutes}m ${seconds}s`;

// Update the countdown every second
setInterval(() => {
    // Recalculate the difference
    const now = new Date();
    const diff = valentinesDay - now;

    // Update days, hours, minutes, and seconds
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((diff % (1000 * 60)) / 1000);

    // Update the display
    document.getElementById('countdown').innerHTML = 
        `${days}d ${hours}h ${minutes}m ${seconds}s`;
}, 1000);