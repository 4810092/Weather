package uz.ganikhodjaev.weather.wear

import android.app.Activity
import android.os.Bundle
import android.view.View
import android.widget.TextView
import androidx.core.splashscreen.SplashScreen.Companion.installSplashScreen
import com.google.android.gms.wearable.DataClient
import com.google.android.gms.wearable.DataEvent
import com.google.android.gms.wearable.DataEventBuffer
import com.google.android.gms.wearable.DataMap
import com.google.android.gms.wearable.DataMapItem
import com.google.android.gms.wearable.Wearable
import uz.ganikhodjaev.weather.surface.SurfaceWeatherKeys
import uz.ganikhodjaev.weather.surface.SurfaceWeatherRenderModel
import uz.ganikhodjaev.weather.surface.SurfaceWeatherState
import uz.ganikhodjaev.weather.surface.buildSurfaceWeatherRenderModel

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
            .putString(
                SurfaceWeatherKeys.LOCATION,
                intent.getStringExtra(SurfaceWeatherKeys.LOCATION) ?: "Tashkent"
            )
            .putInt(
                SurfaceWeatherKeys.TEMPERATURE,
                intent.getIntExtra(SurfaceWeatherKeys.TEMPERATURE, 24)
            )
            .putString(
                SurfaceWeatherKeys.TEMPERATURE_UNIT,
                intent.getStringExtra(SurfaceWeatherKeys.TEMPERATURE_UNIT) ?: "°C"
            )
            .putInt(
                SurfaceWeatherKeys.WEATHER_CODE,
                intent.getIntExtra(SurfaceWeatherKeys.WEATHER_CODE, 1)
            )
            .putInt(
                SurfaceWeatherKeys.RAIN_CHANCE,
                intent.getIntExtra(SurfaceWeatherKeys.RAIN_CHANCE, 10)
            )
            .putInt(
                SurfaceWeatherKeys.AIR_QUALITY,
                intent.getIntExtra(SurfaceWeatherKeys.AIR_QUALITY, 42)
            )
            .putBoolean(SurfaceWeatherKeys.HAS_DAILY_RANGE, true)
            .putInt(
                SurfaceWeatherKeys.TEMPERATURE_MAX,
                intent.getIntExtra(SurfaceWeatherKeys.TEMPERATURE_MAX, 27)
            )
            .putInt(
                SurfaceWeatherKeys.TEMPERATURE_MIN,
                intent.getIntExtra(SurfaceWeatherKeys.TEMPERATURE_MIN, 18)
            )
            .putLong(SurfaceWeatherKeys.UPDATED_AT, System.currentTimeMillis() / 1_000L)
            .apply()
    }

    override fun onResume() {
        super.onResume()
        showSavedWeather()
        Wearable.getDataClient(this).addListener(this)
    }

    override fun onPause() {
        Wearable.getDataClient(this).removeListener(this)
        super.onPause()
    }

    override fun onDataChanged(events: DataEventBuffer) {
        events.filter { event -> event.dataItem.uri.path == WEATHER_DATA_PATH }.forEach { event ->
            when (event.type) {
                DataEvent.TYPE_CHANGED -> saveAndShow(DataMapItem.fromDataItem(event.dataItem))
                DataEvent.TYPE_DELETED -> clearAndShowEmpty()
            }
        }
    }

    private fun saveAndShow(item: DataMapItem) {
        val nowEpochSeconds = System.currentTimeMillis() / 1_000L
        val model = buildSurfaceWeatherRenderModel(
            item.dataMap.toSurfaceValues(),
            nowEpochSeconds
        )
        if (model.state == SurfaceWeatherState.Empty) {
            clearAndShowEmpty()
            return
        }
        persist(model)
        showSavedWeather(nowEpochSeconds)
    }

    private fun persist(model: SurfaceWeatherRenderModel) {
        val preferences = getSharedPreferences(PREFERENCES_NAME, MODE_PRIVATE)
        val editor = preferences.edit()
            .putString(SurfaceWeatherKeys.LOCATION, requireNotNull(model.location))
            .putInt(SurfaceWeatherKeys.TEMPERATURE, requireNotNull(model.temperature))
            .putString(
                SurfaceWeatherKeys.TEMPERATURE_UNIT,
                requireNotNull(model.temperatureUnit)
            )
            .putInt(SurfaceWeatherKeys.WEATHER_CODE, requireNotNull(model.weatherCode))
            .putInt(SurfaceWeatherKeys.RAIN_CHANCE, requireNotNull(model.rainChance))
            .putInt(SurfaceWeatherKeys.AIR_QUALITY, model.airQuality ?: -1)
            .putBoolean(SurfaceWeatherKeys.HAS_DAILY_RANGE, model.showsDailyRange)
            .putLong(
                SurfaceWeatherKeys.UPDATED_AT,
                requireNotNull(model.updatedAtEpochSeconds)
            )
        if (model.showsDailyRange) {
            editor
                .putInt(
                    SurfaceWeatherKeys.TEMPERATURE_MAX,
                    requireNotNull(model.temperatureMaximum)
                )
                .putInt(
                    SurfaceWeatherKeys.TEMPERATURE_MIN,
                    requireNotNull(model.temperatureMinimum)
                )
        } else {
            editor
                .remove(SurfaceWeatherKeys.TEMPERATURE_MAX)
                .remove(SurfaceWeatherKeys.TEMPERATURE_MIN)
        }
        editor.apply()
    }

    private fun showSavedWeather(nowEpochSeconds: Long = System.currentTimeMillis() / 1_000L) {
        val preferences = getSharedPreferences(PREFERENCES_NAME, MODE_PRIVATE)
        val model = buildSurfaceWeatherRenderModel(preferences.all, nowEpochSeconds)
        if (model.state == SurfaceWeatherState.Empty) {
            findViewById<TextView>(R.id.location).text = getString(R.string.open_phone)
            findViewById<TextView>(R.id.temperature).visibility = View.GONE
            findViewById<TextView>(R.id.temperature_range).visibility = View.GONE
            findViewById<TextView>(R.id.details).visibility = View.GONE
            findViewById<TextView>(R.id.status).visibility = View.GONE
            return
        }

        findViewById<TextView>(R.id.location).text = requireNotNull(model.location)
        findViewById<TextView>(R.id.temperature).apply {
            text = getString(
                R.string.temperature,
                requireNotNull(model.temperature),
                requireNotNull(model.temperatureUnit)
            )
            visibility = View.VISIBLE
        }
        findViewById<TextView>(R.id.temperature_range).apply {
            if (model.showsDailyRange) {
                text = getString(
                    R.string.temperature_range,
                    requireNotNull(model.temperatureMaximum),
                    requireNotNull(model.temperatureMinimum)
                )
                visibility = View.VISIBLE
            } else {
                visibility = View.GONE
            }
        }
        findViewById<TextView>(R.id.details).apply {
            text = model.airQuality?.let { airQuality ->
                getString(R.string.details_with_aqi, requireNotNull(model.rainChance), airQuality)
            } ?: getString(R.string.details, requireNotNull(model.rainChance))
            visibility = View.VISIBLE
        }
        findViewById<TextView>(R.id.status).apply {
            text = getString(R.string.saved_weather)
            visibility = if (model.showsStaleStatus) View.VISIBLE else View.GONE
        }
    }

    private fun clearAndShowEmpty() {
        getSharedPreferences(PREFERENCES_NAME, MODE_PRIVATE).edit().clear().apply()
        showSavedWeather()
    }

    private fun DataMap.toSurfaceValues(): Map<String, Any?> =
        keySet().associateWith { key -> get<Any?>(key) }

    private companion object {
        const val WEATHER_DATA_PATH = "/nimbo/weather"
        const val EXTRA_DEMO = "demo"
        const val PREFERENCES_NAME = "nimbo_watch_weather"
    }
}
