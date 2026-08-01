from pathlib import Path
import hashlib
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib


ROOT = Path(__file__).resolve().parents[1]
LOGO = ROOT / "public/assets/logo.png"


def decode_rgba_png(path):
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise AssertionError("logo must be a PNG")

    offset = 8
    compressed = bytearray()
    width = height = color_type = bit_depth = None
    while offset < len(data):
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        kind = data[offset + 4 : offset + 8]
        payload = data[offset + 8 : offset + 8 + length]
        offset += 12 + length
        if kind == b"IHDR":
            width, height, bit_depth, color_type = struct.unpack(">IIBB", payload[:10])
        elif kind == b"IDAT":
            compressed.extend(payload)
        elif kind == b"IEND":
            break

    if (bit_depth, color_type) != (8, 6):
        raise AssertionError("logo must use 8-bit RGBA pixels")

    raw = zlib.decompress(compressed)
    stride = width * 4
    rows = []
    previous = bytearray(stride)
    cursor = 0
    for _ in range(height):
        filter_type = raw[cursor]
        cursor += 1
        encoded = raw[cursor : cursor + stride]
        cursor += stride
        row = bytearray(stride)
        for index, value in enumerate(encoded):
            left = row[index - 4] if index >= 4 else 0
            above = previous[index]
            upper_left = previous[index - 4] if index >= 4 else 0
            if filter_type == 0:
                predictor = 0
            elif filter_type == 1:
                predictor = left
            elif filter_type == 2:
                predictor = above
            elif filter_type == 3:
                predictor = (left + above) // 2
            elif filter_type == 4:
                p = left + above - upper_left
                distances = (abs(p - left), abs(p - above), abs(p - upper_left))
                predictor = (left, above, upper_left)[distances.index(min(distances))]
            else:
                raise AssertionError(f"unsupported PNG filter: {filter_type}")
            row[index] = (value + predictor) & 0xFF
        rows.append(row)
        previous = row
    return width, height, rows


class LogoAssetContractTest(unittest.TestCase):
    def test_shield_right_shoulder_is_present_without_a_background_plate(self):
        width, height, rows = decode_rgba_png(LOGO)
        self.assertEqual((width, height), (611, 203))

        corner_alpha = [
            rows[0][3],
            rows[0][(width - 1) * 4 + 3],
            rows[height - 1][3],
            rows[height - 1][(width - 1) * 4 + 3],
        ]
        self.assertEqual(corner_alpha, [0, 0, 0, 0])

        # This normalized region covers the shield's upper-right shoulder, the
        # area accidentally erased by the previous background-removal pass.
        opaque = 0
        total = 0
        for y in range(35, 115):
            for x in range(70, 190):
                total += 1
                if rows[y][x * 4 + 3] >= 128:
                    opaque += 1
        self.assertGreaterEqual(opaque / total, 0.85)

    def test_generated_header_versions_the_immutable_logo_asset(self):
        digest = hashlib.md5(LOGO.read_bytes()).hexdigest()[:8]
        width, height, _ = decode_rgba_png(LOGO)
        with tempfile.TemporaryDirectory() as output:
            subprocess.run(
                [sys.executable, "tools/build.py", output],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            homepage = (Path(output) / "index.html").read_text(encoding="utf-8")

        self.assertIn(f'<img src="/assets/logo.png?v={digest}"', homepage)
        self.assertIn(f'width="{width}" height="{height}"', homepage)

    def test_published_pages_use_current_header_asset_fingerprints(self):
        logo_ref = f'/assets/logo.png?v={hashlib.md5(LOGO.read_bytes()).hexdigest()[:8]}'
        css = ROOT / "public/style.css"
        css_ref = f'/style.css?v={hashlib.md5(css.read_bytes()).hexdigest()[:8]}'
        stale = []

        for page in (ROOT / "public").rglob("*.html"):
            source = page.read_text(encoding="utf-8")
            if '/assets/logo.png' in source and f'src="{logo_ref}"' not in source:
                stale.append(f"{page.relative_to(ROOT)}: stale logo fingerprint")
            if '/style.css' in source and f'href="{css_ref}"' not in source:
                stale.append(f"{page.relative_to(ROOT)}: stale stylesheet fingerprint")

        self.assertEqual(stale, [])

    def test_published_logo_dimensions_match_the_image(self):
        width, height, _ = decode_rgba_png(LOGO)
        expected = f'width="{width}" height="{height}"'
        stale = []

        for page in (ROOT / "public").rglob("*.html"):
            source = page.read_text(encoding="utf-8")
            if 'src="/assets/logo.png' in source and expected not in source:
                stale.append(str(page.relative_to(ROOT)))

        self.assertEqual(stale, [])


if __name__ == "__main__":
    unittest.main()
