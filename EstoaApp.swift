
import SwiftUI
@main
struct EstoaApp: App {
    var body: some Scene {
        WindowGroup {
            TabView {
                NowView().tabItem { Label("Ahora",systemImage:"wave.3.right") }
                UpcomingView().tabItem { Label("Próximamente",systemImage:"clock") }
                MomentView().tabItem { Label("Momento",systemImage:"calendar") }
                MapView().tabItem { Label("Mapa",systemImage:"map") }
                MoreView().tabItem { Label("Más",systemImage:"ellipsis.circle") }
            }
            .tint(EstoaTheme.active)
            .preferredColorScheme(.dark)
        }
    }
}
