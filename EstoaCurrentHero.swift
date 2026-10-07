
import SwiftUI

struct EstoaCurrentHero: View {
    let current: CurrentCondition

    var phaseColor: Color {
        switch current.phase {
        case "EBB": return EstoaTheme.ebb
        case "FLOOD": return EstoaTheme.flood
        case "SLACK": return EstoaTheme.slack
        default: return .orange
        }
    }
    var phaseText:String {
        ["EBB":"REFLUJO","FLOOD":"FLUJO","SLACK":"ESTOA","VARIABLE":"DÉBIL / VARIABLE"][current.phase] ?? current.phase
    }

    var body: some View {
        EstoaCard {
            VStack(alignment:.leading,spacing:12) {
                Text("CONDICIÓN ACTUAL").font(.caption).bold().foregroundStyle(.white)
                HStack(alignment:.center,spacing:18) {
                    VStack(alignment:.leading,spacing:0) {
                        HStack(alignment:.firstTextBaseline,spacing:6) {
                            Text(current.intensity_kn.map { String(format:"%.2f",$0) } ?? "—")
                                .font(.system(size:64,weight:.semibold,design:.rounded))
                                .foregroundStyle(.white)
                            Text("kn").font(.title2).foregroundStyle(EstoaTheme.secondary)
                        }
                        Text(phaseText).font(.title).bold().foregroundStyle(phaseColor)
                    }
                    Spacer()
                    VStack(spacing:7) {
                        Image(systemName:"location.north.fill")
                            .font(.system(size:40)).rotationEffect(.degrees(current.direction_true ?? 0))
                            .foregroundStyle(phaseColor)
                        Text(current.direction_true.map { "\(Int($0))° V" } ?? "—")
                            .font(.headline).foregroundStyle(.white)
                        Text(current.trend=="DECREASING" ? "DISMINUYENDO" :
                             current.trend=="INCREASING" ? "AUMENTANDO" : "EVENTO")
                            .font(.caption).foregroundStyle(EstoaTheme.secondary)
                    }
                }
                Divider().overlay(.white.opacity(0.12))
                HStack {
                    Image(systemName:"wave.3.right").foregroundStyle(EstoaTheme.active)
                    Text(current.status=="CALCULATED_CONTINUOUS" ? "Cálculo continuo" :
                         current.status=="PUBLISHED_EVENT" ? "Evento publicado" : "Caso especial")
                        .font(.caption).foregroundStyle(EstoaTheme.secondary)
                }
            }
        }
    }
}
