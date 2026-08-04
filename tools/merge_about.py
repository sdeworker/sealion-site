# -*- coding: utf-8 -*-
"""关于海狮：六页合并回一页多锚点，发展历程改横向时间轴

沃思 /about 是一页五块（横幅 → 公司介绍 → 横向时间轴 → 企业文化 → 客户），
导航下拉四项是同一页的锚点。对"关于"这类叙事型内容这样更合适：
客户想了解一家公司时是连着读的，不是挑着读的。

我们此前按"栏目独立成页"的原则拆成了六页——那条原则对产品与案例成立，
对"关于"不成立。这次改回来。

沃思的公司介绍只有三段约 380 字，最后一段给出细分市场地位。
我们的两千多字砍到 400 字以内，长的部分留在各自的锚点区里。
"""
import io, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(p):
    s = io.open(p, encoding="utf-8").read()
    h, sep, b = s.partition("\n---\n")
    if not sep:
        sys.exit(f"✗ {p} 缺元数据分隔符")
    return json.loads(h), b


def save(p, m, b):
    os.makedirs(os.path.dirname(p), exist_ok=True)
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


# ── 精简后的公司介绍：三段，对标沃思的写法 ──────────────────
INTRO = {
    "zh": {
        "eyebrow": "关于海狮",
        "h1": "一家挤出行业的工业控制企业",
        "p1": "广州海狮软件科技有限公司成立于 2008 年，是集研发、生产、销售于一体的国家高新技术企业。"
              "产品覆盖塑料管道、电线电缆、医疗导管、薄膜片材、色母改性等行业，"
              "技术链从硬件 EDA、底层 DSP，到 ARM 与上位机软件、电气控制、PLC 编程与机械设计——"
              "整条链自己走通，不做集成商。",
        "p2": "公司持有 60 项知识产权，权利人都是海狮自己；通过 ISO9001 质量管理体系、"
              "知识产权管理体系与 CE 认证，四次获评国家高新技术企业，并获「专精特新」"
              "「科技创新小巨人」「瞪羚企业」等称号。",
        "p3": "2009 年做出第一台米重控制系统，2010 年做出第一台超声波在线测厚系统——"
              "此后十几年的产品线都长在这两件事上。系统已装在国内外客户的产线上，"
              "从售前选型、现场安装调试到操作培训与备件供应，服务体系一路跟到底。",
    },
    "en": {
        "eyebrow": "About Sealion",
        "h1": "An industrial control company in extrusion",
        "p1": "Founded in 2008, Guangzhou Sealion Software Technology develops, builds and sells "
              "its own systems. They run on lines making plastic pipe, wire and cable, medical "
              "catheter, film and sheet, masterbatch and compounds. The chain is in house — "
              "hardware EDA, DSP firmware, ARM and host software, electrical control, PLC "
              "programming and mechanical design.",
        "p2": "Sixty patents and copyrights, all held by Sealion. ISO9001, IP management "
              "certification and CE marking, with National High-Tech Enterprise status awarded "
              "four times.",
        "p3": "The first gravimetric control system was built in 2009 and the first ultrasonic "
              "wall-thickness gauge in 2010; everything since has grown out of those two. "
              "Selection, commissioning, operator training and spares follow the system onto the line.",
    },
}

# ── 横向时间轴：年份 + 事件 ─────────────────────────────────
TL = [
    ("2008", ["公司成立"]),
    ("2009", ["第一台米重控制系统研发成功"]),
    ("2010", ["第一台超声波在线测厚系统研发成功"]),
    ("2012", ["进驻广州科学城"]),
    ("2013", ["研发中心成立", "设立华东、西南、华北办事处"]),
    ("2014", ["建立机械加工车间"]),
    ("2015", ["通过软件企业认证", "荣获科技创新小巨人企业"]),
    ("2016", ["首次荣获国家高新技术企业"]),
    ("2017", ["通过 ISO9001 质量体系认证", "通过知识产权管理体系认证"]),
    ("2018", ["米重控制系统入选广东省高新技术产品", "超声波在线测厚系统入选广东省高新技术产品"]),
    ("2019", ["第二次通过国家高新技术企业认定"]),
    ("2020", ["挤出云远程监控系统推出"]),
    ("2021", ["管材质量安全入库系统推出"]),
    ("2022", ["荣获专精特新企业称号"]),
    ("2023", ["管材质量安全入库系统入选广东省名优高新技术产品"]),
    ("2025", ["第四次通过国家高新技术企业认定", "累计 60 项知识产权"]),
]
TL_EN = [
    ("2008", ["Company founded"]),
    ("2009", ["First gravimetric control system"]),
    ("2010", ["First ultrasonic wall-thickness gauge"]),
    ("2012", ["Moved to Guangzhou Science City"]),
    ("2013", ["R&D centre established", "Offices in East, Southwest and North China"]),
    ("2014", ["Machining workshop established"]),
    ("2015", ["Software enterprise certification", "Technology Innovation Little Giant"]),
    ("2016", ["National High-Tech Enterprise, first award"]),
    ("2017", ["ISO9001 certification", "IP management system certification"]),
    ("2018", ["Two systems named Guangdong High-Tech Products"]),
    ("2019", ["National High-Tech Enterprise, second award"]),
    ("2020", ["Cloud monitoring system released"]),
    ("2021", ["Quality and storage system released"]),
    ("2022", ["Specialised and Innovative Enterprise"]),
    ("2023", ["Storage system named a Guangdong Premium High-Tech Product"]),
    ("2025", ["National High-Tech Enterprise, fourth award", "Sixty patents and copyrights"]),
]


def timeline(items, title, lead):
    out = ['  <section data-reveal class="section timeline-sec" id="milestones">',
           '    <div class="wrap">',
           '      <div class="sh"><span class="eyebrow">发展历程</span>'
           if title == "zh" else
           '      <div class="sh"><span class="eyebrow">Milestones</span>',
           f'        <h2>{lead[0]}</h2><p class="lead">{lead[1]}</p></div>',
           '      <div class="tl" data-timeline>',
           '        <div class="tl-track">']
    for i, (year, evs) in enumerate(items):
        side = "top" if i % 2 == 0 else "bot"
        li = "".join(f"<li>{e}</li>" for e in evs)
        out.append(f'          <div class="tl-i tl-i--{side}">'
                   f'<b class="tl-y">{year}</b>'
                   f'<span class="tl-dot" aria-hidden="true"></span>'
                   f'<ul class="tl-e">{li}</ul></div>')
    out += ['        </div>', '      </div>', '    </div>', '  </section>', '']
    return "\n".join(out)


for lang in ("zh", "en"):
    ap = os.path.join(ROOT, "src", "content", lang, "about.html")
    meta, body = load(ap)
    if 'id="culture"' in body:
        print(f"  {lang} 已合并过，跳过")
        continue

    # 从各分页取回内容
    blocks = {}
    for key, path in (("culture", f"about/culture.html"),
                      ("certs", f"about/certs.html"),
                      ("partners", f"about/partners.html")):
        p = os.path.join(ROOT, "src", "content", lang, path)
        if not os.path.exists(p):
            continue
        _, b = load(p)
        m = re.search(r"<section.*</section>", b, re.S)
        blocks[key] = m.group(0) if m else b.strip()

    # 企业简介重写为三段
    T = INTRO[lang]
    intro = (f'  <section data-reveal class="section intro-sec" id="about">\n'
             f'    <div class="wrap narrow">\n'
             f'      <span class="eyebrow">{T["eyebrow"]}</span>\n'
             f'      <h1>{T["h1"]}</h1>\n'
             f'      <p class="lead">{T["p1"]}</p>\n'
             f'      <p>{T["p2"]}</p>\n'
             f'      <p>{T["p3"]}</p>\n'
             f'    </div>\n  </section>\n\n')

    # 原 about.html 里的能力四格与成长节保留
    keep_growth, _ = cut(body, "growth")

    tl = timeline(TL if lang == "zh" else TL_EN, lang,
                  ("从一台米重控制系统开始", "2008 年至今，产品线都长在米重与测厚这两件事上。")
                  if lang == "zh" else
                  ("It started with one gravimetric system",
                   "Everything since 2008 has grown out of gravimetric control and thickness gauging."))

    new = (intro + tl
           + (blocks.get("culture", "") + "\n\n" if blocks.get("culture") else "")
           + (blocks.get("certs", "") + "\n\n" if blocks.get("certs") else "")
           + (keep_growth + "\n\n" if keep_growth else "")
           + (blocks.get("partners", "") + "\n" if blocks.get("partners") else ""))

    meta["js"] = sorted(set(meta.get("js", []) + ["motion", "back-to-top"]))
    meta["backToTop"] = True
    save(ap, meta, new)
    print(f"  {lang}/about.html 合并完成（{len(new)} 字符）")

    # 旧分页改成 301 由 build 处理不了，直接删；导航改锚点
    for path in ("about/culture.html", "about/certs.html", "about/partners.html",
                 "about/milestones.html"):
        p = os.path.join(ROOT, "src", "content", lang, path)
        if os.path.exists(p):
            os.remove(p)
            print(f"    删除 {lang}/{path}")

# ── 导航改锚点 ──────────────────────────────────────────────
p = os.path.join(ROOT, "src", "site.json")
d = json.load(io.open(p, encoding="utf-8"))
for n in d["nav"]:
    if n["label"]["zh"] == "关于海狮":
        n["children"] = [
            {"label": {"zh": "企业简介", "en": "Company", "ru": "О компании"}, "href": "/about.html#about"},
            {"label": {"zh": "发展历程", "en": "Milestones", "ru": "История"}, "href": "/about.html#milestones"},
            {"label": {"zh": "企业文化", "en": "Culture", "ru": "Культура"}, "href": "/about.html#culture"},
            {"label": {"zh": "资质荣誉", "en": "Certifications", "ru": "Сертификаты"}, "href": "/about.html#certs"},
            {"label": {"zh": "合作客户", "en": "Customers", "ru": "Клиенты"}, "href": "/about.html#partners"},
            {"label": {"zh": "知识产权", "en": "Patents", "ru": "Патенты"}, "href": "/ip.html"},
        ]
        print("  导航：关于海狮 五项改为同页锚点，知识产权仍为独立页")
io.open(p, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=2) + "\n")
