# ESTOA v11
Se completó la codificación de reglas PUB3009 para las 8 estaciones del catálogo que admiten marea automática:
7 FULL_TIDE + Dalcahue EVENT_TIMES_ONLY.

Nuevas reglas:
- Segunda Angostura: patrón Puerto Montt, -3:05/-3:05, -0.73/+0.12 m.
- Bahía Posesión: patrón Punta Delgada, -0:23/-0:56, +1.21/-0.01 m.
- Punta Wreck: patrón Puerto Montt, -5:10/-5:02, *1.91/*2.46.

El motor ya soporta las cuatro familias necesarias: patrón, suma, multiplicación y lineal.
Siguiente fase de implementación: ingestión estructurada de eventos 2026 de los puertos patrón necesarios y generación
de altura instantánea/creciente-vaciante/próxima PM-BM para las 7 FULL_TIDE.
