import SwiftUI

struct UpcomingView: View {
    @EnvironmentObject var store: StationStore
    @State private var hours=24
    @State private var currentEvents:[ForecastEvent]=[]
    @State private var weak:[WeakWindow]=[]
    @State private var tide:[TideEventDTO]=[]
    @State private var loading=false
    @State private var error:String?

    var body: some View {
        NavigationStack {
            ZStack {
                EstoaTheme.background.ignoresSafeArea()
                ScrollView {
                    VStack(spacing:16) {
                        EstoaBrandHeader()
                        Picker("Horizonte",selection:$hours) {
                            Text("12 h").tag(12); Text("24 h").tag(24); Text("48 h").tag(48)
                        }.pickerStyle(.segmented)

                        if loading { ProgressView().tint(.white) }
                        if let error { Text(error).foregroundStyle(.secondary) }

                        VStack(alignment:.leading,spacing:12) {
                            Text("CORRIENTE").font(.caption.bold()).foregroundStyle(EstoaTheme.active)
                            ForEach(currentEvents,id:\.id) { e in
                                HStack {
                                    Image(systemName:e.event_type=="SLACK" ? "equal.circle" : "arrow.left.and.right.circle")
                                    Text(e.local_datetime).monospacedDigit()
                                    Spacer()
                                    Text(e.event_type=="SLACK" ? "Estoa" : String(format:"%.1f kn",e.intensity_kn ?? 0))
                                }.foregroundStyle(.white)
                            }
                        }.estoaCard()

                        if !weak.isEmpty {
                            VStack(alignment:.leading,spacing:10) {
                                Text("VENTANAS DE CORRIENTE DÉBIL").font(.caption.bold()).foregroundStyle(.yellow)
                                ForEach(weak,id:\.id) { w in
                                    Text("\(w.start) – \(w.end) · ≤ \(String(format:"%.1f",w.threshold_kn)) kn")
                                        .foregroundStyle(.white)
                                }
                            }.estoaCard()
                        }

                        if !tide.isEmpty {
                            VStack(alignment:.leading,spacing:12) {
                                Text("MAREA").font(.caption.bold()).foregroundStyle(EstoaTheme.active)
                                ForEach(tide,id:\.timeLocal) { e in
                                    HStack {
                                        Image(systemName:e.type=="HW" ? "arrow.up.circle" : "arrow.down.circle")
                                        Text(e.timeLocal).monospacedDigit()
                                        Spacer()
                                        Text(e.heightM.map { String(format:"%@ · %.2f m",e.type=="HW" ? "PM":"BM",$0) }
                                             ?? (e.type=="HW" ? "PM":"BM"))
                                    }.foregroundStyle(.white)
                                }
                            }.estoaCard()
                        }
                    }.padding()
                }
            }.navigationBarHidden(true)
             .task(id:"\(store.selectedID)-\(hours)") { await load() }
        }
    }

    @MainActor private func load() async {
        loading=true; error=nil
        let start=Date()
        do {
            async let c=APIClient.shared.forecast(stationID:store.selectedID,start:start,hours:hours)
            async let w=APIClient.shared.weakWindows(stationID:store.selectedID,start:start,hours:hours,threshold:1.0)
            async let t=APIClient.shared.tideEvents(stationID:store.selectedID,start:start,hours:hours)
            let (cr,wr,tr)=try await (c,w,t)
            currentEvents=cr.events; weak=wr.windows; tide=tr.events
        } catch { self.error="No fue posible cargar el período seleccionado." }
        loading=false
    }
}
