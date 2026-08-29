package uz.ganikhodjaev.weather.shared

internal interface AutomaticRefreshAttemptStore {
    suspend fun read(locationId: String): AutomaticRefreshAttemptState?

    suspend fun writeDurably(locationId: String, state: AutomaticRefreshAttemptState): Boolean

    fun writeBestEffort(locationId: String, state: AutomaticRefreshAttemptState)

    suspend fun removeDurably(locationId: String): Boolean
}

internal expect fun createAutomaticRefreshAttemptStore(
    platformContext: PlatformContext
): AutomaticRefreshAttemptStore

internal class InMemoryAutomaticRefreshAttemptStore : AutomaticRefreshAttemptStore {
    private val attempts = mutableMapOf<String, AutomaticRefreshAttemptState>()

    override suspend fun read(locationId: String): AutomaticRefreshAttemptState? =
        attempts[locationId]

    override suspend fun writeDurably(
        locationId: String,
        state: AutomaticRefreshAttemptState
    ): Boolean {
        attempts[locationId] = state
        return true
    }

    override fun writeBestEffort(locationId: String, state: AutomaticRefreshAttemptState) {
        attempts[locationId] = state
    }

    override suspend fun removeDurably(locationId: String): Boolean {
        attempts.remove(locationId)
        return true
    }
}

internal data class AutomaticRefreshAttemptState(
    val token: Long,
    val attemptedAtEpochSeconds: Long,
    val phase: AutomaticRefreshAttemptPhase
)

internal enum class AutomaticRefreshAttemptPhase {
    InFlight,
    Cooldown,
    RetryPending
}

internal fun encodeAutomaticRefreshAttemptState(state: AutomaticRefreshAttemptState): String =
    listOf(
        AUTOMATIC_REFRESH_ATTEMPT_STATE_VERSION,
        state.token.toString(),
        state.attemptedAtEpochSeconds.toString(),
        state.phase.name
    ).joinToString(AUTOMATIC_REFRESH_ATTEMPT_STATE_SEPARATOR)

internal fun decodeAutomaticRefreshAttemptState(value: String): AutomaticRefreshAttemptState {
    val parts = value.split(AUTOMATIC_REFRESH_ATTEMPT_STATE_SEPARATOR)
    require(parts.size == 4 && parts[0] == AUTOMATIC_REFRESH_ATTEMPT_STATE_VERSION) {
        "Unsupported automatic refresh attempt state"
    }
    return AutomaticRefreshAttemptState(
        token = parts[1].toLong(),
        attemptedAtEpochSeconds = parts[2].toLong(),
        phase = AutomaticRefreshAttemptPhase.valueOf(parts[3])
    )
}

internal fun legacyAutomaticRefreshAttemptState(epochSeconds: Long) = AutomaticRefreshAttemptState(
    token = epochSeconds,
    attemptedAtEpochSeconds = epochSeconds,
    phase = AutomaticRefreshAttemptPhase.Cooldown
)

/**
 * Keeps plaintext location ids, including coarse device coordinates, out of preferences.
 * This deterministic key is pseudonymous rather than anonymous and is removed with the location.
 * A collision can only over-throttle automatic refreshes; manual refresh remains available.
 */
internal fun automaticRefreshAttemptStorageKey(locationId: String): String {
    var hash = FNV_1A_64_OFFSET_BASIS
    locationId.forEach { character ->
        hash = (hash xor character.code.toLong()) * FNV_1A_64_PRIME
    }
    return "$AUTOMATIC_REFRESH_ATTEMPT_KEY_PREFIX${hash.toULong().toString(16)}"
}

private const val AUTOMATIC_REFRESH_ATTEMPT_KEY_PREFIX = "last_attempt_"
private const val AUTOMATIC_REFRESH_ATTEMPT_STATE_VERSION = "v1"
private const val AUTOMATIC_REFRESH_ATTEMPT_STATE_SEPARATOR = "|"
private const val FNV_1A_64_OFFSET_BASIS = -3750763034362895579L
private const val FNV_1A_64_PRIME = 1099511628211L
