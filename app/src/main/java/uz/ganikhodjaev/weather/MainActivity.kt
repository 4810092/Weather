package uz.ganikhodjaev.weather

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import uz.ganikhodjaev.weather.shared.NimboApp
import uz.ganikhodjaev.weather.shared.PlatformContext

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            NimboApp(PlatformContext(this))
        }
    }
}
