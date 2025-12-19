document.addEventListener("DOMContentLoaded", () => {       // Esto asegura que el código se ejecute solo cuando el HTML ya esté cargado.
    // ----------------------------------------------
    //      Referenciamos los elementos del DOM
    // ----------------------------------------------
    const form = document.getElementById("registerForm");
    const mensajeDiv = document.getElementById("mensajeCliente");

    // Definimos una función 'async' porque usaremos 'await' para esperar la respuesta del servidor.
    async function manejarRegistro(e) {
        e.preventDefault();             //evita que la página se recargue al enviar el formulario.
        
        mensajeDiv.innerHTML = "";      // Limpiar alertas previas

        try {
            // 2. FormData captura todos los inputs con atributo 'name' automáticamente
            const formData = new FormData(form);

            // 3. Fetch API: Es el puente entre JS y Python.
            const resp = await fetch("http://127.0.0.1:5000/register", {    // Usamos 'await' para esperar la respuesta del servidor sin bloquear el navegador
                method: "POST",         // Envia los datos ocultos en el cuerpo de la solicitud HTTP.    
                body: formData,         // El cuerpo del mensaje lleva los datos
            });

            // 4. Convertimos la respuesta del servidor (Python) a JSON
            const result = await resp.json();

            // 5. Verificamos el código de estado HTTP (200 es OK, 400/500 es error)
            if (resp.ok) {
                // Éxito: Fondo verde (clase bootstrap alert-success)
                mensajeDiv.innerHTML = `<div class="alert alert-success">${result.message}</div>`;
                form.reset(); // Limpia los campos
            } else {
                // Error (ej: mail duplicado): Fondo rojo
                mensajeDiv.innerHTML = `<div class="alert alert-danger">${result.error}</div>`;
            }
        } catch (err) {
            // Error de red (ej: el servidor Python no está corriendo)
            mensajeDiv.innerHTML = `<div class="alert alert-danger">Error de conexión con el servidor.</div>`;
        }
    }

    // Asignamos el evento 'submit' al formulario para que ejecute la función
    if (form) form.addEventListener("submit", manejarRegistro);
});