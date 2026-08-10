package uz.ganikhodjaev.weather.shared

import androidx.compose.ui.window.ComposeUIViewController

fun MainViewController() = ComposeUIViewController {
    NimboApp(PlatformContext())
}
