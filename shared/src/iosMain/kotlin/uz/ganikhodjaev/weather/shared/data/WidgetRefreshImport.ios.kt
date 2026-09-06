package uz.ganikhodjaev.weather.shared.data

import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.contentOrNull
import kotlinx.serialization.json.doubleOrNull
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import kotlinx.serialization.json.longOrNull
import kotlinx.serialization.json.put
import uz.ganikhodjaev.weather.shared.WidgetRefreshInterop

internal actual suspend fun importPendingWidgetRefreshFromPlatform(
    repository: WeatherRepository
): Boolean {
    val pending = requestPending() ?: return false
    val imported = repository.importWidgetRefresh(pending.payload)
    if (!imported) return false
    return acknowledge(pending)
}

private fun requestPending(): PendingDelivery? = try {
    val request = WIDGET_IMPORT_JSON.encodeToString(
        JsonObject.serializer(),
        JsonObject(mapOf("op" to kotlinx.serialization.json.JsonPrimitive("pending")))
    )
    val response = WidgetRefreshInterop.exchange(request)
        ?.let { WIDGET_IMPORT_JSON.parseToJsonElement(it).jsonObject }
        ?: return null
    val pending = response["pending"]?.takeUnless { it is kotlinx.serialization.json.JsonNull }
        ?.jsonObject ?: return null
    val config = pending["config"]?.jsonObject ?: return null
    val payload = WidgetRefreshImportPayload(
        deliveryId = pending.string("deliveryId") ?: return null,
        locationId = config.string("id") ?: return null,
        latitude = config.double("latitude") ?: return null,
        longitude = config.double("longitude") ?: return null,
        fetchedAtEpochSeconds = pending.long("fetchedAt") ?: return null,
        forecast = pending.string("forecast") ?: return null,
        airQuality = pending.string("airQuality"),
        airQualityFetchedAtEpochSeconds = pending.long("airQualityFetchedAt")
    )
    PendingDelivery(payload, pending.string("revision") ?: return null)
} catch (_: Throwable) {
    null
}

private fun acknowledge(delivery: PendingDelivery): Boolean = try {
    val response = WidgetRefreshInterop.exchange(
        WIDGET_IMPORT_JSON.encodeToString(
            JsonObject.serializer(),
            kotlinx.serialization.json.buildJsonObject {
                put("op", "acknowledge")
                put("revision", delivery.revision)
                put("fetchedAt", delivery.payload.fetchedAtEpochSeconds)
                put("deliveryId", delivery.payload.deliveryId)
            }
        )
    )?.let { WIDGET_IMPORT_JSON.parseToJsonElement(it).jsonObject }
    response?.get("ok")?.jsonPrimitive?.content == "true"
} catch (_: Throwable) {
    false
}

private data class PendingDelivery(val payload: WidgetRefreshImportPayload, val revision: String)

private fun JsonObject.string(name: String): String? = this[name]?.jsonPrimitive?.contentOrNull

private fun JsonObject.long(name: String): Long? = this[name]?.jsonPrimitive?.longOrNull

private fun JsonObject.double(name: String): Double? = this[name]?.jsonPrimitive?.doubleOrNull

private val WIDGET_IMPORT_JSON = Json { ignoreUnknownKeys = true }
