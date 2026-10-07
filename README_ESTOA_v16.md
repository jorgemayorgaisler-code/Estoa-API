# ESTOA v16 — iOS Build Readiness

Se hizo auditoría estática del código Swift y se corrigieron bloqueos de compilación detectables sin Xcode:
singleton API, nombre de baseURL y modelos/campos de Próximamente.

El backend mantiene sintaxis Python válida. El proyecto conserva `project.yml` para XcodeGen, iOS 17 y permiso de ubicación.
Este entorno no incluye Xcode/xcodebuild ni XcodeGen, por lo que v16 se declara preparado a nivel de fuente para compilar en Mac,
no como IPA compilada ni aplicación instalada.
