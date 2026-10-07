
import Foundation

struct StationListItem: Codable, Identifiable, Hashable {
    let station_id: String
    let station_name: String
    let app_mode: String
    let tide_automatic_capability: String
    let latitude: Double?
    let longitude: Double?
    var id: String { station_id }

    enum CodingKeys:String,CodingKey {
        case station_id, station_name, app_mode, tide_automatic_capability, latitude, longitude
    }
}

extension APIClient {
    func stations() async throws -> [StationListItem] {
        let url=baseURL.appendingPathComponent("stations")
        let (data,response)=try await URLSession.shared.data(from:url)
        guard let h=response as? HTTPURLResponse,(200..<300).contains(h.statusCode)
        else { throw URLError(.badServerResponse) }
        return try JSONDecoder().decode([StationListItem].self,from:data)
    }
}
