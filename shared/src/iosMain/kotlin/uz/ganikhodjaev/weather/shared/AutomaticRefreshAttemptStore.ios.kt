package uz.ganikhodjaev.weather.shared

import platform.Foundation.NSNumber
import platform.Foundation.NSUserDefaults

internal actual fun createAutomaticRefreshAttemptStore(
    platformContext: PlatformContext
): AutomaticRefreshAttemptStore = IosAutomaticRefreshAttemptStore(
    NSUserDefaults.standardUserDefaults
)

private class IosAutomaticRefreshAttemptStore(private val preferences: NSUserDefaults) :
    AutomaticRefreshAttemptStore {
    override suspend fun read(locationId: String): AutomaticRefreshAttemptState? {
        val key = automaticRefreshAttemptStorageKey(locationId)
        val stored = preferences.objectForKey(key) ?: return null
        if (stored is NSNumber) {
            return legacyAutomaticRefreshAttemptState(stored.longLongValue)
        }
        return preferences.stringForKey(key)
            ?.let(::decodeAutomaticRefreshAttemptState)
            ?: error("Unsupported automatic refresh attempt state")
    }

    override suspend fun writeDurably(
        locationId: String,
        state: AutomaticRefreshAttemptState
    ): Boolean {
        writeBestEffort(locationId, state)
        return preferences.synchronize()
    }

    override fun writeBestEffort(locationId: String, state: AutomaticRefreshAttemptState) {
        preferences.setObject(
            encodeAutomaticRefreshAttemptState(state),
            forKey = automaticRefreshAttemptStorageKey(locationId)
        )
    }

    override suspend fun removeDurably(locationId: String): Boolean {
        preferences.removeObjectForKey(automaticRefreshAttemptStorageKey(locationId))
        return preferences.synchronize()
    }
}
