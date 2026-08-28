package uz.ganikhodjaev.weather.shared

internal interface StoreLinkProvider {
    val storeUrl: String
}

internal expect fun createStoreLinkProvider(platformContext: PlatformContext): StoreLinkProvider

internal object NimboStoreLinks {
    const val GOOGLE_PLAY =
        "https://play.google.com/store/apps/details?id=uz.ganikhodjaev.weather"
    const val APP_STORE = "https://apps.apple.com/app/id6799886897"
}

internal fun formatShareMessage(
    weatherSummary: String,
    storeCallToAction: String,
    storeUrl: String
): String = listOf(weatherSummary.trim(), storeCallToAction.trim(), storeUrl.trim())
    .filter(String::isNotBlank)
    .joinToString("\n")
