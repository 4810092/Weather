package uz.ganikhodjaev.weather.shared

import androidx.compose.ui.window.ComposeUIViewController
import uz.ganikhodjaev.weather.shared.ui.NimboDynamicType

fun MainViewController() = ComposeUIViewController {
    NimboDynamicType {
        NimboApp(PlatformContext())
    }
}
