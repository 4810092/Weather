import CoreFoundation
import Foundation

enum SurfaceWeatherFreshness: Equatable, Sendable {
    case empty
    case fresh
    case stale
}

struct SurfaceWeatherSnapshot: Equatable, Sendable {
    let updatedAt: Date
    let location: String
    let temperature: Int
    let temperatureUnit: String
    let weatherCode: Int
    let rainChance: Int
    let airQuality: Int?
    let maximum: Int?
    let minimum: Int?

    var hasDailyRange: Bool {
        maximum != nil && minimum != nil
    }

    var applicationContext: [String: Any] {
        var context: [String: Any] = [
            "location": location,
            "temperature_c": temperature,
            "temperature_unit": temperatureUnit,
            "weather_code": weatherCode,
            "rain_chance": rainChance,
            "has_daily_range": hasDailyRange,
            "updated_at": Int(updatedAt.timeIntervalSince1970)
        ]
        if let airQuality {
            context["aqi"] = airQuality
        }
        if let maximum, let minimum {
            context["temperature_max"] = maximum
            context["temperature_min"] = minimum
        }
        return context
    }

    func write(to defaults: UserDefaults) {
        defaults.set(location, forKey: "location")
        defaults.set(temperature, forKey: "temperature_c")
        defaults.set(temperatureUnit, forKey: "temperature_unit")
        defaults.set(weatherCode, forKey: "weather_code")
        defaults.set(rainChance, forKey: "rain_chance")
        defaults.set(Int(updatedAt.timeIntervalSince1970), forKey: "updated_at")

        if let airQuality {
            defaults.set(airQuality, forKey: "aqi")
        } else {
            defaults.removeObject(forKey: "aqi")
        }

        defaults.set(hasDailyRange, forKey: "has_daily_range")
        if let maximum, let minimum {
            defaults.set(maximum, forKey: "temperature_max")
            defaults.set(minimum, forKey: "temperature_min")
        } else {
            defaults.removeObject(forKey: "temperature_max")
            defaults.removeObject(forKey: "temperature_min")
        }
    }
}

enum SurfaceWeatherState: Equatable, Sendable {
    case empty
    case fresh(SurfaceWeatherSnapshot)
    case stale(SurfaceWeatherSnapshot)

    var freshness: SurfaceWeatherFreshness {
        switch self {
        case .empty: .empty
        case .fresh: .fresh
        case .stale: .stale
        }
    }

    var snapshot: SurfaceWeatherSnapshot? {
        switch self {
        case .empty: nil
        case let .fresh(snapshot), let .stale(snapshot): snapshot
        }
    }
}

enum SurfaceWeatherStateReader {
    // This must remain aligned with WeatherRepository.STALE_AFTER_SECONDS.
    static let staleAfterSeconds: TimeInterval = 6 * 60 * 60
    static let maximumFutureSkewSeconds: TimeInterval = 5 * 60

    private static let supportedWeatherCodes: Set<Int> = [
        0, 1, 2, 3, 45, 48, 51, 53, 55, 56, 57,
        61, 63, 65, 66, 67, 71, 73, 75, 77,
        80, 81, 82, 85, 86, 95, 96, 99
    ]

    static func read(
        from defaults: UserDefaults?,
        now: Date = Date()
    ) -> SurfaceWeatherState {
        guard let snapshot = snapshot(from: defaults, now: now) else { return .empty }
        return state(for: snapshot, now: now)
    }

    static func read(
        from context: [String: Any],
        now: Date = Date()
    ) -> SurfaceWeatherState {
        guard let snapshot = snapshot(from: context, now: now) else { return .empty }
        return state(for: snapshot, now: now)
    }

    static func snapshot(
        from defaults: UserDefaults?,
        now: Date = Date()
    ) -> SurfaceWeatherSnapshot? {
        guard let defaults else { return nil }
        return snapshot(objectForKey: { defaults.object(forKey: $0) }, now: now)
    }

    static func snapshot(
        from context: [String: Any],
        now: Date = Date()
    ) -> SurfaceWeatherSnapshot? {
        snapshot(objectForKey: { context[$0] }, now: now)
    }

    static func removeSnapshot(from defaults: UserDefaults) {
        for key in [
            "location",
            "temperature_c",
            "temperature_unit",
            "weather_code",
            "rain_chance",
            "aqi",
            "has_daily_range",
            "temperature_max",
            "temperature_min",
            "updated_at"
        ] {
            defaults.removeObject(forKey: key)
        }
    }

    static func state(
        for snapshot: SurfaceWeatherSnapshot?,
        now: Date = Date()
    ) -> SurfaceWeatherState {
        guard let snapshot else { return .empty }
        let age = now.timeIntervalSince(snapshot.updatedAt)
        guard age >= -maximumFutureSkewSeconds else { return .empty }
        if age > staleAfterSeconds {
            return .stale(snapshot)
        }
        return .fresh(snapshot)
    }

    static func freshnessBoundaryRefreshDate(
        for state: SurfaceWeatherState,
        now: Date
    ) -> Date? {
        guard case let .fresh(snapshot) = state else { return nil }
        let firstStaleSecond = snapshot.updatedAt.addingTimeInterval(staleAfterSeconds + 1)
        guard firstStaleSecond > now else { return now.addingTimeInterval(1) }
        return firstStaleSecond
    }

    private static func snapshot(
        objectForKey: (String) -> Any?,
        now: Date
    ) -> SurfaceWeatherSnapshot? {
        guard
            let updatedAtSeconds = integer(objectForKey("updated_at")),
            updatedAtSeconds > 0,
            let location = nonBlankString(objectForKey("location"), maximumLength: 100),
            let temperature = integer(objectForKey("temperature_c")),
            (-200...200).contains(temperature),
            let temperatureUnit = nonBlankString(
                objectForKey("temperature_unit"),
                maximumLength: 8
            ),
            let weatherCode = integer(objectForKey("weather_code")),
            supportedWeatherCodes.contains(weatherCode),
            let rainChance = integer(objectForKey("rain_chance")),
            (0...100).contains(rainChance),
            let hasDailyRange = boolean(objectForKey("has_daily_range"))
        else {
            return nil
        }

        let updatedAt = Date(timeIntervalSince1970: TimeInterval(updatedAtSeconds))
        guard updatedAt.timeIntervalSince(now) <= maximumFutureSkewSeconds else {
            return nil
        }

        let airQualityObject = objectForKey("aqi")
        let airQuality: Int?
        if airQualityObject == nil {
            airQuality = nil
        } else {
            guard
                let storedAirQuality = integer(airQualityObject),
                (-1...1_000).contains(storedAirQuality)
            else {
                return nil
            }
            airQuality = storedAirQuality == -1 ? nil : storedAirQuality
        }

        let maximum: Int?
        let minimum: Int?
        if hasDailyRange {
            guard
                let storedMaximum = integer(objectForKey("temperature_max")),
                let storedMinimum = integer(objectForKey("temperature_min")),
                (-200...200).contains(storedMaximum),
                (-200...200).contains(storedMinimum)
            else {
                return nil
            }
            maximum = storedMaximum
            minimum = storedMinimum
        } else {
            maximum = nil
            minimum = nil
        }

        return SurfaceWeatherSnapshot(
            updatedAt: updatedAt,
            location: location,
            temperature: temperature,
            temperatureUnit: temperatureUnit,
            weatherCode: weatherCode,
            rainChance: rainChance,
            airQuality: airQuality,
            maximum: maximum,
            minimum: minimum
        )
    }

    private static func integer(_ object: Any?) -> Int? {
        guard
            let object,
            let number = object as? NSNumber,
            CFGetTypeID(number) != CFBooleanGetTypeID()
        else {
            return nil
        }
        let integerEncodings: Set<String> = [
            "c", "s", "i", "l", "q",
            "C", "S", "I", "L", "Q"
        ]
        guard integerEncodings.contains(String(cString: number.objCType)) else {
            return nil
        }
        return Int(number.stringValue)
    }

    private static func boolean(_ object: Any?) -> Bool? {
        guard
            let number = object as? NSNumber,
            CFGetTypeID(number) == CFBooleanGetTypeID()
        else {
            return nil
        }
        return number.boolValue
    }

    private static func nonBlankString(
        _ object: Any?,
        maximumLength: Int
    ) -> String? {
        guard let string = object as? String else { return nil }
        let trimmed = string.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty, trimmed.count <= maximumLength else { return nil }
        return trimmed
    }
}
