package uz.ganikhodjaev.weather.shared.ui

import kotlin.test.Test
import kotlin.test.assertEquals
import platform.Foundation.NSNotificationCenter
import platform.UIKit.UIApplicationDidBecomeActiveNotification
import platform.UIKit.UIContentSizeCategoryAccessibilityLarge
import platform.UIKit.UIContentSizeCategoryDidChangeNotification
import platform.UIKit.UIContentSizeCategoryExtraLarge
import platform.UIKit.UIContentSizeCategoryLarge
import platform.UIKit.UIContentSizeCategoryNewValueKey

class NimboDynamicTypeTest {
    @Test
    fun categoryNotificationUpdatesScaleWithoutRecreatingTheScreen() {
        val center = NSNotificationCenter()
        val scales = mutableListOf<Float>()
        val dispose = observeIosContentSize(center, { UIContentSizeCategoryLarge }, scales::add)
        try {
            center.postNotificationName(
                UIContentSizeCategoryDidChangeNotification,
                null,
                mapOf(UIContentSizeCategoryNewValueKey to UIContentSizeCategoryAccessibilityLarge)
            )
            assertEquals(listOf(1.5f), scales)
        } finally {
            dispose()
        }
        center.postNotificationName(UIContentSizeCategoryDidChangeNotification, null)
        assertEquals(listOf(1.5f), scales, "Disposed screens must not retain observers")
    }

    @Test
    fun foregroundResumeRechecksChangesMadeWhileInactive() {
        val center = NSNotificationCenter()
        var category = UIContentSizeCategoryExtraLarge
        val scales = mutableListOf<Float>()
        val dispose = observeIosContentSize(center, { category }, scales::add)
        try {
            center.postNotificationName(UIApplicationDidBecomeActiveNotification, null)
            category = UIContentSizeCategoryLarge
            center.postNotificationName(UIApplicationDidBecomeActiveNotification, null)
            assertEquals(listOf(1.1f, 1f), scales)
        } finally {
            dispose()
        }
    }
}
