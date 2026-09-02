package uz.ganikhodjaev.weather.shared

import kotlinx.cinterop.ExperimentalForeignApi
import platform.UIKit.UIActivityViewController
import platform.UIKit.UIModalPresentationFullScreen
import platform.UIKit.UIViewController
import platform.UIKit.popoverPresentationController

internal actual fun shareText(platformContext: PlatformContext, text: String) {
    val controller = UIActivityViewController(
        activityItems = listOf(text),
        applicationActivities = null
    )
    val presenter = activeIosWindow()?.rootViewController ?: return
    controller.modalPresentationStyle = UIModalPresentationFullScreen
    configureSharePresentation(controller, presenter)
    presenter.presentViewController(controller, animated = true, completion = null)
}

@OptIn(ExperimentalForeignApi::class)
internal fun configureSharePresentation(
    controller: UIActivityViewController,
    presenter: UIViewController
) {
    val sourceView = presenter.view
    controller.popoverPresentationController?.apply {
        this.sourceView = sourceView
        sourceRect = sourceView.bounds
    }
}
