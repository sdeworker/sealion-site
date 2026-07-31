# -*- coding: utf-8 -*-
"""学旧站的头部做法 + 导航透明压图 + Hero 仪表卡让位

旧站头部值得学的三点：
  ① 双层——顶部深蓝细条放欢迎语/热线/语言，下面白条只留 logo 与导航，主导航因此干净
  ② logo 右侧一句 slogan「挤出行业一体化解决方案」，一眼说清是做什么的
  ③ 当前栏目高亮（蓝字 + 下划短横）

再加两件：首页整个头部透明压在 Hero 大图上、滚过 Hero 后变实底；
Hero 右侧仪表卡从占半屏收窄，把厂房实景让出来。
"""
import io, json, re, sys

# ── 1. site.json：补三语文案 ─────────────────────────────────
p = "src/site.json"
d = json.load(io.open(p, encoding="utf-8"))
d["ui"]["welcome"] = {
    "zh": "您好，欢迎进入广州海狮软件科技有限公司",
    "en": "Welcome to Guangzhou Sealion Software Technology",
    "ru": "Добро пожаловать в Guangzhou Sealion Software Technology",
}
d["ui"]["slogan"] = {
    "zh": "挤出行业一体化解决方案",
    "en": "Integrated solutions for plastics extrusion",
    "ru": "Комплексные решения для экструзии",
}
d["ui"]["hotlineLabel"] = {"zh": "服务热线", "en": "Hotline", "ru": "Горячая линия"}
io.open(p, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=2) + "\n")
print("site.json 已补 welcome / slogan / hotlineLabel 三语")

# ── 2. build.py：双层头部 + 当前项高亮 + body class ───────────
b = io.open("tools/build.py", encoding="utf-8").read()

OLD_HEADER = '''    return f\'\'\'<header class="site-header">
  <div class="wrap bar">
    <a class="brand" href="{root}" aria-label="{H.escape(t(SITE["ui"]["brandHome"], lang), quote=True)}">
      <img src="/assets/logo.png" alt="{H.escape(t(SITE["brand"], lang), quote=True)}" width="199" height="63">
    </a>
    <button class="burger" type="button" aria-label="{H.escape(t(SITE["ui"]["menu"], lang), quote=True)}" aria-expanded="false" aria-controls="site-nav">
      <span></span><span></span><span></span>
    </button>
    <nav class="nav" id="site-nav" aria-label="{H.escape(t(SITE["ui"]["mainNav"], lang), quote=True)}">
{nav}
    </nav>
    <div class="header-actions">
{switch}
      <a class="hotline" href="{SITE["hotlineHref"]}"><span class="dot"></span>{SITE["hotline"]}</a>
    </div>
  </div>
</header>\'\'\''''

NEW_HEADER = '''    return f\'\'\'<header class="site-header" data-header>
  <div class="topbar">
    <div class="wrap topbar-in">
      <span class="welcome">{H.escape(t(SITE["ui"]["welcome"], lang))}</span>
      <div class="topbar-right">
        <a class="hotline" href="{SITE["hotlineHref"]}"><span class="dot"></span>{H.escape(t(SITE["ui"]["hotlineLabel"], lang))}：{SITE["hotline"]}</a>
{switch}
      </div>
    </div>
  </div>
  <div class="wrap bar">
    <a class="brand" href="{root}" aria-label="{H.escape(t(SITE["ui"]["brandHome"], lang), quote=True)}">
      <img src="/assets/logo.png" alt="{H.escape(t(SITE["brand"], lang), quote=True)}" width="597" height="189">
    </a>
    <span class="slogan">{H.escape(t(SITE["ui"]["slogan"], lang))}</span>
    <button class="burger" type="button" aria-label="{H.escape(t(SITE["ui"]["menu"], lang), quote=True)}" aria-expanded="false" aria-controls="site-nav">
      <span></span><span></span><span></span>
    </button>
    <nav class="nav" id="site-nav" aria-label="{H.escape(t(SITE["ui"]["mainNav"], lang), quote=True)}">
{nav}
    </nav>
  </div>
</header>\'\'\''''

assert b.count(OLD_HEADER) == 1, "头部模板锚点对不上"
b = b.replace(OLD_HEADER, NEW_HEADER, 1)

# 当前栏目高亮：本页命中该栏目或其子项就打 aria-current
OLD_ITEM = '''        else:
            items.append(f'      <a href="{href}">{label}</a>')'''
NEW_ITEM = '''        else:
            items.append(f'      <a href="{href}"{cur(n)}>{label}</a>')'''
assert b.count(OLD_ITEM) == 1
b = b.replace(OLD_ITEM, NEW_ITEM, 1)

OLD_DROP = '''            items.append(
                f'      <div class="nav-drop">\\n'
                f'        <a href="{href}">{label}</a>\\n\''''
NEW_DROP = '''            items.append(
                f'      <div class="nav-drop">\\n'
                f'        <a href="{href}"{cur(n)}>{label}</a>\\n\''''
assert b.count(OLD_DROP) == 1
b = b.replace(OLD_DROP, NEW_DROP, 1)

OLD_LOOP = '''    root = SITE["langRoot"][lang]
    items = []
    for n in SITE["nav"]:'''
NEW_LOOP = '''    root = SITE["langRoot"][lang]
    here = "/" + rel if not rel.startswith("/") else rel

    def cur(n):
        """本页就在这个栏目下时给它 aria-current，导航才有'我在哪'的提示。"""
        paths = [n["href"]] + [c["href"] for c in n.get("children", [])]
        for h in paths:
            base = h.split("#")[0]
            if base and base != "/" and here.startswith(base.rstrip("/") or "/"):
                return ' aria-current="page"'
        return ""

    items = []
    for n in SITE["nav"]:'''
assert b.count(OLD_LOOP) == 1
b = b.replace(OLD_LOOP, NEW_LOOP, 1)

# body class：首页拿 home，供"导航透明压图"用
assert b.count("<body>") == 1
b = b.replace("<body>", '<body class="{bodycls}">', 1)
OLD_SKIP = '    skip = t(SITE["ui"]["skip"], lang)'
NEW_SKIP = ('    skip = t(SITE["ui"]["skip"], lang)\n'
            '    bodycls = "home" if meta.get("type") == "home" else ""')
assert b.count(OLD_SKIP) == 1
b = b.replace(OLD_SKIP, NEW_SKIP, 1)

# 首页额外挂头部滚动脚本
OLD_TAIL = ("    tail = ['<script>document.getElementById(\\'yr\\').textContent=new Date().getFullYear();</script>',\n"
            "            f'<script src=\"{ver(\"/assets/nav.js\")}\" defer></script>']")
NEW_TAIL = ("    tail = ['<script>document.getElementById(\\'yr\\').textContent=new Date().getFullYear();</script>',\n"
            "            f'<script src=\"{ver(\"/assets/nav.js\")}\" defer></script>']\n"
            "    if meta.get(\"type\") == \"home\":\n"
            "        tail.append(f'<script src=\"{ver(\"/assets/header-scroll.js\")}\" defer></script>')")
assert b.count(OLD_TAIL) == 1
b = b.replace(OLD_TAIL, NEW_TAIL, 1)

io.open("tools/build.py", "w", encoding="utf-8").write(b)
print("build.py 已改：双层头部 / slogan / 当前项高亮 / body class / 首页挂脚本")

# ── 3. 滚动脚本 ──────────────────────────────────────────────
io.open("public/assets/header-scroll.js", "w", encoding="utf-8").write(
    '''/* 首页头部：压在 Hero 大图上时透明，滚过一屏后变实底。零依赖。 */
(function () {
  var h = document.querySelector('[data-header]');
  if (!h || !document.body.classList.contains('home')) return;
  var solid = false;
  function sync() {
    var want = window.scrollY > 60;
    if (want !== solid) { solid = want; h.classList.toggle('is-solid', want); }
  }
  sync();
  window.addEventListener('scroll', sync, { passive: true });
})();
''')
print("已写 public/assets/header-scroll.js")

# ── 4. CSS ──────────────────────────────────────────────────
S = "public/style.css"
s = io.open(S, encoding="utf-8").read()

OLD_BAR = ".bar{display:flex;align-items:center;gap:1.75rem;min-height:88px}"
NEW_BAR = """.bar{display:flex;align-items:center;gap:1.75rem;min-height:88px}
/* ============ 顶部信息条（学旧站：欢迎语 + 热线 + 语言） ============ */
.topbar{background:var(--blue);color:#fff}
.topbar-in{display:flex;align-items:center;justify-content:space-between;gap:1rem;min-height:40px}
.welcome{font-size:0.9375rem;color:rgba(255,255,255,.92)}
.topbar-right{display:flex;align-items:center;gap:1.25rem}
.topbar .hotline{color:#fff;min-height:40px}
.topbar .hotline .dot{background:var(--signal)}
.topbar .langlink{border-color:rgba(255,255,255,.42);color:#fff;min-height:32px}
.topbar .langlink:hover{background:rgba(255,255,255,.16);border-color:#fff}
@media(max-width:760px){.topbar .welcome{display:none}.topbar-in{justify-content:flex-end}}
/* logo 右侧的一句话，直接说清是做什么的 */
.slogan{font-size:1.0625rem;color:var(--steel);border-left:1px solid var(--line);
  padding-left:1.25rem;margin-right:auto;white-space:nowrap}
@media(max-width:1100px){.slogan{display:none}}
/* 当前栏目：蓝字 + 下方短横 */
.nav a[aria-current]{color:var(--blue);font-weight:600;position:relative}
.nav a[aria-current]::after{content:"";position:absolute;left:0.62em;right:0.62em;bottom:0.55em;
  height:2px;background:var(--blue);border-radius:2px}"""
assert s.count(OLD_BAR) == 1
s = s.replace(OLD_BAR, NEW_BAR, 1)

# 首页：头部透明压图，滚动后变实底
OLD_HDR = ".site-header{position:sticky;top:0;z-index:50;"
NEW_HDR = """/* 首页：头部压在 Hero 大图上，图从屏幕最顶端开始；滚过 60px 变实底 */
body.home .site-header{background:transparent;backdrop-filter:none;border-bottom-color:transparent}
body.home .site-header .topbar{background:rgba(10,26,38,.34)}
body.home .site-header .nav a{color:rgba(255,255,255,.92)}
body.home .site-header .nav a:hover{color:#fff;background:rgba(255,255,255,.14)}
body.home .site-header .slogan{color:rgba(255,255,255,.80);border-left-color:rgba(255,255,255,.28)}
body.home .site-header .burger span{background:#fff}
body.home .hero{margin-top:calc(-1 * var(--header-h,128px))}
body.home .hero-grid{padding-top:calc(var(--header-h,128px) + 1rem)}
body.home .site-header.is-solid{background:color-mix(in srgb,var(--paper) 94%,transparent);
  backdrop-filter:blur(10px);border-bottom-color:var(--line)}
body.home .site-header.is-solid .topbar{background:var(--blue)}
body.home .site-header.is-solid .nav a{color:var(--ink-70)}
body.home .site-header.is-solid .nav a[aria-current]{color:var(--blue)}
body.home .site-header.is-solid .slogan{color:var(--steel);border-left-color:var(--line)}
body.home .site-header.is-solid .burger span{background:var(--ink)}
.site-header{position:sticky;top:0;z-index:50;transition:background .25s,border-color .25s;"""
assert s.count(OLD_HDR) == 1
s = s.replace(OLD_HDR, NEW_HDR, 1)

# Hero 占满首屏（头部现在压在上面，不再减去）
assert s.count("min-height:calc(100svh - 76px);") == 1
s = s.replace("min-height:calc(100svh - 76px);", "min-height:100svh;", 1)

# 仪表卡让位：文字栏加宽、卡片收窄并靠下
OLD_GRID = ".hero-grid{display:grid;grid-template-columns:1.05fr 0.95fr;"
NEW_GRID = ".hero-grid{display:grid;grid-template-columns:1.5fr 0.85fr;"
assert s.count(OLD_GRID) == 1
s = s.replace(OLD_GRID, NEW_GRID, 1)

io.open(S, "w", encoding="utf-8").write(s)
print("style.css 已改：顶部条 / slogan / 当前项高亮 / 首页透明头部 / Hero 满屏 / 仪表卡让位")
