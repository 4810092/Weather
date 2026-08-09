package uz.ganikhodjaev.weather.data.model


data class MainModel(
    val temp: Double?,
    val feelsLike: Double?,
    val tempMin: Double?,
    val tempMax: Double?,
    val pressure: Int?,
    val seaLevel: Int?,
    val grndLevel: Int?,
    val humidity: Int?,
    val tempKf: Double?
)

data class WeatherModel(
    val id: Int?,
    val main: String?,
    val description: String?,
    val icon: String?
)

data class CloudsModel(
    val all: Int?
)

data class WindModel(
    val speed: Double?,
    val deg: Int?,
    val gust: Double?
)

data class SysModel(
    val pod: String?
)

data class CoordModel(
    val lat: Double?,
    val lon: Double?
)

data class CityModel(
    val id: Int?,
    val name: String?,
    val coord: CoordModel?,
    val country: String?,
    val population: Int?,
    val timezone: Int?,
    val sunrise: Long?,
    val sunset: Long?
)

data class ListModel(
    val dt: Long?,
    val main: MainModel?,
    val weather: List<WeatherModel>?,
    val clouds: CloudsModel?,
    val wind: WindModel?,
    val visibility: Int?,
    val pop: Float?,
    val sys: SysModel?,
    val dtTxt: String?
)

data class WeatherDataModel(
    val cod: String?,
    val message: Int?,
    val cnt: Int?,
    val listData: List<ListModel>?,
    val city: CityModel?
)
