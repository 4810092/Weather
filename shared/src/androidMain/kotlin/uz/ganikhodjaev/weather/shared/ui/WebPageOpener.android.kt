package uz.ganikhodjaev.weather.shared.ui

import androidx.compose.runtime.Composable
import androidx.compose.ui.platform.LocalUriHandler

@Composable
internal actual fun rememberWebPageOpener(): (String) -> Unit {
    val handler = LocalUriHandler.current
    return handler::openUri
}
