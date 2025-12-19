document.addEventListener("DOMContentLoaded", () => {   // Esto asegura que el código se ejecute solo cuando el HTML ya esté cargado.
    // ----------------------------------------------
    //  Lista de productos (datos)
    // ----------------------------------------------
    const products = [
        { id: 1, name: "Espresso", price: 3000 },
        { id: 2, name: "Cappuccino", price: 4200 },
        { id: 3, name: "Moka", price: 4700 },
        { id: 4, name: "Café Frappe", price: 3800 },
        { id: 5, name: "Medialuna", price: 1500 },
        { id: 6, name: "Porción de torta", price: 2200 },
    ];

    const productSelect = document.getElementById("productSelect");
    
    if (!productSelect) return;             // Verificamos si el elemento existe antes de continuar para evitar errores

    products.forEach(p => {                 // Recorremos el array de productos para crear las opciones del menú desplegable (<select>).
        const opt = document.createElement("option");   // Creamos un nuevo elemento HTML de tipo <option>.
        opt.value = p.id;
        opt.textContent = `${p.name} - $${p.price}`;
        productSelect.appendChild(opt);     // Agregamos la opción creada dentro del <select> en el HTML real.
    });

    // ----------------------------------------------
    //  Referencias a los elementos de la interfaz
    // ----------------------------------------------
    const quantityInput = document.getElementById("quantity");
    const totalPriceSpan = document.getElementById("totalPrice");
    const extrasCheckboxes = document.querySelectorAll(".extra-checkbox");
    const simulateBtn = document.getElementById("simulateBtn");
    const orderSummary = document.getElementById("orderSummary");

    // ----------------------------------------------
    //      Función para calcular el precio total
    // ----------------------------------------------
    function calcularTotal() {
        // ----------------------------------------------
        // Obtener precio base del producto seleccionado
        // ----------------------------------------------
        const productId = parseInt(productSelect.value);
        const product = products.find(p => p.id === productId);     // Buscamos en el array 'products' el objeto que tenga ese ID.
        const base = product ? product.price : 0;                   // Si encontramos el producto usamos su precio, si no, es 0.

        // ----------------------------------------------
        //      Obtener multiplicador de tamaño
        // ----------------------------------------------
        const sizeRadio = document.querySelector('input[name="size"]:checked'); // Buscamos cuál radio button está marcado (:checked)
        const sizeMult = sizeRadio ? parseFloat(sizeRadio.value) : 1.0; // Si hay uno seleccionado, usamos su valor (ej: 1.3), si no, el valor por defecto es 1.0.

        // ----------------------------------------------
        //          Sumar extras seleccionados
        // ----------------------------------------------
        let extrasSum = 0;
        extrasCheckboxes.forEach(cb => {    // Si el checkbox está marcado (.checked es true)
            if (cb.checked) extrasSum += parseFloat(cb.dataset.price || 0);
        });

        // ----------------------------------------------
        //              Validar cantidad
        // ----------------------------------------------
        const qty = Math.max(1, parseInt(quantityInput.value) || 1);    // Leemos el input de cantidad. Si está vacío o es inválido, asumimos 1.
                                                                        // Math.max(1, ...) asegura que nunca sea menor a 1.
        // ----------------------------------------------
        //          Aplicar la Fórmula Matemática
        // ----------------------------------------------
        return Math.round((base * sizeMult + extrasSum) * qty);         // Math.round redondea el resultado para que no queden decimales raros.
    }

    // ----------------------------------------------
    //  Función para actualizar el texto en el HTML
    // ----------------------------------------------
    function actualizarInterfaz() {
        totalPriceSpan.textContent = `$${calcularTotal()}`;
    }

    productSelect.addEventListener("change", actualizarInterfaz);
    quantityInput.addEventListener("input", actualizarInterfaz);
    document.querySelectorAll('input[name="size"]').forEach(r => r.addEventListener("change", actualizarInterfaz));
    extrasCheckboxes.forEach(cb => cb.addEventListener("change", actualizarInterfaz));

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

    actualizarInterfaz();               // Inicializar al cargar
});