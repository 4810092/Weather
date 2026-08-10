package uz.ganikhodjaev.weather.shared.data

import app.cash.sqldelight.db.SqlDriver
import uz.ganikhodjaev.weather.shared.PlatformContext

internal expect class DatabaseDriverFactory(context: PlatformContext) {
    fun create(): SqlDriver
}
