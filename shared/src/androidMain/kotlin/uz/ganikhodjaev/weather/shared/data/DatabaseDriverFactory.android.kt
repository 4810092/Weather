package uz.ganikhodjaev.weather.shared.data

import app.cash.sqldelight.db.SqlDriver
import app.cash.sqldelight.driver.android.AndroidSqliteDriver
import uz.ganikhodjaev.weather.db.NimboDatabase
import uz.ganikhodjaev.weather.shared.PlatformContext

internal actual class DatabaseDriverFactory actual constructor(
    private val context: PlatformContext,
) {
    actual fun create(): SqlDriver = AndroidSqliteDriver(
        schema = NimboDatabase.Schema,
        context = context.activity.applicationContext,
        name = "nimbo.db",
    )
}
