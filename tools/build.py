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
            h = hashlib.md5(open(fp, "rb").read()).hexdigest()[:8]
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
    o.append(f'<link rel="stylesheet" href="{ver("/style.css")}">')
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

    items = []
    for n in SITE["nav"]:
        if not exists_for(n["href"], lang, avail):
            continue
        label = H.escape(t(n["label"], lang))
        href = localize(n["href"], lang)
        kids = n.get("children")
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
    switch = "\n".join(
        f'      <a class="langlink" href="{page_url(l2, rel)[len(BASE):]}" hreflang="{SITE["hreflang"][l2]}">{H.escape(SITE["langLabel"][l2])}</a>'
        for l2 in alts if l2 != lang)
    return f'''<header class="site-header" data-header>
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
               f'        <a href="{SITE["phoneHref"]}">{SITE["phone"]}</a>\n'
               f'        <a href="mailto:{SITE["email"]}">{SITE["email"]}</a>\n'
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
    bodycls = "home" if meta.get("type") == "home" else ""
    tail = ['<script>document.getElementById(\'yr\').textContent=new Date().getFullYear();</script>',
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
<head>
{WARN}{head}
</head>
<body class="{bodycls}">
<a href="#main" class="sr-only">{H.escape(skip)}</a>
{header}
<main id="main">
{body}
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
