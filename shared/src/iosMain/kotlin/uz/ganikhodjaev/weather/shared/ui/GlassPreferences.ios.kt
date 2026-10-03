package uz.ganikhodjaev.weather.shared.ui

import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import platform.Foundation.NSNotificationCenter
import platform.Foundation.NSOperationQueue
import platform.UIKit.UIAccessibilityIsReduceMotionEnabled
import platform.UIKit.UIAccessibilityIsReduceTransparencyEnabled
import platform.UIKit.UIAccessibilityReduceMotionStatusDidChangeNotification
import platform.UIKit.UIAccessibilityReduceTransparencyStatusDidChangeNotification
import platform.UIKit.UIApplicationDidBecomeActiveNotification

@Composable
internal actual fun rememberGlassPreferences(): GlassPreferences {
    fun read() = GlassPreferences(
        reduceMotion = UIAccessibilityIsReduceMotionEnabled(),
        reduceTransparency = UIAccessibilityIsReduceTransparencyEnabled()
    )
    var preferences by remember { mutableStateOf(read()) }
    DisposableEffect(Unit) {
        val center = NSNotificationCenter.defaultCenter
        val observers = listOf(
            UIAccessibilityReduceMotionStatusDidChangeNotification,
            UIAccessibilityReduceTransparencyStatusDidChangeNotification,
            UIApplicationDidBecomeActiveNotification
        ).map { name ->
            center.addObserverForName(name, null, NSOperationQueue.mainQueue) {
                preferences = read()
            }
        }
        onDispose { observers.forEach { center.removeObserver(it) } }
    }
    return preferences
}
