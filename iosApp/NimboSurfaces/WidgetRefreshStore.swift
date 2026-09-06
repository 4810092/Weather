import Foundation
import CoreFoundation
import OSLog
#if canImport(Darwin)
import Darwin
#endif

struct WidgetRefreshConfiguration: Codable, Equatable, Sendable {
    let id: String
    let name: String
    let country: String
    let latitude: Double
    let longitude: Double
    let timezone: String
    let temperatureUnit: String
    let attemptKey: String

    var isValid: Bool {
        !id.isEmpty && id.count <= 256 && !name.isEmpty && name.count <= 100 &&
            latitude.isFinite && (-90...90).contains(latitude) &&
            longitude.isFinite && (-180...180).contains(longitude) &&
            TimeZone(identifier: timezone) != nil &&
            ["°C", "°F"].contains(temperatureUnit) &&
            attemptKey.hasPrefix("last_attempt_") && attemptKey.count <= 64
    }

    func matchesSelection(_ other: Self) -> Bool {
        // The provider can resolve a more accurate timezone for the same point.
        // It is weather metadata, while city, coordinates and units identify the selection.
        id == other.id && latitude == other.latitude && longitude == other.longitude &&
            temperatureUnit == other.temperatureUnit && attemptKey == other.attemptKey &&
            name == other.name && country == other.country
    }
}

struct WidgetRefreshTicket: Codable, Equatable, Sendable {
    let revision: String
    let config: WidgetRefreshConfiguration
    let token: Int64
    let startedAt: Int64
}

enum WidgetDownloadKind: String, Codable, Sendable {
    case forecast
    case airQuality
}

struct PendingWidgetRefresh: Codable, Equatable, Sendable {
    let deliveryId: String
    let revision: String
    let config: WidgetRefreshConfiguration
    let fetchedAt: Int64
    let forecast: String
    let airQuality: String?
    let airQualityFetchedAt: Int64?
}

private struct WidgetAttempt: Codable {
    var token: Int64
    var attemptedAt: Int64
    var phase: String
}

private struct WidgetFlight: Codable {
    var ticket: WidgetRefreshTicket
    var forecastFinished = false
    var airQualityFinished = false
    var forecast: String?
    var airQuality: String?
    var fetchedAt: Int64?
    var airQualityFetchedAt: Int64?
}

private struct WidgetDiskState: Codable {
    var version = 1
    var hasConfigured = false
    var config: WidgetRefreshConfiguration?
    var revision: String?
    var snapshot: SurfaceWeatherSnapshot?
    var pending: PendingWidgetRefresh?
    var attempts: [String: WidgetAttempt] = [:]
    var flight: WidgetFlight?
    var lastEvent: String?
    var lastEventAt: Int64?
}

/// All host/extension reads, claims and commits share this lock and one atomic file.
/// Never hold the lock across a network request or a Kotlin callback.
final class WidgetRefreshStore: @unchecked Sendable {
    static let appGroup = "group.uz.ganikhodjaev.weather"
    static let shared = WidgetRefreshStore(
        directory: FileManager.default.containerURL(
            forSecurityApplicationGroupIdentifier: appGroup
        ),
        legacyDefaults: UserDefaults(suiteName: appGroup)
    )
    static let refreshInterval: TimeInterval = 60 * 60
    private static let processLock = NSRecursiveLock()
    private let directory: URL?
    private let legacyDefaults: UserDefaults?
    private let currentDate: @Sendable () -> Date
    private let logger = Logger(subsystem: "uz.ganikhodjaev.weather", category: "WidgetRefresh")

    init(
        directory: URL?, legacyDefaults: UserDefaults? = nil,
        currentDate: @escaping @Sendable () -> Date = { .now }
    ) {
        self.directory = directory
        self.legacyDefaults = legacyDefaults
        self.currentDate = currentDate
    }

    func readState(now: Date = .now, legacyDefaults: UserDefaults? = nil) -> SurfaceWeatherState {
        do {
            return try access { state, exists in
                if exists && state.hasConfigured {
                    return SurfaceWeatherStateReader.state(for: state.snapshot, now: now)
                }
                return SurfaceWeatherStateReader.read(
                    from: legacyDefaults ?? self.legacyDefaults, now: now
                )
            }
        } catch {
            logger.error("Widget cache read unavailable")
            return .empty
        }
    }

    func nextRefreshDate(now: Date = .now) -> Date {
        (try? access { state, _ in
            let attemptedAt = state.config.flatMap { state.attempts[$0.attemptKey]?.attemptedAt }
            let last = max(TimeInterval(attemptedAt ?? 0), state.snapshot?.updatedAt.timeIntervalSince1970 ?? 0)
            let next = last + Self.refreshInterval
            return Date(timeIntervalSince1970: next > now.timeIntervalSince1970
                ? min(next, now.timeIntervalSince1970 + Self.refreshInterval)
                : now.timeIntervalSince1970 + Self.refreshInterval)
        }) ?? now.addingTimeInterval(Self.refreshInterval)
    }

    func beginRefresh(now: Date = .now) -> WidgetRefreshTicket? {
        do {
            return try mutate { state in
                guard let config = state.config, config.isValid, let revision = state.revision else {
                    return nil
                }
                if let snapshot = state.snapshot {
                    let age = now.timeIntervalSince(snapshot.updatedAt)
                    if age >= 0 && age < Self.refreshInterval { return nil }
                }
                let seconds = Int64(now.timeIntervalSince1970)
                let key = config.attemptKey
                guard Self.isDue(state.attempts[key], now: seconds) else { return nil }
                let attempt = Self.newAttempt(previous: state.attempts[key], now: seconds, phase: "InFlight")
                state.attempts[key] = attempt
                let ticket = WidgetRefreshTicket(
                    revision: revision, config: config, token: attempt.token, startedAt: seconds
                )
                state.flight = WidgetFlight(ticket: ticket)
                Self.event("widget_started", at: seconds, state: &state)
                return ticket
            }
        } catch {
            logger.error("Widget automatic refresh deferred: shared state unavailable")
            return nil
        }
    }

    /// Returns true only when a complete primary response was committed.
    @discardableResult
    func recordDownload(
        ticket: WidgetRefreshTicket, kind: WidgetDownloadKind, data: Data?, now: Date = .now
    ) -> Bool {
        do {
            return try mutate { state in
                guard state.revision == ticket.revision, state.config == ticket.config,
                      state.attempts[ticket.config.attemptKey]?.token == ticket.token,
                      var flight = state.flight, flight.ticket == ticket else { return false }
                let text = data.flatMap { $0.count <= 2 * 1_024 * 1_024 ? String(data: $0, encoding: .utf8) : nil }
                switch kind {
                case .forecast:
                    guard !flight.forecastFinished else { return false }
                    flight.forecastFinished = true
                    flight.forecast = text
                    flight.fetchedAt = text == nil ? nil : Int64(now.timeIntervalSince1970)
                case .airQuality:
                    guard !flight.airQualityFinished else { return false }
                    flight.airQualityFinished = true
                    flight.airQuality = text
                    flight.airQualityFetchedAt = text == nil ? nil : Int64(now.timeIntervalSince1970)
                }
                state.flight = flight
                guard flight.forecastFinished else { return false }
                if flight.airQualityFinished { state.flight = nil }
                if kind == .airQuality && flight.airQuality == nil { return false }
                guard let forecast = flight.forecast, let fetchedAt = flight.fetchedAt,
                      let snapshot = try? WidgetWeatherClient.snapshot(
                        forecast: Data(forecast.utf8),
                        airQuality: flight.airQuality.map { Data($0.utf8) },
                        config: ticket.config,
                        fetchedAt: Date(timeIntervalSince1970: TimeInterval(fetchedAt)),
                        now: now
                      ) else {
                    state.attempts[ticket.config.attemptKey]?.phase = "RetryPending"
                    Self.event("widget_failed", at: Int64(now.timeIntervalSince1970), state: &state)
                    return false
                }
                state.attempts[ticket.config.attemptKey]?.phase = "Cooldown"
                guard state.snapshot.map({ $0.updatedAt <= snapshot.updatedAt }) ?? true else { return false }
                state.snapshot = snapshot
                state.pending = PendingWidgetRefresh(
                    deliveryId: UUID().uuidString,
                    revision: ticket.revision, config: ticket.config, fetchedAt: fetchedAt,
                    forecast: forecast, airQuality: flight.airQuality,
                    airQualityFetchedAt: flight.airQualityFetchedAt
                )
                Self.event("widget_updated", at: Int64(now.timeIntervalSince1970), state: &state)
                return true
            }
        } catch {
            logger.error("Widget download commit unavailable")
            return false
        }
    }

    /// Synchronous RPC used by Kotlin through the host's small Swift adapter.
    /// Errors fail closed and never leak coordinates or payloads to logs.
    func exchange(_ request: String) -> String {
        do {
            guard let bytes = request.data(using: .utf8), bytes.count <= 5 * 1_024 * 1_024,
                  let command = try JSONSerialization.jsonObject(with: bytes) as? [String: Any],
                  let op = command["op"] as? String else { throw StoreError.invalid }
            let response: [String: Any] = try mutate { state in
                switch op {
                case "configure":
                    let config: WidgetRefreshConfiguration?
                    if command["config"] is NSNull { config = nil }
                    else { config = try Self.decode(WidgetRefreshConfiguration.self, object: command["config"]) }
                    guard config?.isValid ?? true else { throw StoreError.invalid }
                    let migrateSnapshot = !state.hasConfigured
                    state.hasConfigured = true
                    if state.config != config {
                        state.config = config
                        state.revision = config == nil ? nil : UUID().uuidString
                        state.snapshot = nil
                        state.pending = nil
                        state.flight = nil
                    }
                    if migrateSnapshot, let config,
                       let legacy = SurfaceWeatherStateReader.snapshot(from: self.legacyDefaults, now: self.currentDate()),
                       legacy.location == config.name,
                       legacy.temperatureUnit == config.temperatureUnit {
                        state.snapshot = legacy
                    }
                    if let config {
                        try Self.migrateLegacy(command["legacy"], key: config.attemptKey, state: &state)
                    }
                    return ["revision": state.revision as Any? ?? NSNull()]
                case "publish":
                    let config = try Self.decode(WidgetRefreshConfiguration.self, object: command["config"])
                    guard config.isValid, state.config.map({ config.matchesSelection($0) }) == true,
                          let fields = command["snapshot"] as? [String: Any],
                          let snapshot = SurfaceWeatherStateReader.snapshot(from: fields, now: self.currentDate()),
                          state.snapshot.map({ $0.updatedAt <= snapshot.updatedAt }) ?? true else { return ["ok": false] }
                    state.snapshot = snapshot
                    return ["ok": true]
                case "pending":
                    return ["pending": try state.pending.map(Self.object) ?? NSNull()]
                case "acknowledge", "validate":
                    guard let pending = state.pending,
                          command["deliveryId"] as? String == pending.deliveryId,
                          command["revision"] as? String == pending.revision,
                          Self.int(command["fetchedAt"]) == pending.fetchedAt else { return ["ok": false] }
                    if op == "acknowledge" { state.pending = nil }
                    return ["ok": true]
                case "claim":
                    let key = try Self.key(command)
                    guard let now = Self.int(command["now"]), now > 0 else { throw StoreError.invalid }
                    try Self.migrateLegacy(command["legacy"], key: key, state: &state)
                    guard Self.isDue(state.attempts[key], now: now) else {
                        return ["status": state.attempts[key]?.phase == "Cooldown" ? "cooldown" : "deferred"]
                    }
                    let attempt = Self.newAttempt(previous: state.attempts[key], now: now, phase: "InFlight")
                    state.attempts[key] = attempt
                    Self.event("host_started", at: now, state: &state)
                    return ["status": "granted", "token": attempt.token]
                case "finish":
                    let key = try Self.key(command)
                    guard let token = Self.int(command["token"]),
                          state.attempts[key]?.token == token,
                          state.attempts[key]?.phase == "InFlight",
                          let phase = command["phase"] as? String,
                          ["Cooldown", "RetryPending"].contains(phase) else { return ["ok": false] }
                    state.attempts[key]?.phase = phase
                    return ["ok": true]
                case "manual":
                    let key = try Self.key(command)
                    guard let now = Self.int(command["now"]), now > 0 else { throw StoreError.invalid }
                    state.attempts[key] = Self.newAttempt(previous: state.attempts[key], now: now, phase: "Cooldown")
                    if state.flight?.ticket.config.attemptKey == key { state.flight = nil }
                    return ["ok": true]
                case "remove":
                    let key = try Self.key(command)
                    state.attempts.removeValue(forKey: key)
                    return ["ok": true]
                default: throw StoreError.invalid
                }
            }
            let output = try JSONSerialization.data(withJSONObject: response, options: [.sortedKeys])
            return String(decoding: output, as: UTF8.self)
        } catch {
            logger.error("Host/widget shared operation unavailable")
            return "{\"ok\":false,\"status\":\"unavailable\"}"
        }
    }

    private static func isDue(_ attempt: WidgetAttempt?, now: Int64) -> Bool {
        guard let attempt else { return true }
        return now < attempt.attemptedAt || now - attempt.attemptedAt >= Int64(refreshInterval)
    }

    private static func newAttempt(previous: WidgetAttempt?, now: Int64, phase: String) -> WidgetAttempt {
        WidgetAttempt(token: max(now, (previous?.token ?? 0) + 1), attemptedAt: now, phase: phase)
    }

    private static func migrateLegacy(_ object: Any?, key: String, state: inout WidgetDiskState) throws {
        guard state.attempts[key] == nil, let legacy = object as? String else { return }
        let parts = legacy.split(separator: "|")
        guard parts.count == 4, parts[0] == "v1",
              let token = Int64(parts[1]), token >= 0, token < Int64.max,
              let at = Int64(parts[2]), at >= 0,
              ["InFlight", "Cooldown", "RetryPending"].contains(String(parts[3])) else { throw StoreError.invalid }
        state.attempts[key] = WidgetAttempt(token: token, attemptedAt: at, phase: String(parts[3]))
    }

    private static func event(_ event: String, at: Int64, state: inout WidgetDiskState) {
        state.lastEvent = event
        state.lastEventAt = at
    }

    private static func key(_ command: [String: Any]) throws -> String {
        guard let key = command["key"] as? String,
              key.hasPrefix("last_attempt_"), key.count <= 64 else { throw StoreError.invalid }
        return key
    }

    private static func int(_ object: Any?) -> Int64? {
        guard let number = object as? NSNumber,
              CFGetTypeID(number) != CFBooleanGetTypeID(),
              ["c", "s", "i", "l", "q", "C", "S", "I", "L", "Q"].contains(String(cString: number.objCType)) else { return nil }
        return Int64(number.stringValue)
    }

    private static func decode<T: Decodable>(_ type: T.Type, object: Any?) throws -> T {
        guard let object else { throw StoreError.invalid }
        return try JSONDecoder().decode(type, from: JSONSerialization.data(withJSONObject: object))
    }

    private static func object<T: Encodable>(_ value: T) throws -> Any {
        try JSONSerialization.jsonObject(with: JSONEncoder().encode(value))
    }

    private func mutate<T>(_ block: (inout WidgetDiskState) throws -> T) throws -> T {
        try locked { url in
            var state = try read(url)
            let result = try block(&state)
            let encoder = JSONEncoder()
            encoder.dateEncodingStrategy = .secondsSince1970
            let bytes = try encoder.encode(state)
            guard bytes.count <= 6 * 1_024 * 1_024 else { throw StoreError.invalid }
            try bytes.write(to: url, options: [.atomic, .completeFileProtectionUntilFirstUserAuthentication])
            // A successful automatic claim must reach durable storage before networking.
            let descriptor = open(url.path, O_RDONLY)
            guard descriptor >= 0 else { throw StoreError.unavailable }
            defer { close(descriptor) }
            guard fsync(descriptor) == 0 else { throw StoreError.unavailable }
            return result
        }
    }

    private func access<T>(_ block: (WidgetDiskState, Bool) throws -> T) throws -> T {
        try locked { url in try block(read(url), FileManager.default.fileExists(atPath: url.path)) }
    }

    private func read(_ url: URL) throws -> WidgetDiskState {
        guard FileManager.default.fileExists(atPath: url.path) else { return WidgetDiskState() }
        let bytes = try Data(contentsOf: url)
        guard bytes.count <= 6 * 1_024 * 1_024 else { throw StoreError.invalid }
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .secondsSince1970
        let state = try decoder.decode(WidgetDiskState.self, from: bytes)
        guard state.version == 1 else { throw StoreError.invalid }
        return state
    }

    private func locked<T>(_ body: (URL) throws -> T) throws -> T {
        Self.processLock.lock()
        defer { Self.processLock.unlock() }
        guard let directory else { throw StoreError.unavailable }
        try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
        let lockURL = directory.appendingPathComponent("weather-refresh-v1.lock")
        let descriptor = open(lockURL.path, O_CREAT | O_RDWR, S_IRUSR | S_IWUSR)
        guard descriptor >= 0 else { throw StoreError.unavailable }
        defer { close(descriptor) }
        guard flock(descriptor, LOCK_EX) == 0 else { throw StoreError.unavailable }
        defer { flock(descriptor, LOCK_UN) }
        return try body(directory.appendingPathComponent("weather-refresh-v1.json"))
    }

    private enum StoreError: Error { case invalid, unavailable }
}
