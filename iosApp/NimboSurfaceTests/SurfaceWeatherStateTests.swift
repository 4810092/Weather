import Foundation
import XCTest

final class SurfaceWeatherStateTests: XCTestCase {
    private let now = Date(timeIntervalSince1970: 2_000_000_000)
    private var suiteName = ""
    private var defaults: UserDefaults!

    override func setUpWithError() throws {
        suiteName = "SurfaceWeatherStateTests.\(UUID().uuidString)"
        defaults = try XCTUnwrap(UserDefaults(suiteName: suiteName))
        defaults.removePersistentDomain(forName: suiteName)
    }

    override func tearDownWithError() throws {
        defaults.removePersistentDomain(forName: suiteName)
        defaults = nil
    }

    func testEmptyDefaultsAreEmpty() {
        XCTAssertEqual(
            SurfaceWeatherStateReader.read(from: defaults, now: now),
            .empty
        )
    }

    func testPartialRequiredSnapshotIsEmpty() {
        defaults.set(Int(now.timeIntervalSince1970), forKey: "updated_at")
        defaults.set("Tashkent", forKey: "location")
        defaults.set(24, forKey: "temperature_c")

        XCTAssertEqual(
            SurfaceWeatherStateReader.read(from: defaults, now: now),
            .empty
        )
    }

    func testValidZeroValuesRemainValid() throws {
        writeRequiredSnapshot(
            updatedAt: now.addingTimeInterval(-60),
            temperature: 0,
            weatherCode: 0,
            rainChance: 0,
            hasDailyRange: true
        )
        defaults.set(0, forKey: "aqi")
        defaults.set(0, forKey: "temperature_max")
        defaults.set(0, forKey: "temperature_min")

        let state = SurfaceWeatherStateReader.read(from: defaults, now: now)
        guard case let .fresh(snapshot) = state else {
            return XCTFail("Expected a fresh snapshot, found \(state)")
        }
        XCTAssertEqual(snapshot.temperature, 0)
        XCTAssertEqual(snapshot.weatherCode, 0)
        XCTAssertEqual(snapshot.rainChance, 0)
        XCTAssertEqual(snapshot.airQuality, 0)
        XCTAssertEqual(snapshot.maximum, 0)
        XCTAssertEqual(snapshot.minimum, 0)
    }

    func testExactlySixHoursIsFreshAndAnythingAfterIsStale() {
        let updatedAt = now.addingTimeInterval(-SurfaceWeatherStateReader.staleAfterSeconds)
        writeRequiredSnapshot(updatedAt: updatedAt)

        XCTAssertEqual(
            SurfaceWeatherStateReader.read(from: defaults, now: now).freshness,
            .fresh
        )
        XCTAssertEqual(
            SurfaceWeatherStateReader.read(
                from: defaults,
                now: now.addingTimeInterval(0.001)
            ).freshness,
            .stale
        )
    }

    func testFarFutureTimestampFailsClosed() {
        writeRequiredSnapshot(
            updatedAt: now.addingTimeInterval(
                SurfaceWeatherStateReader.maximumFutureSkewSeconds + 1
            )
        )

        XCTAssertEqual(
            SurfaceWeatherStateReader.read(from: defaults, now: now),
            .empty
        )
    }

    func testMaximumAllowedClockSkewRemainsFresh() {
        writeRequiredSnapshot(
            updatedAt: now.addingTimeInterval(
                SurfaceWeatherStateReader.maximumFutureSkewSeconds
            )
        )

        XCTAssertEqual(
            SurfaceWeatherStateReader.read(from: defaults, now: now).freshness,
            .fresh
        )
    }

    func testStateRechecksFutureSkewAfterClockRollback() {
        let snapshot = SurfaceWeatherSnapshot(
            updatedAt: now.addingTimeInterval(
                SurfaceWeatherStateReader.maximumFutureSkewSeconds + 1
            ),
            location: "Tashkent",
            temperature: 24,
            temperatureUnit: "°C",
            weatherCode: 1,
            rainChance: 10,
            airQuality: nil,
            maximum: nil,
            minimum: nil
        )

        XCTAssertEqual(
            SurfaceWeatherStateReader.state(for: snapshot, now: now),
            .empty
        )
    }

    func testBooleanCannotMasqueradeAsRequiredZeroOrOne() {
        writeRequiredSnapshot(updatedAt: now)
        defaults.set(false, forKey: "rain_chance")

        XCTAssertEqual(
            SurfaceWeatherStateReader.read(from: defaults, now: now),
            .empty
        )
    }

    func testMissingDailyRangeFlagFailsClosed() {
        writeRequiredSnapshot(updatedAt: now)
        defaults.removeObject(forKey: "has_daily_range")

        XCTAssertEqual(
            SurfaceWeatherStateReader.read(from: defaults, now: now),
            .empty
        )
    }

    func testEnabledDailyRangeRequiresBothBounds() {
        writeRequiredSnapshot(
            updatedAt: now,
            hasDailyRange: true
        )
        defaults.set(27, forKey: "temperature_max")

        XCTAssertEqual(
            SurfaceWeatherStateReader.read(from: defaults, now: now),
            .empty
        )
    }

    func testMissingOptionalAqiDoesNotCreateAZeroClaim() {
        writeRequiredSnapshot(updatedAt: now)

        let state = SurfaceWeatherStateReader.read(from: defaults, now: now)
        guard case let .fresh(snapshot) = state else {
            return XCTFail("Expected a fresh snapshot, found \(state)")
        }
        XCTAssertNil(snapshot.airQuality)
        XCTAssertNil(snapshot.applicationContext["aqi"])
    }

    func testOptionalAqiSentinelDoesNotCreateAZeroClaim() {
        writeRequiredSnapshot(updatedAt: now)
        defaults.set(-1, forKey: "aqi")

        let state = SurfaceWeatherStateReader.read(from: defaults, now: now)
        guard case let .fresh(snapshot) = state else {
            return XCTFail("Expected a fresh snapshot, found \(state)")
        }
        XCTAssertNil(snapshot.airQuality)
        XCTAssertFalse(snapshot.hasDailyRange)
        XCTAssertNil(snapshot.applicationContext["aqi"])
        XCTAssertNil(snapshot.applicationContext["temperature_max"])
        XCTAssertNil(snapshot.applicationContext["temperature_min"])
    }

    func testInvalidOptionalAqiValuesFailClosed() {
        for invalidAqi in [1_001, -2] {
            writeRequiredSnapshot(updatedAt: now)
            defaults.set(invalidAqi, forKey: "aqi")

            XCTAssertEqual(
                SurfaceWeatherStateReader.read(from: defaults, now: now),
                .empty,
                "AQI \(invalidAqi) must invalidate the snapshot"
            )
        }
    }

    func testWrongTypeOptionalAqiFailsClosed() {
        writeRequiredSnapshot(updatedAt: now)
        defaults.set("42", forKey: "aqi")

        XCTAssertEqual(
            SurfaceWeatherStateReader.read(from: defaults, now: now),
            .empty
        )
    }

    func testFloatingPointIntegerFailsClosed() {
        let context: [String: Any] = [
            "updated_at": Int(now.timeIntervalSince1970),
            "location": "Tashkent",
            "temperature_c": 24,
            "temperature_unit": "°C",
            "weather_code": 1,
            "rain_chance": 10.0,
            "has_daily_range": false
        ]

        XCTAssertEqual(
            SurfaceWeatherStateReader.read(from: context, now: now),
            .empty
        )
    }

    func testRemovingSnapshotClearsEveryWeatherFact() {
        writeRequiredSnapshot(updatedAt: now, hasDailyRange: true)
        defaults.set(42, forKey: "aqi")
        defaults.set(27, forKey: "temperature_max")
        defaults.set(18, forKey: "temperature_min")

        SurfaceWeatherStateReader.removeSnapshot(from: defaults)

        XCTAssertEqual(
            SurfaceWeatherStateReader.read(from: defaults, now: now),
            .empty
        )
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
            XCTAssertNil(defaults.object(forKey: key), "Expected \(key) to be removed")
        }
    }

    func testDictionaryReaderPreservesValidZeros() {
        let context: [String: Any] = [
            "updated_at": Int(now.timeIntervalSince1970),
            "location": "Tashkent",
            "temperature_c": 0,
            "temperature_unit": "°C",
            "weather_code": 0,
            "rain_chance": 0,
            "aqi": 0,
            "has_daily_range": false
        ]

        let state = SurfaceWeatherStateReader.read(from: context, now: now)
        guard case let .fresh(snapshot) = state else {
            return XCTFail("Expected a fresh snapshot, found \(state)")
        }
        XCTAssertEqual(snapshot.temperature, 0)
        XCTAssertEqual(snapshot.weatherCode, 0)
        XCTAssertEqual(snapshot.rainChance, 0)
        XCTAssertEqual(snapshot.airQuality, 0)
    }

    func testTimelineRefreshIsFirstWholeSecondAfterStaleBoundary() throws {
        let updatedAt = now.addingTimeInterval(-60)
        writeRequiredSnapshot(updatedAt: updatedAt)
        let state = SurfaceWeatherStateReader.read(from: defaults, now: now)

        let refresh = try XCTUnwrap(
            SurfaceWeatherStateReader.freshnessBoundaryRefreshDate(
                for: state,
                now: now
            )
        )
        XCTAssertEqual(
            refresh,
            updatedAt.addingTimeInterval(
                SurfaceWeatherStateReader.staleAfterSeconds + 1
            )
        )
    }

    private func writeRequiredSnapshot(
        updatedAt: Date,
        temperature: Int = 24,
        weatherCode: Int = 1,
        rainChance: Int = 10,
        hasDailyRange: Bool = false
    ) {
        defaults.set(Int(updatedAt.timeIntervalSince1970), forKey: "updated_at")
        defaults.set("Tashkent", forKey: "location")
        defaults.set(temperature, forKey: "temperature_c")
        defaults.set("°C", forKey: "temperature_unit")
        defaults.set(weatherCode, forKey: "weather_code")
        defaults.set(rainChance, forKey: "rain_chance")
        defaults.set(hasDailyRange, forKey: "has_daily_range")
    }
}
