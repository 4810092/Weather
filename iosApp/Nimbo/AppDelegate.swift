import UIKit
@preconcurrency import BackgroundTasks
import Dispatch
import NimboShared
import WidgetKit
@preconcurrency import WatchConnectivity

private let nimboBackgroundColor = UIColor { traits in
    if traits.userInterfaceStyle == .dark {
        return UIColor(red: 16 / 255, green: 24 / 255, blue: 32 / 255, alpha: 1)
    }
    return UIColor(red: 243 / 255, green: 247 / 255, blue: 252 / 255, alpha: 1)
}

private let nimboThemePreferenceKey = "theme_preference"
private let weatherRefreshTaskIdentifier = "uz.ganikhodjaev.weather.refresh"
private let nimboAppGroup = "group.uz.ganikhodjaev.weather"

private final class BackgroundRefreshState: @unchecked Sendable {
    private let lock = NSLock()
    private var completed = false
    private var refreshHandle: BackgroundRefreshHandle?

    func install(_ handle: BackgroundRefreshHandle) {
        let shouldCancel = lock.withLock {
            guard !completed else { return true }
            refreshHandle = handle
            return false
        }
        if shouldCancel {
            handle.cancel()
        }
    }

    func expire(task: BGAppRefreshTask) {
        let result: (shouldComplete: Bool, handle: BackgroundRefreshHandle?) = lock.withLock {
            guard !completed else { return (false, nil) }
            completed = true
            let handle = refreshHandle
            refreshHandle = nil
            return (true, handle)
        }
        result.handle?.cancel()
        if result.shouldComplete {
            task.setTaskCompleted(success: false)
        }
    }

    func finish(task: BGAppRefreshTask, success: Bool) {
        let shouldComplete = lock.withLock {
            guard !completed else { return false }
            completed = true
            refreshHandle = nil
            return true
        }
        if shouldComplete {
            task.setTaskCompleted(success: success)
        }
    }
}

private func storedInterfaceStyle() -> UIUserInterfaceStyle {
    switch UserDefaults.standard.string(forKey: nimboThemePreferenceKey) {
    case "Light":
        return .light
    case "Dark":
        return .dark
    default:
        return .unspecified
    }
}

@main
@MainActor
final class AppDelegate: UIResponder, UIApplicationDelegate, WCSessionDelegate {
    private var weatherObserver: NSObjectProtocol?
    private let backgroundUpdater = BackgroundWeatherUpdater(platformContext: PlatformContext())

    func application(
        _ application: UIApplication,
        didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]? = nil
    ) -> Bool {
        BGTaskScheduler.shared.register(
            forTaskWithIdentifier: weatherRefreshTaskIdentifier,
            using: .main
        ) { [weak self] task in
            guard let refreshTask = task as? BGAppRefreshTask else {
                task.setTaskCompleted(success: false)
                return
            }
            self?.handleBackgroundRefresh(refreshTask)
        }
        if WCSession.isSupported() {
            let session = WCSession.default
            session.delegate = self
            session.activate()
        }
        weatherObserver = NotificationCenter.default.addObserver(
            forName: Notification.Name("NimboWeatherDidUpdate"),
            object: nil,
            queue: .main
        ) { [weak self] _ in
            Task { @MainActor in
                self?.weatherDidUpdate()
            }
        }
        return true
    }

    func scheduleBackgroundRefresh() {
        let request = BGAppRefreshTaskRequest(identifier: weatherRefreshTaskIdentifier)
        request.earliestBeginDate = Date(timeIntervalSinceNow: 60 * 60)
        try? BGTaskScheduler.shared.submit(request)
    }

    private func handleBackgroundRefresh(_ task: BGAppRefreshTask) {
        scheduleBackgroundRefresh()
        let state = BackgroundRefreshState()
        task.expirationHandler = { state.expire(task: task) }
        let handle = backgroundUpdater.startRefresh { result in
            Task { @MainActor in
                state.finish(task: task, success: result.boolValue)
            }
        }
        state.install(handle)
    }

    private func weatherDidUpdate() {
        WidgetCenter.shared.reloadAllTimelines()
        guard WCSession.isSupported() else { return }
        let defaults = UserDefaults(suiteName: nimboAppGroup)
        let snapshot = SurfaceWeatherStateReader.snapshot(from: defaults)
        let context = snapshot?.applicationContext ?? [:]
        try? WCSession.default.updateApplicationContext(context)
    }

    nonisolated func session(
        _ session: WCSession,
        activationDidCompleteWith activationState: WCSessionActivationState,
        error: Error?
    ) {
        if activationState == .activated {
            Task { @MainActor [weak self] in
                self?.weatherDidUpdate()
            }
        }
    }

    nonisolated func sessionDidBecomeInactive(_ session: WCSession) {}

    nonisolated func sessionDidDeactivate(_ session: WCSession) {
        session.activate()
    }

    nonisolated func sessionWatchStateDidChange(_ session: WCSession) {
        Task { @MainActor [weak self] in
            self?.weatherDidUpdate()
        }
    }

    nonisolated func sessionReachabilityDidChange(_ session: WCSession) {
        guard session.isReachable else { return }
        Task { @MainActor [weak self] in
            self?.weatherDidUpdate()
        }
    }
}

@MainActor
final class SceneDelegate: UIResponder, UIWindowSceneDelegate {
    var window: UIWindow?

    func scene(
        _ scene: UIScene,
        willConnectTo session: UISceneSession,
        options connectionOptions: UIScene.ConnectionOptions
    ) {
        guard let windowScene = scene as? UIWindowScene else { return }
        let window = UIWindow(windowScene: windowScene)
        let rootViewController = MainViewControllerKt.MainViewController()
        let interfaceStyle = storedInterfaceStyle()
        window.overrideUserInterfaceStyle = interfaceStyle
        rootViewController.overrideUserInterfaceStyle = interfaceStyle
        rootViewController.view.backgroundColor = nimboBackgroundColor
        window.backgroundColor = nimboBackgroundColor
        window.rootViewController = rootViewController
        window.makeKeyAndVisible()
        self.window = window
    }

    func sceneDidEnterBackground(_ scene: UIScene) {
        (UIApplication.shared.delegate as? AppDelegate)?.scheduleBackgroundRefresh()
    }
}
