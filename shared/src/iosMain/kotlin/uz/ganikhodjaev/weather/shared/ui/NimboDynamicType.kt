package uz.ganikhodjaev.weather.shared.ui

import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.unit.Density
import platform.Foundation.NSNotificationCenter
import platform.Foundation.NSOperationQueue
import platform.UIKit.UIApplication
import platform.UIKit.UIApplicationDidBecomeActiveNotification
import platform.UIKit.UIContentSizeCategoryAccessibilityExtraExtraExtraLarge
import platform.UIKit.UIContentSizeCategoryAccessibilityExtraExtraLarge
import platform.UIKit.UIContentSizeCategoryAccessibilityExtraLarge
import platform.UIKit.UIContentSizeCategoryAccessibilityLarge
import platform.UIKit.UIContentSizeCategoryAccessibilityMedium
import platform.UIKit.UIContentSizeCategoryDidChangeNotification
import platform.UIKit.UIContentSizeCategoryExtraExtraExtraLarge
import platform.UIKit.UIContentSizeCategoryExtraExtraLarge
import platform.UIKit.UIContentSizeCategoryExtraLarge
import platform.UIKit.UIContentSizeCategoryExtraSmall
import platform.UIKit.UIContentSizeCategoryLarge
import platform.UIKit.UIContentSizeCategoryMedium
import platform.UIKit.UIContentSizeCategoryNewValueKey
import platform.UIKit.UIContentSizeCategorySmall

/** Compose 1.11.1 reads the hosting view's font scale only when creating its scene. */
@Composable
internal fun NimboDynamicType(content: @Composable () -> Unit) {
    val density = LocalDensity.current
    var fontScale by remember { mutableStateOf(iosContentSizeScale(currentContentSize())) }
    DisposableEffect(Unit) {
        val dispose = observeIosContentSize { fontScale = it }
        onDispose { dispose() }
    }
    CompositionLocalProvider(
        LocalDensity provides Density(density.density, fontScale),
        content = content
    )
}

private fun currentContentSize(): String? =
    UIApplication.sharedApplication.preferredContentSizeCategory

internal fun observeIosContentSize(
    center: NSNotificationCenter = NSNotificationCenter.defaultCenter,
    readCategory: () -> String? = ::currentContentSize,
    onScaleChanged: (Float) -> Unit
): () -> Unit {
    val observers = listOf(
        UIContentSizeCategoryDidChangeNotification,
        UIApplicationDidBecomeActiveNotification
    ).map { name ->
        center.addObserverForName(name, null, NSOperationQueue.mainQueue) { notification ->
            val category = notification?.userInfo?.get(UIContentSizeCategoryNewValueKey) as? String
                ?: readCategory()
            onScaleChanged(iosContentSizeScale(category))
        }
    }
    return { observers.forEach { center.removeObserver(it) } }
}

// Keep Compose 1.11.1's existing linear sizes; update timing without restyling text.
internal fun iosContentSizeScale(category: String?): Float = when (category) {
    UIContentSizeCategoryExtraSmall -> 0.8f
    UIContentSizeCategorySmall -> 0.85f
    UIContentSizeCategoryMedium -> 0.9f
    UIContentSizeCategoryLarge -> 1f
    UIContentSizeCategoryExtraLarge -> 1.1f
    UIContentSizeCategoryExtraExtraLarge -> 1.2f
    UIContentSizeCategoryExtraExtraExtraLarge -> 1.3f
    UIContentSizeCategoryAccessibilityMedium -> 1.4f
    UIContentSizeCategoryAccessibilityLarge -> 1.5f
    UIContentSizeCategoryAccessibilityExtraLarge -> 1.6f
    UIContentSizeCategoryAccessibilityExtraExtraLarge -> 1.7f
    UIContentSizeCategoryAccessibilityExtraExtraExtraLarge -> 1.8f
    else -> 1f
}
