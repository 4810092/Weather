package uz.ganikhodjaev.weather.shared

import platform.UIKit.UIActivityViewController
import platform.UIKit.UIApplication
import platform.UIKit.UIModalPresentationFullScreen

internal actual fun shareText(platformContext: PlatformContext, text: String) {
    val controller = UIActivityViewController(
        activityItems = listOf(text),
        applicationActivities = null
    )
    val presenter = UIApplication.sharedApplication.keyWindow?.rootViewController ?: return
    controller.modalPresentationStyle = UIModalPresentationFullScreen
    presenter.presentViewController(controller, animated = true, completion = null)
}
