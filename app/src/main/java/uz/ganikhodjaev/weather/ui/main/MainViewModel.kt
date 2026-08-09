package uz.ganikhodjaev.weather.ui.main

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.launch
import uz.ganikhodjaev.weather.data.model.WeatherDataModel
import uz.ganikhodjaev.weather.data.repository.WeatherRepository
import javax.inject.Inject

class MainViewModel @Inject constructor(private val weatherRepository: WeatherRepository) :
    ViewModel() {

    private val _weatherEvent = MutableSharedFlow<WeatherDataModel>()
    val weatherEvent: SharedFlow<WeatherDataModel> = _weatherEvent


    init {
        getData()
    }

    fun getData() {
        viewModelScope.launch {
            runCatching {
                weatherRepository.getWeatherData()
            }.onSuccess {
                _weatherEvent.emit(it)
            }.onFailure {
it.toString()
            }
        }
    }

}