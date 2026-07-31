# -*- coding: utf-8 -*-
"""① 语言改成导航里的一个栏目（中文 ⌄ → 中文 / English / Русский）
   ② 播放键重做：去掉毛玻璃，换干净的细环 + 正三角
"""
import io, json, sys

# ── 语言全称 ────────────────────────────────────────────────
p = "src/site.json"
d = json.load(io.open(p, encoding="utf-8"))
d["langName"] = {"zh": "中文", "en": "English", "ru": "Русский"}
d["ui"]["language"] = {"zh": "语言", "en": "Language", "ru": "Язык"}
io.open(p, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=2) + "\n")
print("site.json 已补 langName / ui.language")

# ── build.py：语言下拉进主导航，topbar 不再放语言键 ──────────
b = io.open("tools/build.py", encoding="utf-8").read()

OLD_SWITCH = '''    switch = "\\n".join(
        f'      <a class="langlink" href="{page_url(l2, rel)[len(BASE):]}" hreflang="{SITE["hreflang"][l2]}">{H.escape(SITE["langLabel"][l2])}</a>'
        for l2 in alts if l2 != lang)'''
NEW_SWITCH = '''    # 语言做成导航里的一个栏目：当前语言 + 下拉，列出全称。
    lang_items = []
    for l2 in alts:
        url = page_url(l2, rel)[len(BASE):]
        mark = ' aria-current="true"' if l2 == lang else ""
        lang_items.append(
            f'          <a href="{url}" hreflang="{SITE["hreflang"][l2]}"{mark}>'
            f'{H.escape(SITE["langName"][l2])}</a>')
    switch = (
        '      <div class="nav-drop nav-lang">\\n'
        f'        <button type="button" class="nav-lang-btn" aria-haspopup="true" aria-expanded="false">'
        f'{H.escape(SITE["langName"][lang])}</button>\\n'
        '        <div class="nav-drop-menu">\\n'
        + "\\n".join(lang_items) + "\\n"
        '        </div>\\n'
        '      </div>')'''
assert b.count(OLD_SWITCH) == 1, "switch 生成锚点对不上"
b = b.replace(OLD_SWITCH, NEW_SWITCH, 1)

# topbar 去掉语言键；主导航末尾接上语言栏目
OLD_TOP = '''        <a class="hotline" href="{SITE["hotlineHref"]}"><span class="dot"></span>{H.escape(t(SITE["ui"]["hotlineLabel"], lang))}：{SITE["hotline"]}</a>
{switch}
      </div>'''
NEW_TOP = '''        <a class="hotline" href="{SITE["hotlineHref"]}"><span class="dot"></span>{H.escape(t(SITE["ui"]["hotlineLabel"], lang))}：{SITE["hotline"]}</a>
      </div>'''
assert b.count(OLD_TOP) == 1
b = b.replace(OLD_TOP, NEW_TOP, 1)

OLD_NAV = '''{nav}
    </nav>'''
NEW_NAV = '''{nav}
{switch}
    </nav>'''
assert b.count(OLD_NAV) == 1
b = b.replace(OLD_NAV, NEW_NAV, 1)

io.open("tools/build.py", "w", encoding="utf-8").write(b)
print("build.py 已改：语言下拉进主导航，顶条只留欢迎语与热线")

# ── CSS ────────────────────────────────────────────────────
S = "public/style.css"
s = io.open(S, encoding="utf-8").read()

OLD_TOPCSS = ".topbar .langlink{border-color:rgba(255,255,255,.42);color:#fff;min-height:32px}\n.topbar .langlink:hover{background:rgba(255,255,255,.16);border-color:#fff}"
NEW_TOPCSS = """/* 语言栏目：外观与其他导航项一致，只多一个小箭头 */
.nav-lang{margin-left:.35rem}
.nav-lang-btn{display:inline-flex;align-items:center;gap:.45em;background:none;border:0;
  cursor:pointer;font-family:inherit;font-size:1.25rem;color:var(--ink-70);
  padding:.55em .62em;border-radius:var(--radius);transition:color .15s,background .15s}
.nav-lang-btn::after{content:"";width:.42em;height:.42em;border-right:2px solid currentColor;
  border-bottom:2px solid currentColor;transform:rotate(45deg) translateY(-.12em);transition:transform .2s}
.nav-lang-btn:hover,.nav-lang:focus-within .nav-lang-btn{color:var(--blue)}
.nav-lang:hover .nav-lang-btn::after,.nav-lang:focus-within .nav-lang-btn::after{
  transform:rotate(225deg) translateY(-.12em)}
.nav-drop-menu a[aria-current]{color:var(--blue);font-weight:600}
body.home .site-header:not(.is-solid) .nav-lang-btn{color:rgba(255,255,255,.92)}
body.home .site-header:not(.is-solid) .nav-lang-btn:hover{color:#fff}"""
assert s.count(OLD_TOPCSS) == 1
s = s.replace(OLD_TOPCSS, NEW_TOPCSS, 1)

# ── 播放键重做 ──────────────────────────────────────────────
OLD_PLAY_START = s.index("body.home .hero-play{flex-direction:column")
OLD_PLAY_END = s.index("/* ===== 试排结束 ===== */")
NEW_PLAY = """body.home .hero-play{flex-direction:column;gap:1.1rem;margin:0;min-height:0;
  color:#fff;letter-spacing:0.04em;font-size:1.0625rem;text-shadow:0 1px 12px rgba(0,0,0,.45)}
/* 细环 + 正三角。不用毛玻璃——它在明亮照片上会糊成一团灰。 */
body.home .hero-play::before{content:"";width:92px;height:92px;border-radius:50%;
  border:2px solid rgba(255,255,255,.92);background:rgba(10,26,38,.30);
  box-shadow:0 6px 28px rgba(0,0,0,.30);
  background-image:url("data:image/svg+xml;charset=utf-8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='34' height='38' viewBox='0 0 34 38'%3E%3Cpath d='M2 1.6 32 19 2 36.4Z' fill='%23fff'/%3E%3C/svg%3E");
  background-repeat:no-repeat;background-position:calc(50% + 3px) 50%;background-size:26px 29px;
  transition:transform .25s,background-color .25s}
body.home .hero-play:hover{text-decoration:none}
body.home .hero-play:hover::before{transform:scale(1.07);background-color:rgba(10,26,38,.52);
  border-color:#fff}
body.home .hero-play:focus-visible::before{outline:3px solid var(--signal);outline-offset:4px}
body.home .hero-play svg{display:none}
@media(prefers-reduced-motion:reduce){body.home .hero-play::before{transition:none}}
@media(max-width:760px){body.home .hero-play::before{width:72px;height:72px;background-size:21px 23px}}
"""
s = s[:OLD_PLAY_START] + NEW_PLAY + s[OLD_PLAY_END:]
io.open(S, "w", encoding="utf-8").write(s)
print("style.css 已改：语言栏目样式 + 播放键重做")
