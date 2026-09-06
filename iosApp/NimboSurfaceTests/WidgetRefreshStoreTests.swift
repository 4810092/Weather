import Foundation
import XCTest

final class WidgetRefreshStoreTests: XCTestCase {
    private let now = Date(timeIntervalSince1970: 2_000_000_000)
    private var directory: URL!
    private var store: WidgetRefreshStore!
    private let config = WidgetRefreshConfiguration(
        id: "tashkent", name: "Tashkent", country: "Uzbekistan",
        latitude: 41.31, longitude: 69.28, timezone: "Asia/Tashkent",
        temperatureUnit: "°C", attemptKey: "last_attempt_tashkent"
    )

    override func setUpWithError() throws {
        directory = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString)
        let fixedNow = now
        store = WidgetRefreshStore(directory: directory, currentDate: { fixedNow })
    }

    override func tearDownWithError() throws {
        if FileManager.default.fileExists(atPath: directory.path) {
            try FileManager.default.removeItem(at: directory)
        }
    }

    func testUnconfiguredWidgetDoesNotRequestWeatherAndKeepsChecking() {
        XCTAssertNil(store.beginRefresh(now: now))
        XCTAssertGreaterThan(store.nextRefreshDate(now: now), now)
    }

    func testConcurrentHostAndWidgetShareOneDurableClaim() throws {
        try configure()
        let stores = (0..<20).map { _ in WidgetRefreshStore(directory: directory) }
        let results = Results()
        let config = config
        let now = now
        DispatchQueue.concurrentPerform(iterations: stores.count) { index in
            if index.isMultiple(of: 2) {
                results.append(stores[index].beginRefresh(now: now) != nil)
            } else {
                let response = stores[index].exchange(
                    "{\"op\":\"claim\",\"key\":\"\(config.attemptKey)\",\"now\":2000000000}"
                )
                results.append(response.contains("granted"))
            }
        }
        XCTAssertEqual(results.successCount, 1)
        let restarted = WidgetRefreshStore(directory: directory)
        XCTAssertNil(restarted.beginRefresh(now: now.addingTimeInterval(3_599)))
        XCTAssertNotNil(restarted.beginRefresh(now: now.addingTimeInterval(3_600)))
    }

    func testPrimaryPublishesWithoutWaitingForOptionalAqiAndSurvivesRestart() throws {
        try configure()
        let ticket = try XCTUnwrap(store.beginRefresh(now: now))
        XCTAssertTrue(store.recordDownload(ticket: ticket, kind: .forecast, data: forecast(), now: now))
        let restarted = WidgetRefreshStore(directory: directory)
        XCTAssertEqual(restarted.readState(now: now).snapshot?.temperature, 24)
        let primary = try pending(restarted)
        XCTAssertEqual(primary["fetchedAt"] as? Int, 2_000_000_000)
        XCTAssertTrue(restarted.recordDownload(
            ticket: ticket, kind: .airQuality,
            data: Data("{\"hourly\":{\"time\":[2000000000],\"us_aqi\":[42]}}".utf8),
            now: now.addingTimeInterval(5)
        ))
        let enriched = try pending(restarted)
        XCTAssertEqual(enriched["fetchedAt"] as? Int, 2_000_000_000)
        XCTAssertEqual(enriched["airQualityFetchedAt"] as? Int, 2_000_000_005)
        XCTAssertEqual(restarted.readState(now: now).snapshot?.airQuality, 42)
        // An earlier host import must not acknowledge a newer enrichment delivery.
        let acknowledgement = try rpc(restarted, [
            "op": "acknowledge", "deliveryId": primary["deliveryId"]!,
            "revision": primary["revision"]!, "fetchedAt": primary["fetchedAt"]!
        ])
        XCTAssertEqual(acknowledgement["ok"] as? Bool, false)
        XCTAssertNotNil(try pending(restarted)["forecast"])
    }

    func testFailureKeepsOriginalTimestampAndRetriesAfterHour() throws {
        try configure()
        let first = try XCTUnwrap(store.beginRefresh(now: now))
        _ = store.recordDownload(ticket: first, kind: .forecast, data: forecast(), now: now)
        _ = store.recordDownload(ticket: first, kind: .airQuality, data: nil, now: now)
        let later = now.addingTimeInterval(7 * 3_600)
        let failed = try XCTUnwrap(store.beginRefresh(now: later))
        XCTAssertFalse(store.recordDownload(ticket: failed, kind: .forecast, data: nil, now: later))
        XCTAssertEqual(store.readState(now: later).freshness, .stale)
        XCTAssertEqual(store.readState(now: later).snapshot?.updatedAt, now)
        XCTAssertNil(store.beginRefresh(now: later.addingTimeInterval(3_599)))
        XCTAssertNotNil(store.beginRefresh(now: later.addingTimeInterval(3_600)))
    }

    func testMalformedPrimaryDoesNotReplaceCache() throws {
        try configure()
        let ticket = try XCTUnwrap(store.beginRefresh(now: now))
        XCTAssertFalse(store.recordDownload(ticket: ticket, kind: .forecast, data: Data("{}".utf8), now: now))
        XCTAssertEqual(store.readState(now: now), .empty)
        XCTAssertNil(store.beginRefresh(now: now.addingTimeInterval(30)))
    }

    func testChangedCityDiscardsLateDownloadEvenAfterSwitchingBack() throws {
        try configure()
        let ticket = try XCTUnwrap(store.beginRefresh(now: now))
        var changed = try object(config)
        changed["id"] = "samarkand"
        changed["name"] = "Samarkand"
        changed["attemptKey"] = "last_attempt_samarkand"
        _ = try rpc(store, ["op": "configure", "config": changed])
        XCTAssertFalse(store.recordDownload(ticket: ticket, kind: .forecast, data: forecast(), now: now))
        try configure()
        XCTAssertFalse(store.recordDownload(ticket: ticket, kind: .forecast, data: forecast(), now: now))
        XCTAssertNil(store.beginRefresh(now: now.addingTimeInterval(60)))
    }

    func testOldHostSnapshotCannotOverwriteNewWidgetSnapshot() throws {
        try configure()
        let ticket = try XCTUnwrap(store.beginRefresh(now: now))
        _ = store.recordDownload(ticket: ticket, kind: .forecast, data: forecast(), now: now)
        let stale = SurfaceWeatherSnapshot(
            updatedAt: now.addingTimeInterval(-3_600), location: config.name,
            temperature: 10, temperatureUnit: "°C", weatherCode: 1, rainChance: 0,
            airQuality: nil, maximum: nil, minimum: nil
        )
        let result = try rpc(store, ["op": "publish", "config": object(config), "snapshot": stale.applicationContext])
        XCTAssertEqual(result["ok"] as? Bool, false)
        XCTAssertEqual(store.readState(now: now).snapshot?.temperature, 24)
    }

    func testReadPendingDeliveryIsInvalidatedByNewConfiguration() throws {
        try configure()
        let ticket = try XCTUnwrap(store.beginRefresh(now: now))
        _ = store.recordDownload(ticket: ticket, kind: .forecast, data: forecast(), now: now)
        let delivery = try pending(store)
        let validation: [String: Any] = [
            "op": "validate", "deliveryId": delivery["deliveryId"]!,
            "revision": delivery["revision"]!, "fetchedAt": delivery["fetchedAt"]!
        ]
        XCTAssertEqual(try rpc(store, validation)["ok"] as? Bool, true)
        var changed = try object(config)
        changed["temperatureUnit"] = "°F"
        _ = try rpc(store, ["op": "configure", "config": changed])
        XCTAssertEqual(try rpc(store, validation)["ok"] as? Bool, false)
    }

    func testManualRefreshRemainsImmediateAndInvalidatesOlderWidgetWork() throws {
        try configure()
        let ticket = try XCTUnwrap(store.beginRefresh(now: now))
        let result = try rpc(store, ["op": "manual", "key": config.attemptKey, "now": 2_000_000_010])
        XCTAssertEqual(result["ok"] as? Bool, true)
        XCTAssertFalse(store.recordDownload(ticket: ticket, kind: .forecast, data: forecast(), now: now))
    }

    func testLegacyAttemptMigratesBeforeFirstWidgetFetch() throws {
        _ = try rpc(store, [
            "op": "configure", "config": object(config),
            "legacy": "v1|1|1999999940|Cooldown"
        ])
        XCTAssertNil(store.beginRefresh(now: now))
        XCTAssertNotNil(store.beginRefresh(now: now.addingTimeInterval(3_540)))
    }

    func testUnreadableBudgetFailsClosed() throws {
        try Data("not a directory".utf8).write(to: directory)
        XCTAssertNil(store.beginRefresh(now: now))
        let response = try rpc(store, ["op": "claim", "key": config.attemptKey, "now": 2_000_000_000])
        XCTAssertEqual(response["status"] as? String, "unavailable")
    }

    func testLegacySnapshotReadAndMigrationKeepTimestampButClearForNewCity() throws {
        let name = "WidgetRefreshStoreTests.\(UUID().uuidString)"
        let defaults = try XCTUnwrap(UserDefaults(suiteName: name))
        defer { defaults.removePersistentDomain(forName: name) }
        // Use a real past timestamp because configure's legacy validator uses the wall clock.
        let fetched = Date(timeIntervalSince1970: floor(Date().timeIntervalSince1970) - 60)
        let snapshot = SurfaceWeatherSnapshot(
            updatedAt: fetched, location: "Tashkent", temperature: 24,
            temperatureUnit: "°C", weatherCode: 1, rainChance: 0,
            airQuality: nil, maximum: nil, minimum: nil
        )
        snapshot.write(to: defaults)
        let migrated = WidgetRefreshStore(directory: directory, legacyDefaults: defaults)
        XCTAssertEqual(migrated.readState().snapshot, snapshot)
        XCTAssertNil(migrated.beginRefresh())
        XCTAssertEqual(migrated.readState().snapshot, snapshot)
        _ = try rpc(migrated, ["op": "configure", "config": object(config)])
        XCTAssertEqual(migrated.readState().snapshot, snapshot)
        _ = try rpc(migrated, ["op": "configure", "config": NSNull()])
        XCTAssertEqual(migrated.readState(), .empty)
    }

    private func configure() throws {
        let result = try rpc(store, ["op": "configure", "config": object(config)])
        XCTAssertNotNil(result["revision"] as? String)
    }

    private func rpc(_ store: WidgetRefreshStore, _ command: [String: Any]) throws -> [String: Any] {
        let bytes = try JSONSerialization.data(withJSONObject: command)
        let response = store.exchange(String(decoding: bytes, as: UTF8.self))
        return try XCTUnwrap(JSONSerialization.jsonObject(with: Data(response.utf8)) as? [String: Any])
    }

    private func pending(_ store: WidgetRefreshStore) throws -> [String: Any] {
        try XCTUnwrap(rpc(store, ["op": "pending"])["pending"] as? [String: Any])
    }

    private func object<T: Encodable>(_ value: T) throws -> [String: Any] {
        try XCTUnwrap(JSONSerialization.jsonObject(with: JSONEncoder().encode(value)) as? [String: Any])
    }

    private func forecast() -> Data {
        Data("""
        {"latitude":41.31,"longitude":69.28,"timezone":"Asia/Tashkent","utc_offset_seconds":18000,
         "hourly":{"time":[2000000000],"temperature_2m":[24],"apparent_temperature":[24],
         "weather_code":[1],"precipitation_probability":[10],"wind_speed_10m":[5],"relative_humidity_2m":[40]}}
        """.utf8)
    }
}

private final class Results: @unchecked Sendable {
    private let lock = NSLock()
    private var values: [Bool] = []
    func append(_ value: Bool) { lock.withLock { values.append(value) } }
    var successCount: Int { lock.withLock { values.filter { $0 }.count } }
}
