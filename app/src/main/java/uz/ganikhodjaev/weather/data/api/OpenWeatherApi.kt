package uz.ganikhodjaev.weather.data.api

import retrofit2.Response
import retrofit2.http.GET
import retrofit2.http.Url
import uz.ganikhodjaev.weather.data.dto.WeatherDataDto


interface OpenWeatherApi {

    @GET
    suspend fun getWeather(
        @Url url: String = "https://api.openweathermap.org/data/2.5/forecast?lat=41.3374468&lon=69.2928337&units=metric&appid=3d94d6fd6c0627d780d57ad67e7ca6d0"
    ): Response<WeatherDataDto>

//    https://api.openweathermap.org/data/2.5/forecast?lat=41.3374468&lon=69.2928337&appid=3d94d6fd6c0627d780d57ad67e7ca6d0
}