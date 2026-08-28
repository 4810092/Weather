package uz.ganikhodjaev.weather.shared

import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

internal object AutomaticRefreshCoordinator {
    private val registryMutex = Mutex()
    private val locationMutexes = mutableMapOf<String, Mutex>()
    private val lastAttemptEpochSeconds = mutableMapOf<String, Long>()

    suspend fun <T> withLocationLock(locationId: String, block: suspend () -> T): T {
        val locationMutex = registryMutex.withLock {
            locationMutexes.getOrPut(locationId) { Mutex() }
        }
        return locationMutex.withLock { block() }
    }

    suspend fun claimAutomaticAttempt(locationId: String, nowEpochSeconds: Long): Boolean =
        registryMutex.withLock {
            if (!isAutomaticRefreshAttemptDue(
                    lastAttemptEpochSeconds[locationId],
                    nowEpochSeconds
                )
            ) {
                return@withLock false
            }
            lastAttemptEpochSeconds[locationId] = nowEpochSeconds
            true
        }

    suspend fun recordAttempt(locationId: String, nowEpochSeconds: Long) {
        registryMutex.withLock {
            lastAttemptEpochSeconds[locationId] = nowEpochSeconds
        }
    }

    internal suspend fun resetAttemptHistoryForTests() {
        registryMutex.withLock {
            lastAttemptEpochSeconds.clear()
        }
    }
}
