# Header Navigation Responsive Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修复三语页头中 Logo 被横向压缩和一级导航在窄桌面宽度下拥挤的问题。

**Architecture:** 只调整公共 `public/style.css`：页头使用独立的 1760px 宽容器，品牌、口号和导航不参与 Flex 收缩，1320px 以下沿用现有移动菜单。用标准库 `unittest` 解析实际 CSS 规则形成回归约束，再用真实浏览器测量三语页面几何。

**Tech Stack:** HTML5、CSS3、Python 3 标准库 `unittest`、本地 HTTP 服务、Playwright 浏览器检查

## Global Constraints

- 保持 Logo 高度 72px，显示宽高比与源图 `611 / 203 = 3.010` 的误差不超过 0.01。
- 保持一级导航字号 1.25rem，栏目文案、链接、下拉菜单结构不变。
- 页头最大宽度 1760px；正文 `.wrap` 仍为 1440px。
- 1560px 及以下隐藏口号；1320px 及以下启用现有汉堡菜单。
- 不编辑 `public/assets/logo.png`，不修改页面正文、Hero 或移动菜单 JavaScript。
- 当前 `main` 的 `tests/test_back_to_top.py` 在本任务开始前已有 4 项失败；不得把这些既有失败归因于本次页头改动，也不得越界修复。

---

### Task 1: 添加页头布局回归测试并完成 CSS 修复

**Files:**
- Create: `tests/test_header_layout.py`
- Modify: `public/style.css:136-200`

**Interfaces:**
- Consumes: `public/style.css` 中的 `.site-header .bar`、`.brand`、`.brand img`、`.slogan`、`.burger`、`.nav` 和响应式媒体规则。
- Produces: `HeaderLayoutContractTest`，以及桌面/窄桌面/移动端共用的稳定页头布局规则。

- [ ] **Step 1: 写入会失败的回归测试**

```python
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
```

- [ ] **Step 2: 运行新测试，确认按预期失败**

Run:

```powershell
python -m unittest tests.test_header_layout -v
```

Expected: 3 tests fail because `.site-header .bar`、不可收缩规则、1320px 媒体规则和汉堡按钮右对齐尚未实现；失败不得来自语法错误或找不到 `public/style.css`。

- [ ] **Step 3: 写入最小 CSS 修复**

在现有页头规则中应用以下最终声明，保留当前颜色、字号和交互规则：

```css
.site-header .bar{max-width:1760px}

.slogan{font-size:1.0625rem;color:var(--steel);border-left:1px solid var(--line);
  padding-left:1.25rem;margin-right:0;white-space:nowrap;flex:0 0 auto}

.brand{display:inline-flex;align-items:center;gap:0.65rem;margin-right:0;flex:0 0 auto}
.brand img{height:72px;width:auto;max-width:none}

.nav{display:flex;gap:clamp(0.1rem,0.6vw,0.5rem);margin-left:auto;flex:0 0 auto}

.burger{display:none;flex-direction:column;gap:5px;cursor:pointer;padding:6px;background:none;
  border:0;color:inherit;margin-left:auto}

@media(max-width:1320px){
  .header-actions .hotline{display:none}
  .burger{display:flex;order:3}
  .nav{position:absolute;top:100%;left:0;right:0;flex-direction:column;gap:0;background:var(--paper-2);border-bottom:1px solid var(--line);max-height:0;overflow:hidden;transition:max-height .28s}
  .nav a{padding:0.9em var(--gutter);border-top:1px solid var(--line)}
  .burger[aria-expanded="true"] ~ .nav{max-height:70vh}
  .burger[aria-expanded="true"] span:nth-child(1){transform:translateY(7px) rotate(45deg)}
  .burger[aria-expanded="true"] span:nth-child(2){opacity:0}
  .burger[aria-expanded="true"] span:nth-child(3){transform:translateY(-7px) rotate(-45deg)}
}
```

同步更新原来描述 1024px 的注释为 1320px，不改动其他页面样式。

- [ ] **Step 4: 运行目标测试，确认全部通过**

Run:

```powershell
python -m unittest tests.test_header_layout -v
```

Expected: `Ran 3 tests` and `OK`。

- [ ] **Step 5: 运行静态站检查**

Run:

```powershell
python tools/check.py
python -m unittest tests.test_back_to_top.BackToTopContractTest.test_modified_pages_keep_balanced_tags -v
```

Expected: `tools/check.py` 无新增错误，HTML 标签平衡测试通过。既有的回到顶部功能测试不在本任务中修复。

- [ ] **Step 6: 提交实现与测试**

```powershell
git add public/style.css tests/test_header_layout.py
git commit -m "Fix responsive header logo and navigation"
```

### Task 2: 真实浏览器三语响应式验证

**Files:**
- Verify only: `public/index.html`
- Verify only: `public/en/index.html`
- Verify only: `public/ru/index.html`
- Verify only: `public/style.css`

**Interfaces:**
- Consumes: Task 1 的公共 CSS 和三语首页。
- Produces: 可复核的 Logo 宽高比、口号显示状态、导航/汉堡显示状态和页面截图。

- [ ] **Step 1: 启动本地静态服务**

```powershell
cd public
python -m http.server 8765 --bind 127.0.0.1
```

- [ ] **Step 2: 在三语首页执行桌面与窄屏几何检查**

使用真实浏览器分别打开 `/`、`/en/`、`/ru/`，检查：

| 视口 | Logo 比例 | 口号 | 完整导航 | 汉堡 |
|---|---:|---|---|---|
| 1920×1080 | 3.010±0.01 | 显示 | 显示、单行 | 隐藏 |
| 1536×864 | 3.010±0.01 | 隐藏 | 显示、单行 | 隐藏 |
| 1440×900 | 3.010±0.01 | 隐藏 | 显示、单行 | 隐藏 |
| 1280×800 | 3.010±0.01 | 隐藏 | 折叠 | 显示 |
| 390×844 | 3.010±0.01 | 隐藏 | 折叠 | 显示 |

对每个页面读取 `.brand img` 的 `getBoundingClientRect()`，并确认 `.bar` 的 `scrollWidth === clientWidth`。桌面状态下所有一级导航链接保持一行。

- [ ] **Step 3: 检查首页透明页头与滚动后实底页头**

在中文首页 1920×1080 下记录顶部状态；向下滚动超过 60px，确认 `.site-header` 获得 `is-solid`，Logo、导航和 Hero 顶部偏移不跳动。

- [ ] **Step 4: 检查最终差异与仓库状态**

```powershell
git diff main...HEAD --check
git diff main...HEAD --stat
git status --short --branch
```

Expected: 只有设计说明、实施计划、`public/style.css` 和 `tests/test_header_layout.py`；工作区干净。
