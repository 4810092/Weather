import Foundation

/// The small, native decoder used when WidgetKit is given time to refresh without
/// launching the Kotlin application.  It intentionally asks Open-Meteo for the
/// same payload as `OpenMeteoService`, so its result can be published through the
/// existing surface cache.
enum WidgetWeatherClient {
    static let forecastEndpoint = URL(string: "https://api.open-meteo.com/v1/forecast")!
    static let airQualityEndpoint = URL(string: "https://air-quality-api.open-meteo.com/v1/air-quality")!

    static func forecastURL(config: WidgetRefreshConfiguration) -> URL {
        var components = URLComponents(url: forecastEndpoint, resolvingAgainstBaseURL: false)!
        components.queryItems = [
            .init(name: "latitude", value: String(config.latitude)),
            .init(name: "longitude", value: String(config.longitude)),
            .init(name: "timezone", value: "auto"),
            .init(name: "timeformat", value: "unixtime"),
            .init(name: "past_days", value: "1"),
            .init(name: "forecast_days", value: "10"),
            .init(name: "hourly", value: [
                "temperature_2m", "apparent_temperature", "weather_code",
                "precipitation_probability", "precipitation", "wind_speed_10m",
                "wind_gusts_10m", "relative_humidity_2m", "uv_index"
            ].joined(separator: ",")),
            .init(name: "daily", value: [
                "weather_code", "temperature_2m_max", "temperature_2m_min",
                "apparent_temperature_max", "apparent_temperature_min",
                "precipitation_probability_max", "precipitation_sum",
                "wind_speed_10m_max", "wind_gusts_10m_max", "uv_index_max",
                "sunrise", "sunset"
            ].joined(separator: ","))
        ]
        return components.url!
    }

    static func airQualityURL(config: WidgetRefreshConfiguration) -> URL {
        var components = URLComponents(url: airQualityEndpoint, resolvingAgainstBaseURL: false)!
        components.queryItems = [
            .init(name: "latitude", value: String(config.latitude)),
            .init(name: "longitude", value: String(config.longitude)),
            .init(name: "timezone", value: "auto"),
            .init(name: "timeformat", value: "unixtime"),
            .init(name: "forecast_days", value: "5"),
            .init(name: "hourly", value: "us_aqi,pm2_5,pm10,dust,ozone,nitrogen_dioxide")
        ]
        return components.url!
    }

    static func snapshot(
        forecast: Data,
        airQuality: Data?,
        config: WidgetRefreshConfiguration,
        fetchedAt: Date,
        now: Date
    ) throws -> SurfaceWeatherSnapshot {
        try validate(config: config)
        let decoded = try JSONDecoder().decode(ForecastResponse.self, from: forecast)
        let current = try decoded.hourly.nearest(to: now)
        let today = decoded.daily?.today(at: now, timezone: decoded.timezone)
        let aqi = airQuality.flatMap { try? decodeAirQuality($0, nearestTo: current.time) }
        let temperature = try displayTemperature(current.temperature, unit: config.temperatureUnit)
        let dailyRange: (maximum: Int, minimum: Int)? = today.flatMap { day in
            guard let maximum = try? displayTemperature(day.maximum, unit: config.temperatureUnit),
                  let minimum = try? displayTemperature(day.minimum, unit: config.temperatureUnit) else {
                return nil
            }
            return (maximum, minimum)
        }

        return SurfaceWeatherSnapshot(
            updatedAt: fetchedAt,
            location: displayLocation(config),
            temperature: temperature,
            temperatureUnit: temperatureSymbol(config.temperatureUnit),
            weatherCode: current.weatherCode,
            rainChance: current.precipitationProbability,
            airQuality: aqi,
            maximum: dailyRange?.maximum,
            minimum: dailyRange?.minimum
        )
    }

    private static func validate(config: WidgetRefreshConfiguration) throws {
        guard config.isValid else {
            throw Error.invalidConfiguration
        }
    }

    private static func displayLocation(_ config: WidgetRefreshConfiguration) -> String {
        let name = config.name.trimmingCharacters(in: .whitespacesAndNewlines)
        if !name.isEmpty { return name }
        return config.country.trimmingCharacters(in: .whitespacesAndNewlines)
    }

    private static func temperatureSymbol(_ unit: String) -> String {
        switch unit.trimmingCharacters(in: .whitespacesAndNewlines).lowercased() {
        case "imperial", "fahrenheit", "°f", "f": return "°F"
        default: return "°C"
        }
    }

    private static func displayTemperature(_ celsius: Double, unit: String) throws -> Int {
        let value = temperatureSymbol(unit) == "°F" ? celsius * 9 / 5 + 32 : celsius
        // kotlin.math.roundToInt is floor(value + 0.5), including negative ties.
        guard value.isFinite else { throw Error.invalidForecast }
        let rounded = floor(value + 0.5)
        guard (-200...200).contains(rounded) else { throw Error.invalidForecast }
        return Int(rounded)
    }

    private static func decodeAirQuality(_ data: Data, nearestTo time: Int64) throws -> Int? {
        let response = try JSONDecoder().decode(AirQualityResponse.self, from: data)
        guard let index = response.hourly.time.indices.min(by: {
            abs(response.hourly.time[$0] - time) < abs(response.hourly.time[$1] - time)
        }) else { return nil }
        guard response.hourly.usAqi.indices.contains(index),
              let aqi = response.hourly.usAqi[index] else { return nil }
        guard (-1...1_000).contains(aqi) else { return nil }
        return aqi < 0 ? nil : aqi
    }
}

extension WidgetWeatherClient {
    enum Error: Swift.Error, Equatable {
        case invalidConfiguration
        case invalidForecast
    }
}

private struct ForecastResponse: Decodable {
    let latitude: Double
    let longitude: Double
    let timezone: String
    let utcOffsetSeconds: Int
    let hourly: Hourly
    let daily: Daily?

    enum CodingKeys: String, CodingKey {
        case latitude, longitude, timezone, hourly, daily
        case utcOffsetSeconds = "utc_offset_seconds"
    }

    init(from decoder: Decoder) throws {
        let values = try decoder.container(keyedBy: CodingKeys.self)
        latitude = try values.decode(Double.self, forKey: .latitude)
        longitude = try values.decode(Double.self, forKey: .longitude)
        timezone = try values.decode(String.self, forKey: .timezone)
        utcOffsetSeconds = try values.decode(Int.self, forKey: .utcOffsetSeconds)
        hourly = try values.decode(Hourly.self, forKey: .hourly)
        daily = try values.decodeIfPresent(Daily.self, forKey: .daily)
    }

    struct Hourly: Decodable {
        let time: [Int64]
        let temperature: [Double]
        let apparentTemperature: [Double]
        let weatherCode: [Int]
        let precipitationProbability: [Int?]
        let windSpeed: [Double]
        let humidity: [Int]

        enum CodingKeys: String, CodingKey {
            case time
            case temperature = "temperature_2m"
            case apparentTemperature = "apparent_temperature"
            case weatherCode = "weather_code"
            case precipitationProbability = "precipitation_probability"
            case windSpeed = "wind_speed_10m"
            case humidity = "relative_humidity_2m"
        }

        init(from decoder: Decoder) throws {
            let values = try decoder.container(keyedBy: CodingKeys.self)
            time = try values.decode([Int64].self, forKey: .time)
            temperature = try values.decode([Double].self, forKey: .temperature)
            apparentTemperature = try values.decode([Double].self, forKey: .apparentTemperature)
            weatherCode = try values.decode([Int].self, forKey: .weatherCode)
            precipitationProbability = try values.decodeIfPresent([Int?].self, forKey: .precipitationProbability) ?? []
            windSpeed = try values.decode([Double].self, forKey: .windSpeed)
            humidity = try values.decode([Int].self, forKey: .humidity)
        }

        func nearest(to now: Date) throws -> (time: Int64, temperature: Double, weatherCode: Int, precipitationProbability: Int) {
            let requiredCount = [
                time.count, temperature.count, apparentTemperature.count,
                weatherCode.count, windSpeed.count, humidity.count
            ].min() ?? 0
            guard requiredCount > 0 else { throw WidgetWeatherClient.Error.invalidForecast }
            let target = Int64(now.timeIntervalSince1970)
            guard let index = (0..<requiredCount).min(by: {
                distance(time[$0], from: target) < distance(time[$1], from: target)
            }) else { throw WidgetWeatherClient.Error.invalidForecast }
            let rain: Int = precipitationProbability.indices.contains(index)
                ? (precipitationProbability[index] ?? 0)
                : 0
            guard temperature[index].isFinite,
                  distance(time[index], from: target) <= WidgetWeatherClient.maximumCurrentObservationDistance,
                  WidgetWeatherClient.supportedWeatherCodes.contains(weatherCode[index]),
                  (0...100).contains(rain) else {
                throw WidgetWeatherClient.Error.invalidForecast
            }
            return (time[index], temperature[index], weatherCode[index], rain)
        }
    }

    struct Daily: Decodable {
        let time: [Int64]
        let weatherCode: [Int]
        let maximum: [Double]
        let minimum: [Double]
        let apparentMaximum: [Double]
        let apparentMinimum: [Double]
        let windMaximum: [Double]
        let sunrise: [Int64]
        let sunset: [Int64]

        enum CodingKeys: String, CodingKey {
            case time
            case weatherCode = "weather_code"
            case maximum = "temperature_2m_max"
            case minimum = "temperature_2m_min"
            case apparentMaximum = "apparent_temperature_max"
            case apparentMinimum = "apparent_temperature_min"
            case windMaximum = "wind_speed_10m_max"
            case sunrise
            case sunset
        }

        init(from decoder: Decoder) throws {
            let values = try decoder.container(keyedBy: CodingKeys.self)
            time = try values.decodeIfPresent([Int64].self, forKey: .time) ?? []
            weatherCode = try values.decodeIfPresent([Int].self, forKey: .weatherCode) ?? []
            maximum = try values.decodeIfPresent([Double].self, forKey: .maximum) ?? []
            minimum = try values.decodeIfPresent([Double].self, forKey: .minimum) ?? []
            apparentMaximum = try values.decodeIfPresent([Double].self, forKey: .apparentMaximum) ?? []
            apparentMinimum = try values.decodeIfPresent([Double].self, forKey: .apparentMinimum) ?? []
            windMaximum = try values.decodeIfPresent([Double].self, forKey: .windMaximum) ?? []
            sunrise = try values.decodeIfPresent([Int64].self, forKey: .sunrise) ?? []
            sunset = try values.decodeIfPresent([Int64].self, forKey: .sunset) ?? []
        }

        func today(at now: Date, timezone: String) -> (maximum: Double, minimum: Double)? {
            let count = [
                time.count, weatherCode.count, maximum.count, minimum.count,
                apparentMaximum.count, apparentMinimum.count, windMaximum.count,
                sunrise.count, sunset.count
            ].min() ?? 0
            guard count > 0 else { return nil }
            let calendar = Calendar(identifier: .gregorian)
            guard let zone = TimeZone(identifier: timezone) else { return nil }
            let today = calendar.dateComponents(in: zone, from: now)
            guard let index = (0..<count).first(where: {
                let day = calendar.dateComponents(in: zone, from: Date(timeIntervalSince1970: TimeInterval(time[$0])))
                return day.year == today.year && day.month == today.month && day.day == today.day
            }), maximum[index].isFinite, minimum[index].isFinite else { return nil }
            return (maximum[index], minimum[index])
        }
    }
}

private struct AirQualityResponse: Decodable {
    let hourly: Hourly

    struct Hourly: Decodable {
        let time: [Int64]
        let usAqi: [Int?]

        enum CodingKeys: String, CodingKey {
            case time
            case usAqi = "us_aqi"
        }
    }
}

private extension Array {
    subscript(safe index: Index) -> Element? {
        indices.contains(index) ? self[index] : nil
    }
}

private extension WidgetWeatherClient {
    static let maximumCurrentObservationDistance: Int64 = 3 * 60 * 60
    static let supportedWeatherCodes: Set<Int> = [
        0, 1, 2, 3, 45, 48, 51, 53, 55, 56, 57,
        61, 63, 65, 66, 67, 71, 73, 75, 77,
        80, 81, 82, 85, 86, 95, 96, 99
    ]
}

private func distance(_ lhs: Int64, from rhs: Int64) -> Int64 {
    let result = lhs >= rhs
        ? lhs.subtractingReportingOverflow(rhs)
        : rhs.subtractingReportingOverflow(lhs)
    return result.overflow ? .max : result.partialValue
}
