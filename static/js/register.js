// Espera a que todo el HTML esté cargado antes de ejecutar el script
document.addEventListener("DOMContentLoaded", () => {
    // Referenciamos los elementos del DOM que vamos a manipular
    const form = document.getElementById("registerForm");
    const mensajeDiv = document.getElementById("mensajeCliente");

    // Definimos una función asíncrona para manejar el envío de datos
    async function manejarRegistro(e) {
        // 1. Evita que la página se recargue (comportamiento por defecto del formulario)
        e.preventDefault();
        
        // Limpiamos mensajes previos en la interfaz
        mensajeDiv.innerHTML = "";

        try {
            // 2. Empaquetamos todos los datos del formulario en un objeto FormData
            const formData = new FormData(form);

            // 3. Realizamos una petición HTTP POST al servidor de Flask
            // Usamos 'await' para esperar la respuesta del servidor sin bloquear el navegador
            const resp = await fetch("http://127.0.0.1:5000/register", {
                method: "POST",
                body: formData, // Enviamos el objeto con los datos del usuario
            });

            // 4. Convertimos la respuesta del servidor a un objeto JSON usable
            const result = await resp.json();

            // 5. Verificamos si la respuesta es exitosa (código HTTP 200-299)
            if (resp.ok) {
                // Si es éxito, mostramos el mensaje positivo y limpiamos los campos
                mensajeDiv.innerHTML = `<div class="alert alert-success">${result.message}</div>`;
                form.reset();
            } else {
                // Si el servidor detectó un error (ej: email duplicado), mostramos el motivo
                mensajeDiv.innerHTML = `<div class="alert alert-danger">${result.error}</div>`;
            }
        } catch (err) {
            // 6. Capturamos errores de red (ej: el servidor Flask está apagado)
            mensajeDiv.innerHTML = `<div class="alert alert-danger">Error de conexión con el servidor.</div>`;
        }
    }

    // Asignamos el evento 'submit' al formulario para que dispare nuestra función
    if (form) form.addEventListener("submit", manejarRegistro);
});