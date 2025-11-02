// --- Regisrto en la base de datos ---
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("registerForm");
    const mensajeDiv = document.getElementById("mensajeCliente");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        mensajeDiv.innerHTML = "";

        try {
            const formData = new FormData(form);
            const BACKEND_URL = "http://127.0.0.1:5050/register";

            const resp = await fetch(BACKEND_URL, {
                method: "POST",
                body: formData,
            });

            const result = await resp.json();

            if (resp.ok) {
                mensajeDiv.innerHTML = `<div class="alert alert-success" role="alert">${result.message}</div>`;
                form.reset();
            } else {
                mensajeDiv.innerHTML = `<div class="alert alert-danger" role="alert">${result.error || result.message || 'Error'}</div>`;
            }
        } catch (err) {
            console.error(err);
            mensajeDiv.innerHTML = `<div class="alert alert-danger" role="alert">Error en el cliente: ${err.message}</div>`;
        }
    });
});

// --- Calculadora de pedidos ---
document.addEventListener("DOMContentLoaded", function () {
    const products = [
        { id: 1, name: "Espresso", price: 3000 },
        { id: 2, name: "Cappuccino", price: 4200 },
        { id: 3, name: "Moka", price: 4700 },
        { id: 4, name: "Café Frappe", price: 3800 },
        { id: 5, name: "Medialuna", price: 1500 },
        { id: 6, name: "Porción de torta", price: 2200 },
    ];

    const productSelect = document.getElementById("productSelect");
    if (productSelect) {
        products.forEach(p => {
            const opt = document.createElement("option");
            opt.value = p.id;
            opt.textContent = `${p.name} - $${p.price}`;
            productSelect.appendChild(opt);
        });

        const quantityInput = document.getElementById("quantity");
        const totalPriceSpan = document.getElementById("totalPrice");
        const extrasCheckboxes = document.querySelectorAll(".extra-checkbox");
        const simulateBtn = document.getElementById("simulateBtn");
        const orderSummary = document.getElementById("orderSummary");

        function getSelectedProduct() {
            const id = parseInt(productSelect.value, 10);
            return products.find(p => p.id === id);
        }

        function getSizeMultiplier() {
            const radios = document.getElementsByName("size");
            for (let r of radios) {
                if (r.checked) return parseFloat(r.value);
            }
            return 1.0;
        }

        function getExtrasSum() {
            let sum = 0;
            extrasCheckboxes.forEach(cb => {
                if (cb.checked) sum += parseFloat(cb.dataset.price || 0);
            });
            return sum;
        }

        function calculateTotal() {
            const product = getSelectedProduct();
            const qty = Math.max(1, parseInt(quantityInput.value, 10) || 1);
            const sizeMult = getSizeMultiplier();
            const extras = getExtrasSum();
            const base = product ? product.price : 0;
            const total = Math.round((base * sizeMult + extras) * qty);
            return total;
        }

        function updateUI() {
            const total = calculateTotal();
            totalPriceSpan.textContent = `$${total}`;
        }

        // EventListeners
        productSelect.addEventListener("change", updateUI);
        quantityInput.addEventListener("input", updateUI);
        document.getElementsByName("size").forEach(r => r.addEventListener("change", updateUI));
        extrasCheckboxes.forEach(cb => cb.addEventListener("change", updateUI));

        updateUI();

        // Simular pedido
        simulateBtn.addEventListener("click", function () {
            const product = getSelectedProduct();
            const qty = Math.max(1, parseInt(quantityInput.value, 10) || 1);
            const sizeMult = getSizeMultiplier();
            const extras = Array.from(extrasCheckboxes)
                .filter(cb => cb.checked)
                .map(cb => {
                    return {
                        name: cb.nextElementSibling ? cb.nextElementSibling.textContent.split(" (+")[0] : cb.id,
                        price: parseFloat(cb.dataset.price || 0)
                    };
                });

            const total = calculateTotal();

            let html = `<h5>Resumen del pedido</h5>`;
            html += `<p><strong>Producto:</strong> ${product ? product.name : "—"}</p>`;
            html += `<p><strong>Tamaño:</strong> ${sizeMult === 1 ? "Pequeño" : sizeMult === 1.3 ? "Mediano" : "Grande"}</p>`;
            if (extras.length > 0) {
                html += `<p><strong>Extras:</strong></p><ul>`;
                extras.forEach(ex => html += `<li>${ex.name} (+$${ex.price})</li>`);
                html += `</ul>`;
            } else {
                html += `<p><strong>Extras:</strong> Ninguno</p>`;
            }
            html += `<p><strong>Cantidad:</strong> ${qty}</p>`;
            html += `<p><strong>Total:</strong> $${total}</p>`;

            orderSummary.innerHTML = html;
            orderSummary.classList.remove("d-none");
            orderSummary.scrollIntoView({ behavior: "smooth" });
        });
    }
});
