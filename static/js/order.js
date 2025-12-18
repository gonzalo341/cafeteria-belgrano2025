document.addEventListener("DOMContentLoaded", () => {
    // 1. Base de datos local de productos (Array de objetos)
    const products = [
        { id: 1, name: "Espresso", price: 3000 },
        { id: 2, name: "Cappuccino", price: 4200 },
        { id: 3, name: "Moka", price: 4700 },
        { id: 4, name: "Café Frappe", price: 3800 },
        { id: 5, name: "Medialuna", price: 1500 },
        { id: 6, name: "Porción de torta", price: 2200 },
    ];

    const productSelect = document.getElementById("productSelect");
    
    // Verificamos si el elemento existe antes de continuar para evitar errores en otras páginas
    if (!productSelect) return;

    // 2. Carga dinámica de productos en el menú desplegable (DOM Manipulation)
    products.forEach(p => {
        const opt = document.createElement("option");
        opt.value = p.id;
        opt.textContent = `${p.name} - $${p.price}`;
        productSelect.appendChild(opt);
    });

    // Referencias a los elementos de la interfaz
    const quantityInput = document.getElementById("quantity");
    const totalPriceSpan = document.getElementById("totalPrice");
    const extrasCheckboxes = document.querySelectorAll(".extra-checkbox");
    const simulateBtn = document.getElementById("simulateBtn");
    const orderSummary = document.getElementById("orderSummary");

    // 3. Función lógica para calcular el precio total
    function calcularTotal() {
        const productId = parseInt(productSelect.value);
        const product = products.find(p => p.id === productId);
        const base = product ? product.price : 0;

        // Obtener multiplicador de tamaño (Radio Buttons)
        const sizeRadio = document.querySelector('input[name="size"]:checked');
        const sizeMult = sizeRadio ? parseFloat(sizeRadio.value) : 1.0;

        // Sumar valores de los extras seleccionados (Checkboxes)
        let extrasSum = 0;
        extrasCheckboxes.forEach(cb => {
            if (cb.checked) extrasSum += parseFloat(cb.dataset.price || 0);
        });

        // Validar cantidad (mínimo 1)
        const qty = Math.max(1, parseInt(quantityInput.value) || 1);

        // Fórmula de negocio: (Base * Tamaño + Extras) * Cantidad
        return Math.round((base * sizeMult + extrasSum) * qty);
    }

    // 4. Función para actualizar el texto en el HTML
    function actualizarInterfaz() {
        totalPriceSpan.textContent = `$${calcularTotal()}`;
    }

    // 5. Asignación de Event Listeners (Reactividad)
    productSelect.addEventListener("change", actualizarInterfaz);
    quantityInput.addEventListener("input", actualizarInterfaz);
    document.querySelectorAll('input[name="size"]').forEach(r => r.addEventListener("change", actualizarInterfaz));
    extrasCheckboxes.forEach(cb => cb.addEventListener("change", actualizarInterfaz));

    // 6. Manejo del botón final de simulación
    simulateBtn.addEventListener("click", () => {
        const total = calcularTotal();
        const product = products.find(p => p.id === parseInt(productSelect.value));
        
        // Mostrar el resumen oculto y actualizar su contenido
        orderSummary.classList.remove("d-none");
        orderSummary.innerHTML = `
            <h5>Resumen del pedido</h5>
            <p><strong>Producto:</strong> ${product ? product.name : "-"}</p>
            <p><strong>Total a pagar:</strong> $${total}</p>
            <div class="alert alert-info">¡Pedido simulado correctamente!</div>
        `;
    });

    // Inicializar el precio al cargar la página
    actualizarInterfaz();
});