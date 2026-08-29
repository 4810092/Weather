package uz.ganikhodjaev.weather.shared

internal interface StoreLinkProvider {
    val storeUrl: String
    val reviewUrl: String
}

internal expect fun createStoreLinkProvider(platformContext: PlatformContext): StoreLinkProvider

internal object NimboStoreLinks {
    const val GOOGLE_PLAY =
        "https://play.google.com/store/apps/details?id=uz.ganikhodjaev.weather"
    const val APP_STORE = "https://apps.apple.com/app/id6799886897"
    const val GOOGLE_PLAY_REVIEW = GOOGLE_PLAY
    const val APP_STORE_REVIEW = "$APP_STORE?action=write-review"
}

internal object NimboPublicLinks {
    const val SUPPORT = "https://nimbo.uz/support/"
}

internal fun formatShareMessage(
    weatherSummary: String,
    storeCallToAction: String,
    storeUrl: String
): String = listOf(weatherSummary.trim(), storeCallToAction.trim(), storeUrl.trim())
    .filter(String::isNotBlank)
    .joinToString("\n")
