import UIKit
import NimboShared

private let nimboBackgroundColor = UIColor { traits in
    if traits.userInterfaceStyle == .dark {
        return UIColor(red: 16 / 255, green: 24 / 255, blue: 32 / 255, alpha: 1)
    }
    return UIColor(red: 243 / 255, green: 247 / 255, blue: 252 / 255, alpha: 1)
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
        rootViewController.view.backgroundColor = nimboBackgroundColor
        window.backgroundColor = nimboBackgroundColor
        window.rootViewController = rootViewController
        window.makeKeyAndVisible()
        self.window = window
        return true
    }
}
