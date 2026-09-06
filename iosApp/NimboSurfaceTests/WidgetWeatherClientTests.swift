import Foundation
import XCTest

final class WidgetWeatherClientTests: XCTestCase {
    private let now = Date(timeIntervalSince1970: 1_780_000_000)

    func testForecastURLMatchesTheApplicationOpenMeteoRequest() throws {
        let items = try XCTUnwrap(URLComponents(
            url: WidgetWeatherClient.forecastURL(config: configuration()),
            resolvingAgainstBaseURL: false
        )?.queryItems)
        let values = Dictionary(uniqueKeysWithValues: items.compactMap { item in
            item.value.map { (item.name, $0) }
        })

        XCTAssertEqual(values["past_days"], "1")
        XCTAssertEqual(values["forecast_days"], "10")
        XCTAssertEqual(values["timezone"], "auto")
        XCTAssertEqual(values["timeformat"], "unixtime")
        XCTAssertEqual(values["hourly"], "temperature_2m,apparent_temperature,weather_code,precipitation_probability,precipitation,wind_speed_10m,wind_gusts_10m,relative_humidity_2m,uv_index")
        XCTAssertEqual(values["daily"], "weather_code,temperature_2m_max,temperature_2m_min,apparent_temperature_max,apparent_temperature_min,precipitation_probability_max,precipitation_sum,wind_speed_10m_max,wind_gusts_10m_max,uv_index_max,sunrise,sunset")
    }

    func testMapsNearestHourlyValueAndTodaysRange() throws {
        let fetchedAt = now.addingTimeInterval(-1)
        let snapshot = try WidgetWeatherClient.snapshot(
            forecast: forecastJSON(hourlyTimes: [1_779_999_600, 1_780_000_400]),
            airQuality: airQualityJSON(times: [1_779_999_600], values: [42]),
            config: configuration(),
            fetchedAt: fetchedAt,
            now: now
        )

        XCTAssertEqual(snapshot.updatedAt, fetchedAt)
        XCTAssertEqual(snapshot.location, "Tashkent")
        XCTAssertEqual(snapshot.temperature, 21)
        XCTAssertEqual(snapshot.temperatureUnit, "°C")
        XCTAssertEqual(snapshot.weatherCode, 3)
        XCTAssertEqual(snapshot.rainChance, 22)
        XCTAssertEqual(snapshot.airQuality, 42)
        XCTAssertEqual(snapshot.maximum, 27)
        XCTAssertEqual(snapshot.minimum, 16)
    }

    func testFahrenheitUsesKotlinHalfAwayFromZeroRounding() throws {
        let snapshot = try WidgetWeatherClient.snapshot(
            forecast: forecastJSON(hourlyTimes: [1_780_000_000], temperatures: [20.25]),
            airQuality: nil,
            config: configuration(temperatureUnit: "°F"),
            fetchedAt: now,
            now: now
        )

        XCTAssertEqual(snapshot.temperatureUnit, "°F")
        XCTAssertEqual(snapshot.temperature, 68)
        XCTAssertEqual(snapshot.maximum, 81)
        XCTAssertEqual(snapshot.minimum, 60)
    }

    func testNegativeHalfRoundsTowardPositiveInfinityLikeKotlin() throws {
        let snapshot = try WidgetWeatherClient.snapshot(
            forecast: forecastJSON(hourlyTimes: [1_780_000_000], temperatures: [-1.5]),
            airQuality: nil,
            config: configuration(),
            fetchedAt: now,
            now: now
        )

        XCTAssertEqual(snapshot.temperature, -1)
    }

    func testMalformedOptionalAirQualityDoesNotRejectForecast() throws {
        let snapshot = try WidgetWeatherClient.snapshot(
            forecast: forecastJSON(hourlyTimes: [1_780_000_000]),
            airQuality: Data("{bad json".utf8),
            config: configuration(),
            fetchedAt: now,
            now: now
        )

        XCTAssertNil(snapshot.airQuality)
    }

    func testInvalidPrimaryWeatherDoesNotPublish() {
        XCTAssertThrowsError(
            try WidgetWeatherClient.snapshot(
                forecast: forecastJSON(hourlyTimes: [1_780_000_000], weatherCodes: [999]),
                airQuality: nil,
                config: configuration(),
                fetchedAt: now,
                now: now
            )
        )
    }

    private func configuration(temperatureUnit: String = "°C") -> WidgetRefreshConfiguration {
        WidgetRefreshConfiguration(
            id: "1512569",
            name: "Tashkent",
            country: "Uzbekistan",
            latitude: 41.2995,
            longitude: 69.2401,
            timezone: "UTC",
            temperatureUnit: temperatureUnit,
            attemptKey: "last_attempt_1512569"
        )
    }

    private func forecastJSON(
        hourlyTimes: [Int64],
        temperatures: [Double] = [20.5, 21.4],
        weatherCodes: [Int] = [3, 2]
    ) -> Data {
        let payload: [String: Any] = [
            "latitude": 41.2995,
            "longitude": 69.2401,
            "timezone": "UTC",
            "utc_offset_seconds": 0,
            "hourly": [
                "time": hourlyTimes,
                "temperature_2m": Array(temperatures.prefix(hourlyTimes.count)),
                "apparent_temperature": Array(temperatures.prefix(hourlyTimes.count)),
                "weather_code": Array(weatherCodes.prefix(hourlyTimes.count)),
                "precipitation_probability": [22, 41],
                "wind_speed_10m": Array(repeating: 10, count: hourlyTimes.count),
                "relative_humidity_2m": Array(repeating: 50, count: hourlyTimes.count)
            ],
            "daily": [
                "time": [1_779_994_800],
                "weather_code": [3],
                "temperature_2m_max": [27.4],
                "temperature_2m_min": [15.6],
                "apparent_temperature_max": [27.4],
                "apparent_temperature_min": [15.6],
                "wind_speed_10m_max": [10],
                "sunrise": [1_780_016_400],
                "sunset": [1_780_066_800]
            ]
        ]
        return try! JSONSerialization.data(withJSONObject: payload)
    }

    private func airQualityJSON(times: [Int64], values: [Int?]) -> Data {
        let payload: [String: Any] = [
            "hourly": ["time": times, "us_aqi": values]
        ]
        return try! JSONSerialization.data(withJSONObject: payload)
    }
}
