# Despliegue rápido del backend ESTOA

1. Crear un repositorio privado con el contenido de este paquete.
2. En Render, crear un Blueprint/Web Service usando `render.yaml`.
3. Esperar que `/health` responda `{"status":"ok","service":"ESTOA","edition":2026}`.
4. Verificar `/version`.
5. Copiar la URL HTTPS del servicio.
6. Sustituir `https://YOUR-ESTOA-API.example.com` por esa URL en la configuración de compilación.
7. Compilar el cliente iOS.

No incluir claves privadas dentro del proyecto. Los datos hidrográficos permanecen en el backend del servicio.
