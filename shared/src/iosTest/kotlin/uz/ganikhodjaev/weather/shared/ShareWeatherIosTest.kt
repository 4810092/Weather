package uz.ganikhodjaev.weather.shared

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue
import kotlinx.cinterop.ExperimentalForeignApi
import platform.UIKit.UIActivityViewController
import platform.UIKit.UIViewController
import platform.UIKit.popoverPresentationController

@OptIn(ExperimentalForeignApi::class)
class ShareWeatherIosTest {
    @Test
    fun activityControllerIsAnchoredForIpadPopoverPresentation() {
        val presenter = UIViewController()
        presenter.loadViewIfNeeded()
        val controller = UIActivityViewController(
            activityItems = listOf("Nimbo weather"),
            applicationActivities = null
        )

        configureSharePresentation(controller, presenter)

        val popover = controller.popoverPresentationController
        assertTrue(popover != null)
        assertEquals(presenter.view, popover.sourceView)
        assertEquals(presenter.view.bounds, popover.sourceRect)
    }
}
