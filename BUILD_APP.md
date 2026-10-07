# ESTOA v9 — App Candidate

## Crear proyecto Xcode
Con XcodeGen instalado:
1. `xcodegen generate`
2. abrir `ESTOA.xcodeproj`
3. ejecutar backend: `uvicorn app:app --reload`
4. en `ios/APIClient.swift`, configurar `baseURL`
5. Run en simulador/iPhone.

## Funciones conectadas
- Ahora → `/conditions/at`
- Próximamente → `/forecast` + `/weak-windows`
- Momento → `/conditions/at`
- Mapa → `/stations` con 22 coordenadas
- Más → `/capabilities`

## Estado
Las cinco pestañas ya tienen conexión real con el backend para sus funciones principales.
Marea numérica nacional PUB3009 todavía se habilita sólo donde el motor tiene datos codificados; no se inventan alturas.
