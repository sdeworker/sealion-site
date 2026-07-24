from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


class BackToTopContractTest(unittest.TestCase):
    def assert_localized_page(self, relative_path, label):
        html = (ROOT / relative_path).read_text(encoding="utf-8")
        self.assertIn('class="back-to-top"', html)
        self.assertIn('data-back-to-top', html)
        self.assertIn(f'aria-label="{label}"', html)
        self.assertIn(f'title="{label}"', html)
        self.assertIn('src="/assets/back-to-top.js" defer', html)
        self.assertIn('<main tabindex="-1">', html)

    def test_chinese_homepage_contract(self):
        self.assert_localized_page("public/index.html", "返回顶部")

    def test_english_homepage_contract(self):
        self.assert_localized_page("public/en/index.html", "Back to top")

    def test_shared_css_contract(self):
        css = (ROOT / "public/style.css").read_text(encoding="utf-8")
        for expected in (
            ".back-to-top{",
            "width:44px;height:44px",
            "bottom:calc(clamp(1rem,3vw,2rem) + var(--ai-launcher-height,2.6875rem) + .875rem)",
            ".back-to-top.is-visible{",
            "pointer-events:auto",
        ):
            self.assertIn(expected, css)

    def test_shared_script_contract(self):
        script = (ROOT / "public/assets/back-to-top.js").read_text(encoding="utf-8")
        for expected in (
            "document.querySelector('[data-back-to-top]')",
            "document.querySelector('main')",
            "document.querySelector('.ai-launcher')",
            "window.scrollY >= window.innerHeight",
            "requestAnimationFrame(syncVisibility)",
            "prefers-reduced-motion: reduce",
            "window.scrollTo({ top: 0, left: 0, behavior: behavior })",
            "focusTarget.focus({ preventScroll: true })",
            "button.style.setProperty('--ai-launcher-height'",
            "new ResizeObserver(syncAssistantOffset)",
            "{ passive: true }",
        ):
            self.assertIn(expected, script)

    def test_modified_pages_keep_balanced_tags(self):
        for relative_path in ("public/index.html", "public/en/index.html"):
            html = (ROOT / relative_path).read_text(encoding="utf-8")
            for tag in ("div", "section", "article", "a", "span", "button"):
                opens = len(re.findall(fr"<{tag}(?:\s|>)", html))
                closes = len(re.findall(fr"</{tag}>", html))
                self.assertEqual(opens, closes, f"{relative_path}: unbalanced <{tag}>")


if __name__ == "__main__":
    unittest.main()
