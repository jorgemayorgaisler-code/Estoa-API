# ESTOA v6 — avance rápido

## Ya integrado
- Marca ESTOA en app.
- Sistema visual común.
- 5 pestañas funcionales.
- Ahora rediseñado con componentes definitivos.
- Próximamente y Momento migrados a paleta ESTOA.
- Mapa con MapKit/CoreLocation y sugerencia sin selección silenciosa.
- Más con preferencias y limitaciones.
- Backend/API previo compatible.

## Bloques siguientes
1. Añadir coordenadas al `/stations` del backend.
2. Llevar ventanas empíricas A–G al endpoint `/forecast`.
3. Llevar marea PUB3009 y astronomía al payload nacional.
4. Crear proyecto Xcode compilable con assets/icono.
5. QA de UI + motor en las 22 estaciones.

Regla de producción: ningún valor hidrográfico se genera en SwiftUI.
