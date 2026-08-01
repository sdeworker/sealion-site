from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / "public/style.css").read_text(encoding="utf-8")


def block(source, header):
    marker = f"{header}{{"
    start = source.find(marker)
    if start < 0:
        raise AssertionError(f"missing CSS block: {header}")
    start += len(marker)
    depth = 1
    for index in range(start, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return source[start:index]
    raise AssertionError(f"unclosed CSS block: {header}")


def declarations(source, selector):
    body = block(source, selector)
    result = {}
    for item in body.replace("\n", "").split(";"):
        if ":" in item:
            name, value = item.split(":", 1)
            result[name.strip()] = value.strip()
    return result


class HeaderLayoutContractTest(unittest.TestCase):
    def test_wide_header_preserves_logo_aspect_ratio(self):
        bar = declarations(CSS, ".site-header .bar")
        brand = declarations(CSS, ".brand")
        logo = declarations(CSS, ".brand img")
        nav = declarations(CSS, ".nav")

        self.assertEqual(bar.get("max-width"), "1760px")
        self.assertEqual(brand.get("flex"), "0 0 auto")
        self.assertEqual(brand.get("margin-right"), "0")
        self.assertEqual(logo.get("height"), "72px")
        self.assertEqual(logo.get("width"), "auto")
        self.assertEqual(logo.get("max-width"), "none")
        self.assertEqual(nav.get("flex"), "0 0 auto")
        self.assertEqual(nav.get("margin-left"), "auto")

    def test_mobile_navigation_activates_before_header_can_compress(self):
        media = block(CSS, "@media(max-width:1320px)")
        burger = declarations(media, ".burger")
        nav = declarations(media, ".nav")

        self.assertEqual(burger.get("display"), "flex")
        self.assertEqual(nav.get("position"), "absolute")
        self.assertEqual(nav.get("max-height"), "0")

    def test_mobile_button_stays_on_the_right(self):
        burger = declarations(CSS, ".burger")
        self.assertEqual(burger.get("margin-left"), "auto")


if __name__ == "__main__":
    unittest.main()
