import java.awt.AlphaComposite;
import java.awt.Graphics2D;
import java.awt.RenderingHints;
import java.awt.geom.Ellipse2D;
import java.awt.geom.RoundRectangle2D;
import java.awt.image.BufferedImage;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.LinkedHashMap;
import java.util.Map;
import javax.imageio.ImageIO;

/** Generates the pre-Android-8 launcher resources from the canonical Nimbo icon. */
public final class GenerateAndroidLegacyIcons {
    private static final Path ROOT = Path.of("").toAbsolutePath().normalize();
    private static final Path SOURCE =
            ROOT.resolve("branding/store/nimbo-app-icon-1024.png");
    private static final Map<String, Integer> DENSITIES = new LinkedHashMap<>();

    static {
        DENSITIES.put("mdpi", 48);
        DENSITIES.put("hdpi", 72);
        DENSITIES.put("xhdpi", 96);
        DENSITIES.put("xxhdpi", 144);
        DENSITIES.put("xxxhdpi", 192);
    }

    private GenerateAndroidLegacyIcons() {}

    public static void main(String[] arguments) throws Exception {
        boolean check = arguments.length == 1 && "--check".equals(arguments[0]);
        if (arguments.length > 1 || (arguments.length == 1 && !check)) {
            throw new IllegalArgumentException("usage: java scripts/GenerateAndroidLegacyIcons.java [--check]");
        }

        BufferedImage source = readImage(SOURCE);
        if (source.getWidth() != 1024 || source.getHeight() != 1024) {
            throw new IllegalStateException("canonical Nimbo icon must be 1024 x 1024");
        }

        for (Map.Entry<String, Integer> density : DENSITIES.entrySet()) {
            Path directory = ROOT.resolve("app/src/main/res/mipmap-" + density.getKey());
            BufferedImage square = render(source, density.getValue(), false);
            BufferedImage round = render(source, density.getValue(), true);
            writeOrCheck(directory.resolve("ic_launcher.png"), square, check);
            writeOrCheck(directory.resolve("ic_launcher_round.png"), round, check);
        }
    }

    private static BufferedImage render(BufferedImage source, int size, boolean round) {
        BufferedImage output = new BufferedImage(size, size, BufferedImage.TYPE_INT_ARGB);
        Graphics2D graphics = output.createGraphics();
        try {
            graphics.setComposite(AlphaComposite.Src);
            graphics.setRenderingHint(
                    RenderingHints.KEY_ANTIALIASING,
                    RenderingHints.VALUE_ANTIALIAS_ON);
            graphics.setRenderingHint(
                    RenderingHints.KEY_INTERPOLATION,
                    RenderingHints.VALUE_INTERPOLATION_BICUBIC);
            graphics.setRenderingHint(
                    RenderingHints.KEY_RENDERING,
                    RenderingHints.VALUE_RENDER_QUALITY);
            double inset = 0.5;
            if (round) {
                graphics.setClip(new Ellipse2D.Double(inset, inset, size - 1.0, size - 1.0));
            } else {
                double radius = size * 0.18;
                graphics.setClip(
                        new RoundRectangle2D.Double(
                                inset,
                                inset,
                                size - 1.0,
                                size - 1.0,
                                radius,
                                radius));
            }
            graphics.drawImage(source, 0, 0, size, size, null);
        } finally {
            graphics.dispose();
        }
        return output;
    }

    private static BufferedImage readImage(Path path) throws IOException {
        BufferedImage image = ImageIO.read(path.toFile());
        if (image == null) {
            throw new IOException("cannot decode image: " + path);
        }
        return image;
    }

    private static void writeOrCheck(Path path, BufferedImage expected, boolean check)
            throws IOException {
        if (!check) {
            Files.createDirectories(path.getParent());
            if (!ImageIO.write(expected, "png", path.toFile())) {
                throw new IOException("PNG writer unavailable for " + path);
            }
            return;
        }

        BufferedImage actual = readImage(path);
        if (actual.getWidth() != expected.getWidth() || actual.getHeight() != expected.getHeight()) {
            throw new IllegalStateException("legacy launcher dimensions differ: " + path);
        }
        for (int y = 0; y < expected.getHeight(); y++) {
            for (int x = 0; x < expected.getWidth(); x++) {
                if (actual.getRGB(x, y) != expected.getRGB(x, y)) {
                    throw new IllegalStateException(
                            "legacy launcher pixels differ from canonical artwork: " + path);
                }
            }
        }
    }
}
