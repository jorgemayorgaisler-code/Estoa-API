
import Foundation

struct CurrentCondition: Codable {
    let status: String
    let intensity_kn: Double?
    let phase: String
    let direction_true: Double?
    let trend: String
}
struct StationRef: Codable { let station_id: String; let name: String }
struct QueryRef: Codable { let local_datetime: String }
struct TideRef: Codable {
    let capability: String
    let available: Bool?
    let height_m: Double?
    let display_height_m: Double?
    let trend: String?
    let previous: TideEventDTO?
    let next: TideEventDTO?
    let method: String?
}
struct AstronomyRef: Codable { let role: String }
struct ConditionsResponse: Codable {
    let station: StationRef
    let query: QueryRef
    let current: CurrentCondition
    let tide: TideRef
    let astronomy: AstronomyRef
}

struct ForecastEvent: Codable, Identifiable {
    let local_datetime: String
    let event_type: String
    let intensity_kn: Double?
    let direction_true: Double?
    var id: String { local_datetime + event_type }
}
struct ForecastResponse: Codable {
    let station_id: String
    let start: String
    let hours: Int
    let events: [ForecastEvent]
}

struct WeakWindow: Codable, Identifiable {
    let start: String
    let end: String
    let center: String
    let threshold_kn: Double
    let table: String
    let `case`: String
    var id: String { start + end }
}
struct WeakWindowsResponse: Codable {
    let station_id: String
    let threshold_kn: Double
    let windows: [WeakWindow]
}
struct TideCapability: Codable {
    let capability: String
    let height_available: Bool
    let event_times_available: Bool
    let policy: String
}
struct AstronomyPolicy: Codable {
    let role: String
    let does_not_modify_current_prediction: Bool
    let priority: [String]
}
struct CapabilitiesResponse: Codable {
    let station_id: String
    let tide: TideCapability
    let astronomy: AstronomyPolicy
}

struct TideEventDTO: Codable {
    let timeLocal: String
    let type: String
    let heightM: Double?
    enum CodingKeys: String, CodingKey { case timeLocal = "time_local", type, heightM = "height_m" }
}
struct TideInstantDTO: Codable {
    let available: Bool
    let heightM: Double?
    let displayHeightM: Double?
    let trend: String?
    let previous: TideEventDTO?
    let next: TideEventDTO?
    let method: String?
    enum CodingKeys: String, CodingKey {
        case available, trend, previous, next, method
        case heightM = "height_m"; case displayHeightM = "display_height_m"
    }
}

struct TideEventsResponse: Codable {
    let station_id: String
    let start_local: String
    let hours: Int
    let events: [TideEventDTO]
}
