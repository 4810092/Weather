package uz.ganikhodjaev.weather.shared

import uz.ganikhodjaev.weather.db.NimboDatabase
import uz.ganikhodjaev.weather.shared.data.DatabaseDriverFactory
import uz.ganikhodjaev.weather.shared.data.OpenMeteoService
import uz.ganikhodjaev.weather.shared.data.WeatherRepository

internal class NimboContainer(context: PlatformContext) {
    private val database = NimboDatabase(DatabaseDriverFactory(context).create())
    val weatherRepository = WeatherRepository(database, OpenMeteoService())
}
