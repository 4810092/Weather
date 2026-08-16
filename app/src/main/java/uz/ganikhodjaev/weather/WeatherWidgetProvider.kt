package uz.ganikhodjaev.weather

import android.app.PendingIntent
import android.appwidget.AppWidgetManager
import android.appwidget.AppWidgetProvider
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.view.View
import android.widget.RemoteViews
import com.google.android.gms.wearable.PutDataMapRequest
import com.google.android.gms.wearable.Wearable

class WeatherWidgetProvider : AppWidgetProvider() {
    override fun onUpdate(
        context: Context,
        appWidgetManager: AppWidgetManager,
        appWidgetIds: IntArray
    ) {
        appWidgetIds.forEach { appWidgetId ->
            appWidgetManager.updateAppWidget(appWidgetId, views(context))
        }
        syncWithWatch(context)
    }

    override fun onReceive(context: Context, intent: Intent) {
        super.onReceive(context, intent)
        if (intent.action == ACTION_WIDGET_DATA_CHANGED) {
            val manager = AppWidgetManager.getInstance(context)
            val component = ComponentName(context, WeatherWidgetProvider::class.java)
            onUpdate(context, manager, manager.getAppWidgetIds(component))
        }
    }

    private fun syncWithWatch(context: Context) {
        val preferences = context.getSharedPreferences(PREFERENCES_NAME, Context.MODE_PRIVATE)
        if (!preferences.contains(KEY_UPDATED_AT)) return
        val request = PutDataMapRequest.create(WEATHER_DATA_PATH).apply {
            dataMap.putString(KEY_LOCATION, preferences.getString(KEY_LOCATION, "") ?: "")
            dataMap.putInt(KEY_TEMPERATURE, preferences.getInt(KEY_TEMPERATURE, 0))
            dataMap.putString(
                KEY_TEMPERATURE_UNIT,
                preferences.getString(KEY_TEMPERATURE_UNIT, "°C") ?: "°C"
            )
            dataMap.putInt(KEY_WEATHER_CODE, preferences.getInt(KEY_WEATHER_CODE, -1))
            dataMap.putInt(KEY_RAIN_CHANCE, preferences.getInt(KEY_RAIN_CHANCE, 0))
            dataMap.putInt(KEY_AQI, preferences.getInt(KEY_AQI, -1))
            dataMap.putBoolean(
                KEY_HAS_DAILY_RANGE,
                preferences.getBoolean(KEY_HAS_DAILY_RANGE, false)
            )
            if (preferences.getBoolean(KEY_HAS_DAILY_RANGE, false)) {
                dataMap.putInt(
                    KEY_TEMPERATURE_MAX,
                    preferences.getInt(KEY_TEMPERATURE_MAX, 0)
                )
                dataMap.putInt(
                    KEY_TEMPERATURE_MIN,
                    preferences.getInt(KEY_TEMPERATURE_MIN, 0)
                )
            }
            dataMap.putLong(KEY_UPDATED_AT, preferences.getLong(KEY_UPDATED_AT, 0))
        }.asPutDataRequest().setUrgent()
        Wearable.getDataClient(context).putDataItem(request)
    }

    private fun views(context: Context): RemoteViews {
        val preferences = context.getSharedPreferences(PREFERENCES_NAME, Context.MODE_PRIVATE)
        val location = preferences.getString(KEY_LOCATION, null)
            ?: context.getString(R.string.widget_open_nimbo)
        val temperature = preferences.getInt(KEY_TEMPERATURE, Int.MIN_VALUE)
        val temperatureUnit = preferences.getString(KEY_TEMPERATURE_UNIT, "°C") ?: "°C"
        val weatherCode = preferences.getInt(KEY_WEATHER_CODE, -1)
        val rainChance = preferences.getInt(KEY_RAIN_CHANCE, 0)
        val aqi = preferences.getInt(KEY_AQI, -1)
        val hasDailyRange = preferences.getBoolean(KEY_HAS_DAILY_RANGE, false)
        val maximum = preferences.getInt(KEY_TEMPERATURE_MAX, 0)
        val minimum = preferences.getInt(KEY_TEMPERATURE_MIN, 0)
        val details = buildString {
            append(weatherSymbol(weatherCode))
            append("  ·  ")
            append(context.getString(R.string.widget_rain, rainChance))
            if (aqi >= 0) {
                append("  ·  ")
                append(context.getString(R.string.widget_aqi, aqi))
            }
        }
        val openApp = PendingIntent.getActivity(
            context,
            0,
            Intent(context, MainActivity::class.java),
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        return RemoteViews(context.packageName, R.layout.weather_widget).apply {
            setTextViewText(R.id.widget_location, location)
            setTextViewText(
                R.id.widget_temperature,
                if (temperature == Int.MIN_VALUE) "—°" else "$temperature$temperatureUnit"
            )
            setTextViewText(
                R.id.widget_temperature_range,
                context.getString(R.string.widget_temperature_range, maximum, minimum)
            )
            setViewVisibility(
                R.id.widget_temperature_range,
                if (hasDailyRange) View.VISIBLE else View.GONE
            )
            setTextViewText(R.id.widget_details, details)
            setOnClickPendingIntent(R.id.widget_root, openApp)
        }
    }

    private fun weatherSymbol(code: Int): String = when (code) {
        0 -> "☀"
        1, 2 -> "🌤"
        3 -> "☁"
        45, 48 -> "≋"
        51, 53, 55, 56, 57 -> "☂"
        61, 63, 65, 66, 67, 80, 81, 82 -> "☔"
        71, 73, 75, 77, 85, 86 -> "❄"
        95, 96, 99 -> "ϟ"
        else -> "Nimbo"
    }

    private companion object {
        const val PREFERENCES_NAME = "nimbo_surface_weather"
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
        const val WEATHER_DATA_PATH = "/nimbo/weather"
        const val ACTION_WIDGET_DATA_CHANGED =
            "uz.ganikhodjaev.weather.action.WIDGET_DATA_CHANGED"
    }
}
