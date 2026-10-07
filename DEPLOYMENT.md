# ESTOA — despliegue para prueba en iPhone

## Backend
El paquete incluye Dockerfile, requirements.txt y `/health`.
Despliegue el contenido en un servicio HTTPS que ejecute el contenedor. El proceso escucha en `$PORT` (8080 por defecto).

## iOS
`APIClient` ya no depende de localhost. Lee `ESTOA_API_BASE_URL` desde Info.plist.
Antes de compilar, establezca esa clave con la URL HTTPS real, por ejemplo `https://api.su-dominio.cl`.

## Comprobación mínima
1. Abrir `https://<backend>/health` y confirmar `status: ok`.
2. Probar `/stations`.
3. Probar `/conditions/at` con una estación.
4. Probar `/forecast`, `/weak-windows` y `/tide-events`.
5. Compilar en Xcode y ejecutar en iPhone.

La ubicación del iPhone se usa para sugerir una estación; no activa cambios silenciosos.
