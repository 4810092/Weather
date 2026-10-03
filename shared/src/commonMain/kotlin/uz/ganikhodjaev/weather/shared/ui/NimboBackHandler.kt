package uz.ganikhodjaev.weather.shared.ui

import androidx.compose.runtime.Composable

@Composable
internal expect fun NimboBackHandler(enabled: Boolean, onBack: () -> Unit)
