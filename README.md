# Mares Chile iOS UI v4 — 5/5 pestañas

Implementadas:
- Ahora
- Próximamente
- Momento
- Mapa
- Más

## Mapa
Usa MapKit/CoreLocation. Los puntos se dibujan cuando `/stations` entrega `latitude` y `longitude`.
La ubicación del dispositivo **solo sugiere** la estación geográficamente más cercana; no cambia automáticamente el punto hidrográfico.

Agregar a Info.plist:
`NSLocationWhenInUseUsageDescription` = `Tu ubicación se usa únicamente para sugerir el punto de predicción más cercano.`

## Más
Incluye preferencias de hora, método de cálculo, edición de datos, alcance y limitaciones.

## Importante
La UI está completa a nivel de código de prototipo. Para compilarla como app instalable todavía debe crearse/configurarse el proyecto Xcode, desplegar la API y completar el endpoint `/stations` con coordenadas.
