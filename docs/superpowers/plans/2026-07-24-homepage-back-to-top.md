# Homepage Back-to-Top Button Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an accessible, localized back-to-top button to the Chinese and English homepages without affecting the existing AI consultation widget.

**Architecture:** Both homepages render the same icon-only button with localized accessible text. Shared CSS controls fixed positioning and visibility, while a focused zero-dependency script owns scroll-state updates and the return-to-top action.

**Tech Stack:** Static HTML, CSS, browser JavaScript, Python standard-library `unittest`, in-app browser responsive verification.

## Global Constraints

- Change only `public/index.html`, `public/en/index.html`, `public/style.css`, and the new shared files named in this plan.
- The control must remain 44 × 44 pixels on desktop and mobile.
- Show the control when `window.scrollY >= window.innerHeight`; hide it above that threshold.
- Use Chinese copy `返回顶部` and English copy `Back to top` for both `aria-label` and `title`.
- Default to smooth scrolling; use immediate scrolling when `prefers-reduced-motion: reduce` matches.
- Keep the control right-aligned with and exactly 14 pixels above the AI launcher.
- Use no third-party dependencies and no build step.
- Do not change subpages, navigation, homepage content order, or AI assistant behavior.
- Do not push or deploy during this implementation; stop after a verified local commit.

---

## File Map

- `tests/test_back_to_top.py`: Static contract tests for localized markup, shared assets, behavior hooks, and balanced tags.
- `public/index.html`: Chinese back-to-top button markup and shared script reference.
- `public/en/index.html`: English back-to-top button markup and shared script reference.
- `public/style.css`: Shared hidden, visible, hover, positioning, and transition states.
- `public/assets/back-to-top.js`: Scroll threshold, animation-frame scheduling, reduced-motion handling, and click behavior.

### Task 1: Implement and verify the shared homepage control

**Files:**

- Create: `tests/test_back_to_top.py`
- Create: `public/assets/back-to-top.js`
- Modify: `public/index.html` immediately after `</footer>` and in the existing script block before `</body>`
- Modify: `public/en/index.html` immediately after `</footer>` and in the existing script block before `</body>`
- Modify: `public/style.css` immediately before the existing `/* ============ AI ASSISTANT WIDGET ============ */` section

**Interfaces:**

- Consumes: one homepage element matching `[data-back-to-top]`, browser `scroll`, `resize`, `matchMedia`, `requestAnimationFrame`, and `scrollTo` APIs.
- Produces: CSS state class `is-visible`; no exported JavaScript globals and no dependency on the AI widget.

- [ ] **Step 1: Add the failing contract test**

Create `tests/test_back_to_top.py` with this exact content:

```python
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
            "window.scrollY >= window.innerHeight",
            "requestAnimationFrame(syncVisibility)",
            "prefers-reduced-motion: reduce",
            "window.scrollTo({ top: 0, left: 0, behavior: behavior })",
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
```

- [ ] **Step 2: Run the contract test and confirm the expected failure**

Run:

```powershell
python -m unittest tests/test_back_to_top.py -v
```

Expected: the two localized-page tests and CSS contract fail because the control is absent, and the script contract errors because `public/assets/back-to-top.js` does not exist. The existing tag-balance test passes.

- [ ] **Step 3: Add localized button markup and the shared script reference**

Insert this immediately after `</footer>` in `public/index.html`:

```html
<button class="back-to-top" type="button" data-back-to-top aria-label="返回顶部" title="返回顶部">
  <svg viewBox="0 0 24 24" width="20" height="20" fill="none" aria-hidden="true">
    <path d="M12 19V5m-6 6 6-6 6 6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>
</button>
```

Insert the same structure immediately after `</footer>` in `public/en/index.html`, replacing both localized attributes with:

```html
aria-label="Back to top" title="Back to top"
```

Add this line to both pages immediately before the existing `/assets/app.js` script reference:

```html
<script src="/assets/back-to-top.js" defer></script>
```

- [ ] **Step 4: Add the shared visual states and collision-free position**

Insert this CSS immediately before the AI assistant section in `public/style.css`:

```css
/* ============ BACK TO TOP ============ */
.back-to-top{
  position:fixed;right:clamp(1rem,3vw,2rem);
  bottom:calc(clamp(1rem,3vw,2rem) + var(--ai-launcher-height,2.6875rem) + .875rem);z-index:89;
  width:44px;height:44px;border:1px solid var(--line);border-radius:50%;
  display:grid;place-items:center;background:var(--paper-2);color:var(--ink);
  box-shadow:0 8px 24px -8px rgba(10,26,38,.38);cursor:pointer;
  opacity:0;visibility:hidden;pointer-events:none;transform:translateY(8px);
  transition:opacity .18s ease,visibility .18s,transform .18s ease,
             color .18s ease,border-color .18s ease,background .18s ease;
}
.back-to-top svg{width:20px;height:20px}
.back-to-top.is-visible{opacity:1;visibility:visible;pointer-events:auto;transform:none}
.back-to-top:hover{color:var(--blue);border-color:var(--blue);background:var(--blue-ghost)}
```

The AI launcher bottom edge remains `clamp(1rem,3vw,2rem)`. JavaScript measures the actual `.ai-launcher` height into `--ai-launcher-height`, and CSS adds a `.875rem` gap. The `2.6875rem` fallback preserves the current 43-pixel launcher height before measurement or when `ResizeObserver` is unavailable.

- [ ] **Step 5: Implement scroll state and reduced-motion behavior**

Create `public/assets/back-to-top.js` with this exact content:

```javascript
/* Sealion Tech — shared homepage back-to-top control. Zero dependencies. */
(function () {
  var button = document.querySelector('[data-back-to-top]');
  if (!button) return;

  var reduceMotion = window.matchMedia
    ? window.matchMedia('(prefers-reduced-motion: reduce)')
    : null;
  var ticking = false;

  function syncVisibility() {
    button.classList.toggle('is-visible', window.scrollY >= window.innerHeight);
    ticking = false;
  }

  function scheduleVisibilitySync() {
    if (ticking) return;
    ticking = true;
    window.requestAnimationFrame(syncVisibility);
  }

  button.addEventListener('click', function () {
    var behavior = reduceMotion && reduceMotion.matches ? 'auto' : 'smooth';
    window.scrollTo({ top: 0, left: 0, behavior: behavior });
  });
  window.addEventListener('scroll', scheduleVisibilitySync, { passive: true });
  window.addEventListener('resize', scheduleVisibilitySync);
  syncVisibility();
})();
```

- [ ] **Step 6: Run automated checks**

Run:

```powershell
python -m unittest tests/test_back_to_top.py -v
```

Expected: `Ran 5 tests` followed by `OK`.

Run:

```powershell
& 'C:\Program Files\Git\cmd\git.exe' diff --check
```

Expected: no output and exit code 0.

- [ ] **Step 7: Verify both languages and responsive behavior in a local browser**

Start the static site with a recoverable process handle:

```powershell
$siteServer = Start-Process -FilePath python -ArgumentList '-m','http.server','8000','--directory','public' -WindowStyle Hidden -PassThru
```

Use the in-app browser to verify both `http://127.0.0.1:8000/` and `http://127.0.0.1:8000/en/` at 1280 × 720 and 390 × 844:

1. The control is hidden at the top of the page.
2. It appears after scrolling at least one viewport height.
3. Its right edge aligns with the AI launcher and the controls do not overlap.
4. Clicking it returns to the top and hides it again.
5. Tab focus reaches it only while visible; Enter and Space activate it.
6. Opening the AI panel remains functional and does not expose the back-to-top control above the panel.
7. Neither viewport has horizontal overflow, and the browser console has no new errors.

Stop only the server process started above:

```powershell
Stop-Process -Id $siteServer.Id
```

- [ ] **Step 8: Commit the verified implementation without deploying**

Run:

```powershell
& 'C:\Program Files\Git\cmd\git.exe' add -- tests/test_back_to_top.py public/index.html public/en/index.html public/style.css public/assets/back-to-top.js
& 'C:\Program Files\Git\cmd\git.exe' -c user.name=Codex -c user.email=codex@local commit -m "feat: add homepage back-to-top button"
& 'C:\Program Files\Git\cmd\git.exe' status --short --branch
```

Expected: the feature commit succeeds and the worktree is clean. The branch is ahead of `origin/main`; do not push until the user explicitly approves deployment.
