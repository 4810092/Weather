package uz.ganikhodjaev.weather.shared

import io.ktor.client.network.sockets.ConnectTimeoutException
import io.ktor.client.network.sockets.SocketTimeoutException
import io.ktor.client.plugins.HttpRequestTimeoutException
import io.ktor.client.plugins.ResponseException
import kotlin.time.Clock
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.ensureActive
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch
import kotlinx.serialization.SerializationException
import uz.ganikhodjaev.weather.shared.data.WeatherDataSource
import uz.ganikhodjaev.weather.shared.model.Location
import uz.ganikhodjaev.weather.shared.model.WeatherSnapshot
import uz.ganikhodjaev.weather.shared.model.resolve
import uz.ganikhodjaev.weather.shared.units.automaticUnitSystem

enum class BackgroundRefreshOutcome {
    Updated,
    NothingToRefresh,
    TransientFailure,
    PermanentFailure
}

class BackgroundWeatherUpdater(platformContext: PlatformContext) {
    private val context = platformContext
    private val repository = NimboContainer(platformContext).weatherRepository
    private val refreshScope = CoroutineScope(SupervisorJob() + Dispatchers.Default)

    suspend fun refreshOutcome(): BackgroundRefreshOutcome =
        refreshBackgroundWeather(repository) { snapshot ->
            val units = repository.unitPreference().resolve(automaticUnitSystem())
            publishWeatherSnapshot(
                platformContext = context,
                snapshot = snapshot,
                displayUnits = units
            )
        }

    suspend fun refresh(): Boolean = when (refreshOutcome()) {
        BackgroundRefreshOutcome.Updated,
        BackgroundRefreshOutcome.NothingToRefresh -> true
        BackgroundRefreshOutcome.TransientFailure,
        BackgroundRefreshOutcome.PermanentFailure -> false
    }

    fun startRefresh(onComplete: (Boolean) -> Unit): BackgroundRefreshHandle =
        startCancellableBackgroundRefresh(
            scope = refreshScope,
            refresh = ::refresh,
            onComplete = onComplete
        )
}

class BackgroundRefreshHandle internal constructor(private val job: Job) {
    fun cancel() {
        job.cancel()
    }

    internal suspend fun join() {
        job.join()
    }
}

internal fun startCancellableBackgroundRefresh(
    scope: CoroutineScope,
    refresh: suspend () -> Boolean,
    onComplete: (Boolean) -> Unit
): BackgroundRefreshHandle {
    val job = scope.launch {
        val succeeded = try {
            refresh()
        } catch (cancelled: CancellationException) {
            throw cancelled
        } catch (_: Throwable) {
            false
        }
        coroutineContext.ensureActive()
        onComplete(succeeded)
    }
    return BackgroundRefreshHandle(job)
}

internal suspend fun refreshBackgroundWeather(
    repository: WeatherDataSource,
    nowEpochSeconds: Long? = null,
    currentEpochSeconds: () -> Long = { Clock.System.now().epochSeconds },
    publishSnapshot: suspend (WeatherSnapshot) -> Unit
): BackgroundRefreshOutcome {
    val location = repository.activeLocation()
        ?: return BackgroundRefreshOutcome.NothingToRefresh
    return AutomaticRefreshCoordinator.withLocationLock(location.id) {
        refreshBackgroundWeatherForLocation(
            repository = repository,
            location = location,
            nowEpochSeconds = nowEpochSeconds ?: currentEpochSeconds(),
            publishSnapshot = publishSnapshot
        )
    }
}

private suspend fun refreshBackgroundWeatherForLocation(
    repository: WeatherDataSource,
    location: Location,
    nowEpochSeconds: Long,
    publishSnapshot: suspend (WeatherSnapshot) -> Unit
): BackgroundRefreshOutcome {
    val cachedSnapshot = try {
        repository.observe(location).first()
    } catch (cancelled: CancellationException) {
        throw cancelled
    } catch (error: Throwable) {
        return classifyBackgroundRefreshFailure(error)
    }
    if (cachedSnapshot != null && !cachedSnapshot.isAutomaticRefreshDue(nowEpochSeconds)) {
        return try {
            publishSnapshot(cachedSnapshot)
            BackgroundRefreshOutcome.NothingToRefresh
        } catch (cancelled: CancellationException) {
            throw cancelled
        } catch (error: Throwable) {
            classifyBackgroundRefreshFailure(error)
        }
    }
    if (!AutomaticRefreshCoordinator.claimAutomaticAttempt(location.id, nowEpochSeconds)) {
        if (cachedSnapshot == null) return BackgroundRefreshOutcome.NothingToRefresh
        return try {
            publishSnapshot(cachedSnapshot)
            BackgroundRefreshOutcome.NothingToRefresh
        } catch (cancelled: CancellationException) {
            throw cancelled
        } catch (error: Throwable) {
            classifyBackgroundRefreshFailure(error)
        }
    }
    val primaryOutcome = try {
        repository.refreshPrimary(location)
        BackgroundRefreshOutcome.Updated
    } catch (cancelled: CancellationException) {
        throw cancelled
    } catch (error: Throwable) {
        classifyBackgroundRefreshFailure(error)
    }

    if (primaryOutcome == BackgroundRefreshOutcome.Updated) {
        try {
            repository.refreshAirQuality(location)
        } catch (cancelled: CancellationException) {
            throw cancelled
        } catch (_: Throwable) {
            // Air quality is optional; a successful primary forecast remains useful.
        }
    }

    try {
        repository.observe(location).first()?.let { snapshot ->
            publishSnapshot(snapshot)
        }
    } catch (cancelled: CancellationException) {
        throw cancelled
    } catch (error: Throwable) {
        if (primaryOutcome == BackgroundRefreshOutcome.Updated) {
            return classifyBackgroundRefreshFailure(error)
        }
    }
    return primaryOutcome
}

internal fun classifyBackgroundRefreshFailure(error: Throwable): BackgroundRefreshOutcome = when {
    error.causeChain().any { it is SerializationException } -> {
        BackgroundRefreshOutcome.PermanentFailure
    }
    error.causeChain().filterIsInstance<ResponseException>().any { responseError ->
        responseError.response.status.value.isTransientHttpStatus()
    } -> {
        BackgroundRefreshOutcome.TransientFailure
    }
    error.causeChain().any { it is ResponseException } -> {
        BackgroundRefreshOutcome.PermanentFailure
    }
    error.causeChain().any { cause ->
        cause is HttpRequestTimeoutException ||
            cause is ConnectTimeoutException ||
            cause is SocketTimeoutException
    } -> {
        BackgroundRefreshOutcome.TransientFailure
    }
    isTransientPlatformNetworkFailure(error) -> BackgroundRefreshOutcome.TransientFailure
    else -> BackgroundRefreshOutcome.PermanentFailure
}

internal fun Int.isTransientHttpStatus(): Boolean = this in TRANSIENT_HTTP_CODES || this in 500..599

private fun Throwable.causeChain(): Sequence<Throwable> = sequence {
    val visited = mutableSetOf<Throwable>()
    var current: Throwable? = this@causeChain
    while (current != null && visited.add(current)) {
        yield(current)
        current = current.cause
    }
}

internal expect fun isTransientPlatformNetworkFailure(error: Throwable): Boolean

private val TRANSIENT_HTTP_CODES = setOf(408, 425, 429)
