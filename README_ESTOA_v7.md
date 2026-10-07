# ESTOA Full Stack v7

Este paquete une el backend hidrográfico y la interfaz SwiftUI.

## Completado
- 22/22 puntos de corriente con coordenadas verificadas en el registro del proyecto.
- `/stations` entrega latitud/longitud y direcciones de flujo/reflujo.
- Mapa SwiftUI puede dibujar los 22 puntos.
- GPS sólo sugiere el punto más cercano; no cambia la estación sin confirmación.
- Ahora / Próximamente / Momento / Mapa / Más incluidos.
- Motor nacional PUB3015 incluido.
- Identidad visual ESTOA incluida.

## Backend
Desde la carpeta raíz:
`pip install -r requirements.txt`
`uvicorn app:app --reload`

## iOS
Crear un proyecto iOS SwiftUI llamado ESTOA y agregar los archivos de `ios/`.
Configurar la URL del backend en `APIClient.swift`.
Agregar permiso de ubicación:
`NSLocationWhenInUseUsageDescription` = `Tu ubicación se usa únicamente para sugerir el punto de predicción más cercano.`

## Próximo bloque técnico
Integrar en la API nacional:
1. ventanas empíricas de corriente débil A–G,
2. marea PUB3009 según capacidad de cada estación,
3. astronomía contextual,
4. pruebas end-to-end de las 22 estaciones.

No se debe generar ningún valor hidrográfico en SwiftUI.
