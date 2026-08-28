package uz.ganikhodjaev.weather.wear

import android.app.Activity
import android.os.Bundle
import android.view.View
import android.widget.TextView
import androidx.core.splashscreen.SplashScreen.Companion.installSplashScreen
import com.google.android.gms.wearable.DataClient
import com.google.android.gms.wearable.DataEvent
import com.google.android.gms.wearable.DataEventBuffer
import com.google.android.gms.wearable.DataMapItem
import com.google.android.gms.wearable.Wearable

class WearWeatherActivity :
    Activity(),
    DataClient.OnDataChangedListener {
    override fun onCreate(savedInstanceState: Bundle?) {
        installSplashScreen()
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_weather)
        if (intent.getBooleanExtra(EXTRA_DEMO, false)) {
            saveDemoWeather()
        }
        showSavedWeather()
        Wearable.getDataClient(this).dataItems.addOnSuccessListener { items ->
            items.firstOrNull { it.uri.path == WEATHER_DATA_PATH }?.let { item ->
                saveAndShow(DataMapItem.fromDataItem(item))
            }
            items.release()
        }
    }

    private fun saveDemoWeather() {
        getSharedPreferences(PREFERENCES_NAME, MODE_PRIVATE).edit()
            .putString(KEY_LOCATION, intent.getStringExtra(KEY_LOCATION) ?: "Tashkent")
            .putInt(KEY_TEMPERATURE, intent.getIntExtra(KEY_TEMPERATURE, 24))
            .putString(KEY_TEMPERATURE_UNIT, intent.getStringExtra(KEY_TEMPERATURE_UNIT) ?: "°C")
            .putInt(KEY_WEATHER_CODE, intent.getIntExtra(KEY_WEATHER_CODE, 1))
            .putInt(KEY_RAIN_CHANCE, intent.getIntExtra(KEY_RAIN_CHANCE, 10))
            .putInt(KEY_AQI, intent.getIntExtra(KEY_AQI, 42))
            .putBoolean(KEY_HAS_DAILY_RANGE, true)
            .putInt(KEY_TEMPERATURE_MAX, intent.getIntExtra(KEY_TEMPERATURE_MAX, 27))
            .putInt(KEY_TEMPERATURE_MIN, intent.getIntExtra(KEY_TEMPERATURE_MIN, 18))
            .putLong(KEY_UPDATED_AT, System.currentTimeMillis() / 1_000L)
            .apply()
    }

    override fun onResume() {
        super.onResume()
        Wearable.getDataClient(this).addListener(this)
    }

    override fun onPause() {
        Wearable.getDataClient(this).removeListener(this)
        super.onPause()
    }

    override fun onDataChanged(events: DataEventBuffer) {
        events.filter { event ->
            event.type == DataEvent.TYPE_CHANGED && event.dataItem.uri.path == WEATHER_DATA_PATH
        }.forEach { event ->
            saveAndShow(DataMapItem.fromDataItem(event.dataItem))
        }
    }

    private fun saveAndShow(item: DataMapItem) {
        val data = item.dataMap
        getSharedPreferences(PREFERENCES_NAME, MODE_PRIVATE).edit()
            .putString(KEY_LOCATION, data.getString(KEY_LOCATION, ""))
            .putInt(KEY_TEMPERATURE, data.getInt(KEY_TEMPERATURE))
            .putString(KEY_TEMPERATURE_UNIT, data.getString(KEY_TEMPERATURE_UNIT, "°C"))
            .putInt(KEY_WEATHER_CODE, data.getInt(KEY_WEATHER_CODE, -1))
            .putInt(KEY_RAIN_CHANCE, data.getInt(KEY_RAIN_CHANCE))
            .putInt(KEY_AQI, data.getInt(KEY_AQI, -1))
            .putBoolean(KEY_HAS_DAILY_RANGE, data.getBoolean(KEY_HAS_DAILY_RANGE, false))
            .putInt(KEY_TEMPERATURE_MAX, data.getInt(KEY_TEMPERATURE_MAX))
            .putInt(KEY_TEMPERATURE_MIN, data.getInt(KEY_TEMPERATURE_MIN))
            .putLong(KEY_UPDATED_AT, data.getLong(KEY_UPDATED_AT))
            .apply()
        showSavedWeather()
    }

    private fun showSavedWeather() {
        val preferences = getSharedPreferences(PREFERENCES_NAME, MODE_PRIVATE)
        val hasData = preferences.contains(KEY_UPDATED_AT)
        findViewById<TextView>(R.id.location).text = if (hasData) {
            preferences.getString(KEY_LOCATION, "")
        } else {
            getString(R.string.open_phone)
        }
        findViewById<TextView>(R.id.temperature).text = if (hasData) {
            getString(
                R.string.temperature,
                preferences.getInt(KEY_TEMPERATURE, 0),
                preferences.getString(KEY_TEMPERATURE_UNIT, "°C") ?: "°C"
            )
        } else {
            "—°"
        }
        val hasDailyRange = preferences.getBoolean(KEY_HAS_DAILY_RANGE, false)
        findViewById<TextView>(R.id.temperature_range).apply {
            text = getString(
                R.string.temperature_range,
                preferences.getInt(KEY_TEMPERATURE_MAX, 0),
                preferences.getInt(KEY_TEMPERATURE_MIN, 0)
            )
            visibility = if (hasDailyRange) View.VISIBLE else View.GONE
        }
        val rain = preferences.getInt(KEY_RAIN_CHANCE, 0)
        val airQuality = preferences.getInt(KEY_AQI, -1)
        findViewById<TextView>(R.id.details).text = if (airQuality >= 0) {
            getString(R.string.details_with_aqi, rain, airQuality)
        } else {
            getString(R.string.details, rain)
        }
    }

    private companion object {
        const val WEATHER_DATA_PATH = "/nimbo/weather"
        const val EXTRA_DEMO = "demo"
        const val PREFERENCES_NAME = "nimbo_watch_weather"
        const val KEY_LOCATION = "location"
        const val KEY_TEMPERATURE = "temperature_c"
        const val KEY_TEMPERATURE_UNIT = "temperature_unit"
        const val KEY_WEATHER_CODE = "weather_code"
        const val KEY_RAIN_CHANCE = "rain_chance"
        const val KEY_AQI = "aqi"
        const val KEY_HAS_DAILY_RANGE = "has_daily_range"
        const val KEY_TEMPERATURE_MAX = "temperature_max"
        const val KEY_TEMPERATURE_MIN = "temperature_min"
        const val KEY_UPDATED_AT = "updated_at"
    }
}
