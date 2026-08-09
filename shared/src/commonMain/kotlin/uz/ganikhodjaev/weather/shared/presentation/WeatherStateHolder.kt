package uz.ganikhodjaev.weather.shared.presentation

import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Job
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import uz.ganikhodjaev.weather.shared.data.WeatherRepository
import uz.ganikhodjaev.weather.shared.model.WeatherSnapshot

internal sealed interface WeatherUiState {
    data object Loading : WeatherUiState
    data class Content(
        val weather: WeatherSnapshot,
        val isRefreshing: Boolean,
        val refreshMessage: String? = null,
    ) : WeatherUiState
    data class EmptyError(val message: String) : WeatherUiState
}

internal class WeatherStateHolder(
    private val repository: WeatherRepository,
    private val scope: CoroutineScope,
) {
    private val mutableState = MutableStateFlow<WeatherUiState>(WeatherUiState.Loading)
    val state: StateFlow<WeatherUiState> = mutableState.asStateFlow()

    private var observationJob: Job? = null
    private var activeLocationId: String? = null

    fun start() {
        if (observationJob != null) return
        scope.launch {
            val location = repository.ensureActiveLocation()
            activeLocationId = location.id
            observationJob = launch {
                repository.observe(location).collect { weather ->
                    if (weather != null) {
                        val old = mutableState.value as? WeatherUiState.Content
                        mutableState.value = WeatherUiState.Content(
                            weather = weather,
                            isRefreshing = old?.isRefreshing ?: false,
                            refreshMessage = old?.refreshMessage,
                        )
                    }
                }
            }
            refreshInternal(location)
        }
    }

    fun refresh() {
        scope.launch {
            refreshInternal(repository.ensureActiveLocation())
        }
    }

    private suspend fun refreshInternal(location: uz.ganikhodjaev.weather.shared.model.Location) {
        val current = mutableState.value
        if (current is WeatherUiState.Content) {
            mutableState.value = current.copy(isRefreshing = true, refreshMessage = null)
        }
        try {
            repository.refresh(location)
            val updated = mutableState.value
            if (updated is WeatherUiState.Content) {
                mutableState.value = updated.copy(isRefreshing = false, refreshMessage = null)
            }
        } catch (_: Throwable) {
            val cached = mutableState.value
            mutableState.value = if (cached is WeatherUiState.Content) {
                cached.copy(
                    isRefreshing = false,
                    refreshMessage = "Couldn't refresh. Showing saved weather.",
                )
            } else {
                WeatherUiState.EmptyError(
                    "Weather is unavailable. Check your connection and try again.",
                )
            }
        }
    }
}
