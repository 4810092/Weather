package uz.ganikhodjaev.weather.data.di

import android.content.Context
import com.google.gson.Gson
import dagger.Module
import dagger.Provides
import uz.ganikhodjaev.weather.App

@Module
class AppModule(private val application: App) {

    @Provides
    @AppScope
    fun provideApp(): App = application

    @Provides
    @AppScope
    fun provideApplicationContext(): Context = application


    @Provides
    @AppScope
    fun provideGson(): Gson {
        return Gson()
    }

}