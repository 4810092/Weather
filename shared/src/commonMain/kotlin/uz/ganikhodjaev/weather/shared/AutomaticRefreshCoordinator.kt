package uz.ganikhodjaev.weather.shared

import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

internal sealed interface AutomaticRefreshClaimResult {
    data class Granted(val token: Long) : AutomaticRefreshClaimResult

    data object Cooldown : AutomaticRefreshClaimResult

    data object RetryDeferred : AutomaticRefreshClaimResult

    data object StoreUnavailable : AutomaticRefreshClaimResult
}

internal enum class AutomaticRefreshAttemptCompletion {
    Cooldown,
    RetryPending
}

internal object AutomaticRefreshCoordinator {
    private val registryMutex = Mutex()
    private val locationLocks = mutableMapOf<String, LocationLockEntry>()
    private val attemptEntries = mutableMapOf<String, AttemptEntry>()

    suspend fun <T> withLocationLock(locationId: String, block: suspend () -> T): T {
        val entry = registryMutex.withLock {
            locationLocks.getOrPut(locationId) { LocationLockEntry() }
                .also { it.users += 1 }
        }
        return try {
            entry.mutex.withLock { block() }
        } finally {
            registryMutex.withLock {
                entry.users -= 1
                if (entry.users == 0 && locationLocks[locationId] === entry) {
                    locationLocks.remove(locationId)
                }
            }
        }
    }

    suspend fun claimAutomaticAttempt(
        locationId: String,
        nowEpochSeconds: Long,
        attemptStore: AutomaticRefreshAttemptStore
    ): AutomaticRefreshClaimResult = withAttemptEntry(locationId) { entry ->
        val storedAttempt = try {
            attemptStore.read(locationId)
        } catch (cancelled: CancellationException) {
            throw cancelled
        } catch (_: Throwable) {
            // Automatic refresh is fail-closed when durable budget state is unavailable.
            return@withAttemptEntry AutomaticRefreshClaimResult.StoreUnavailable
        }
        val lastAttempt = entry.state ?: storedAttempt?.also { entry.state = it }
        if (!isAutomaticRefreshAttemptDue(
                lastAttempt?.attemptedAtEpochSeconds,
                nowEpochSeconds
            )
        ) {
            return@withAttemptEntry when (lastAttempt?.phase) {
                AutomaticRefreshAttemptPhase.InFlight,
                AutomaticRefreshAttemptPhase.RetryPending -> {
                    AutomaticRefreshClaimResult.RetryDeferred
                }
                AutomaticRefreshAttemptPhase.Cooldown -> AutomaticRefreshClaimResult.Cooldown
                null -> error("Missing automatic refresh attempt state")
            }
        }

        val claimed = AutomaticRefreshAttemptState(
            token = issueToken(lastAttempt?.token),
            attemptedAtEpochSeconds = nowEpochSeconds,
            phase = AutomaticRefreshAttemptPhase.InFlight
        )
        // Keep the in-process state conservative even if the strict durable write fails.
        entry.state = claimed
        val persisted = try {
            attemptStore.writeDurably(locationId, claimed)
        } catch (cancelled: CancellationException) {
            throw cancelled
        } catch (_: Throwable) {
            false
        }
        if (persisted) {
            AutomaticRefreshClaimResult.Granted(claimed.token)
        } else {
            AutomaticRefreshClaimResult.StoreUnavailable
        }
    }

    suspend fun finalizeAutomaticAttempt(
        locationId: String,
        token: Long,
        completion: AutomaticRefreshAttemptCompletion,
        attemptStore: AutomaticRefreshAttemptStore
    ): Boolean = withAttemptEntry(locationId) { entry ->
        val current = entry.state
        if (current?.token != token || current.phase != AutomaticRefreshAttemptPhase.InFlight) {
            return@withAttemptEntry false
        }
        val finalized = current.copy(
            phase = when (completion) {
                AutomaticRefreshAttemptCompletion.Cooldown -> {
                    AutomaticRefreshAttemptPhase.Cooldown
                }
                AutomaticRefreshAttemptCompletion.RetryPending -> {
                    AutomaticRefreshAttemptPhase.RetryPending
                }
            }
        )
        entry.state = finalized
        try {
            attemptStore.writeDurably(locationId, finalized)
        } catch (cancelled: CancellationException) {
            throw cancelled
        } catch (_: Throwable) {
            false
        }
    }

    suspend fun recordManualAttempt(
        locationId: String,
        nowEpochSeconds: Long,
        attemptStore: AutomaticRefreshAttemptStore
    ) {
        withAttemptEntry(locationId) { entry ->
            val recorded = AutomaticRefreshAttemptState(
                token = issueToken(entry.state?.token),
                attemptedAtEpochSeconds = nowEpochSeconds,
                phase = AutomaticRefreshAttemptPhase.Cooldown
            )
            entry.state = recorded
            try {
                // This is outside the registry mutex but inside the per-location critical
                // section, so deletion cannot race a pending best-effort write. Android uses
                // SharedPreferences.apply(), which updates memory now and schedules disk I/O.
                attemptStore.writeBestEffort(locationId, recorded)
            } catch (cancelled: CancellationException) {
                throw cancelled
            } catch (_: Throwable) {
                // A manual refresh remains available when best-effort persistence fails.
            }
        }
    }

    suspend fun removeAttemptState(
        locationId: String,
        attemptStore: AutomaticRefreshAttemptStore
    ): Boolean = withAttemptEntry(locationId) { entry ->
        val removed = try {
            attemptStore.removeDurably(locationId)
        } catch (cancelled: CancellationException) {
            throw cancelled
        } catch (_: Throwable) {
            false
        }
        if (removed) entry.state = null
        removed
    }

    internal suspend fun resetAttemptHistoryForTests() {
        registryMutex.withLock {
            attemptEntries.clear()
        }
    }

    internal suspend fun retainsLocationForTests(locationId: String): Boolean =
        registryMutex.withLock {
            locationLocks.containsKey(locationId) || attemptEntries.containsKey(locationId)
        }

    private suspend fun <T> withAttemptEntry(
        locationId: String,
        block: suspend (AttemptEntry) -> T
    ): T {
        val entry = registryMutex.withLock {
            attemptEntries.getOrPut(locationId) { AttemptEntry() }
                .also { it.users += 1 }
        }
        return try {
            entry.mutex.withLock { block(entry) }
        } finally {
            registryMutex.withLock {
                entry.users -= 1
                if (
                    entry.users == 0 &&
                    entry.state == null &&
                    attemptEntries[locationId] === entry
                ) {
                    attemptEntries.remove(locationId)
                }
            }
        }
    }

    private fun issueToken(previousToken: Long?): Long = when (previousToken) {
        null,
        Long.MAX_VALUE -> 1L
        else -> previousToken + 1L
    }

    private class LocationLockEntry(val mutex: Mutex = Mutex(), var users: Int = 0)

    private class AttemptEntry(
        val mutex: Mutex = Mutex(),
        var users: Int = 0,
        var state: AutomaticRefreshAttemptState? = null
    )
}
