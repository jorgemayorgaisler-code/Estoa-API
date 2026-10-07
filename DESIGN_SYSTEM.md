# ESTOA Design System v5

Diseño aprobado trasladado a componentes SwiftUI reutilizables.

## Identidad
- Marca: ESTOA
- Descriptor: CORRIENTES Y MAREAS
- Territorio visual: Patagonia · Chile
- Fondo: azul marino profundo
- Activo: cian
- Flujo: verde/cian
- Reflujo: rojo
- Estoa: blanco
- Casos débiles/variables: ámbar

## Jerarquía
1. Intensidad + estado de corriente
2. Dirección verdadera + tendencia
3. Próxima estoa / próxima máxima
4. Ventana de corriente débil
5. Marea
6. Contexto astronómico

## Principio
Los componentes visuales no calculan datos hidrográficos. Solo representan el payload del motor.

## Archivos nuevos
- EstoaTheme.swift: tokens visuales, tarjetas y cabecera de marca.
- EstoaCurrentHero.swift: componente principal de corriente.

La siguiente integración debe sustituir gradualmente estilos hard-coded de las cinco vistas por estos componentes.
