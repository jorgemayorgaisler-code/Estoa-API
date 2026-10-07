
import Foundation

final class APIClient {
    static let shared = APIClient()
    private let baseURL: URL
    private init() {
        let raw = (Bundle.main.object(forInfoDictionaryKey: "ESTOA_API_BASE_URL") as? String) ?? ""
        guard let url = URL(string: raw), !raw.isEmpty,
              url.scheme == "https" else {
            fatalError("ESTOA_API_BASE_URL must be a valid HTTPS URL")
        }
        self.baseURL = url
    }
    // Replace with deployed backend URL.

    func conditions(stationID: String, at date: Date) async throws -> ConditionsResponse {
        var c = URLComponents(url: baseURL.appendingPathComponent("conditions/at"),
                              resolvingAgainstBaseURL: false)!
        let f = ISO8601DateFormatter()
        f.formatOptions = [.withInternetDateTime]
        c.queryItems = [
            URLQueryItem(name: "station_id", value: stationID),
            URLQueryItem(name: "local_datetime", value: f.string(from: date))
        ]
        let (data, response) = try await URLSession.shared.data(from: c.url!)
        guard let h = response as? HTTPURLResponse, (200..<300).contains(h.statusCode)
        else { throw URLError(.badServerResponse) }
        return try JSONDecoder().decode(ConditionsResponse.self, from: data)
    }
}

extension APIClient {
    func forecast(stationID:String, start:Date, hours:Int=24) async throws -> ForecastResponse {
        var c=URLComponents(url:baseURL.appendingPathComponent("forecast"),resolvingAgainstBaseURL:false)!
        let iso=ISO8601DateFormatter()
        c.queryItems=[
            URLQueryItem(name:"station_id",value:stationID),
            URLQueryItem(name:"start",value:iso.string(from:start)),
            URLQueryItem(name:"hours",value:String(hours))
        ]
        let (data,response)=try await URLSession.shared.data(from:c.url!)
        guard let h=response as? HTTPURLResponse,(200..<300).contains(h.statusCode)
        else { throw URLError(.badServerResponse) }
        return try JSONDecoder().decode(ForecastResponse.self,from:data)
    }
}

extension APIClient {
    func weakWindows(stationID:String,start:Date,hours:Int=24,threshold:Double=1.0) async throws -> WeakWindowsResponse {
        var c=URLComponents(url:baseURL.appendingPathComponent("weak-windows"),resolvingAgainstBaseURL:false)!
        let iso=ISO8601DateFormatter()
        c.queryItems=[
            .init(name:"station_id",value:stationID),
            .init(name:"start",value:iso.string(from:start)),
            .init(name:"hours",value:String(hours)),
            .init(name:"threshold_kn",value:String(threshold))
        ]
        let (data,response)=try await URLSession.shared.data(from:c.url!)
        guard let h=response as? HTTPURLResponse,(200..<300).contains(h.statusCode) else { throw URLError(.badServerResponse) }
        return try JSONDecoder().decode(WeakWindowsResponse.self,from:data)
    }

    func capabilities(stationID:String) async throws -> CapabilitiesResponse {
        var c=URLComponents(url:baseURL.appendingPathComponent("capabilities"),resolvingAgainstBaseURL:false)!
        c.queryItems=[.init(name:"station_id",value:stationID)]
        let (data,response)=try await URLSession.shared.data(from:c.url!)
        guard let h=response as? HTTPURLResponse,(200..<300).contains(h.statusCode) else { throw URLError(.badServerResponse) }
        return try JSONDecoder().decode(CapabilitiesResponse.self,from:data)
    }

    func tideEvents(stationID: String, start: Date, hours: Int) async throws -> TideEventsResponse {
        var c=URLComponents(url:baseURL.appendingPathComponent("tide-events"),resolvingAgainstBaseURL:false)!
        let f=ISO8601DateFormatter()
        c.queryItems=[
            URLQueryItem(name:"station_id",value:stationID),
            URLQueryItem(name:"start_local",value:f.string(from:start)),
            URLQueryItem(name:"hours",value:String(hours))
        ]
        let (d,r)=try await URLSession.shared.data(from:c.url!)
        guard (r as? HTTPURLResponse)?.statusCode==200 else { throw URLError(.badServerResponse) }
        return try JSONDecoder().decode(TideEventsResponse.self,from:d)
    }
}
