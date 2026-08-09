package uz.ganikhodjaev.weather.data.mapper

import uz.ganikhodjaev.weather.data.dto.CityDto
import uz.ganikhodjaev.weather.data.dto.CloudsDto
import uz.ganikhodjaev.weather.data.dto.CoordDto
import uz.ganikhodjaev.weather.data.dto.ListDto
import uz.ganikhodjaev.weather.data.dto.MainDto
import uz.ganikhodjaev.weather.data.dto.SysDto
import uz.ganikhodjaev.weather.data.dto.WeatherDataDto
import uz.ganikhodjaev.weather.data.dto.WeatherDto
import uz.ganikhodjaev.weather.data.dto.WindDto
import uz.ganikhodjaev.weather.data.model.CityModel
import uz.ganikhodjaev.weather.data.model.CloudsModel
import uz.ganikhodjaev.weather.data.model.CoordModel
import uz.ganikhodjaev.weather.data.model.ListModel
import uz.ganikhodjaev.weather.data.model.MainModel
import uz.ganikhodjaev.weather.data.model.SysModel
import uz.ganikhodjaev.weather.data.model.WeatherDataModel
import uz.ganikhodjaev.weather.data.model.WeatherModel
import uz.ganikhodjaev.weather.data.model.WindModel
import javax.inject.Inject

class MainMapper @Inject constructor() {
    fun fromDto(dto: MainDto?): MainModel? {
        return dto?.let {
            MainModel(
                temp = it.temp,
                feelsLike = it.feelsLike,
                tempMin = it.tempMin,
                tempMax = it.tempMax,
                pressure = it.pressure,
                seaLevel = it.seaLevel,
                grndLevel = it.grndLevel,
                humidity = it.humidity,
                tempKf = it.tempKf
            )
        }
    }
}

class WeatherMapper @Inject constructor() {
    fun fromDto(dto: WeatherDto?): WeatherModel? {
        return dto?.let {
            WeatherModel(
                id = it.id, main = it.main, description = it.description, icon = it.icon
            )
        }
    }
}

class CloudsMapper @Inject constructor() {
    fun fromDto(dto: CloudsDto?): CloudsModel? {
        return dto?.let {
            CloudsModel(
                all = it.all
            )
        }
    }
}

class WindMapper @Inject constructor() {
    fun fromDto(dto: WindDto?): WindModel? {
        return dto?.let {
            WindModel(
                speed = it.speed, deg = it.deg, gust = it.gust
            )
        }
    }
}

class SysMapper @Inject constructor() {
    fun fromDto(dto: SysDto?): SysModel? {
        return dto?.let {
            SysModel(
                pod = it.pod
            )
        }
    }
}

class CoordMapper @Inject constructor() {
    fun fromDto(dto: CoordDto?): CoordModel? {
        return dto?.let {
            CoordModel(
                lat = it.lat, lon = it.lon
            )
        }
    }
}

class CityMapper @Inject constructor(private val coordMapper: CoordMapper) {
    fun fromDto(dto: CityDto?): CityModel? {
        return dto?.let {
            CityModel(
                id = it.id,
                name = it.name,
                coord = coordMapper.fromDto(it.coord),
                country = it.country,
                population = it.population,
                timezone = it.timezone,
                sunrise = it.sunrise,
                sunset = it.sunset
            )
        }
    }
}

class ListMapper @Inject constructor(
    private val mainMapper: MainMapper,
    private val weatherMapper: WeatherMapper,
    private val cloudsMapper: CloudsMapper,
    private val windMapper: WindMapper,
    private val sysMapper: SysMapper,
) {
    fun fromDto(dto: ListDto?): ListModel? {
        return dto?.let {
            ListModel(
                dt = it.dt,
                main = mainMapper.fromDto(it.main),
                weather = it.weather?.mapNotNull { weatherDto -> weatherMapper.fromDto(weatherDto) },
                clouds = cloudsMapper.fromDto(it.clouds),
                wind = windMapper.fromDto(it.wind),
                visibility = it.visibility,
                pop = it.pop,
                sys = sysMapper.fromDto(it.sys),
                dtTxt = it.dtTxt
            )
        }
    }
}

class WeatherDataMapper @Inject constructor(
    private val listMapper: ListMapper, private val cityMapper: CityMapper
) {
    fun fromDto(dto: WeatherDataDto): WeatherDataModel {
        return WeatherDataModel(
            cod = dto.cod,
            message = dto.message,
            cnt = dto.cnt,
            listData = dto.listData?.mapNotNull { listDto -> listMapper.fromDto(listDto) },
            city = cityMapper.fromDto(dto.city)
        )
    }
}
