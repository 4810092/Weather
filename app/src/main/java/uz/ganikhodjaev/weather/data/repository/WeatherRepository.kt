package uz.ganikhodjaev.weather.data.repository

import retrofit2.Response
import uz.ganikhodjaev.weather.data.api.OpenWeatherApi
import uz.ganikhodjaev.weather.data.mapper.WeatherDataMapper
import uz.ganikhodjaev.weather.data.model.WeatherDataModel
import javax.inject.Inject

class WeatherRepository @Inject constructor(
    private val openWeatherApi: OpenWeatherApi, private val weatherDataMapper: WeatherDataMapper
) {

    suspend fun getWeatherData(): WeatherDataModel {
        val response = openWeatherApi.getWeather()
        val data = checkResult(response)
        return weatherDataMapper.fromDto(data)
    }


    private fun <T> checkResult(response: Response<T>): T {
        return response.body() ?: parseError(response)
    }

    private fun <T> parseError(response: Response<T>): Nothing {

        throw IllegalArgumentException()


    }

}