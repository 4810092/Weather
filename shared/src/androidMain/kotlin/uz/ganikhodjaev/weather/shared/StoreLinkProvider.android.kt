package uz.ganikhodjaev.weather.shared

internal actual fun createStoreLinkProvider(platformContext: PlatformContext): StoreLinkProvider =
    object : StoreLinkProvider {
        override val storeUrl: String = NimboStoreLinks.GOOGLE_PLAY
        override val reviewUrl: String = NimboStoreLinks.GOOGLE_PLAY_REVIEW
    }
