# ESTOA v18 — Release Candidate checklist

## Motor
- [x] PUB3015 2026: 22 estaciones de corriente.
- [x] Interpolación estándar seno/coseno.
- [x] Secuencias débiles/no estándar protegidas contra valores inventados.
- [x] PUB3009 2026: motor de marea para 8 estaciones con relación exacta.
- [x] Dalcahue mantiene alturas nulas donde la publicación no entrega corrección.
- [x] Hora fuente y hora local separadas.

## Aplicación
- [x] Ahora.
- [x] Próximamente 12/24/48 h.
- [x] Momento elegido.
- [x] Mapa de 22 puntos.
- [x] Más / capacidades.
- [x] GPS solo sugiere estación.
- [x] Sin ruta, ETA ni asesoría de navegación.

## Producción
- [x] Dockerfile.
- [x] /health.
- [x] /version.
- [x] Configuración Render.
- [x] URL API exige HTTPS.
- [ ] Desplegar backend en cuenta/host real.
- [ ] Colocar URL HTTPS definitiva en ESTOA_API_BASE_URL.
- [ ] Generar .xcodeproj en macOS.
- [ ] Compilar y firmar con Apple Development Team.
- [ ] Prueba física en iPhone.
- [ ] TestFlight/App Store, si se decide publicar.

Los cinco puntos pendientes requieren infraestructura o credenciales externas y no deben marcarse como completados hasta ejecutarlos realmente.
