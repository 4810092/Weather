import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.URL;
import javax.net.ssl.HttpsURLConnection;

/** Standalone diagnostic probe executed with Android app_process; not product code. */
public final class TlsProbe {
    public static void main(String[] args) {
        if (args.length == 0) {
            System.err.println("usage: TlsProbe <https-url> [<https-url> ...]");
            System.exit(2);
        }
        for (String value : args) {
            System.out.println("URL=" + value);
            try {
                HttpsURLConnection connection =
                    (HttpsURLConnection) new URL(value).openConnection();
                connection.setConnectTimeout(8000);
                connection.setReadTimeout(15000);
                connection.setInstanceFollowRedirects(true);
                int status = connection.getResponseCode();
                System.out.println("STATUS=" + status);
                BufferedReader reader = new BufferedReader(
                    new InputStreamReader(connection.getInputStream()));
                String line = reader.readLine();
                int previewLength = line == null ? 0 : Math.min(200, line.length());
                System.out.println(
                    "FIRST_LINE=" + (line == null ? "<null>" : line.substring(0, previewLength))
                );
                reader.close();
                connection.disconnect();
            } catch (Throwable error) {
                System.out.println("ERROR=" + error.getClass().getName());
                error.printStackTrace(System.out);
            }
        }
    }
}
