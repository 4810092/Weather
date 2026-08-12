import SwiftUI
@preconcurrency import WatchConnectivity

@main
struct NimboWatchApp: App {
    @StateObject private var weather = WatchWeatherModel()

    var body: some Scene {
        WindowGroup {
            WatchWeatherView(weather: weather)
        }
    }
}

private struct WatchWeatherView: View {
    @ObservedObject var weather: WatchWeatherModel

    var body: some View {
        Group {
            if weather.hasData {
                VStack(spacing: 4) {
                    Text(weather.location.isEmpty ? "Nimbo" : weather.location)
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(.secondary)
                        .lineLimit(1)
                    Text("\(weather.temperature)\(weather.temperatureUnit)")
                        .font(.system(size: 42, weight: .light, design: .rounded))
                        .monospacedDigit()
                    if weather.hasDailyRange {
                        Text("↑\(weather.maximum)°   ↓\(weather.minimum)°")
                            .font(.caption.weight(.semibold))
                            .foregroundStyle(.secondary)
                            .monospacedDigit()
                            .accessibilityLabel(weather.dailyRangeAccessibilityLabel)
                    }
                    Text("\(weather.symbol)  ·  \(weather.rainLabel)")
                        .font(.caption2)
                    if weather.airQuality >= 0 {
                        Text("AQI \(weather.airQuality)")
                            .font(.caption2)
                            .foregroundStyle(.secondary)
                    }
                }
            } else {
                VStack(spacing: 8) {
                    Text("Nimbo")
                        .font(.headline)
                    Text(String(localized: "Open Nimbo on your phone"))
                        .font(.caption)
                        .foregroundStyle(.secondary)
                        .multilineTextAlignment(.center)
                }
                .accessibilityElement(children: .combine)
            }
        }
        .multilineTextAlignment(.center)
        .padding(.horizontal, 8)
    }
}

@MainActor
private final class WatchWeatherModel: NSObject, ObservableObject, WCSessionDelegate {
    @Published private(set) var location = ""
    @Published private(set) var temperature = 0
    @Published private(set) var temperatureUnit = "°C"
    @Published private(set) var weatherCode = -1
    @Published private(set) var rainChance = 0
    @Published private(set) var airQuality = -1
    @Published private(set) var hasDailyRange = false
    @Published private(set) var maximum = 0
    @Published private(set) var minimum = 0
    @Published private(set) var hasData = false

    override init() {
        super.init()
        readDefaults()
        if WCSession.isSupported() {
            WCSession.default.delegate = self
            WCSession.default.activate()
        }
    }

    nonisolated func session(
        _ session: WCSession,
        activationDidCompleteWith activationState: WCSessionActivationState,
        error: Error?
    ) {
        let payload = WeatherPayload(session.receivedApplicationContext)
        Task { @MainActor in
            apply(payload)
        }
    }

    nonisolated func session(
        _ session: WCSession,
        didReceiveApplicationContext applicationContext: [String: Any]
    ) {
        let payload = WeatherPayload(applicationContext)
        Task { @MainActor in
            apply(payload)
        }
    }

    nonisolated func sessionReachabilityDidChange(_ session: WCSession) {
        guard session.isReachable else { return }
        let payload = WeatherPayload(session.receivedApplicationContext)
        Task { @MainActor in
            apply(payload)
        }
    }

    private func apply(_ payload: WeatherPayload) {
        let defaults = UserDefaults.standard
        defaults.set(payload.location, forKey: "location")
        defaults.set(payload.temperature, forKey: "temperature_c")
        defaults.set(payload.temperatureUnit, forKey: "temperature_unit")
        defaults.set(payload.weatherCode, forKey: "weather_code")
        defaults.set(payload.rainChance, forKey: "rain_chance")
        defaults.set(payload.airQuality, forKey: "aqi")
        defaults.set(payload.hasDailyRange, forKey: "has_daily_range")
        defaults.set(payload.maximum, forKey: "temperature_max")
        defaults.set(payload.minimum, forKey: "temperature_min")
        defaults.set(payload.updatedAt, forKey: "updated_at")
        readDefaults()
    }

    private func readDefaults() {
        let defaults = UserDefaults.standard
        location = defaults.string(forKey: "location") ?? ""
        temperature = defaults.integer(forKey: "temperature_c")
        temperatureUnit = defaults.string(forKey: "temperature_unit") ?? "°C"
        weatherCode = defaults.integer(forKey: "weather_code")
        rainChance = defaults.integer(forKey: "rain_chance")
        airQuality = defaults.object(forKey: "aqi") == nil ? -1 : defaults.integer(forKey: "aqi")
        hasDailyRange = defaults.bool(forKey: "has_daily_range")
        maximum = defaults.integer(forKey: "temperature_max")
        minimum = defaults.integer(forKey: "temperature_min")
        hasData = defaults.integer(forKey: "updated_at") > 0
    }

    var symbol: String {
        switch weatherCode {
        case 0: "☀︎"
        case 1, 2: "🌤"
        case 3: "☁︎"
        case 45, 48: "≋"
        case 51...67, 80...82: "☔︎"
        case 71...77, 85, 86: "❄︎"
        case 95...99: "ϟ"
        default: ""
        }
    }

    var rainLabel: String {
        "\(String(localized: "Rain")) \(rainChance)%"
    }

    var dailyRangeAccessibilityLabel: String {
        let high = String(localized: "High")
        let low = String(localized: "Low")
        return "\(high) \(maximum)°, \(low) \(minimum)°"
    }
}

private struct WeatherPayload: Sendable {
    let location: String
    let temperature: Int
    let temperatureUnit: String
    let weatherCode: Int
    let rainChance: Int
    let airQuality: Int
    let hasDailyRange: Bool
    let maximum: Int
    let minimum: Int
    let updatedAt: Int

    init(_ context: [String: Any]) {
        location = context["location"] as? String ?? ""
        temperature = context["temperature_c"] as? Int ?? 0
        temperatureUnit = context["temperature_unit"] as? String ?? "°C"
        weatherCode = context["weather_code"] as? Int ?? -1
        rainChance = context["rain_chance"] as? Int ?? 0
        airQuality = context["aqi"] as? Int ?? -1
        hasDailyRange = context["has_daily_range"] as? Bool ?? false
        maximum = context["temperature_max"] as? Int ?? 0
        minimum = context["temperature_min"] as? Int ?? 0
        updatedAt = context["updated_at"] as? Int ?? 0
    }
}
