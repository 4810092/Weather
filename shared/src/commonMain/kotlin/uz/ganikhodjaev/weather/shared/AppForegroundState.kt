package uz.ganikhodjaev.weather.shared

import androidx.compose.runtime.Composable
import androidx.compose.runtime.State

@Composable
internal expect fun rememberAppIsForeground(platformContext: PlatformContext): State<Boolean>
