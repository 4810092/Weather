package uz.ganikhodjaev.weather.shared.ui

import androidx.compose.runtime.Composable
import platform.Foundation.NSURL
import platform.SafariServices.SFSafariViewController
import uz.ganikhodjaev.weather.shared.activeIosWindow

@Composable
internal actual fun rememberWebPageOpener(): (String) -> Unit = { uri ->
    NSURL.URLWithString(uri)?.let { url ->
        val presenter = activeIosWindow()?.rootViewController
        if (presenter != null && presenter.presentedViewController == null) {
            presenter.presentViewController(
                SFSafariViewController(url),
                animated = true,
                completion = null
            )
        }
    }
}
