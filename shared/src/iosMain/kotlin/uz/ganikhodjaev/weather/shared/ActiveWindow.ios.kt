package uz.ganikhodjaev.weather.shared

import platform.UIKit.UIApplication
import platform.UIKit.UISceneActivationStateForegroundActive
import platform.UIKit.UIWindow
import platform.UIKit.UIWindowScene

internal fun activeIosWindow(): UIWindow? {
    val application = UIApplication.sharedApplication
    return application.connectedScenes
        .asSequence()
        .filterIsInstance<UIWindowScene>()
        .firstOrNull { it.activationState == UISceneActivationStateForegroundActive }
        ?.keyWindow
        ?: application.keyWindow
}
