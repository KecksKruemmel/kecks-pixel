"""Builds Kecks Pixel (TTF), the specimen image and the release ZIP.

python build.py
"""
import shutil
import zipfile
from pathlib import Path

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

from glyphs import all_glyphs

FAMILY = "Kecks Pixel"
VERSION = "1.000"
AUTHOR = "KecksKruemmel"
P, R, EPS = 100, 26, 2
ROOT = Path(__file__).parent
OUT = ROOT / "out"
TTF = OUT / "KecksPixel-Regular.ttf"


def outline(rows, top_row):
    pen = TTGlyphPen(None)
    filled = lambda r, c: 0 <= r < len(rows) and 0 <= c < len(rows[r]) and rows[r][c] == "#"
    for r, line in enumerate(rows):
        for c, ch in enumerate(line):
            if ch != "#":
                continue
            row = r + top_row
            up, down, left, right = filled(r - 1, c), filled(r + 1, c), filled(r, c - 1), filled(r, c + 1)
            rounded = [not (down or left or filled(r + 1, c - 1)), not (up or left or filled(r - 1, c - 1)),
                       not (up or right or filled(r - 1, c + 1)), not (down or right or filled(r + 1, c + 1))]
            x0, x1 = c * P - EPS * left, (c + 1) * P + EPS * right
            y0, y1 = (6 - row) * P - EPS * down, (7 - row) * P + EPS * up
            corners = [(x0, y0), (x0, y1), (x1, y1), (x1, y0)]
            nodes = []
            for i, (cx, cy) in enumerate(corners):
                if not rounded[i]:
                    nodes.append(("on", (cx, cy)))
                    continue
                px, py = corners[i - 1]
                nx, ny = corners[(i + 1) % 4]
                step = lambda tx, ty: (cx + (tx > cx) * R - (tx < cx) * R, cy + (ty > cy) * R - (ty < cy) * R)
                nodes += [("on", step(px, py)), ("off", (cx, cy)), ("on", step(nx, ny))]
            pen.moveTo(nodes[0][1])
            i = 1
            while i < len(nodes):
                kind, pt = nodes[i]
                if kind == "off":
                    pen.qCurveTo(pt, nodes[(i + 1) % len(nodes)][1])
                    i += 2
                else:
                    pen.lineTo(pt)
                    i += 1
            pen.closePath()
    return pen.glyph()


def build():
    OUT.mkdir(exist_ok=True)
    glyphs = all_glyphs()
    name = lambda ch: f"uni{ord(ch):04X}"
    outlines = {".notdef": outline(["#####", "#...#", "#...#", "#...#", "#...#", "#...#", "#####"], 0),
                "space": TTGlyphPen(None).glyph()}
    advances = {".notdef": 600, "space": 400}
    for ch, (rows, top) in glyphs.items():
        outlines[name(ch)] = outline(rows, top)
        advances[name(ch)] = (max(len(r) for r in rows) + 1) * P
    fb = FontBuilder(1000, isTTF=True)
    fb.setupGlyphOrder(list(outlines))
    fb.setupCharacterMap({32: "space", 160: "space", **{ord(ch): name(ch) for ch in glyphs}})
    fb.setupGlyf(outlines)
    fb.setupHorizontalMetrics({g: (w, 0) for g, w in advances.items()})
    fb.setupHorizontalHeader(ascent=950, descent=-250, lineGap=0)
    fb.setupNameTable({
        "copyright": f"Copyright 2026 {AUTHOR}", "familyName": FAMILY, "styleName": "Regular",
        "uniqueFontIdentifier": f"KecksPixel-Regular;{VERSION}", "fullName": f"{FAMILY} Regular",
        "psName": "KecksPixel-Regular", "version": f"Version {VERSION}", "designer": AUTHOR,
        "licenseDescription": "This Font Software is licensed under the SIL Open Font License, Version 1.1.",
        "licenseInfoURL": "https://openfontlicense.org",
    })
    fb.setupOS2(sTypoAscender=950, sTypoDescender=-250, sTypoLineGap=0, usWinAscent=950, usWinDescent=250,
                sxHeight=500, sCapHeight=700, achVendID="KECK", fsType=0, usWeightClass=400)
    fb.setupPost()
    fb.font["head"].fontRevision = float(VERSION)
    fb.save(TTF)
    font = TTFont(TTF)
    assert all(ord(ch) in font.getBestCmap() for ch in glyphs) and font["name"].getDebugName(1) == FAMILY
    return glyphs


def specimen():
    img = Image.new("RGB", (1500, 820), (12, 9, 18))
    d = ImageDraw.Draw(img)
    f = lambda s: ImageFont.truetype(str(TTF), s)
    beige, lila, blau, orange = (232, 216, 189), (154, 128, 245), (90, 140, 255), (245, 155, 91)
    d.text((50, 40), "Kecks Pixel", font=f(120), fill=orange)
    d.text((54, 200), "free pixel font - SIL Open Font License", font=f(30), fill=beige)
    d.text((50, 280), "ABCDEFGHIJKLMNOPQRSTUVWXYZ ÄÖÜ", font=f(50), fill=(245, 242, 236))
    d.text((50, 370), "abcdefghijklmnopqrstuvwxyz äöüß", font=f(50), fill=(245, 242, 236))
    d.text((50, 460), "0123456789 .,:;!?-+=/()[]#%&*@<>€°", font=f(50), fill=lila)
    d.text((50, 570), "Bedwars mit den Jungs - GG!", font=f(60), fill=blau)
    d.text((50, 680), "The quick brown fox jumps over the lazy dog.", font=f(40), fill=beige)
    img.save(OUT / "specimen.png")


def package():
    shutil.copy2(TTF, ROOT / "docs" / "fonts" / TTF.name)
    zip_path = OUT / f"KecksPixel-v{VERSION}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(TTF, TTF.name)
        for extra in ("OFL.txt", "README.md"):
            z.write(ROOT / extra, extra)
        z.write(OUT / "specimen.png", "specimen.png")
    return zip_path


if __name__ == "__main__":
    print(len(build()), "glyphs")
    specimen()
    print(package())
