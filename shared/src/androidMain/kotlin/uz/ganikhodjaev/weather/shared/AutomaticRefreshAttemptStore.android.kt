package uz.ganikhodjaev.weather.shared

import android.content.Context
import android.content.SharedPreferences
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

internal actual fun createAutomaticRefreshAttemptStore(
    platformContext: PlatformContext
): AutomaticRefreshAttemptStore = AndroidAutomaticRefreshAttemptStore(
    platformContext.applicationContext.getSharedPreferences(
        AUTOMATIC_REFRESH_PREFERENCES_NAME,
        Context.MODE_PRIVATE
    )
)

private class AndroidAutomaticRefreshAttemptStore(private val preferences: SharedPreferences) :
    AutomaticRefreshAttemptStore {
    override suspend fun read(locationId: String): AutomaticRefreshAttemptState? {
        val key = automaticRefreshAttemptStorageKey(locationId)
        return when (val stored = preferences.all[key]) {
            null -> null
            is String -> decodeAutomaticRefreshAttemptState(stored)
            is Long -> legacyAutomaticRefreshAttemptState(stored)
            else -> error("Unsupported automatic refresh attempt state")
        }
    }

    override suspend fun writeDurably(
        locationId: String,
        state: AutomaticRefreshAttemptState
    ): Boolean = withContext(Dispatchers.IO) {
        preferences.edit()
            .putString(
                automaticRefreshAttemptStorageKey(locationId),
                encodeAutomaticRefreshAttemptState(state)
            )
            .commit()
    }

    override fun writeBestEffort(locationId: String, state: AutomaticRefreshAttemptState) {
        preferences.edit()
            .putString(
                automaticRefreshAttemptStorageKey(locationId),
                encodeAutomaticRefreshAttemptState(state)
            )
            .apply()
    }

    override suspend fun removeDurably(locationId: String): Boolean = withContext(Dispatchers.IO) {
        preferences.edit()
            .remove(automaticRefreshAttemptStorageKey(locationId))
            .commit()
    }
}

private const val AUTOMATIC_REFRESH_PREFERENCES_NAME = "nimbo_automatic_refresh"
