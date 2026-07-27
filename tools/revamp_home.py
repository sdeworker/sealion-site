# -*- coding: utf-8 -*-
"""
首页改版：按 B 端采购决策路径重排，并把挤在首页里的内容拆成独立页
  拆出：/about（公司）· /cases（案例与客户）· /news（动态）· /service（服务）
  首页保留：hero → 事业部分岔 → 产品 → 行业 → 省料测算 → 案例摘要 → 动态摘要 → 联系
"""
import json, os, re

LANGS = ("zh", "en")

TXT = {
    "zh": {
        "about_title": "关于海狮 — 海狮科技",
        "about_desc": "广州海狮软件科技：十六年专注塑料挤出测控，自主研发米重、色母、超声波测厚与在线检测系统，60 项专利与软件著作权。",
        "cases_title": "案例与客户 — 海狮科技",
        "cases_desc": "海狮测控系统在真实产线上的 26 组现场记录，以及 18 家长期合作客户。",
        "news_title": "海狮动态 — 海狮科技",
        "news_desc": "海狮科技公司动态、产品发布与历年橡塑展参展记录。",
        "service_title": "服务与支持 — 海狮科技",
        "service_desc": "海狮的服务从进厂那天算起：产品培训、现场安装指导、终身维护与二年免费保修。",
        "div_eyebrow": "从这里开始",
        "div_h2": "你的产线，挤的是管还是线缆？",
        "div_lead": "两条产线的测量难处不一样：管材可以切开量壁厚，线缆护套不行；管材按根交货，线缆按盘。所以我们把产品按事业部分开讲，你直接进对应的那一边。",
        "pipe_name": "管道挤出事业部",
        "pipe_line": "PE 给水管、燃气管、PPR、PVC、波纹管产线",
        "pipe_meta": "8 套系统 · 米重 / 色母 / 超声波测厚 / 质量入库 / 在线检测",
        "cable_name": "线缆挤出事业部",
        "cable_line": "电缆护套、绝缘层、医疗导管产线",
        "cable_meta": "5 套系统 · 米重 / 色母 / 细径测厚 / 云端监控",
        "enter": "进入",
        "more": "查看全部",
        "back_home": "返回首页",
    },
    "en": {
        "about_title": "About Sealion — Sealion Tech",
        "about_desc": "Guangzhou Sealion Software Technology: sixteen years in measurement and control for plastics extrusion, with 60 patents and software copyrights behind our gravimetric, masterbatch, ultrasonic and inspection systems.",
        "cases_title": "Cases & customers — Sealion Tech",
        "cases_desc": "Twenty-six records of Sealion systems on real production lines, and the eighteen customers who keep them running.",
        "news_title": "News — Sealion Tech",
        "news_desc": "Company news, product releases and our record at the Chinaplas exhibitions.",
        "service_title": "Service & support — Sealion Tech",
        "service_desc": "Our service starts the day the system arrives: training, on-site commissioning, lifetime maintenance and a two-year warranty.",
        "div_eyebrow": "Start here",
        "div_h2": "Is your line running pipe, or cable?",
        "div_lead": "The measurement problem differs. You can cut a pipe open to check the wall; you cannot do that to a sheath. Pipe ships by the length, cable by the drum. So the products are split by division — go straight to the side that matches your line.",
        "pipe_name": "Pipe Extrusion Division",
        "pipe_line": "PE water and gas pipe, PPR, PVC, corrugated pipe",
        "pipe_meta": "8 systems · gravimetric / masterbatch / ultrasonic / inbound quality / inspection",
        "cable_name": "Cable Extrusion Division",
        "cable_line": "Cable sheathing, insulation, medical tubing",
        "cable_meta": "5 systems · gravimetric / masterbatch / fine-bore gauging / cloud monitoring",
        "enter": "Enter",
        "more": "See all",
        "back_home": "Back to home",
    },
}

# 首页新顺序（B 端决策路径）；括号内为原区块 id
HOME_ORDER = ["hero", "__divisions__", "products", "apply", "apply-detail",
              "calc", "__cases_teaser__", "partners", "__news_teaser__", "contact"]
# 迁出到独立页
TO_ABOUT = ["about", "growth", "culture", "milestones", "techstr", "certs"]
TO_CASES = ["cases"]
TO_NEWS = ["news"]
TO_SERVICE = ["service"]


def split_sections(body):
    """把正文按顶层 <section> 切成 {id: html}，保持顺序"""
    idx = [m.start() for m in re.finditer(r"<section\b", body)]
    idx.append(len(body))
    out = []
    for i in range(len(idx) - 1):
        seg = body[idx[i]:idx[i + 1]]
        m = re.search(r'id="([^"]*)"', seg[:220])
        out.append(((m.group(1) if m else "hero"), seg.rstrip() + "\n"))
    return out


def page(meta, body):
    return json.dumps(meta, ensure_ascii=False, indent=1) + "\n---\n" + body.strip("\n") + "\n"


def divisions_block(lang):
    T = TXT[lang]
    root = "/" if lang == "zh" else "/en/"
    return f'''<section class="section divisions" id="divisions"><div class="wrap">
  <div class="sh">
    <span class="eyebrow">{T["div_eyebrow"]}</span>
    <h2>{T["div_h2"]}</h2>
    <p class="lead">{T["div_lead"]}</p>
  </div>
  <div class="div-grid">
    <a class="div-card" href="{root}pipe/">
      <img src="/assets/2026/industry/pipe-pe-1.webp" alt="{T["pipe_name"]}" width="1600" height="900" loading="lazy">
      <div class="div-body">
        <h3>{T["pipe_name"]}</h3>
        <p>{T["pipe_line"]}</p>
        <span class="div-meta">{T["pipe_meta"]}</span>
        <span class="arrow-link">{T["enter"]} &rarr;</span>
      </div>
    </a>
    <a class="div-card" href="{root}cable/">
      <img src="/assets/2026/industry/cable-1.webp" alt="{T["cable_name"]}" width="1600" height="900" loading="lazy">
      <div class="div-body">
        <h3>{T["cable_name"]}</h3>
        <p>{T["cable_line"]}</p>
        <span class="div-meta">{T["cable_meta"]}</span>
        <span class="arrow-link">{T["enter"]} &rarr;</span>
      </div>
    </a>
  </div>
</div></section>
'''


def extract_items(html, tag, cls, n):
    """按标签配对精确提取前 n 个 <tag class="cls..."> 块"""
    out=[]; pos=0
    open_re=re.compile(r'<%s\b[^>]*class="%s(?:[ "])' % (tag, cls))
    any_re=re.compile(r'<(/?)%s\b' % tag)
    while len(out)<n:
        m=open_re.search(html,pos)
        if not m: break
        i=m.start(); depth=0; j=i
        for mm in any_re.finditer(html,i):
            depth += -1 if mm.group(1) else 1
            j=mm.end()
            if depth==0:
                j=html.find('>',mm.start())+1
                break
        out.append(html[i:j]); pos=j
    return out


def teaser(sec_html, lang, href, keep_items, tag, item_cls, grid_cls):
    T = TXT[lang]
    opentag = re.search(r'<section[^>]*>\s*<div class="wrap[^"]*">', sec_html)
    opentag = opentag.group(0) if opentag else '<section class="section"><div class="wrap">'
    sh = re.search(r'<div class="sh".*?</div>\s*(?=<)', sec_html, re.S)
    sh = sh.group(0) if sh else ""
    items = extract_items(sec_html, tag, item_cls, keep_items)
    if not items:
        print(f"    ⚠ {item_cls} 摘要裁不出条目，原样保留该区块")
        return sec_html
    inner = "\n".join(x.rstrip() for x in items)
    return (f'{opentag}\n{sh}\n  <div class="{grid_cls}">\n{inner}\n  </div>\n'
            f'  <p class="lead" style="margin-top:1.6rem">'
            f'<a class="arrow-link" href="{href}">{T["more"]} &rarr;</a></p>\n</div></section>\n')

for lang in LANGS:
    src = f"src/content/{lang}/index.html"
    raw = open(src, encoding="utf-8").read()
    meta_s, _, body = raw.partition("\n---\n")
    meta = json.loads(meta_s)
    secs = dict(split_sections(body))
    T = TXT[lang]
    root = "/" if lang == "zh" else "/en/"

    # ---- 拆出独立页 ----
    def make(fname, ids, title, desc):
        blocks = [secs[i] for i in ids if i in secs]
        if not blocks:
            return
        crumb = (f'<section class="section prod-hero"><div class="wrap">\n'
                 f'  <nav class="crumb"><a href="{root}">{TXT[lang]["back_home"]}</a></nav>\n'
                 f'</div></section>\n')
        open(f"src/content/{lang}/{fname}", "w", encoding="utf-8").write(
            page({"title": title, "description": desc, "css": ["product"], "type": "page"},
                 crumb + "\n".join(blocks)))

    make("about.html", TO_ABOUT, T["about_title"], T["about_desc"])
    make("cases.html", TO_CASES, T["cases_title"], T["cases_desc"])
    make("news.html", TO_NEWS, T["news_title"], T["news_desc"])
    make("service.html", TO_SERVICE, T["service_title"], T["service_desc"])

    # ---- 重排首页 ----
    parts = []
    for key in HOME_ORDER:
        if key == "__divisions__":
            parts.append(divisions_block(lang))
        elif key == "__cases_teaser__":
            if "cases" in secs:
                parts.append(teaser(secs["cases"], lang, f"{root}cases.html", 6, "article", "case", "case-grid"))
        elif key == "__news_teaser__":
            if "news" in secs:
                parts.append(teaser(secs["news"], lang, f"{root}news.html", 3, "article", "nw", "nw-grid"))
        elif key in secs:
            parts.append(secs[key])

    open(src, "w", encoding="utf-8").write(page(meta, "\n".join(parts)))
    print(f"  {lang}: 首页 {len(body)/1024:.0f}KB → {sum(len(p) for p in parts)/1024:.0f}KB，"
          f"拆出 about/cases/news/service 四页")
