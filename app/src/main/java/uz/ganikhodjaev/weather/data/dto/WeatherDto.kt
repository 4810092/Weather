package uz.ganikhodjaev.weather.data.dto

import com.google.gson.annotations.SerializedName


data class MainDto(
    @SerializedName("temp") val temp: Double?,
    @SerializedName("feels_like") val feelsLike: Double?,
    @SerializedName("temp_min") val tempMin: Double?,
    @SerializedName("temp_max") val tempMax: Double?,
    @SerializedName("pressure") val pressure: Int?,
    @SerializedName("sea_level") val seaLevel: Int?,
    @SerializedName("grnd_level") val grndLevel: Int?,
    @SerializedName("humidity") val humidity: Int?,
    @SerializedName("temp_kf") val tempKf: Double?
)

data class WeatherDto(
    @SerializedName("id") val id: Int?,
    @SerializedName("main") val main: String?,
    @SerializedName("description") val description: String?,
    @SerializedName("icon") val icon: String?
)

data class CloudsDto(
    @SerializedName("all") val all: Int?
)

data class WindDto(
    @SerializedName("speed") val speed: Double?,
    @SerializedName("deg") val deg: Int?,
    @SerializedName("gust") val gust: Double?
)

data class SysDto(
    @SerializedName("pod") val pod: String?
)

data class CoordDto(
    @SerializedName("lat") val lat: Double?,
    @SerializedName("lon") val lon: Double?
)

data class CityDto(
    @SerializedName("id") val id: Int?,
    @SerializedName("name") val name: String?,
    @SerializedName("coord") val coord: CoordDto?,
    @SerializedName("country") val country: String?,
    @SerializedName("population") val population: Int?,
    @SerializedName("timezone") val timezone: Int?,
    @SerializedName("sunrise") val sunrise: Long?,
    @SerializedName("sunset") val sunset: Long?
)

data class ListDto(
    @SerializedName("dt") val dt: Long?,
    @SerializedName("main") val main: MainDto?,
    @SerializedName("weather") val weather: List<WeatherDto>?,
    @SerializedName("clouds") val clouds: CloudsDto?,
    @SerializedName("wind") val wind: WindDto?,
    @SerializedName("visibility") val visibility: Int?,
    @SerializedName("pop") val pop: Float?,
    @SerializedName("sys") val sys: SysDto?,
    @SerializedName("dt_txt") val dtTxt: String?
)

data class WeatherDataDto(
    @SerializedName("cod") val cod: String?,
    @SerializedName("message") val message: Int?,
    @SerializedName("cnt") val cnt: Int?,
    @SerializedName("list") val listData: List<ListDto>?,
    @SerializedName("city") val city: CityDto?
)
