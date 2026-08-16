package uz.ganikhodjaev.weather.shared

import android.content.Intent

internal actual fun shareText(platformContext: PlatformContext, text: String) {
    val intent = Intent(Intent.ACTION_SEND).apply {
        type = "text/plain"
        putExtra(Intent.EXTRA_TEXT, text)
    }
    platformContext.requireActivity().startActivity(Intent.createChooser(intent, null))
}
