package uz.ganikhodjaev.weather.shared.data

import app.cash.sqldelight.driver.jdbc.sqlite.JdbcSqliteDriver
import java.nio.file.Files
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertNotNull
import kotlin.test.assertTrue
import uz.ganikhodjaev.weather.db.NimboDatabase

class ReleasedDatabaseMigrationTest {
    @Test
    fun migratesDatabaseCapturedFromReleasedSchemaOne() {
        val fixture = assertNotNull(
            javaClass.classLoader?.getResourceAsStream("databases/nimbo-v1.db"),
            "The released v1 database fixture must be packaged with host tests"
        )
        val databaseFile = Files.createTempFile("nimbo-v1-migration", ".db")
        fixture.use { input ->
            Files.copy(input, databaseFile, java.nio.file.StandardCopyOption.REPLACE_EXISTING)
        }

        val driver = JdbcSqliteDriver("jdbc:sqlite:$databaseFile")
        try {
            val beforeVersion = driver.executeQuery(
                identifier = null,
                sql = "PRAGMA user_version",
                mapper = { cursor ->
                    app.cash.sqldelight.db.QueryResult.Value(cursor.getLong(0)!!)
                },
                parameters = 0
            ).value
            assertEquals(1L, beforeVersion)

            NimboDatabase.Schema.migrate(driver, oldVersion = 1L, newVersion = 2L)
            val migrated = NimboDatabase(driver)

            val location =
                assertNotNull(migrated.weatherQueries.selectActiveLocation().executeAsOneOrNull())
            assertTrue(
                migrated.weatherQueries.selectTimeline(
                    location_id = location.id,
                    epoch_seconds = 0,
                    epoch_seconds_ = Long.MAX_VALUE
                ).executeAsList().isNotEmpty()
            )
            migrated.weatherQueries.upsertSetting("unit_preference", "Metric")
            assertEquals(
                "Metric",
                migrated.weatherQueries.selectSetting("unit_preference").executeAsOne()
            )
        } finally {
            driver.close()
            Files.deleteIfExists(databaseFile)
        }
    }
}
