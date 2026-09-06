import Foundation
import WidgetKit

/// Owns the background URLSession used by the widget extension.  A background
/// session may deliver callbacks to a new extension process, so task metadata is
/// self-contained and the session is recreated before accepting its completion
/// handler.
final class WidgetBackgroundSession: NSObject, URLSessionDownloadDelegate, @unchecked Sendable {
    static let shared = WidgetBackgroundSession()

    static let identifier = "uz.ganikhodjaev.weather.widget.refresh"
    static let appGroup = "group.uz.ganikhodjaev.weather"
    static let maximumResponseBytes = 2 * 1024 * 1024

    private let store = WidgetRefreshStore.shared
    private let lock = NSLock()
    private let delegateQueue: OperationQueue = {
        let queue = OperationQueue()
        queue.name = "uz.ganikhodjaev.weather.widget.refresh.delegate"
        queue.maxConcurrentOperationCount = 1
        return queue
    }()
    private var session: URLSession?
    private var completedTaskIdentifiers = Set<Int>()
    private var backgroundEventsFinished = false
    private var backgroundEventsCompletion: (() -> Void)?

    private override init() {
        super.init()
    }

    func refreshIfNeeded() {
        let session = makeSession()
        guard let ticket = store.beginRefresh() else { return }

        enqueue(
            session: session,
            ticket: ticket,
            kind: .forecast,
            url: WidgetWeatherClient.forecastURL(config: ticket.config)
        )
        enqueue(
            session: session,
            ticket: ticket,
            kind: .airQuality,
            url: WidgetWeatherClient.airQualityURL(config: ticket.config)
        )
    }

    func handleEvents(identifier: String, completion: @escaping () -> Void) {
        guard identifier == Self.identifier else {
            completion()
            return
        }
        lock.lock()
        backgroundEventsCompletion = completion
        lock.unlock()
        _ = makeSession()
        finishBackgroundEventsIfReady()
    }

    func urlSession(
        _ session: URLSession,
        downloadTask: URLSessionDownloadTask,
        didFinishDownloadingTo location: URL
    ) {
        guard let metadata = metadata(for: downloadTask) else { return }
        let success = httpStatusIsSuccessful(downloadTask.response)
        let data = success ? boundedData(at: location) : nil
        complete(downloadTask: downloadTask, metadata: metadata, data: data)
    }

    func urlSession(
        _ session: URLSession,
        task: URLSessionTask,
        didCompleteWithError error: (any Swift.Error)?
    ) {
        guard let downloadTask = task as? URLSessionDownloadTask,
              let metadata = metadata(for: downloadTask) else { return }
        // Successful downloads are published from didFinishDownloadingTo.  An
        // error, an HTTP response without a downloaded body, or a malformed task
        // therefore becomes a single failed result.
        if error != nil || !httpStatusIsSuccessful(task.response) {
            complete(downloadTask: downloadTask, metadata: metadata, data: nil)
        }
    }

    func urlSessionDidFinishEvents(forBackgroundURLSession session: URLSession) {
        lock.lock()
        backgroundEventsFinished = true
        lock.unlock()
        finishBackgroundEventsIfReady()
    }

    private func makeSession() -> URLSession {
        lock.lock()
        defer { lock.unlock() }
        if let session { return session }
        let configuration = URLSessionConfiguration.background(withIdentifier: Self.identifier)
        configuration.sharedContainerIdentifier = Self.appGroup
        configuration.timeoutIntervalForRequest = 15
        configuration.timeoutIntervalForResource = 15
        configuration.sessionSendsLaunchEvents = true
        let session = URLSession(configuration: configuration, delegate: self, delegateQueue: delegateQueue)
        self.session = session
        return session
    }

    private func enqueue(
        session: URLSession,
        ticket: WidgetRefreshTicket,
        kind: WidgetDownloadKind,
        url: URL
    ) {
        guard let description = try? JSONEncoder().encode(TaskMetadata(ticket: ticket, kind: kind)) else {
            store.recordDownload(ticket: ticket, kind: kind, data: nil)
            return
        }
        let task = session.downloadTask(with: url)
        task.taskDescription = String(decoding: description, as: UTF8.self)
        task.resume()
    }

    private func metadata(for task: URLSessionDownloadTask) -> TaskMetadata? {
        guard let description = task.taskDescription else { return nil }
        return try? JSONDecoder().decode(TaskMetadata.self, from: Data(description.utf8))
    }

    private func complete(downloadTask: URLSessionDownloadTask, metadata: TaskMetadata, data: Data?) {
        lock.lock()
        let inserted = completedTaskIdentifiers.insert(downloadTask.taskIdentifier).inserted
        lock.unlock()
        guard inserted else { return }
        if store.recordDownload(ticket: metadata.ticket, kind: metadata.kind, data: data) {
            WidgetCenter.shared.reloadTimelines(ofKind: "NimboWidget")
        }
    }

    private func boundedData(at location: URL) -> Data? {
        guard let attributes = try? FileManager.default.attributesOfItem(atPath: location.path),
              let size = attributes[.size] as? NSNumber,
              size.intValue >= 0,
              size.intValue <= Self.maximumResponseBytes else {
            return nil
        }
        return try? Data(contentsOf: location, options: .mappedIfSafe)
    }

    private func httpStatusIsSuccessful(_ response: URLResponse?) -> Bool {
        guard let response = response as? HTTPURLResponse else { return false }
        return (200...299).contains(response.statusCode)
    }

    private func finishBackgroundEventsIfReady() {
        lock.lock()
        guard backgroundEventsFinished, let completion = backgroundEventsCompletion else {
            lock.unlock()
            return
        }
        backgroundEventsFinished = false
        backgroundEventsCompletion = nil
        lock.unlock()
        completion()
    }
}

private struct TaskMetadata: Codable, Sendable {
    let ticket: WidgetRefreshTicket
    let kind: WidgetDownloadKind
}
