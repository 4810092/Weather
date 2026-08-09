package uz.ganikhodjaev.weather.data.di

import androidx.lifecycle.ViewModelProvider
import dagger.Component
import uz.ganikhodjaev.weather.App
import uz.ganikhodjaev.weather.MainActivity

@AppScope
@Component(
    modules = [
        AppModule::class,
        NetworkModule::class,
        ViewModelModule::class,
    ]
)
interface AppComponent {
    fun inject(app: App)
    fun inject(mainActivity: MainActivity)

    fun getViewModelFactory(): ViewModelProvider.Factory
}