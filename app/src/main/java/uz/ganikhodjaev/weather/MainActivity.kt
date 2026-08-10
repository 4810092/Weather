package uz.ganikhodjaev.weather

import android.content.res.Configuration
import android.graphics.Color
import android.graphics.drawable.ColorDrawable
import android.os.Build
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.SystemBarStyle
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import uz.ganikhodjaev.weather.shared.NimboApp
import uz.ganikhodjaev.weather.shared.PlatformContext

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        val darkTheme = initialDarkTheme()
        val systemBarStyle = if (darkTheme) {
            SystemBarStyle.dark(Color.TRANSPARENT)
        } else {
            SystemBarStyle.light(Color.TRANSPARENT, Color.TRANSPARENT)
        }
        enableEdgeToEdge(
            statusBarStyle = systemBarStyle,
            navigationBarStyle = systemBarStyle
        )
        super.onCreate(savedInstanceState)
        window.setBackgroundDrawable(
            ColorDrawable(if (darkTheme) DARK_BACKGROUND else LIGHT_BACKGROUND)
        )
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            window.isNavigationBarContrastEnforced = false
        }
        setContent {
            NimboApp(PlatformContext(this))
        }
    }

    private fun initialDarkTheme(): Boolean {
        val storedPreference = getSharedPreferences(PREFERENCES_NAME, MODE_PRIVATE)
            .getString(THEME_PREFERENCE_KEY, null)
        return when (storedPreference) {
            "Dark" -> true
            "Light" -> false
            else ->
                resources.configuration.uiMode and Configuration.UI_MODE_NIGHT_MASK ==
                    Configuration.UI_MODE_NIGHT_YES
        }
    }

    private companion object {
        const val PREFERENCES_NAME = "nimbo_preferences"
        const val THEME_PREFERENCE_KEY = "theme_preference"
        const val LIGHT_BACKGROUND = 0xFFF3F7FC.toInt()
        const val DARK_BACKGROUND = 0xFF101820.toInt()
    }
}
