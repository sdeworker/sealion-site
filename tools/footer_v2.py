# -*- coding: utf-8 -*-
"""三件事，全部按参考站的做法，并且做成全站生效而不是只改一页

一、页脚重做
   参考站页脚是两层：上层一句「了解更多产品信息／咨询其他」配一个「联系我们」按钮，
   下层是按主导航分的四列链接 + 二维码 + 版权。
   我们现在的页脚是品牌名 + 一行挤在一起的链接，没有分栏。
   直接从 site.json 的 nav 生成四列——以后导航一改，页脚跟着改，不用维护两份。

二、栏目眉题放大
   「发展历程」「资质荣誉」「合作客户」这些是每一节的名字，此前走 --step--1（15–17px），
   比正文还小。参考站这一层是明显能看见的。改到 --step-1 并加粗。
   这是全站样式，一改所有页面都跟着变。

三、企业简介去掉配图
   参考站这一节就是标题居中 + 一块文字，没有配图。
"""
import io, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── 一、页脚 ────────────────────────────────────────────────
b = io.open(os.path.join(ROOT, "tools", "build.py"), encoding="utf-8").read()

old_start = b.index("def render_footer(lang, avail):")
old_end = b.index("def render_page(")
NEW_FOOTER = '''def render_footer(lang, avail):
    """页脚：上层一句话 + 联系按钮，下层按主导航分栏。

    分栏直接从 SITE["nav"] 生成——导航改了页脚自动跟上，
    不必维护第二份链接表（此前 footerCols 就是第二份，一直在漂）。
    """
    root = SITE["langRoot"][lang]
    L = {
        "zh": ("了解更多产品信息", "咨询其他", "联系我们", "服务热线", "地址"),
        "en": ("More about our systems", "Ask us anything", "Contact us", "Hotline", "Address"),
        "ru": ("Подробнее о системах", "Задать вопрос", "Свяжитесь с нами", "Горячая линия", "Адрес"),
    }[lang]

    cols = []
    for n in SITE["nav"]:
        kids = [c for c in n.get("children", []) if exists_for(c["href"], lang, avail)]
        if not kids:
            continue
        links = "\\n".join(
            f'          <a href="{localize(c["href"], lang)}">{H.escape(t(c["label"], lang))}</a>'
            for c in kids)
        cols.append(
            f'        <div class="fcol">\\n'
            f'          <h4><a href="{localize(n["href"], lang)}">{H.escape(t(n["label"], lang))}</a></h4>\\n'
            f'{links}\\n        </div>')

    contact_href = localize("/contact.html", lang) if exists_for("/contact.html", lang, avail) else SITE["hotlineHref"]
    addr = t(SITE.get("address", {"zh": "", "en": "", "ru": ""}), lang)
    return f\'\'\'<footer class="site-footer">
  <div class="foot-cta">
    <div class="wrap foot-cta-in">
      <p>{H.escape(L[0])}<br>{H.escape(L[1])}</p>
      <a class="btn btn--primary" href="{contact_href}">{H.escape(L[2])}</a>
    </div>
  </div>
  <div class="wrap foot-cols">
{chr(10).join(cols)}
        <div class="fcol fcol--contact">
          <h4>{H.escape(L[2])}</h4>
          <a href="{SITE["hotlineHref"]}">{SITE["hotline"]}</a>
          <a href="mailto:{SITE.get("email", "2428582102@qq.com")}">{SITE.get("email", "2428582102@qq.com")}</a>
          {'<span class="fc-addr">' + H.escape(addr) + '</span>' if addr else ''}
        </div>
  </div>
  <div class="foot-btm">
    <div class="wrap foot-btm-in">
      <span>© <span id="yr"></span> {H.escape(t(SITE["legalName"], lang))}</span>
      <span class="fb-icp">{SITE.get("icp", "")}</span>
    </div>
  </div>
</footer>\'\'\'


'''
b = b[:old_start] + NEW_FOOTER + b[old_end:]
io.open(os.path.join(ROOT, "tools", "build.py"), "w", encoding="utf-8").write(b)
print("  build.py：页脚改为 CTA 条 + 按导航分栏")

# ── 二、企业简介去配图 ──────────────────────────────────────
for lang in ("zh", "en"):
    p = os.path.join(ROOT, "src", "content", lang, "about.html")
    s = io.open(p, encoding="utf-8").read()
    h, sep, body = s.partition("\n---\n")
    if 'class="ab-fig"' not in body:
        print(f"  {lang} 简介已无配图")
        continue
    body = re.sub(r'\s*<figure class="ab-fig">.*?</figure>', "", body, flags=re.S, count=1)
    body = body.replace('<div class="ab-grid ab-grid--plain">', '<div class="ab-plain">', 1)
    io.open(p, "w", encoding="utf-8").write(h + sep + body)
    print(f"  {lang} 企业简介去掉配图")

# ── 三、样式 ────────────────────────────────────────────────
S = os.path.join(ROOT, "public", "style.css")
s = io.open(S, encoding="utf-8").read()

# 眉题放大：这一层是每节的名字，此前比正文还小
old = ".eyebrow{font-family:var(--body);font-size:var(--step--1);"
new = ".eyebrow{font-family:var(--body);font-size:var(--step-1);font-weight:600;"
assert s.count(old) == 1, "eyebrow 锚点"
s = s.replace(old, new, 1)

A = "/* a11y + motion */"
CSS = """/* 企业简介：照参考站收成一栏——标题居中带下划线，正文一块读完，不配图 */
.ab-plain{max-width:62rem;margin-inline:auto;text-align:center}
.ab-plain h2{display:inline-block;position:relative;padding-bottom:.7rem;margin-bottom:var(--sp-1)}
.ab-plain h2::after{content:"";position:absolute;left:50%;transform:translateX(-50%);bottom:0;
  width:4rem;height:3px;background:var(--blue);border-radius:2px}
.ab-plain p{max-width:none;text-align:left;color:var(--ink-70)}
.ab-plain .lead{color:var(--ink)}

/* ============ 页脚：上层一句话 + 联系按钮，下层按导航分栏 ============ */
.foot-cta{background:var(--mist);border-top:1px solid var(--line)}
.foot-cta-in{display:flex;align-items:center;justify-content:space-between;gap:1.5rem;
  padding-block:var(--sp-2);flex-wrap:wrap}
.foot-cta p{margin:0;font-family:var(--display);font-weight:600;line-height:1.35;
  font-size:var(--step-4);color:var(--ink)}
.foot-cols{display:grid;grid-template-columns:repeat(auto-fit,minmax(11rem,1fr));
  gap:clamp(1.5rem,3vw,3rem);padding-block:var(--sp-3) var(--sp-2)}
.fcol{display:flex;flex-direction:column;gap:.75rem}
.fcol h4{margin:0 0 .35rem;font-size:var(--step-1);color:var(--ink)}
.fcol h4 a{color:inherit}
.fcol h4 a:hover{color:var(--blue)}
.fcol a{color:var(--steel);font-size:1.0625rem;transition:color .15s}
.fcol a:hover{color:var(--blue)}
.fc-addr{color:var(--steel);font-size:1rem;line-height:1.5}
.foot-btm{border-top:1px solid var(--line);background:var(--paper)}
.foot-btm-in{display:flex;flex-wrap:wrap;justify-content:space-between;gap:.75rem;
  padding-block:1.25rem;color:var(--steel);font-size:1rem}
.site-footer{background:var(--paper);color:var(--ink)}
@media(max-width:760px){
  .foot-cta p{font-size:var(--step-2)}
  .foot-cols{grid-template-columns:repeat(2,1fr);row-gap:2rem}}

"""
assert s.count(A) == 1
io.open(S, "w", encoding="utf-8").write(s.replace(A, CSS + A, 1))
print("  style.css：眉题放大到 --step-1、简介一栏、页脚新样式")
