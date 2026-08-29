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
        TimelineView(.periodic(from: .now, by: 60)) { context in
            WatchWeatherContent(state: weather.state(at: context.date))
        }
    }
}

private struct WatchWeatherContent: View {
    let state: SurfaceWeatherState

    var body: some View {
        Group {
            switch state {
            case .empty:
                Text(String(localized: "Open Nimbo on your phone"))
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(.secondary)
                    .multilineTextAlignment(.center)
                    .accessibilityElement(children: .combine)
            case let .fresh(snapshot):
                weather(snapshot, isStale: false)
            case let .stale(snapshot):
                weather(snapshot, isStale: true)
            }
        }
        .multilineTextAlignment(.center)
        .padding(.horizontal, 8)
    }

    private func weather(
        _ snapshot: SurfaceWeatherSnapshot,
        isStale: Bool
    ) -> some View {
        VStack(spacing: isStale ? 2 : 4) {
            Text(snapshot.location)
                .font(.caption.weight(.semibold))
                .foregroundStyle(.secondary)
                .lineLimit(1)
            Text("\(snapshot.temperature)\(snapshot.temperatureUnit)")
                .font(.system(size: 42, weight: .light, design: .rounded))
                .monospacedDigit()
            if snapshot.hasDailyRange {
                Text("↑\(snapshot.maximum ?? 0)°   ↓\(snapshot.minimum ?? 0)°")
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(.secondary)
                    .monospacedDigit()
                    .accessibilityLabel(dailyRangeAccessibilityLabel(snapshot))
            }
            Text("\(symbol(snapshot.weatherCode))  ·  \(rainLabel(snapshot))")
                .font(.caption2)
            if let airQuality = snapshot.airQuality {
                Text("AQI \(airQuality)")
                    .font(.caption2)
                    .foregroundStyle(.secondary)
            }
            if isStale {
                Text(String(localized: "Saved weather · update needed"))
                    .font(.system(size: 9, weight: .semibold))
                    .foregroundStyle(.secondary)
                    .lineLimit(2)
                    .minimumScaleFactor(0.7)
            }
        }
    }

    private func symbol(_ weatherCode: Int) -> String {
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

    private func rainLabel(_ snapshot: SurfaceWeatherSnapshot) -> String {
        "\(String(localized: "Rain")) \(snapshot.rainChance)%"
    }

    private func dailyRangeAccessibilityLabel(_ snapshot: SurfaceWeatherSnapshot) -> String {
        let high = String(localized: "High")
        let low = String(localized: "Low")
        return "\(high) \(snapshot.maximum ?? 0)°, \(low) \(snapshot.minimum ?? 0)°"
    }
}

@MainActor
private final class WatchWeatherModel: NSObject, ObservableObject, WCSessionDelegate {
    @Published private(set) var snapshot: SurfaceWeatherSnapshot?

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
        guard
            activationState == .activated,
            error == nil,
            !session.receivedApplicationContext.isEmpty
        else {
            return
        }
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

    private func apply(_ payload: WeatherPayload) {
        let defaults = UserDefaults.standard
        if let snapshot = payload.snapshot {
            snapshot.write(to: defaults)
        } else {
            // An empty or malformed latest phone payload must not leave an old
            // snapshot presented as current weather.
            SurfaceWeatherStateReader.removeSnapshot(from: defaults)
        }
        self.snapshot = payload.snapshot
    }

    private func readDefaults() {
        snapshot = SurfaceWeatherStateReader.snapshot(from: UserDefaults.standard)
    }

    func state(at date: Date) -> SurfaceWeatherState {
        SurfaceWeatherStateReader.state(for: snapshot, now: date)
    }
}

private struct WeatherPayload: Sendable {
    let snapshot: SurfaceWeatherSnapshot?

    init(_ context: [String: Any]) {
        snapshot = SurfaceWeatherStateReader.snapshot(from: context)
    }
}

#if DEBUG
private struct WatchWeatherContentPreviews: PreviewProvider {
    private static let freshSnapshot = SurfaceWeatherSnapshot(
        updatedAt: .now,
        location: "Tashkent",
        temperature: 24,
        temperatureUnit: "°C",
        weatherCode: 1,
        rainChance: 10,
        airQuality: 42,
        maximum: 27,
        minimum: 18
    )

    static var previews: some View {
        Group {
            WatchWeatherContent(state: .empty)
                .previewDisplayName("Empty")
            WatchWeatherContent(state: .fresh(freshSnapshot))
                .previewDisplayName("Fresh")
            WatchWeatherContent(state: .stale(freshSnapshot))
                .previewDisplayName("Stale")
        }
    }
}
#endif
