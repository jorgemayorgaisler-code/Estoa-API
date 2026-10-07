
import SwiftUI

struct NowView: View {
    @State private var result:ConditionsResponse?
    @State private var loading=false
    @State private var error:String?
    let api=APIClient()
    @AppStorage("activeStation") private var stationID="CUR011"

    var body:some View {
        NavigationStack {
            ZStack {
                EstoaTheme.background.ignoresSafeArea()
                ScrollView {
                    VStack(spacing:14) {
                        EstoaBrandHeader()
                        stationHeader
                        if loading { ProgressView().tint(EstoaTheme.active) }
                        if let r=result {
                            EstoaCurrentHero(current:r.current)
                            quickCards(r)
                            weakCard
                            capabilityCards(r)
                        }
                        if let error { Text(error).foregroundStyle(.orange).font(.footnote) }
                    }.padding(EstoaTheme.pagePadding)
                }
            }.task { await refresh() }.refreshable { await refresh() }
        }
    }
    private var stationHeader:some View {
        EstoaCard {
            HStack {
                Image(systemName:"mappin.and.ellipse").font(.title2).foregroundStyle(EstoaTheme.active)
                VStack(alignment:.leading) {
                    Text(result?.station.name ?? "Punto de predicción").font(.headline).foregroundStyle(.white)
                    Text(stationID).font(.caption).foregroundStyle(EstoaTheme.secondary)
                }
                Spacer(); Image(systemName:"chevron.down").foregroundStyle(EstoaTheme.secondary)
            }
        }
    }
    private func quickCards(_ r:ConditionsResponse)->some View {
        HStack(spacing:10) {
            EstoaCard { VStack(alignment:.leading) {
                Text("PRÓXIMA ESTOA").font(.caption2).foregroundStyle(EstoaTheme.secondary)
                Text("Ver próximos eventos").font(.subheadline).bold().foregroundStyle(.white)
            }}
            EstoaCard { VStack(alignment:.leading) {
                Text("TENDENCIA").font(.caption2).foregroundStyle(EstoaTheme.secondary)
                Text(r.current.trend=="DECREASING" ? "Disminuyendo" : r.current.trend=="INCREASING" ? "Aumentando" : "Evento")
                    .font(.subheadline).bold().foregroundStyle(.white)
            }}
        }
    }
    private var weakCard:some View {
        EstoaCard {
            HStack {
                Image(systemName:"water.waves").foregroundStyle(EstoaTheme.active)
                VStack(alignment:.leading) {
                    Text("VENTANA DE CORRIENTE DÉBIL").font(.caption2).foregroundStyle(EstoaTheme.secondary)
                    Text("Consultar en Próximamente").font(.subheadline).foregroundStyle(.white)
                }
                Spacer(); Image(systemName:"chevron.right").foregroundStyle(EstoaTheme.secondary)
            }
        }
    }
    private func capabilityCards(_ r:ConditionsResponse)->some View {
        HStack(spacing:10) {
            EstoaCard { VStack(alignment:.leading) {
                Image(systemName:"water.waves").foregroundStyle(EstoaTheme.active)
                Text("MAREA").font(.caption2).foregroundStyle(EstoaTheme.secondary)
                Text(r.tide.display_height_m.map { String(format:"%.2f m · %@", $0, r.tide.trend=="RISING" ? "creciente" : r.tide.trend=="FALLING" ? "vaciante" : "evento") } ?? (r.tide.capability=="EVENT_TIMES_ONLY" ? "Horarios PM/BM" : "Según estación")).foregroundStyle(.white)
                        if let e=r.tide.next {
                            Text("Próxima PM/BM · \(e.type == "HW" ? "PM" : "BM") \(e.timeLocal)")
                                .font(.caption).foregroundStyle(.white.opacity(0.65))
                        }
            }}
            EstoaCard { VStack(alignment:.leading) {
                Image(systemName:"moon.stars.fill").foregroundStyle(EstoaTheme.active)
                Text("ASTRONOMÍA").font(.caption2).foregroundStyle(EstoaTheme.secondary)
                Text("Contexto").foregroundStyle(.white)
            }}
        }
    }
    @MainActor private func refresh() async {
        loading=true; error=nil
        do { result=try await api.conditions(stationID:stationID,at:Date()) }
        catch { self.error="No fue posible obtener la condición." }
        loading=false
    }
}
