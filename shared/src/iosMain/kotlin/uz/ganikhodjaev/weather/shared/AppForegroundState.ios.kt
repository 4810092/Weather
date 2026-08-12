package uz.ganikhodjaev.weather.shared

import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.State
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import platform.Foundation.NSNotificationCenter
import platform.UIKit.UIApplication
import platform.UIKit.UIApplicationDidBecomeActiveNotification
import platform.UIKit.UIApplicationState
import platform.UIKit.UIApplicationWillResignActiveNotification
import platform.darwin.NSObjectProtocol

@Composable
internal actual fun rememberAppIsForeground(platformContext: PlatformContext): State<Boolean> {
    val foreground = remember {
        mutableStateOf(
            UIApplication.sharedApplication.applicationState ==
                UIApplicationState.UIApplicationStateActive
        )
    }
    DisposableEffect(Unit) {
        val center = NSNotificationCenter.defaultCenter
        val observers = mutableListOf<NSObjectProtocol>()
        observers += center.addObserverForName(
            name = UIApplicationDidBecomeActiveNotification,
            `object` = null,
            queue = null
        ) { foreground.value = true }
        observers += center.addObserverForName(
            name = UIApplicationWillResignActiveNotification,
            `object` = null,
            queue = null
        ) { foreground.value = false }
        onDispose { observers.forEach(center::removeObserver) }
    }
    return foreground
}
