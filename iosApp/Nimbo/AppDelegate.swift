import UIKit
import NimboShared

private let nimboBackgroundColor = UIColor { traits in
    if traits.userInterfaceStyle == .dark {
        return UIColor(red: 16 / 255, green: 24 / 255, blue: 32 / 255, alpha: 1)
    }
    return UIColor(red: 243 / 255, green: 247 / 255, blue: 252 / 255, alpha: 1)
}

private let nimboThemePreferenceKey = "theme_preference"

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
final class AppDelegate: UIResponder, UIApplicationDelegate {
    var window: UIWindow?

    func application(
        _ application: UIApplication,
        didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]? = nil
    ) -> Bool {
        let window = UIWindow(frame: UIScreen.main.bounds)
        let rootViewController = MainViewControllerKt.MainViewController()
        let interfaceStyle = storedInterfaceStyle()
        window.overrideUserInterfaceStyle = interfaceStyle
        rootViewController.overrideUserInterfaceStyle = interfaceStyle
        rootViewController.view.backgroundColor = nimboBackgroundColor
        window.backgroundColor = nimboBackgroundColor
        window.rootViewController = rootViewController
        window.makeKeyAndVisible()
        self.window = window
        return true
    }
}
