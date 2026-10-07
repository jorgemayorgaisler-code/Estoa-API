# ESTOA v12 — Integrated conditions
Se unificó el contrato de marea con la capa de corriente para que Ahora/Momento puedan presentar ambos fenómenos sin mezclarlos.
Caso de referencia Kirke 2026-10-04 18:30 local:
- corriente 4.899 kn, reflujo, 290°V, disminuyendo;
- próxima estoa 21:07;
- ventana <=1 kn 20:45–21:55;
- marea ~0.28 m, vaciante;
- próxima bajamar 18:39, 0.28 m.

Se agregaron TideEventDTO y TideInstantDTO al modelo Swift.
La ingestión masiva de todos los eventos patrón 2026 sigue siendo una fase separada porque la maquetación trimestral de PUB3009
requiere validación de columnas/días antes de automatizarla; no se aceptan asociaciones ambiguas.
