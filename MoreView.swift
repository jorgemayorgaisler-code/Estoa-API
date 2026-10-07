
import SwiftUI

struct MoreView: View {
    @AppStorage("activeStation") private var activeStation="CUR011"
    @State private var capabilities:CapabilitiesResponse?
    private let api=APIClient()
    @AppStorage("displayTimeMode") private var timeMode="Estación"
    @AppStorage("showMethod") private var showMethod=true

    var body:some View {
        NavigationStack {
            List {
                Section("Visualización") {
                    Picker("Hora mostrada",selection:$timeMode) {
                        Text("Hora de estación").tag("Estación")
                        Text("Hora del dispositivo").tag("Dispositivo")
                        Text("Hora fuente SHOA").tag("Fuente")
                    }
                    Toggle("Mostrar método de cálculo",isOn:$showMethod)
                }
                Section("Datos") {
                    LabeledContent("Edición","2026")
                    LabeledContent("Corrientes","22 puntos")
                    LabeledContent("Núcleo","RC1")
                }
                Section("Alcance") {
                    Text("ESTOA consulta predicciones hidrográficas. No calcula rutas, ETA ni reemplaza publicaciones, cartas, avisos o procedimientos oficiales.")
                    Text("Las predicciones astronómicas pueden diferir de las condiciones observadas por efectos meteorológicos y locales.")
                }
                Section("Selección por ubicación") {
                    Text("La ubicación puede sugerir un punto cercano, pero la aplicación exige confirmación del usuario antes de cambiar el punto de predicción.")
                }
                Section("Capacidad del punto activo") {
                    LabeledContent("Punto", activeStation)
                    if let c=capabilities {
                        LabeledContent("Marea", c.tide.capability)
                        LabeledContent("Astronomía", c.astronomy.role=="CONTEXT_ONLY" ? "Contexto" : c.astronomy.role)
                    } else {
                        Text("Consultando capacidades…")
                    }
                }
                Section("Información") {
                    LabeledContent("Motor","PUB 3015 / PUB 3009")
                    LabeledContent("Astronomía","Contexto solamente")
                    Text("Antes de una distribución comercial debe resolverse la autorización/licencia aplicable al contenido de las publicaciones.")
                }
            }
            .navigationTitle("Más")
            .task { capabilities = try? await api.capabilities(stationID: activeStation) }
        }
    }
}
