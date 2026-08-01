# -*- coding: utf-8 -*-
"""
海狮官网静态生成器
  src/site.json           全站配置（品牌/导航/页脚/三语 UI 文案）
  src/content/<lang>/...  各页正文（JSON 元数据 + <main> 内容）
        ↓  python3 tools/build.py
  public/                 生成的静态站（请勿手改）

设计原则：
  · 正文原样保留，不做改写；外壳（head/header/footer）由本文件统一生成
  · 某语种缺页则该页不生成，hreflang 只列真实存在的语种
  · 输出仍是纯静态 HTML，Cloudflare 部署方式不变
"""
import glob, json, os, re, shutil, subprocess, sys, html as H

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
SITE = json.load(open("src/site.json", encoding="utf-8"))
OUT = sys.argv[1] if len(sys.argv) > 1 else "public"

BASE = SITE["base"]
LANGS = SITE["languages"]

WARN = ("<!-- 本文件由 tools/build.py 从 src/ 生成，请勿直接编辑。\n"
        "     改内容 → src/content/<语种>/...；改导航页脚 → src/site.json -->\n")


# ---------- 工具 ----------
def t(node, lang):
    """取多语言文案，缺失回退到中文"""
    if isinstance(node, str):
        return node
    return node.get(lang) or node.get("zh") or ""


def page_url(lang, rel):
    """规范 URL（无扩展名；index 用目录形式）"""
    root = SITE["langRoot"][lang]
    if rel == "index.html":
        return BASE + root
    p = rel[:-5] if rel.endswith(".html") else rel
    if p.endswith("/index"):
        p = p[:-5]
    return BASE + root + p


def page_path(lang, rel):
    """输出文件路径"""
    sub = "" if lang == "zh" else lang + "/"
    return os.path.join(OUT, sub + rel)


def load(path):
    raw = open(path, encoding="utf-8").read()
    meta_s, _, body = raw.partition("\n---\n")
    return json.loads(meta_s), body


def git_date(path):
    try:
        d = subprocess.check_output(["git", "log", "-1", "--format=%cs", path],
                                    text=True, stderr=subprocess.DEVNULL).strip()
        return d or None
    except Exception:
        return None



def localize(href, lang):
    """把站内绝对路径按语种加前缀：/pipe/ → /en/pipe/；/#apply → /en/#apply"""
    if not href.startswith("/"):
        return href
    root = SITE["langRoot"][lang]          # "/" | "/en/" | "/ru/"
    return root + href[1:]                 # 保证只有一个斜杠



def exists_for(href, lang, avail):
    """该语种是否真的有这个页面；锚点与外链一律放行"""
    if not href.startswith("/") or href.startswith("/#"):
        return True
    rel = href[1:]
    if rel.endswith("/"):
        rel += "index.html"
    rel = rel.split("#")[0]
    return rel in avail.get(lang, set())



_ASSET_HASH = {}


def ver(path):
    """给样式/脚本加内容指纹：/style.css → /style.css?v=ab12cd34
       内容一变指纹就变，浏览器立刻取新版；不变则可长期缓存"""
    import hashlib
    if path not in _ASSET_HASH:
        fp = "public" + path
        try:
            data = open(fp, "rb").read()
            if os.path.splitext(path)[1].lower() in {".css", ".js", ".json", ".html", ".xml"}:
                data = data.replace(b"\r\n", b"\n")
            h = hashlib.md5(data).hexdigest()[:8]
        except OSError:
            h = ""
        _ASSET_HASH[path] = f"{path}?v={h}" if h else path
    return _ASSET_HASH[path]


# ---------- 外壳 ----------
def render_head(lang, rel, meta, alts):
    u = page_url(lang, rel)
    title = meta.get("title", "")
    desc = meta.get("description", "")
    o = [f'<meta charset="utf-8">',
         f'<meta name="viewport" content="width=device-width,initial-scale=1">',
         f'<title>{H.escape(title)}</title>']
    if desc:
        o.append(f'<meta name="description" content="{H.escape(desc, quote=True)}">')
    o.append(f'<link rel="canonical" href="{u}">')
    for l2 in alts:
        o.append(f'<link rel="alternate" hreflang="{SITE["hreflang"][l2]}" href="{page_url(l2, rel)}">')
    if "zh" in alts:
        o.append(f'<link rel="alternate" hreflang="x-default" href="{page_url("zh", rel)}">')
    # Open Graph
    o += [f'<meta property="og:type" content="website">',
          f'<meta property="og:title" content="{H.escape(title, quote=True)}">',
          f'<meta property="og:url" content="{u}">',
          f'<meta property="og:image" content="{BASE}{SITE["ogImage"]}">',
          f'<meta property="og:site_name" content="{H.escape(t(SITE["brand"], lang))}">',
          f'<meta property="og:locale" content="{SITE["ogLocale"][lang]}">',
          '<meta name="twitter:card" content="summary_large_image">']
    if desc:
        o.append(f'<meta property="og:description" content="{H.escape(desc, quote=True)}">')
    o.append('<link rel="icon" href="/assets/favicon.ico">')
    o.append('<link rel="preconnect" href="https://fonts.googleapis.com">')
    o.append('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>')
    o.append('<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Inter:wght@400;500;600;700&family=Noto+Sans+SC:wght@400;500;600;700&display=swap" rel="stylesheet">')
    o.append(f'<link rel="stylesheet" href="{ver("/style.css")}">'
             f'<link rel="stylesheet" href="{ver("/print.css")}" media="print">')
    for c in meta.get("css", []):
        o.append(f'<link rel="stylesheet" href="{ver("/" + c + ".css")}">')
    for block in json_ld(lang, rel, meta):
        o.append('<script type="application/ld+json">' +
                 json.dumps(block, ensure_ascii=False, separators=(",", ":")) + "</script>")
    return "\n".join(o)


def json_ld(lang, rel, meta):
    u = page_url(lang, rel)
    legal = t(SITE["legalName"], lang)
    org = {"@context": "https://schema.org", "@type": "Organization",
           "name": legal, "alternateName": t(SITE["brand"], lang),
           "url": BASE + SITE["langRoot"][lang], "logo": BASE + "/assets/logo.png",
           "address": {"@type": "PostalAddress", "streetAddress": t(SITE["address"], lang),
                       "addressCountry": "CN"},
           "contactPoint": [{"@type": "ContactPoint", "telephone": SITE["phone"],
                             "contactType": "sales",
                             "availableLanguage": [SITE["hreflang"][l] for l in LANGS]}]}
    out = []
    typ = meta.get("type", "page")
    title = re.sub(r"\s*[—-]\s*(海狮科技|Sealion Tech).*$", "", meta.get("title", "")).strip()
    if typ == "home":
        out += [org, {"@context": "https://schema.org", "@type": "WebSite",
                      "name": t(SITE["brand"], lang), "url": BASE + SITE["langRoot"][lang],
                      "inLanguage": SITE["hreflang"][lang]}]
    elif typ == "product":
        out.append({"@context": "https://schema.org", "@type": "Product",
                    "name": title, "description": meta.get("description", ""), "url": u,
                    "image": BASE + SITE["ogImage"],
                    "brand": {"@type": "Brand", "name": t(SITE["brand"], lang)},
                    "manufacturer": {"@type": "Organization", "name": legal}})
    elif typ == "article":
        out.append({"@context": "https://schema.org", "@type": "Article",
                    "headline": meta.get("title", ""), "description": meta.get("description", ""),
                    "url": u, "image": BASE + SITE["ogImage"],
                    "inLanguage": SITE["hreflang"][lang],
                    "publisher": {"@type": "Organization", "name": legal,
                                  "logo": {"@type": "ImageObject", "url": BASE + "/assets/logo.png"}}})
    # 面包屑
    if rel != "index.html":
        SEC = {"products": {"zh": "产品中心", "en": "Products", "ru": "Продукция"},
               "industries": {"zh": "应用行业", "en": "Industries", "ru": "Отрасли"},
               "news": {"zh": "海狮动态", "en": "News", "ru": "Новости"},
               "manual": {"zh": "产品手册", "en": "Manuals", "ru": "Руководства"}}
        parts = [p for p in rel[:-5].split("/") if p and p != "index"]
        items = [{"@type": "ListItem", "position": 1, "name": t(SITE["ui"]["home"], lang),
                  "item": BASE + SITE["langRoot"][lang]}]
        acc = SITE["langRoot"][lang].rstrip("/")
        for i, seg in enumerate(parts, start=2):
            acc += "/" + seg
            nm = title if i - 1 == len(parts) else (t(SEC[seg], lang) if seg in SEC else seg.replace("-", " "))
            items.append({"@type": "ListItem", "position": i, "name": nm, "item": BASE + acc})
        if len(items) > 1:
            out.append({"@context": "https://schema.org", "@type": "BreadcrumbList",
                        "itemListElement": items})
    return out


# ---------- 面包屑与新闻上下篇 ----------
# 缘由：135 页有 BreadcrumbList 结构化数据（给搜索引擎看），页面上真正
# 看得见的面包屑只有 95 页。缺的 40 页里，32 页是新闻详情——而新闻恰恰
# 是自然流量的第一落点，访客从搜索结果直接落进来，页面上没有任何东西
# 告诉他这是哪个网站的哪一层，读完也只有"返回列表"一条出路。
import re as _re

_NEWS_ORDER = {}


def news_order(lang):
    """从新闻列表页解析出文章顺序与标题，列表页的排序就是权威顺序。"""
    if lang in _NEWS_ORDER:
        return _NEWS_ORDER[lang]
    path = os.path.join(ROOT, "src", "content", lang, "news.html")
    items = []
    if os.path.exists(path):
        txt = io.open(path, encoding="utf-8").read() if "io" in dir() else open(path, encoding="utf-8").read()
        seen = set()
        for m in _re.finditer(r'<h3><a href="([^"]+)">(.*?)</a></h3>', txt, _re.S):
            href, title = m.group(1), _re.sub(r"<[^>]+>", "", m.group(2)).strip()
            if href not in seen:
                seen.add(href)
                items.append((href, title))
    _NEWS_ORDER[lang] = items
    return items


def crumb_for(rel, lang, meta):
    """给没有手写面包屑的页面补一条。产品页等已有的不动。"""
    root = SITE["langRoot"][lang]
    home = t(SITE["ui"]["home"], lang) if "home" in SITE["ui"] else {"zh": "首页", "en": "Home", "ru": "Главная"}[lang]
    parts = rel.split("/")
    label = None
    parent = None
    # 页面自己在元数据里声明了归属，就按它来——拆栏目时新页只要写 crumb + parent
    if meta.get("crumb"):
        label = meta["crumb"]
        pa = meta.get("parent")
        if pa:
            href = pa["href"]
            if lang != "zh" and not href.startswith(f"/{lang}/"):
                href = f"/{lang}" + href
            parent = (href, pa["label"])
        mid = f'<a href="{parent[0]}">{H.escape(parent[1])}</a> / ' if parent else ""
        return (f'<nav class="crumb wrap"><a href="{root}">{H.escape(home)}</a> / '
                f'{mid}<span>{H.escape(label)}</span></nav>')
    if parts[0] == "news" and len(parts) > 1:
        parent = (f"{root}news.html", t(SITE["ui"]["newsSection"], lang)
                  if "newsSection" in SITE["ui"] else {"zh": "海狮动态", "en": "News", "ru": "Новости"}[lang])
        label = meta.get("crumb") or _re.sub(r"\s*[—|]\s*.*$", "", meta.get("title", "")).strip()
    elif parts[0] in ("pipe", "cable") and parts[-1] == "index.html":
        label = {"pipe": {"zh": "管道挤出事业部", "en": "Pipe Extrusion", "ru": "Экструзия труб"},
                 "cable": {"zh": "线缆挤出事业部", "en": "Cable Extrusion", "ru": "Экструзия кабеля"}}[parts[0]][lang]
    elif parts[0] == "manual":
        parent = (f"{root}manual/", {"zh": "产品手册", "en": "Manual", "ru": "Руководство"}[lang])
        label = meta.get("crumb") or _re.sub(r"\s*[—|]\s*.*$", "", meta.get("title", "")).strip()
        if parts[-1] == "index.html":
            parent, label = None, {"zh": "产品手册", "en": "Manual", "ru": "Руководство"}[lang]
    if not label:
        return ""
    mid = f'<a href="{parent[0]}">{H.escape(parent[1])}</a> / ' if parent else ""
    return (f'<nav class="crumb wrap"><a href="{root}">{H.escape(home)}</a> / '
            f'{mid}<span>{H.escape(label)}</span></nav>')


def news_updown(rel, lang):
    """上一篇 / 下一篇 / 回列表，外加两个事业部的去处——读完不能是死胡同。"""
    items = news_order(lang)
    if not items:
        return ""
    root = SITE["langRoot"][lang]
    # rel 是语种内的相对路径，列表页里的 href 是本地化全路径，这里补上语种前缀
    here = root.rstrip("/") + "/" + rel.lstrip("/")
    idx = next((i for i, (h, _) in enumerate(items) if h.rstrip("/") == here.rstrip("/")), None)
    if idx is None:
        return ""
    L = {"zh": ("上一篇", "下一篇", "全部动态", "看看我们的产品", "管道挤出", "线缆挤出"),
         "en": ("Previous", "Next", "All news", "Browse our systems", "Pipe extrusion", "Cable extrusion"),
         "ru": ("Предыдущая", "Следующая", "Все новости", "Наши системы", "Экструзия труб", "Экструзия кабеля")}[lang]
    out = ['<nav class="artnav wrap" aria-label="' + H.escape(L[2]) + '">']
    if idx > 0:
        h, ti = items[idx - 1]
        out.append(f'  <a class="artnav-i artnav-i--prev" href="{h}">'
                   f'<span>{L[0]}</span><b>{H.escape(ti)}</b></a>')
    if idx < len(items) - 1:
        h, ti = items[idx + 1]
        out.append(f'  <a class="artnav-i artnav-i--next" href="{h}">'
                   f'<span>{L[1]}</span><b>{H.escape(ti)}</b></a>')
    out.append('</nav>')
    out.append(f'<div class="artmore wrap"><span>{H.escape(L[3])}</span>'
               f'<a href="{root}pipe/">{H.escape(L[4])}</a>'
               f'<a href="{root}cable/">{H.escape(L[5])}</a>'
               f'<a href="{root}news.html">{H.escape(L[2])}</a></div>')
    return "\n".join(out)


def section_children(rel, lang):
    """栏目页末尾列出它的子栏目。

    栏目拆成独立页面之后，子页只能从导航下拉进；栏目页本身反而成了死胡同。
    这里按 site.json 的层级自动补一组入口，以后再拆栏目不用重复写。
    """
    root = SITE["langRoot"][lang]
    here = root.rstrip("/") + "/" + rel.lstrip("/")
    here = here.replace("/index.html", "/")
    for n in SITE["nav"]:
        kids = n.get("children", [])
        if not kids:
            continue
        base = n["href"].split("#")[0]
        base = root.rstrip("/") + base if lang != "zh" else base
        if base.rstrip("/") != here.rstrip("/"):
            continue
        # 只列这个语种真实存在的子页——俄语只做了 16 页，照单全列会造死链
        def exists(href):
            rp = href.split("#")[0].lstrip("/")
            if rp.endswith("/"):
                rp += "index.html"
            return os.path.exists(os.path.join(ROOT, "src", "content", lang, rp))
        kids = [c for c in kids if exists(c["href"])]
        if not kids:
            return ""
        L = {"zh": "本栏目", "en": "In this section", "ru": "В этом разделе"}[lang]
        out = [f'<nav class="subnav wrap" aria-label="{H.escape(L)}"><h2>{H.escape(L)}</h2><div class="subnav-l">']
        for c in kids:
            href = c["href"]
            if lang != "zh" and href.startswith("/") and not href.startswith(f"/{lang}/"):
                href = f"/{lang}" + href
            out.append(f'  <a href="{href}">{H.escape(t(c["label"], lang))}</a>')
        out.append("</div></nav>")
        return "\n".join(out)
    return ""


def render_header(lang, rel, alts, avail):
    root = SITE["langRoot"][lang]
    here = "/" + rel if not rel.startswith("/") else rel

    def cur(n):
        """本页就在这个栏目下时给它 aria-current，导航才有'我在哪'的提示。"""
        paths = [n["href"]] + [c["href"] for c in n.get("children", [])]
        for h in paths:
            base = h.split("#")[0]
            if base and base != "/" and here.startswith(base.rstrip("/") or "/"):
                return ' aria-current="page"'
        return ""

    marked = [False]

    def cur1(n):
        if marked[0]:
            return ""
        v = cur(n)
        if v:
            marked[0] = True
        return v

    def _has(href):
        rp = href.split("#")[0].lstrip("/")
        if rp.endswith("/"):
            rp += "index.html"
        return (not rp) or os.path.exists(os.path.join(ROOT, "src", "content", lang, rp))

    items = []
    for n in SITE["nav"]:
        if not exists_for(n["href"], lang, avail):
            continue
        label = H.escape(t(n["label"], lang))
        href = localize(n["href"], lang)
        kids = [c for c in (n.get("children") or []) if _has(c["href"])] or None
        if kids and any(exists_for(c["href"], lang, avail) for c in kids):
            kids = [c for c in kids if exists_for(c["href"], lang, avail)]
            sub = "\n".join(
                f'          <a href="{localize(c["href"], lang)}">{H.escape(t(c["label"], lang))}</a>'
                for c in kids)
            items.append(
                f'      <div class="nav-drop">\n'
                f'        <a href="{href}"{cur1(n)}>{label}</a>\n'
                f'        <div class="nav-drop-menu">\n{sub}\n        </div>\n'
                f'      </div>')
        else:
            items.append(f'      <a href="{href}"{cur1(n)}>{label}</a>')
    nav = "\n".join(items)
    # 语言切换：只列本页真实存在的其它语种
    # 语言做成导航里的一个栏目：当前语言 + 下拉，列出全称。
    lang_items = []
    for l2 in alts:
        url = page_url(l2, rel)[len(BASE):]
        mark = ' aria-current="true"' if l2 == lang else ""
        lang_items.append(
            f'          <a href="{url}" hreflang="{SITE["hreflang"][l2]}"{mark}>'
            f'{H.escape(SITE["langName"][l2])}</a>')
    switch = (
        '      <div class="nav-drop nav-lang">\n'
        f'        <button type="button" class="nav-lang-btn" aria-haspopup="true" aria-expanded="false">'
        f'{H.escape(SITE["langName"][lang])}</button>\n'
        '        <div class="nav-drop-menu">\n'
        + "\n".join(lang_items) + "\n"
        '        </div>\n'
        '      </div>')
    return f'''<header class="site-header" data-header>
  <div class="topbar">
    <div class="wrap topbar-in">
      <span class="welcome">{H.escape(t(SITE["ui"]["welcome"], lang))}</span>
      <div class="topbar-right">
        <a class="hotline" href="{SITE["hotlineHref"]}"><span class="dot"></span>{H.escape(t(SITE["ui"]["hotlineLabel"], lang))}：{SITE["hotline"]}</a>
      </div>
    </div>
  </div>
  <div class="wrap bar">
    <a class="brand" href="{root}" aria-label="{H.escape(t(SITE["ui"]["brandHome"], lang), quote=True)}">
      <img src="{ver("/assets/logo.png")}" alt="{H.escape(t(SITE["brand"], lang), quote=True)}" width="611" height="203">
    </a>
    <span class="slogan">{H.escape(t(SITE["ui"]["slogan"], lang))}</span>
    <button class="burger" type="button" aria-label="{H.escape(t(SITE["ui"]["menu"], lang), quote=True)}" aria-expanded="false" aria-controls="site-nav">
      <span></span><span></span><span></span>
    </button>
    <nav class="nav" id="site-nav" aria-label="{H.escape(t(SITE["ui"]["mainNav"], lang), quote=True)}">
{nav}
{switch}
    </nav>
  </div>
</header>'''


def render_footer(lang, avail):
    root = SITE["langRoot"][lang]
    cols = []
    for c in SITE["footerCols"]:
        links = "\n".join(
            f'        <a href="{localize(l["href"], lang)}">{H.escape(t(l["label"], lang))}</a>'
            for l in c["links"] if exists_for(l["href"], lang, avail))
        cols.append(f'      <div class="fcol">\n        <h4>{H.escape(t(c["title"], lang))}</h4>\n{links}\n      </div>')
    contact = (f'      <div class="fcol">\n'
               f'        <h4>{H.escape(t(SITE["ui"]["contact"], lang))}</h4>\n'
               f'        <a href="{SITE["hotlineHref"]}">{SITE["hotline"]}</a>\n'
               f'      </div>')
    return f'''<footer class="site-footer">
  <div class="wrap foot-grid">
    <div class="foot-brand">
      <strong>{H.escape(t(SITE["brand"], lang))}</strong>
      <span>{H.escape(t(SITE["legalName"], lang))}</span>
      <p class="fb-tag">{H.escape(t(SITE["tagline"], lang))}</p>
    </div>
{chr(10).join(cols)}
{contact}
  </div>
  <div class="wrap foot-btm">
    <span>© <span id="yr"></span> {H.escape(t(SITE["legalName"], lang))}</span>
  </div>
</footer>'''


def render_page(lang, rel, meta, body, alts, avail):
    head = render_head(lang, rel, meta, alts)
    header = render_header(lang, rel, alts, avail)
    footer = render_footer(lang, avail)
    skip = t(SITE["ui"]["skip"], lang)
    print_stamp = '<p class="print-stamp" data-print-stamp></p>'
    bodycls = "home" if meta.get("type") == "home" else ""
    crumb = "" if 'class="crumb"' in body else crumb_for(rel, lang, meta)
    updown = news_updown(rel, lang) if "news/" in ("/" + rel) and rel.count("news/") else ""
    updown = updown or ("" if 'class="pcard-grid"' in body else section_children(rel, lang))
    tail = [print_stamp,
            f'<script src="{ver("/assets/motion.js")}" defer></script>',
            f'<script src="{ver("/assets/print.js")}" defer></script>',
            '<script>document.getElementById(\'yr\').textContent=new Date().getFullYear();</script>',
            f'<script src="{ver("/assets/nav.js")}" defer></script>']
    if meta.get("type") == "home":
        tail.append(f'<script src="{ver("/assets/header-scroll.js")}" defer></script>')
    for j in meta.get("js", []):
        tail.append(f'<script src="{ver("/assets/" + j + ".js")}" defer></script>')
    btt = ""
    if meta.get("backToTop"):
        lbl = H.escape(t(SITE["ui"]["backToTop"], lang), quote=True)
        btt = (f'<button class="back-to-top" type="button" data-back-to-top aria-label="{lbl}" title="{lbl}">\n'
               f'  <svg viewBox="0 0 24 24" width="20" height="20" fill="none" aria-hidden="true">\n'
               f'    <path d="M12 19V5m-6 6 6-6 6 6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>\n'
               f'  </svg>\n</button>')
    return f'''<!DOCTYPE html>
<html lang="{SITE["htmlLang"][lang]}">
<script>document.documentElement.className+=" js";</script>
<head>
{WARN}{head}
</head>
<body class="{bodycls}">
<a href="#main" class="sr-only">{H.escape(skip)}</a>
{header}
<main id="main" tabindex="-1">
{crumb}
{body}
{updown}
</main>
{footer}
{btt}
{chr(10).join(tail)}
</body>
</html>
'''


# ---------- 主流程 ----------
def main():
    # 每页在哪些语种下存在
    exists = {}
    for lang in LANGS:
        for f in glob.glob(f"src/content/{lang}/**/*.html", recursive=True):
            rel = f[len(f"src/content/{lang}/"):]
            exists.setdefault(rel, []).append(lang)

    avail = {}
    for lang in LANGS:
        avail[lang] = {f[len(f"src/content/{lang}/"):]
                       for f in glob.glob(f"src/content/{lang}/**/*.html", recursive=True)}

    n = standalone = 0
    for rel, langs in sorted(exists.items()):
        alts = [l for l in LANGS if l in langs]
        for lang in alts:
            meta, body = load(f"src/content/{lang}/{rel}")
            out = page_path(lang, rel)
            os.makedirs(os.path.dirname(out), exist_ok=True)
            if meta.get("standalone"):
                open(out, "w", encoding="utf-8").write(body)
                standalone += 1
                continue
            open(out, "w", encoding="utf-8").write(render_page(lang, rel, meta, body, alts, avail))
            n += 1

    # sitemap
    urls = []
    for rel, langs in sorted(exists.items()):
        if rel == "404.html":
            continue
        alts = [l for l in LANGS if l in langs]
        for lang in alts:
            u = page_url(lang, rel)
            lm = git_date(f"src/content/{lang}/{rel}")
            alt = "".join(
                f'\n    <xhtml:link rel="alternate" hreflang="{SITE["hreflang"][l2]}" href="{page_url(l2, rel)}"/>'
                for l2 in alts)
            if "zh" in alts:
                alt += f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{page_url("zh", rel)}"/>'
            urls.append(f"  <url>\n    <loc>{u}</loc>{alt}" +
                        (f"\n    <lastmod>{lm}</lastmod>" if lm else "") + "\n  </url>")
    open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + "\n".join(urls) + "\n</urlset>\n")

    print(f"生成 {n} 页（含独立页 {standalone}），sitemap {len(urls)} 条 → {OUT}/")
    per = {}
    for rel, langs in exists.items():
        for l in langs:
            per[l] = per.get(l, 0) + 1
    print("  " + " | ".join(f"{k}: {v} 页" for k, v in sorted(per.items())))


if __name__ == "__main__":
    main()
