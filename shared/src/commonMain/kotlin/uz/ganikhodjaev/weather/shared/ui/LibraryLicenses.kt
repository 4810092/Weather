package uz.ganikhodjaev.weather.shared.ui

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeDrawingPadding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.text.selection.SelectionContainer
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.semantics.heading
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.dp
import org.jetbrains.compose.resources.ExperimentalResourceApi
import org.jetbrains.compose.resources.stringResource
import uz.ganikhodjaev.weather.shared.resources.Res
import uz.ganikhodjaev.weather.shared.resources.back
import uz.ganikhodjaev.weather.shared.resources.open_source_licenses

@OptIn(ExperimentalResourceApi::class)
@Composable
internal fun LibraryLicenses(onBack: () -> Unit) {
    var sections by remember { mutableStateOf(emptyList<String>()) }
    LaunchedEffect(Unit) {
        sections = Res.readBytes("files/licenses/notices.txt")
            .decodeToString()
            .split('\u000c')
            .flatMap { section -> section.trim().chunked(6000) }
    }
    Column(
        modifier = Modifier.fillMaxSize().safeDrawingPadding().padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        GlassButton(onClick = onBack) {
            Text(stringResource(Res.string.back))
        }
        Text(
            text = stringResource(Res.string.open_source_licenses),
            style = MaterialTheme.typography.headlineSmall,
            modifier = Modifier.semantics { heading() }
        )
        LazyColumn(
            modifier = Modifier.fillMaxWidth().weight(1f),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            items(sections) { section ->
                SelectionContainer {
                    Text(
                        text = section,
                        style = MaterialTheme.typography.bodySmall,
                        modifier = Modifier.fillMaxWidth().nimboGlass().padding(16.dp)
                    )
                }
            }
        }
    }
}
