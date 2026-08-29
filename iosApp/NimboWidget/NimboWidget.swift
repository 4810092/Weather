import SwiftUI
import WidgetKit

private let appGroup = "group.uz.ganikhodjaev.weather"

private struct WeatherEntry: TimelineEntry {
    let date: Date
    let state: SurfaceWeatherState

    static let placeholder = WeatherEntry(
        date: .now,
        state: .fresh(.preview(updatedAt: .now))
    )
}

private struct WeatherProvider: TimelineProvider {
    func placeholder(in context: Context) -> WeatherEntry {
        .placeholder
    }

    func getSnapshot(in context: Context, completion: @escaping (WeatherEntry) -> Void) {
        completion(readEntry())
    }

    func getTimeline(in context: Context, completion: @escaping (Timeline<WeatherEntry>) -> Void) {
        let now = Date()
        let entry = readEntry(now: now)
        if let boundary = SurfaceWeatherStateReader.freshnessBoundaryRefreshDate(
            for: entry.state,
            now: now
        ) {
            // The boundary reload reads the app-group cache only. It never calls
            // the weather provider or starts a network refresh.
            completion(Timeline(entries: [entry], policy: .after(boundary)))
        } else {
            completion(Timeline(entries: [entry], policy: .never))
        }
    }

    private func readEntry(now: Date = Date()) -> WeatherEntry {
        let defaults = UserDefaults(suiteName: appGroup)
        return WeatherEntry(
            date: now,
            state: SurfaceWeatherStateReader.read(from: defaults, now: now)
        )
    }
}

private struct NimboWidgetView: View {
    @Environment(\.widgetFamily) private var family
    @Environment(\.colorScheme) private var colorScheme
    let entry: WeatherEntry

    @ViewBuilder
    var body: some View {
        switch entry.state {
        case .empty:
            emptyWidget
        case let .fresh(snapshot):
            weatherWidget(snapshot, isStale: false)
        case let .stale(snapshot):
            weatherWidget(snapshot, isStale: true)
        }
    }

    @ViewBuilder
    private var emptyWidget: some View {
        if #available(iOS 16.0, *) {
            switch family {
            case .accessoryInline, .accessoryCircular, .accessoryRectangular:
                Text(String(localized: "Open Nimbo"))
                    .font(.caption.weight(.semibold))
                    .lineLimit(2)
                    .minimumScaleFactor(0.65)
                    .multilineTextAlignment(.center)
            default:
                emptyHomeWidget
            }
        } else {
            emptyHomeWidget
        }
    }

    private var emptyHomeWidget: some View {
        VStack {
            Spacer(minLength: 0)
            Text(String(localized: "Open Nimbo"))
                .font(.headline)
                .multilineTextAlignment(.center)
            Spacer(minLength: 0)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .nimboWidgetBackground(widgetBackgroundColor)
        .accessibilityElement(children: .combine)
    }

    @ViewBuilder
    private func weatherWidget(
        _ snapshot: SurfaceWeatherSnapshot,
        isStale: Bool
    ) -> some View {
        if #available(iOS 16.0, *) {
            switch family {
            case .accessoryInline:
                Text(accessoryInlineText(snapshot, isStale: isStale))
            case .accessoryCircular:
                accessoryCircular(snapshot, isStale: isStale)
            case .accessoryRectangular:
                accessoryRectangular(snapshot, isStale: isStale)
            default:
                homeWidget(snapshot, isStale: isStale)
            }
        } else {
            homeWidget(snapshot, isStale: isStale)
        }
    }

    private func accessoryCircular(
        _ snapshot: SurfaceWeatherSnapshot,
        isStale: Bool
    ) -> some View {
        VStack(spacing: 0) {
            Text(symbol(snapshot.weatherCode))
            Text(temperature(snapshot)).font(.caption.bold())
            if snapshot.hasDailyRange {
                Text(
                    isStale
                        ? "\(rangeText(snapshot)) · \(String(localized: "Saved"))"
                        : rangeText(snapshot)
                )
                .font(.system(size: isStale ? 6 : 8, weight: .semibold))
                .lineLimit(1)
                .minimumScaleFactor(0.5)
                .accessibilityLabel(
                    isStale
                        ? "\(dailyRangeAccessibilityLabel(snapshot)), \(String(localized: "Saved weather · update needed"))"
                        : dailyRangeAccessibilityLabel(snapshot)
                )
            } else if isStale {
                Text(String(localized: "Saved"))
                    .font(.system(size: 7, weight: .semibold))
                    .lineLimit(1)
                    .minimumScaleFactor(0.6)
                    .accessibilityLabel(String(localized: "Saved weather · update needed"))
            }
        }
    }

    private func accessoryRectangular(
        _ snapshot: SurfaceWeatherSnapshot,
        isStale: Bool
    ) -> some View {
        VStack(alignment: .leading, spacing: 1) {
            Text(snapshot.location).font(.headline).lineLimit(1)
            Text("\(symbol(snapshot.weatherCode)) \(temperature(snapshot)) · \(rainLabel(snapshot))")
                .font(.caption)
            if snapshot.hasDailyRange {
                Text(rangeText(snapshot)).font(.caption2.weight(.semibold))
            }
            if isStale {
                staleStatus
            }
        }
    }

    private func homeWidget(
        _ snapshot: SurfaceWeatherSnapshot,
        isStale: Bool
    ) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(snapshot.location)
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(.secondary)
                .lineLimit(1)
            Spacer(minLength: 2)
            HStack(alignment: .firstTextBaseline) {
                Text(temperature(snapshot))
                    .font(.system(size: 40, weight: .light, design: .rounded))
                    .monospacedDigit()
                Spacer()
                Text(symbol(snapshot.weatherCode)).font(.title)
            }
            if snapshot.hasDailyRange {
                Text(rangeText(snapshot))
                    .font(.caption.weight(.semibold))
                    .monospacedDigit()
                    .accessibilityLabel(dailyRangeAccessibilityLabel(snapshot))
            }
            HStack(spacing: 6) {
                Label("\(snapshot.rainChance)%", systemImage: "drop.fill")
                if let airQuality = snapshot.airQuality {
                    Text("· AQI \(airQuality)")
                }
            }
            .font(.caption)
            .foregroundStyle(.secondary)
            if isStale {
                staleStatus
            }
        }
        .nimboWidgetBackground(widgetBackgroundColor)
    }

    private var staleStatus: some View {
        Text(String(localized: "Saved weather · update needed"))
            .font(.system(size: 9, weight: .semibold))
            .foregroundStyle(.secondary)
            .lineLimit(1)
            .minimumScaleFactor(0.65)
    }

    private func rangeText(_ snapshot: SurfaceWeatherSnapshot) -> String {
        guard let maximum = snapshot.maximum, let minimum = snapshot.minimum else { return "—" }
        return "↑\(maximum)°  ↓\(minimum)°"
    }

    private func rainLabel(_ snapshot: SurfaceWeatherSnapshot) -> String {
        "\(String(localized: "Rain")) \(snapshot.rainChance)%"
    }

    private func dailyRangeAccessibilityLabel(_ snapshot: SurfaceWeatherSnapshot) -> String {
        let high = String(localized: "High")
        let low = String(localized: "Low")
        return "\(high) \(snapshot.maximum ?? 0)°, \(low) \(snapshot.minimum ?? 0)°"
    }

    private func temperature(_ snapshot: SurfaceWeatherSnapshot) -> String {
        "\(snapshot.temperature)\(snapshot.temperatureUnit)"
    }

    private func symbol(_ weatherCode: Int) -> String {
        switch weatherCode {
        case 0: "☀︎"
        case 1, 2: "🌤"
        case 3: "☁︎"
        case 45, 48: "≋"
        case 51, 53, 55, 56, 57: "☂︎"
        case 61, 63, 65, 66, 67, 80, 81, 82: "☔︎"
        case 71, 73, 75, 77, 85, 86: "❄︎"
        case 95, 96, 99: "ϟ"
        default: "N"
        }
    }

    private func accessoryInlineText(
        _ snapshot: SurfaceWeatherSnapshot,
        isStale: Bool
    ) -> String {
        let rangeOrRain = snapshot.hasDailyRange
            ? rangeText(snapshot)
            : rainLabel(snapshot)
        let weather = "\(symbol(snapshot.weatherCode)) \(temperature(snapshot)) · \(rangeOrRain)"
        if isStale {
            return "\(weather) · \(String(localized: "Saved"))"
        }
        return weather
    }

    private var widgetBackgroundColor: Color {
        colorScheme == .dark
            ? Color(red: 0.063, green: 0.094, blue: 0.125)
            : Color(red: 0.953, green: 0.969, blue: 0.988)
    }
}

private extension SurfaceWeatherSnapshot {
    static func preview(updatedAt: Date) -> SurfaceWeatherSnapshot {
        SurfaceWeatherSnapshot(
            updatedAt: updatedAt,
            location: "Tashkent",
            temperature: 24,
            temperatureUnit: "°C",
            weatherCode: 1,
            rainChance: 10,
            airQuality: 42,
            maximum: 27,
            minimum: 18
        )
    }
}

#if DEBUG
@available(iOS 16.0, *)
private struct NimboWidgetViewPreviews: PreviewProvider {
    private static let empty = WeatherEntry(date: .now, state: .empty)
    private static let fresh = WeatherEntry(
        date: .now,
        state: .fresh(.preview(updatedAt: .now))
    )
    private static let stale = WeatherEntry(
        date: .now,
        state: .stale(
            .preview(
                updatedAt: .now.addingTimeInterval(
                    -(SurfaceWeatherStateReader.staleAfterSeconds + 1)
                )
            )
        )
    )

    static var previews: some View {
        Group {
            Group {
                preview(empty, family: .systemSmall, name: "Small · Empty")
                preview(fresh, family: .systemSmall, name: "Small · Fresh")
                preview(stale, family: .systemSmall, name: "Small · Stale")
                preview(empty, family: .systemMedium, name: "Medium · Empty")
                preview(fresh, family: .systemMedium, name: "Medium · Fresh")
                preview(stale, family: .systemMedium, name: "Medium · Stale")
            }
            Group {
                preview(empty, family: .accessoryInline, name: "Inline · Empty")
                preview(fresh, family: .accessoryInline, name: "Inline · Fresh")
                preview(stale, family: .accessoryInline, name: "Inline · Stale")
                preview(empty, family: .accessoryCircular, name: "Circular · Empty")
                preview(fresh, family: .accessoryCircular, name: "Circular · Fresh")
                preview(stale, family: .accessoryCircular, name: "Circular · Stale")
                preview(empty, family: .accessoryRectangular, name: "Rectangular · Empty")
                preview(fresh, family: .accessoryRectangular, name: "Rectangular · Fresh")
                preview(stale, family: .accessoryRectangular, name: "Rectangular · Stale")
            }
        }
    }

    private static func preview(
        _ entry: WeatherEntry,
        family: WidgetFamily,
        name: String
    ) -> some View {
        NimboWidgetView(entry: entry)
            .previewContext(WidgetPreviewContext(family: family))
            .previewDisplayName(name)
    }
}
#endif

private extension View {
    @ViewBuilder
    func nimboWidgetBackground(_ color: Color) -> some View {
        if #available(iOS 17.0, *) {
            containerBackground(for: .widget) {
                color
            }
        } else {
            background(color)
        }
    }
}

@main
struct NimboWidget: Widget {
    let kind = "NimboWeather"

    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: WeatherProvider()) { entry in
            NimboWidgetView(entry: entry)
        }
        .configurationDisplayName(String(localized: "Nimbo Weather"))
        .description(String(localized: "Weather you can understand at a glance."))
        .supportedFamilies(supportedWidgetFamilies)
    }

    private var supportedWidgetFamilies: [WidgetFamily] {
        var families: [WidgetFamily] = [.systemSmall, .systemMedium]
        if #available(iOS 16.0, *) {
            families.append(contentsOf: [
                .accessoryInline,
                .accessoryCircular,
                .accessoryRectangular
            ])
        }
        return families
    }
}
