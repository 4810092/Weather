package uz.ganikhodjaev.weather.shared.data

import io.ktor.client.HttpClient
import io.ktor.client.engine.mock.MockEngine
import io.ktor.client.engine.mock.respond
import io.ktor.http.ContentType
import io.ktor.http.HttpHeaders
import io.ktor.http.headersOf
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue
import kotlinx.coroutines.runBlocking

class OpenMeteoServiceTest {
    @Test
    fun unicodeQueryUsesNormalizedRequestedLanguageAndMapsLocalizedResult() = runBlocking {
        val (service, requests) = recordingService {
            cityResponse(name = "Москва", country = "Россия")
        }

        val results = service.searchCities("  Москва ", "RU")

        assertEquals(listOf(SearchRequest("Москва", "ru")), requests)
        assertEquals("Москва", results.single().name)
        assertEquals("Россия", results.single().country)
    }

    @Test
    fun emptyLocalizedResponseFallsBackToEnglish() = runBlocking {
        val (service, requests) = recordingService { language ->
            if (language == "ru") EMPTY_RESPONSE else cityResponse("Moscow", "Russia")
        }

        val results = service.searchCities("Moscow", "ru")

        assertEquals(
            listOf(SearchRequest("Moscow", "ru"), SearchRequest("Moscow", "en")),
            requests
        )
        assertEquals("Moscow", results.single().name)
    }

    @Test
    fun emptyEnglishResponseDoesNotRetry() = runBlocking {
        val (service, requests) = recordingService { EMPTY_RESPONSE }

        val results = service.searchCities("Nowhere", "en")

        assertTrue(results.isEmpty())
        assertEquals(listOf(SearchRequest("Nowhere", "en")), requests)
    }

    @Test
    fun twoEmptyResponsesReturnNoMatches() = runBlocking {
        val (service, requests) = recordingService { EMPTY_RESPONSE }

        val results = service.searchCities("غير موجود", "ar")

        assertTrue(results.isEmpty())
        assertEquals(
            listOf(SearchRequest("غير موجود", "ar"), SearchRequest("غير موجود", "en")),
            requests
        )
    }

    private fun recordingService(
        responseForLanguage: (String) -> String
    ): Pair<OpenMeteoService, MutableList<SearchRequest>> {
        val requests = mutableListOf<SearchRequest>()
        val engine = MockEngine { request ->
            val language = request.url.parameters["language"].orEmpty()
            requests += SearchRequest(
                query = request.url.parameters["name"].orEmpty(),
                language = language
            )
            respond(
                content = responseForLanguage(language),
                headers = headersOf(
                    HttpHeaders.ContentType,
                    ContentType.Application.Json.toString()
                )
            )
        }
        return OpenMeteoService(HttpClient(engine)) to requests
    }

    private fun cityResponse(name: String, country: String): String =
        """
        {
          "results": [
            {
              "id": 524901,
              "name": "$name",
              "latitude": 55.75204,
              "longitude": 37.61781,
              "timezone": "Europe/Moscow",
              "country_code": "RU",
              "country": "$country"
            }
          ]
        }
        """.trimIndent()

    private data class SearchRequest(val query: String, val language: String)

    private companion object {
        const val EMPTY_RESPONSE = "{\"results\":[]}"
    }
}
