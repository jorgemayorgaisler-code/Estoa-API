
import SwiftUI
import MapKit
import CoreLocation

final class UserLocation: NSObject, ObservableObject, CLLocationManagerDelegate {
    private let manager=CLLocationManager()
    @Published var coordinate:CLLocationCoordinate2D?
    override init() { super.init(); manager.delegate=self }
    func request() { manager.requestWhenInUseAuthorization(); manager.requestLocation() }
    func locationManager(_ manager:CLLocationManager,didUpdateLocations locations:[CLLocation]) {
        coordinate=locations.last?.coordinate
    }
    func locationManager(_ manager:CLLocationManager,didFailWithError error:Error) {}
}

struct MapStation: Identifiable {
    let item:StationListItem
    var id:String { item.station_id }
    var coordinate:CLLocationCoordinate2D {
        .init(latitude:item.latitude!,longitude:item.longitude!)
    }
}

struct MapView: View {
    @State private var stations:[StationListItem]=[]
    @State private var selected:StationListItem?
    @StateObject private var location=UserLocation()
    @State private var position:MapCameraPosition = .region(
        MKCoordinateRegion(center:.init(latitude:-45,longitude:-73),
                           span:.init(latitudeDelta:24,longitudeDelta:12)))
    let api=APIClient()

    var mapped:[MapStation] {
        stations.filter{$0.latitude != nil && $0.longitude != nil}.map{MapStation(item:$0)}
    }

    var body:some View {
        NavigationStack {
            ZStack(alignment:.bottom) {
                Map(position:$position) {
                    UserAnnotation()
                    ForEach(mapped) { s in
                        Annotation(s.item.station_name,coordinate:s.coordinate) {
                            Button { selected=s.item } label: {
                                Image(systemName:"wave.3.right.circle.fill")
                                    .font(.title2).foregroundStyle(.cyan)
                                    .background(Circle().fill(.black.opacity(0.65)))
                            }
                        }
                    }
                }.mapStyle(.standard(elevation:.realistic))
                VStack(spacing:10) {
                    if let s=selected { stationCard(s) }
                    HStack {
                        Button { suggestNearest() } label: {
                            Label("Sugerir más cercana",systemImage:"location.fill")
                        }.buttonStyle(.borderedProminent).tint(.cyan)
                        Button { location.request() } label: {
                            Image(systemName:"location.circle")
                        }.buttonStyle(.bordered)
                    }
                }.padding()
            }
            .navigationTitle("Mapa")
            .task { try? await stations=api.stations() }
        }
    }

    private func stationCard(_ s:StationListItem)->some View {
        VStack(alignment:.leading,spacing:5) {
            Text("PUNTO DE PREDICCIÓN").font(.caption2).bold().foregroundStyle(.cyan)
            Text(s.station_name).bold().foregroundStyle(.white)
            Text("Toca este punto para consultarlo. La cercanía geográfica no implica equivalencia hidrográfica.")
                .font(.caption).foregroundStyle(.secondary)
        }.padding().frame(maxWidth:.infinity,alignment:.leading)
         .background(.ultraThinMaterial,in:RoundedRectangle(cornerRadius:18))
    }

    private func suggestNearest() {
        guard let u=location.coordinate else { location.request(); return }
        let candidates=mapped
        selected=candidates.min {
            distance(u,$0.coordinate) < distance(u,$1.coordinate)
        }?.item
        // Deliberately only suggests. It never changes the active prediction station silently.
    }

    private func distance(_ a:CLLocationCoordinate2D,_ b:CLLocationCoordinate2D)->CLLocationDistance {
        CLLocation(latitude:a.latitude,longitude:a.longitude)
            .distance(from:CLLocation(latitude:b.latitude,longitude:b.longitude))
    }
}
