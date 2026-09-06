package uz.ganikhodjaev.weather.shared

import platform.Foundation.NSNumber
import platform.Foundation.NSUserDefaults
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonNull
import kotlinx.serialization.json.buildJsonObject
import kotlinx.serialization.json.jsonPrimitive
import kotlinx.serialization.json.longOrNull
import kotlinx.serialization.json.booleanOrNull
import kotlinx.serialization.json.put

internal actual fun createAutomaticRefreshAttemptStore(
    platformContext: PlatformContext
): AutomaticRefreshAttemptStore = IosAutomaticRefreshAttemptStore(
    NSUserDefaults.standardUserDefaults
)

private class IosAutomaticRefreshAttemptStore(private val preferences: NSUserDefaults) :
    AtomicAutomaticRefreshAttemptStore {
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

    override suspend fun claimAtomically(
        locationId: String,
        nowEpochSeconds: Long
    ): AutomaticRefreshClaimResult {
        val key = automaticRefreshAttemptStorageKey(locationId)
        val legacy = legacyValue(key)
        val response = exchange(
            buildJsonObject {
                put("op", "claim")
                put("key", key)
                put("now", nowEpochSeconds)
                if (legacy != null) put("legacy", legacy) else put("legacy", JsonNull)
            }
        ) ?: return if (WidgetRefreshInterop.isInstalled()) {
            AutomaticRefreshClaimResult.StoreUnavailable
        } else {
            fallbackClaim(locationId, nowEpochSeconds)
        }
        return when (response["status"]?.jsonPrimitive?.content) {
            "granted" -> response["token"]?.jsonPrimitive?.longOrNull
                ?.let(AutomaticRefreshClaimResult::Granted)
                ?: AutomaticRefreshClaimResult.StoreUnavailable
            "cooldown" -> AutomaticRefreshClaimResult.Cooldown
            "deferred" -> AutomaticRefreshClaimResult.RetryDeferred
            else -> AutomaticRefreshClaimResult.StoreUnavailable
        }
    }

    override suspend fun finishAtomically(
        locationId: String,
        token: Long,
        completion: AutomaticRefreshAttemptCompletion
    ): Boolean = exchange(
        buildJsonObject {
            put("op", "finish")
            put("key", automaticRefreshAttemptStorageKey(locationId))
            put("token", token)
            put("phase", completion.name)
        }
    )?.get("ok")?.jsonPrimitive?.booleanOrNull ?: if (WidgetRefreshInterop.isInstalled()) {
        false
    } else fallbackFinish(locationId, token, completion)

    override suspend fun recordManualAttemptAtomically(locationId: String, nowEpochSeconds: Long) {
        val key = automaticRefreshAttemptStorageKey(locationId)
        val response = exchange(buildJsonObject {
            put("op", "manual")
            put("key", key)
            put("now", nowEpochSeconds)
        })
        if (response == null && !WidgetRefreshInterop.isInstalled()) {
            writeBestEffort(
                locationId,
                AutomaticRefreshAttemptState(nowEpochSeconds, nowEpochSeconds, AutomaticRefreshAttemptPhase.Cooldown)
            )
        }
    }

    override suspend fun removeAtomically(locationId: String): Boolean = exchange(buildJsonObject {
        put("op", "remove")
        put("key", automaticRefreshAttemptStorageKey(locationId))
    })?.get("ok")?.jsonPrimitive?.booleanOrNull ?: if (WidgetRefreshInterop.isInstalled()) {
        false
    } else removeDurably(locationId)

    private fun legacyValue(key: String): String? = when (val stored = preferences.objectForKey(key)) {
        is NSNumber -> legacyAutomaticRefreshAttemptState(stored.longLongValue)
            .let(::encodeAutomaticRefreshAttemptState)
        else -> preferences.stringForKey(key)
    }

    private fun exchange(request: JsonObject): JsonObject? = try {
        WidgetRefreshInterop.exchange(RPC_JSON.encodeToString(JsonObject.serializer(), request))
            ?.let { RPC_JSON.parseToJsonElement(it) as? JsonObject }
    } catch (_: Throwable) {
        null
    }

    private suspend fun fallbackClaim(locationId: String, now: Long): AutomaticRefreshClaimResult {
        val state = read(locationId)
        if (!isAutomaticRefreshAttemptDue(state?.attemptedAtEpochSeconds, now)) {
            return if (state?.phase == AutomaticRefreshAttemptPhase.Cooldown) {
                AutomaticRefreshClaimResult.Cooldown
            } else AutomaticRefreshClaimResult.RetryDeferred
        }
        val claimed = AutomaticRefreshAttemptState(
            token = (state?.token ?: 0) + 1,
            attemptedAtEpochSeconds = now,
            phase = AutomaticRefreshAttemptPhase.InFlight
        )
        return if (writeDurably(locationId, claimed)) AutomaticRefreshClaimResult.Granted(claimed.token)
        else AutomaticRefreshClaimResult.StoreUnavailable
    }

    private suspend fun fallbackFinish(
        locationId: String,
        token: Long,
        completion: AutomaticRefreshAttemptCompletion
    ): Boolean {
        val current = read(locationId) ?: return false
        if (current.token != token || current.phase != AutomaticRefreshAttemptPhase.InFlight) return false
        return writeDurably(locationId, current.copy(phase = when (completion) {
            AutomaticRefreshAttemptCompletion.Cooldown -> AutomaticRefreshAttemptPhase.Cooldown
            AutomaticRefreshAttemptCompletion.RetryPending -> AutomaticRefreshAttemptPhase.RetryPending
        }))
    }
}

private val RPC_JSON = Json { ignoreUnknownKeys = true }
