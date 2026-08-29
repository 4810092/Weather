package uz.ganikhodjaev.weather.shared

import platform.UIKit.UIActivityViewController
import platform.UIKit.UIModalPresentationFullScreen

internal actual fun shareText(platformContext: PlatformContext, text: String) {
    val controller = UIActivityViewController(
        activityItems = listOf(text),
        applicationActivities = null
    )
    val presenter = activeIosWindow()?.rootViewController ?: return
    controller.modalPresentationStyle = UIModalPresentationFullScreen
    presenter.presentViewController(controller, animated = true, completion = null)
}
