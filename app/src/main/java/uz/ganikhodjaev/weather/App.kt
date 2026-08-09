package uz.ganikhodjaev.weather

import android.app.Application
import uz.ganikhodjaev.weather.data.di.AppComponent
import uz.ganikhodjaev.weather.data.di.AppModule
import uz.ganikhodjaev.weather.data.di.DaggerAppComponent

class App : Application() {


    companion object {
        lateinit var appComponent: AppComponent
            private set

    }


    override fun onCreate() {
        super.onCreate()

        appComponent = DaggerAppComponent.builder().appModule(AppModule(this)).build()
        appComponent.inject(this)


    }

}
