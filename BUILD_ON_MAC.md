# Compilar ESTOA en Mac

1. Instalar Xcode y XcodeGen.
2. En Terminal, entrar a esta carpeta.
3. Ejecutar `xcodegen generate`.
4. Abrir `ESTOA.xcodeproj`.
5. Seleccionar el Team de firma en Signing & Capabilities.
6. Configurar `APIClient.baseURL` con el backend desplegado o accesible desde el iPhone.
7. Elegir un iPhone/simulador y Build/Run.

Nota: `127.0.0.1` dentro de un iPhone apunta al propio iPhone, no al Mac. Para pruebas en dispositivo, usar la IP LAN del backend o una URL HTTPS desplegada.
