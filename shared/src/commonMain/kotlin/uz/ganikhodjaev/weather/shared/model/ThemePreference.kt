package uz.ganikhodjaev.weather.shared.model

internal enum class ThemePreference {
    System,
    Light,
    Dark;

    fun resolve(systemIsDark: Boolean): Boolean = when (this) {
        System -> systemIsDark
        Light -> false
        Dark -> true
    }

    companion object {
        fun fromStoredValue(value: String?): ThemePreference =
            entries.firstOrNull { it.name == value } ?: System
    }
}
