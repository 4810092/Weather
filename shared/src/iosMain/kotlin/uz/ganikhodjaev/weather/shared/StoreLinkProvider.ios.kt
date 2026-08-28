package uz.ganikhodjaev.weather.shared

internal actual fun createStoreLinkProvider(platformContext: PlatformContext): StoreLinkProvider =
    object : StoreLinkProvider {
        override val storeUrl: String = NimboStoreLinks.APP_STORE
    }
