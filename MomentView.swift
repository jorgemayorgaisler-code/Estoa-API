
import SwiftUI

struct MomentView: View {
    @State private var stations:[StationListItem] = []
    @State private var selectedID = "CUR011"
    @State private var selectedDate = Date()
    @State private var result: ConditionsResponse?
    @State private var loading = false
    @State private var error:String?
    private let api = APIClient()

    var body: some View {
        NavigationStack {
            ZStack {
                EstoaTheme.background.ignoresSafeArea()
                ScrollView {
                    VStack(spacing:16) {
                        VStack(alignment:.leading,spacing:6) {
                            Text("MOMENTO").font(.caption).bold().foregroundStyle(EstoaTheme.active)
                            Text("Consulta una fecha y hora").font(.title2).bold().foregroundStyle(.white)
                            Text("Elige el punto de predicción y el instante que quieres consultar.")
                                .font(.subheadline).foregroundStyle(.secondary)
                        }.frame(maxWidth:.infinity,alignment:.leading)

                        VStack(spacing:12) {
                            Picker("Lugar", selection:$selectedID) {
                                ForEach(stations) { s in Text(s.station_name).tag(s.station_id) }
                            }
                            .pickerStyle(.menu).tint(EstoaTheme.active)
                            DatePicker("Fecha y hora",selection:$selectedDate,
                                       displayedComponents:[.date,.hourAndMinute])
                                .datePickerStyle(.compact).tint(EstoaTheme.active).foregroundStyle(.white)
                            Button { Task { await calculate() } } label: {
                                Label("Consultar condiciones",systemImage:"wave.3.right.circle.fill")
                                    .frame(maxWidth:.infinity).padding(.vertical,12).bold()
                            }.buttonStyle(.borderedProminent).tint(EstoaTheme.active)
                        }
                        .padding().background(.white.opacity(0.07),in:RoundedRectangle(cornerRadius:20))

                        if loading { ProgressView().tint(.white) }
                        if let r=result { resultCard(r) }
                        if let error { Text(error).foregroundStyle(.orange).font(.footnote) }
                    }.padding()
                }
            }
            .task { await loadStations() }
        }
    }

    private func resultCard(_ r:ConditionsResponse)->some View {
        VStack(alignment:.leading,spacing:12) {
            Text(r.station.name).font(.headline).foregroundStyle(.white)
            Text(phase(r.current.phase)).font(.caption).bold().foregroundStyle(EstoaTheme.active)
            HStack(alignment:.firstTextBaseline) {
                Text(r.current.intensity_kn.map{String(format:"%.2f",$0)} ?? "—")
                    .font(.system(size:52,weight:.semibold,design:.rounded)).foregroundStyle(.white)
                Text("kn").foregroundStyle(.secondary)
            }
            if let d=r.current.direction_true {
                Label("\(Int(d))° V",systemImage:"location.north.fill").foregroundStyle(.white)
            }
            if let h=r.tide.display_height_m {
                Divider().overlay(.white.opacity(0.15))
                HStack {
                    Label(String(format:"Marea %.2f m",h),systemImage:"water.waves")
                    Spacer()
                    Text(r.tide.trend=="RISING" ? "Creciente" : r.tide.trend=="FALLING" ? "Vaciante" : "Evento")
                }.font(.subheadline).foregroundStyle(.white)
            }
            Divider().overlay(.white.opacity(0.15))
            HStack {
                Label(trend(r.current.trend),systemImage:"chart.line.uptrend.xyaxis")
                Spacer()
                Text(method(r.current.status))
            }.font(.caption).foregroundStyle(.secondary)
        }
        .padding(20).frame(maxWidth:.infinity,alignment:.leading)
        .background(.white.opacity(0.07),in:RoundedRectangle(cornerRadius:22))
    }

    @MainActor private func loadStations() async {
        do { stations = try await api.stations() }
        catch { self.error="No fue posible cargar las estaciones." }
    }
    @MainActor private func calculate() async {
        loading=true; error=nil
        do { result=try await api.conditions(stationID:selectedID,at:selectedDate) }
        catch { self.error="No fue posible calcular este momento." }
        loading=false
    }
    private func phase(_ s:String)->String { ["FLOOD":"FLUJO","EBB":"REFLUJO","SLACK":"ESTOA","VARIABLE":"DÉBIL / VARIABLE"][s] ?? s }
    private func trend(_ s:String)->String { ["INCREASING":"Aumentando","DECREASING":"Disminuyendo","EVENT":"Evento publicado"][s] ?? "Sin tendencia calculable" }
    private func method(_ s:String)->String { s=="CALCULATED_CONTINUOUS" ? "Cálculo continuo" : s=="PUBLISHED_EVENT" ? "Publicado" : "Caso especial" }
}
