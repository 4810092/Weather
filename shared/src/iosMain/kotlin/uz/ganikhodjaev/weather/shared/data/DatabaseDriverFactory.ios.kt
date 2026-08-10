package uz.ganikhodjaev.weather.shared.data

import app.cash.sqldelight.db.SqlDriver
import app.cash.sqldelight.driver.native.NativeSqliteDriver
import uz.ganikhodjaev.weather.db.NimboDatabase
import uz.ganikhodjaev.weather.shared.PlatformContext

internal actual class DatabaseDriverFactory actual constructor(context: PlatformContext) {
    actual fun create(): SqlDriver = NativeSqliteDriver(
        schema = NimboDatabase.Schema,
        name = "nimbo.db"
    )
}
