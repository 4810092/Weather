package uz.ganikhodjaev.weather.shared.data

import io.ktor.client.HttpClient

internal expect fun createPlatformHttpClient(): HttpClient
