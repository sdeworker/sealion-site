# -*- coding: utf-8 -*-
"""每个大栏目一张封面图，栏目名压在图上——照参考站的做法

参考站每个一级栏目进去先是一整幅相关实景，栏目名压在图正中。
我们现在是一条面包屑加一行小字眉题，没有画面。

同时去掉两样：栏目页顶部的面包屑（一级页面不需要路径，导航已高亮），
以及那行与横幅重复的眉题。
"""
import io, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 栏目 → 封面图（挑与该栏目内容最贴的一张宽幅实景）
BANNER = {
    "pipe/index.html":       ("/assets/2026/industry/pipe-assorted.webp", "管道挤出事业部", "Pipe Extrusion"),
    "cable/index.html":      ("/assets/apply/cable-dark-industrial-hd.jpg", "线缆挤出事业部", "Cable Extrusion"),
    "strength.html":         ("/assets/2026/quality-storage/site-1.webp", "海狮实力", "Capability"),
    "cases.html":            ("/assets/cases/sealion-gravimetric-coextrusion-hd.jpg", "案例展示", "Cases"),
    "news.html":             ("/assets/2026/video/company-intro-poster.webp", "海狮动态", "News"),
    "service.html":          ("/assets/service/onsite.jpg", "售后与服务", "Service"),
    "contact.html":          ("/assets/tech/research-knowledge-city.jpg", "联系我们", "Contact"),
    "industries/index.html": ("/assets/apply/water-pipe.jpg", "应用行业", "Industries"),
    "applications.html":     ("/assets/apply/gas-pipe.jpg", "产品应用", "Applications"),
    "technology.html":       ("/assets/tech/research.jpg", "技术实力", "Technology"),
    "ip.html":               ("/assets/certs/aaa-credit.jpg", "知识产权", "Patents"),
    "manual/index.html":     ("/assets/2026/core/core-quality-storage.webp", "产品手册", "Manual"),
}
EN_TITLE = {v[1]: v[2] for v in BANNER.values()}


def load(p):
    s = io.open(p, encoding="utf-8").read()
    h, sep, b = s.partition("\n---\n")
    if not sep:
        return None, None
    return json.loads(h), b


def save(p, m, b):
    io.open(p, "w", encoding="utf-8").write(
        json.dumps(m, ensure_ascii=False, indent=1) + "\n---\n" + b)


for lang in ("zh", "en", "ru"):
    for rel, (img, zh, en) in BANNER.items():
        p = os.path.join(ROOT, "src", "content", lang, rel)
        if not os.path.exists(p):
            continue
        if not os.path.exists(os.path.join(ROOT, "public") + img):
            print(f"  ✗ 缺图 {img}")
            continue
        meta, body = load(p)
        if meta is None or "sec-banner" in body:
            continue
        title = zh if lang == "zh" else en
        # 去掉顶部只有路径的面包屑节，以及与栏目名重复的眉题
        body = re.sub(r'\s*<section class="section prod-hero"><div class="wrap">\s*'
                      r'<nav class="crumb">.*?</nav>\s*</div></section>\s*', "\n", body, flags=re.S)
        body = re.sub(r'\s*<nav class="crumb">.*?</nav>', "", body, count=1, flags=re.S)
        body = re.sub(r'\s*<span class="eyebrow">%s</span>' % re.escape(title), "", body, count=1)
        banner = (f'  <section class="sec-banner">\n'
                  f'    <img src="{img}" alt="{title}" width="1600" height="900" fetchpriority="high">\n'
                  f'    <div class="sec-banner-in"><h1>{title}</h1></div>\n'
                  f'  </section>\n\n')
        # 原页面若已有 h1，降为 h2——一页只留横幅这一个 h1
        first = body.find("<h1")
        if first >= 0:
            body = re.sub(r"<h1([^>]*)>(.*?)</h1>", r"<h2\1>\2</h2>", body, count=1, flags=re.S)
        save(p, meta, banner + body.lstrip("\n"))
        print(f"  {lang}/{rel} 加封面：{img.rsplit('/', 1)[-1]}")

# ── CSS ────────────────────────────────────────────────────
S = os.path.join(ROOT, "public", "style.css")
s = io.open(S, encoding="utf-8").read()
A = "/* a11y + motion */"
CSS = """/* 栏目封面：一整幅实景，栏目名压在正中。参考站每个一级栏目都是这样开场的。 */
.sec-banner{position:relative;min-height:clamp(17rem,26vw,24rem);overflow:hidden;
  background:var(--ink);display:flex;align-items:center;justify-content:center}
.sec-banner img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:.62}
.sec-banner::after{content:"";position:absolute;inset:0;
  background:linear-gradient(180deg,rgba(10,26,38,.42),rgba(10,26,38,.62))}
.sec-banner-in{position:relative;z-index:2;text-align:center;padding-inline:var(--gutter)}
.sec-banner h1{color:#fff;margin:0;font-size:clamp(2.25rem,1.6rem + 2.6vw,3.75rem);
  letter-spacing:.04em;text-shadow:0 2px 18px rgba(0,0,0,.35)}

"""
assert s.count(A) == 1
io.open(S, "w", encoding="utf-8").write(s.replace(A, CSS + A, 1))
print("  style.css：栏目封面样式")
