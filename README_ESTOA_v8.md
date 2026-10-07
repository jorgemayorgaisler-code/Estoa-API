# ESTOA Full Stack v8 — integración hidrográfica

## Integrado en este bloque
- Motor nacional de ventanas empíricas A–G.
- Endpoint `/weak-windows`.
- Enrutamiento por capacidades de marea.
- Endpoint `/capabilities`.
- Política astronómica contextual.
- Fixtures verificados de Kirke para marea + astronomía.
- QA nacional de ventanas débiles.
- Caso patrón Kirke ≤1 kn: 04-10-2026 20:45–21:55 local, PASS.

## Marea
La arquitectura nacional ya sabe qué puede mostrar por estación:
- FULL_TIDE
- EVENT_TIMES_ONLY
- REFERENCE/NO_AUTOMATIC_TIDE

No se fabrican alturas donde PUB3009 no entrega una corrección utilizable.
La integración numérica nacional completa de PUB3009 requiere que las series/eventos mareográficos
de todos los puertos patrón necesarios estén codificados en la base, por lo que v8 no afirma algo que
todavía no está cargado.

## Astronomía
Es contexto únicamente. No altera la intensidad PUB3015.
Kirke conserva prioridad especial a declinación lunar.

## Endpoints principales
- `/stations`
- `/conditions/at`
- `/conditions/now`
- `/forecast`
- `/weak-windows`
- `/capabilities`
