"""Werbematerial für Kecks Pixel: nur eigene Schrift, eigene Farben, keine fremden Marken oder Musik.

python promo.py -> docs/social.png (Link-Vorschau), promo/insta_*.png, promo/kecks-pixel-9x16.mp4
"""
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent
TTF = ROOT / "out" / "KecksPixel-Regular.ttf"
PROMO = ROOT / "promo"
BG, INK = (12, 9, 18), (245, 242, 236)
BEIGE, LILA, BLAU, ORANGE = (232, 216, 189), (154, 128, 245), (90, 140, 255), (245, 155, 91)
URL = "keckskruemmel.github.io/kecks-pixel"


def font(size):
    return ImageFont.truetype(str(TTF), size)


def gradient_bar(d, x0, y0, x1, h):
    stops = [BLAU, LILA, ORANGE]
    for x in range(x0, x1):
        t = (x - x0) / max(1, x1 - x0 - 1) * (len(stops) - 1)
        i = min(int(t), len(stops) - 2)
        u = t - i
        c = tuple(round(a + (b - a) * u) for a, b in zip(stops[i], stops[i + 1]))
        d.line((x, y0, x, y0 + h), fill=c)


def pixel_grid(img, step, alpha=10):
    over = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(over)
    for x in range(0, img.size[0], step):
        d.line((x, 0, x, img.size[1]), fill=(255, 255, 255, alpha))
    for y in range(0, img.size[1], step):
        d.line((0, y, img.size[0], y), fill=(255, 255, 255, alpha))
    img.alpha_composite(over)


def centered(d, y, text, size, fill, w):
    f = font(size)
    tw = d.textlength(text, font=f)
    d.text(((w - tw) / 2, y), text, font=f, fill=fill)


def social():
    w, h = 1280, 640
    img = Image.new("RGBA", (w, h), BG + (255,))
    pixel_grid(img, 40)
    d = ImageDraw.Draw(img)
    centered(d, 150, "Kecks Pixel", 140, ORANGE, w)
    centered(d, 330, "FREE PIXEL FONT", 50, BEIGE, w)
    gradient_bar(d, 340, 420, 940, 8)
    centered(d, 470, "commercial use OK - SIL Open Font License", 30, LILA, w)
    centered(d, 540, URL, 30, BLAU, w)
    out = ROOT / "docs" / "social.png"
    img.convert("RGB").save(out)
    return out


def insta():
    PROMO.mkdir(exist_ok=True)
    slides = [
        [("Kecks Pixel", 150, ORANGE, 330), ("FREE PIXEL FONT", 60, BEIGE, 540), ("swipe ->", 40, LILA, 860)],
        [("ABCDEFGHIJKLM", 80, INK, 220), ("NOPQRSTUVWXYZ", 80, INK, 340), ("abcdefghijklm", 80, BEIGE, 500),
         ("nopqrstuvwxyz", 80, BEIGE, 620), ("ÄÖÜ äöüß € @ &", 70, LILA, 780)],
        [("Kostenlos.", 110, ORANGE, 300), ("Auch kommerziell.", 70, BEIGE, 470), ("SIL Open Font License", 46, LILA, 620),
         ("Link in Bio", 50, BLAU, 820)],
    ]
    paths = []
    for i, lines in enumerate(slides, 1):
        img = Image.new("RGBA", (1080, 1080), BG + (255,))
        pixel_grid(img, 40)
        d = ImageDraw.Draw(img)
        for text, size, col, y in lines:
            centered(d, y, text, size, col, 1080)
        gradient_bar(d, 140, 990, 940, 8)
        p = PROMO / f"insta_{i}.png"
        img.convert("RGB").save(p)
        paths.append(p)
    return paths


def video():
    """8 s, 30 fps, 1080x1920: Titel tippt sich ein, dann Alphabet und 'free to use'. Stumm - Musik in der App aus deren Lizenz-Bibliothek wählen."""
    PROMO.mkdir(exist_ok=True)
    frames = PROMO / "frames"
    frames.mkdir(exist_ok=True)
    w, h, fps, total = 1080, 1920, 30, 240
    title = "KECKS PIXEL"
    for f in range(total):
        img = Image.new("RGBA", (w, h), BG + (255,))
        pixel_grid(img, 60, 8)
        d = ImageDraw.Draw(img)
        n = min(len(title), f // 4)
        cursor = "_" if (f // 8) % 2 == 0 and f < 90 else ""
        centered(d, 560, title[:n] + cursor, 130, ORANGE, w)
        if f > 60:
            k = min(1.0, (f - 60) / 20)
            gradient_bar(d, 140, 760, 140 + int(800 * k), 10)
        if f > 80:
            centered(d, 860, "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[: (f - 80) // 2], 54, INK, w)
        if f > 120:
            centered(d, 960, "abcdefghijklmnopqrstuvwxyz"[: (f - 120) // 2], 54, BEIGE, w)
        if f > 170:
            centered(d, 1160, "FREE TO USE", 100, LILA, w)
        if f > 200:
            centered(d, 1320, "auch kommerziell - Link in Bio", 44, BLAU, w)
        img.convert("RGB").save(frames / f"f_{f:04d}.png")
    out = PROMO / "kecks-pixel-9x16.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-i", str(frames / "f_%04d.png"),
                    "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", str(out)], check=True)
    for p in frames.glob("*.png"):
        p.unlink()
    frames.rmdir()
    return out


if __name__ == "__main__":
    print(social())
    print(*insta(), sep="\n")
    print(video())
