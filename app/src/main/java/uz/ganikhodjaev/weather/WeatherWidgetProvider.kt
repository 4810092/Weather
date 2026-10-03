package uz.ganikhodjaev.weather

import android.app.PendingIntent
import android.appwidget.AppWidgetManager
import android.appwidget.AppWidgetProvider
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.util.TypedValue
import android.view.View
import android.widget.RemoteViews
import java.text.DateFormat
import java.util.Date
import uz.ganikhodjaev.weather.surface.SurfaceWeatherRenderModel
import uz.ganikhodjaev.weather.surface.SurfaceWeatherState
import uz.ganikhodjaev.weather.surface.buildSurfaceWeatherRenderModel

class WeatherWidgetProvider : AppWidgetProvider() {
    override fun onAppWidgetOptionsChanged(
        context: Context,
        appWidgetManager: AppWidgetManager,
        appWidgetId: Int,
        newOptions: Bundle
    ) {
        updateWidgets(context, appWidgetManager, intArrayOf(appWidgetId))
    }

    override fun onUpdate(
        context: Context,
        appWidgetManager: AppWidgetManager,
        appWidgetIds: IntArray
    ) {
        updateWidgets(context, appWidgetManager, appWidgetIds)
    }

    private fun updateWidgets(
        context: Context,
        appWidgetManager: AppWidgetManager,
        appWidgetIds: IntArray
    ) {
        val nowEpochSeconds = System.currentTimeMillis() / 1_000L
        appWidgetIds.forEach { appWidgetId ->
            val height = appWidgetManager.getAppWidgetOptions(appWidgetId)
                .getInt(AppWidgetManager.OPTION_APPWIDGET_MIN_HEIGHT, 180)
            val compact = height < 180 * context.resources.configuration.fontScale
            appWidgetManager.updateAppWidget(appWidgetId, views(context, nowEpochSeconds, compact))
        }
    }

    override fun onReceive(context: Context, intent: Intent) {
        super.onReceive(context, intent)
        if (intent.action == ACTION_WIDGET_DATA_CHANGED) {
            val manager = AppWidgetManager.getInstance(context)
            val component = ComponentName(context, WeatherWidgetProvider::class.java)
            updateWidgets(context, manager, manager.getAppWidgetIds(component))
        }
    }

    private fun views(context: Context, nowEpochSeconds: Long, compact: Boolean): RemoteViews {
        val preferences = context.getSharedPreferences(PREFERENCES_NAME, Context.MODE_PRIVATE)
        val model = buildSurfaceWeatherRenderModel(preferences.all, nowEpochSeconds)
        val openApp = PendingIntent.getActivity(
            context,
            0,
            Intent(context, MainActivity::class.java),
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        return RemoteViews(context.packageName, R.layout.weather_widget).apply {
            if (model.state == SurfaceWeatherState.Empty) {
                setTextViewText(R.id.widget_location, context.getString(R.string.widget_open_nimbo))
                setViewVisibility(R.id.widget_temperature, View.GONE)
                setViewVisibility(R.id.widget_temperature_range, View.GONE)
                setViewVisibility(R.id.widget_details, View.GONE)
                setViewVisibility(R.id.widget_status, View.GONE)
            } else {
                renderWeather(context, model, compact)
            }
            setOnClickPendingIntent(R.id.widget_root, openApp)
        }
    }

    private fun RemoteViews.renderWeather(
        context: Context,
        model: SurfaceWeatherRenderModel,
        compact: Boolean
    ) {
        val temperature = requireNotNull(model.temperature)
        val temperatureUnit = requireNotNull(model.temperatureUnit)
        val maximum = model.temperatureMaximum
        val minimum = model.temperatureMinimum
        val details = buildString {
            append(weatherSymbol(requireNotNull(model.weatherCode)))
            append("  ·  ")
            append(context.getString(R.string.widget_rain, requireNotNull(model.rainChance)))
            model.airQuality?.let { airQuality ->
                append("  ·  ")
                append(context.getString(R.string.widget_aqi, airQuality))
            }
        }

        setTextViewText(R.id.widget_location, requireNotNull(model.location))
        setTextViewText(R.id.widget_temperature, "$temperature$temperatureUnit")
        setViewVisibility(R.id.widget_temperature, View.VISIBLE)
        if (model.showsDailyRange && !compact) {
            setTextViewText(
                R.id.widget_temperature_range,
                context.getString(
                    R.string.widget_temperature_range,
                    requireNotNull(maximum),
                    requireNotNull(minimum)
                )
            )
            setViewVisibility(R.id.widget_temperature_range, View.VISIBLE)
        } else {
            setViewVisibility(R.id.widget_temperature_range, View.GONE)
        }
        setTextViewText(R.id.widget_details, details)
        setViewVisibility(R.id.widget_details, if (compact) View.GONE else View.VISIBLE)
        val updated = DateFormat.getDateTimeInstance(DateFormat.SHORT, DateFormat.SHORT)
            .format(Date(requireNotNull(model.updatedAtEpochSeconds) * 1_000))
        setTextViewText(
            R.id.widget_status,
            listOfNotNull(
                if (compact) updated else context.getString(R.string.last_updated, updated),
                context.getString(
                    if (compact) R.string.saved_weather_short else R.string.saved_weather
                ).takeIf { model.showsStaleStatus }
            ).joinToString("\n")
        )
        setViewVisibility(R.id.widget_status, View.VISIBLE)
        setContentDescription(
            R.id.widget_status,
            listOfNotNull(
                context.getString(R.string.last_updated, updated),
                context.getString(R.string.saved_weather).takeIf { model.showsStaleStatus }
            ).joinToString(". ")
        )
        if (compact) {
            val padding = (8 * context.resources.displayMetrics.density).toInt()
            setViewPadding(R.id.widget_root, padding, padding, padding, padding)
            val fontScale = context.resources.configuration.fontScale
            // Home widgets cannot scroll. Keep the status readable in a short resized widget.
            val scale = minOf(fontScale, 1.2f)
            setTextViewTextSize(R.id.widget_temperature, TypedValue.COMPLEX_UNIT_DIP, 28f * scale)
            setTextViewTextSize(R.id.widget_status, TypedValue.COMPLEX_UNIT_DIP, 12f * scale)
            setTextViewTextSize(R.id.widget_location, TypedValue.COMPLEX_UNIT_SP, 12f)
            if (fontScale > 1.2f) {
                setViewVisibility(R.id.widget_location, View.GONE)
                setContentDescription(
                    R.id.widget_temperature,
                    "${model.location}, $temperature$temperatureUnit"
                )
            }
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
        const val ACTION_WIDGET_DATA_CHANGED =
            "uz.ganikhodjaev.weather.action.WIDGET_DATA_CHANGED"
    }
}
