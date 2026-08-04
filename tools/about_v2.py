# -*- coding: utf-8 -*-
"""关于海狮：照沃思的做法重做

沃思 /about 的骨架：
  hero-section    整幅横幅图 + 「关于沃思 / About us」大标题压在图上
  intro-section   about-layout 图文并排，不是一整块文字
  timeline        is-animated is-clickable，会动、可点
  企业文化 / 资质荣誉 / 合作客户

我上一版只做了"合并成一页"，排版还是一整块文字居中——参考图摆在眼前没抄到位。
这次补上：横幅、图文并排、时间轴动起来。

同时去掉两处冗余：
  · 页尾「本栏目」入口——五项现在是本页锚点，页尾再列一遍是重复
  · 「海狮成长 展会、认证与全球客户」——它的四张卡说的是展会、
    海外客户、培训、证书，而这四件事在资质荣誉与合作客户两节里都有
"""
import io, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(p):
    s = io.open(p, encoding="utf-8").read()
    h, sep, b = s.partition("\n---\n")
    if not sep:
        sys.exit(f"✗ {p} 缺分隔符")
    return json.loads(h), b


def save(p, m, b):
    io.open(p, "w", encoding="utf-8").write(
        json.dumps(m, ensure_ascii=False, indent=1) + "\n---\n" + b)


def cut(body, sid):
    m = re.search(r'<section[^>]*\bid="%s"[^>]*>' % re.escape(sid), body)
    if not m:
        return None, body
    st = m.start()
    depth = 0
    end = None
    for mm in re.finditer(r"</?section\b", body[st:]):
        depth += 1 if mm.group(0) == "<section" else -1
        if depth == 0:
            end = st + mm.end()
            break
    while end < len(body) and body[end] in ">\n":
        end += 1
    return body[st:end], body[:st] + body[end:]


T = {
    "zh": dict(
        banner_eb="About us", banner_h="关于海狮",
        eyebrow="关于海狮", h1="一家挤出行业的工业控制企业",
        p1="广州海狮软件科技有限公司成立于 2008 年，是集研发、生产、销售于一体的国家高新技术企业。"
           "产品覆盖塑料管道、电线电缆、医疗导管、薄膜片材、色母改性等行业，技术链从硬件 EDA、"
           "底层 DSP，到 ARM 与上位机软件、电气控制、PLC 编程与机械设计——整条链自己走通，不做集成商。",
        p2="公司持有 60 项知识产权，权利人都是海狮自己；通过 ISO9001 质量管理体系、知识产权管理体系"
           "与 CE 认证，四次获评国家高新技术企业，并获「专精特新」「科技创新小巨人」「瞪羚企业」等称号。",
        p3="2009 年做出第一台米重控制系统，2010 年做出第一台超声波在线测厚系统——此后十几年的产品线"
           "都长在这两件事上。系统已装在国内外客户的产线上，从售前选型、现场安装调试到操作培训与备件供应，"
           "服务体系一路跟到底。",
        figcap="广州科学城研发中心",
        stats=[("2008", "年成立"), ("60", "项知识产权"), ("4", "次高新认定"), ("18", "家长期客户")],
    ),
    "en": dict(
        banner_eb="About us", banner_h="About Sealion",
        eyebrow="About Sealion", h1="An industrial control company in extrusion",
        p1="Founded in 2008, Guangzhou Sealion Software Technology develops, builds and sells its own "
           "systems. They run on lines making plastic pipe, wire and cable, medical catheter, film and "
           "sheet, masterbatch and compounds. The chain is in house — hardware EDA, DSP firmware, ARM "
           "and host software, electrical control, PLC programming and mechanical design.",
        p2="Sixty patents and copyrights, all held by Sealion. ISO9001, IP management certification and "
           "CE marking, with National High-Tech Enterprise status awarded four times.",
        p3="The first gravimetric control system was built in 2009 and the first ultrasonic gauge in "
           "2010; everything since has grown out of those two. Selection, commissioning, operator "
           "training and spares follow the system onto the line.",
        figcap="R&D centre, Guangzhou Science City",
        stats=[("2008", "founded"), ("60", "patents"), ("4", "high-tech awards"), ("18", "customers")],
    ),
}

for lang in ("zh", "en"):
    p = os.path.join(ROOT, "src", "content", lang, "about.html")
    meta, body = load(p)
    if "about-banner" in body:
        print(f"  {lang} 已改过，跳过")
        continue

    # 去掉「海狮成长」整节
    g, body = cut(body, "growth")
    print(f"  {lang} 去掉海狮成长节（{len(g) if g else 0} 字符）")

    # 简介改成图文并排 + 数字条
    old, body = cut(body, "about")
    t = T[lang]
    stats = "".join(
        f'<div class="ab-s"><b>{n}</b><span>{u}</span></div>' for n, u in t["stats"])
    intro = (
        f'  <section class="about-banner">\n'
        f'    <img src="/assets/tech/research-knowledge-city.jpg" alt="{t["figcap"]}"\n'
        f'         width="1440" height="985" fetchpriority="high">\n'
        f'    <div class="about-banner-in wrap">\n'
        f'      <span class="eyebrow">{t["banner_eb"]}</span>\n'
        f'      <h1>{t["banner_h"]}</h1>\n'
        f'    </div>\n'
        f'  </section>\n\n'
        f'  <section data-reveal class="section intro-sec" id="about">\n'
        f'    <div class="wrap">\n'
        f'      <div class="ab-grid">\n'
        f'        <div class="ab-copy">\n'
        f'          <span class="eyebrow">{t["eyebrow"]}</span>\n'
        f'          <h2>{t["h1"]}</h2>\n'
        f'          <p class="lead">{t["p1"]}</p>\n'
        f'          <p>{t["p2"]}</p>\n'
        f'          <p>{t["p3"]}</p>\n'
        f'        </div>\n'
        f'        <figure class="ab-fig">\n'
        f'          <img src="/assets/2026/video/company-intro-poster.webp" alt="{t["figcap"]}"\n'
        f'               loading="lazy" width="1920" height="1080">\n'
        f'          <figcaption>{t["figcap"]}</figcaption>\n'
        f'        </figure>\n'
        f'      </div>\n'
        f'      <div class="ab-stats">{stats}</div>\n'
        f'    </div>\n'
        f'  </section>\n\n')
    body = intro + body

    # 时间轴：加可点年份与自动推进的钩子
    body = body.replace('<div class="tl" data-timeline>',
                        '<div class="tl" data-timeline>\n        '
                        '<div class="tl-nav" data-tl-nav aria-hidden="true"></div>', 1)
    meta["js"] = sorted(set(meta.get("js", []) + ["motion"]))
    save(p, meta, body)
    print(f"  {lang}/about.html 重排完成（{len(body)} 字符）")

# 页尾「本栏目」：子项是同页锚点时不再列
b = io.open(os.path.join(ROOT, "tools", "build.py"), encoding="utf-8").read()
a = '        if len(kids) > 9:'
if a in b:
    b = b.replace(a, '        if all("#" in c["href"] for c in kids):\n'
                     '            return ""   # 子项是本页锚点，页尾再列一遍是重复\n' + a, 1)
else:
    a2 = '        kids = [c for c in n.get("children", []) if exists(c["href"])]'
    assert b.count(a2) == 1, "section_children 锚点"
    b = b.replace(a2, a2 + '\n        if kids and all("#" in c["href"] for c in kids):\n'
                          '            return ""   # 子项是本页锚点，页尾再列一遍是重复', 1)
io.open(os.path.join(ROOT, "tools", "build.py"), "w", encoding="utf-8").write(b)
print("  build.py：锚点型子栏目不再生成页尾「本栏目」")
