import SwiftUI
import WidgetKit

private let appGroup = "group.uz.ganikhodjaev.weather"

private struct WeatherEntry: TimelineEntry {
    let date: Date
    let location: String
    let temperature: Int?
    let temperatureUnit: String
    let weatherCode: Int
    let rainChance: Int
    let airQuality: Int?
    let maximum: Int?
    let minimum: Int?

    static let placeholder = WeatherEntry(
        date: .now,
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

private struct WeatherProvider: TimelineProvider {
    func placeholder(in context: Context) -> WeatherEntry {
        .placeholder
    }

    func getSnapshot(in context: Context, completion: @escaping (WeatherEntry) -> Void) {
        completion(readEntry())
    }

    func getTimeline(in context: Context, completion: @escaping (Timeline<WeatherEntry>) -> Void) {
        let entry = readEntry()
        let nextUpdate = Calendar.current.date(byAdding: .minute, value: 30, to: .now) ?? .now
        completion(Timeline(entries: [entry], policy: .after(nextUpdate)))
    }

    private func readEntry() -> WeatherEntry {
        let defaults = UserDefaults(suiteName: appGroup)
        let updatedAt = defaults?.integer(forKey: "updated_at") ?? 0
        let aqi = defaults?.integer(forKey: "aqi") ?? -1
        let hasDailyRange = defaults?.bool(forKey: "has_daily_range") ?? false
        return WeatherEntry(
            date: updatedAt > 0 ? Date(timeIntervalSince1970: TimeInterval(updatedAt)) : .now,
            location: defaults?.string(forKey: "location") ?? String(localized: "Open Nimbo"),
            temperature: updatedAt > 0 ? defaults?.integer(forKey: "temperature_c") : nil,
            temperatureUnit: defaults?.string(forKey: "temperature_unit") ?? "°C",
            weatherCode: defaults?.integer(forKey: "weather_code") ?? -1,
            rainChance: defaults?.integer(forKey: "rain_chance") ?? 0,
            airQuality: aqi >= 0 ? aqi : nil,
            maximum: hasDailyRange ? defaults?.integer(forKey: "temperature_max") : nil,
            minimum: hasDailyRange ? defaults?.integer(forKey: "temperature_min") : nil
        )
    }
}

private struct NimboWidgetView: View {
    @Environment(\.widgetFamily) private var family
    @Environment(\.colorScheme) private var colorScheme
    let entry: WeatherEntry

    @ViewBuilder
    var body: some View {
        if #available(iOS 16.0, *) {
            switch family {
            case .accessoryInline:
                Text("\(symbol) \(temperature) · \(rangeText)")
            case .accessoryCircular:
                VStack(spacing: 0) {
                    Text(symbol)
                    Text(temperature).font(.caption.bold())
                    if hasDailyRange {
                        Text(rangeText).font(.system(size: 8, weight: .semibold))
                    }
                }
            case .accessoryRectangular:
                VStack(alignment: .leading, spacing: 1) {
                    Text(entry.location).font(.headline).lineLimit(1)
                    Text("\(symbol) \(temperature) · \(rainLabel)")
                        .font(.caption)
                    if hasDailyRange {
                        Text(rangeText).font(.caption2.weight(.semibold))
                    }
                }
            default:
                homeWidget
            }
        } else {
            homeWidget
        }
    }

    private var homeWidget: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(entry.location)
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(.secondary)
                .lineLimit(1)
            Spacer(minLength: 2)
            HStack(alignment: .firstTextBaseline) {
                Text(temperature)
                    .font(.system(size: 40, weight: .light, design: .rounded))
                    .monospacedDigit()
                Spacer()
                Text(symbol).font(.title)
            }
            if hasDailyRange {
                Text(rangeText)
                    .font(.caption.weight(.semibold))
                    .monospacedDigit()
                    .accessibilityLabel(dailyRangeAccessibilityLabel)
            }
            HStack(spacing: 6) {
                Label("\(entry.rainChance)%", systemImage: "drop.fill")
                if let airQuality = entry.airQuality {
                    Text("· AQI \(airQuality)")
                }
            }
            .font(.caption)
            .foregroundStyle(.secondary)
        }
        .nimboWidgetBackground(
            colorScheme == .dark
                ? Color(red: 0.063, green: 0.094, blue: 0.125)
                : Color(red: 0.953, green: 0.969, blue: 0.988)
        )
    }

    private var hasDailyRange: Bool {
        entry.maximum != nil && entry.minimum != nil
    }

    private var rangeText: String {
        guard let maximum = entry.maximum, let minimum = entry.minimum else { return "—" }
        return "↑\(maximum)°  ↓\(minimum)°"
    }

    private var rainLabel: String {
        "\(String(localized: "Rain")) \(entry.rainChance)%"
    }

    private var dailyRangeAccessibilityLabel: String {
        let high = String(localized: "High")
        let low = String(localized: "Low")
        return "\(high) \(entry.maximum ?? 0)°, \(low) \(entry.minimum ?? 0)°"
    }

    private var temperature: String {
        entry.temperature.map { "\($0)\(entry.temperatureUnit)" } ?? "—°"
    }

    private var symbol: String {
        switch entry.weatherCode {
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
}

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
