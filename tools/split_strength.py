# -*- coding: utf-8 -*-
"""栏目改成独立页面 —— 第二片：海狮实力

三处毛病：
  · 「海狮实力」本身指向 /about.html#apply-detail，而这个锚点在首页，不在 about.html
    上——点进去落在 about.html 顶部，什么都对不上
  · 「产品应用」同一个错地址
  · 「应用行业」指向 /#apply（首页锚点），而真正的 12 个行业页只有 1–2 个入链，几乎是孤岛
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
    if end is None:
        return None, body
    while end < len(body) and body[end] in ">\n":
        end += 1
    return body[st:end], body[:st] + body[end:]


TXT = {
    "zh": dict(
        strength_title="海狮实力 — 海狮科技",
        strength_desc="研发、质控、产品应用、售后服务与产品手册——海狮的底子，摊开来看。",
        strength_h1="把产品做出来之前，先把技术做透",
        strength_lead="从硬件 EDA、底层 DSP，到 ARM 与上位机软件、电气控制、PLC 编程与机械设计——整条链自己走通，不做集成商。这一栏把研发、质控、应用与服务分开讲清楚。",
        strength_eyebrow="海狮实力",
        apps_title="产品应用 — 海狮科技",
        apps_desc="七个典型应用场景——每个场景该配哪几套系统，这里写清楚。",
        apps_crumb="产品应用",
        ind_title="应用行业 — 海狮科技",
        ind_desc="塑料管道、燃气管、给水管、PPR、PVC、波纹管、片材板材、电缆护套、吹膜流延、医疗导管、熔喷布、色母与改性料——十二个行业的测控方案。",
        ind_h1="挑你的那一个行业",
        ind_lead="每个行业的挤出工艺不一样，要控的指标也不一样。下面十二个行业，各自该配哪几套系统，点进去写清楚了。",
        ind_eyebrow="应用行业",
        parent_label="海狮实力",
    ),
    "en": dict(
        strength_title="Capability — Sealion Technology",
        strength_desc="R&D, quality control, applications, service and the product manual.",
        strength_h1="Get the engineering right before the product",
        strength_lead="Hardware EDA, DSP firmware, ARM and host software, electrical control, PLC programming and mechanical design — the whole chain in house rather than integration.",
        strength_eyebrow="Capability",
        apps_title="Applications — Sealion Technology",
        apps_desc="Typical extrusion lines and which systems each one needs.",
        apps_crumb="Applications",
        ind_title="Industries — Sealion Technology",
        ind_desc="Plastic piping, gas and water pipe, PPR, PVC, corrugated pipe, sheet and board, cable sheathing, film, medical catheter, meltblown, masterbatch and compounds.",
        ind_h1="Pick your industry",
        ind_lead="Every extrusion process controls something different. Twelve industries, and which systems each one needs.",
        ind_eyebrow="Industries",
        parent_label="Capability",
    ),
}

made = []

# ── 1. 产品应用：从首页搬出来 ───────────────────────────────
for lang in ("zh", "en"):
    ip = os.path.join(ROOT, "src", "content", lang, "index.html")
    meta, body = load(ip)
    blk, rest = cut(body, "apply-detail")
    if blk is None:
        print(f"  {lang}/index.html 没有 apply-detail，跳过")
        continue
    T = TXT[lang]
    save(os.path.join(ROOT, "src", "content", lang, "applications.html"),
         {"title": T["apps_title"], "description": T["apps_desc"],
          "css": meta.get("css", []), "type": "page", "crumb": T["apps_crumb"],
          "parent": {"href": "/strength.html", "label": T["parent_label"]},
          "backToTop": True, "js": ["back-to-top"]},
         blk)
    save(ip, meta, rest)
    made.append(f"{lang}/applications.html")
    print(f"  {lang}/index.html#apply-detail → {lang}/applications.html（{len(blk)} 字符）")

# ── 2. 行业索引页：把 12 个孤岛串起来 ───────────────────────
for lang in ("zh", "en"):
    d = os.path.join(ROOT, "src", "content", lang, "industries")
    if not os.path.isdir(d):
        continue
    files = sorted(f for f in os.listdir(d) if f.endswith(".html") and f != "index.html")
    if not files:
        continue
    T = TXT[lang]
    root = "/" if lang == "zh" else f"/{lang}/"
    cards = []
    for f in files:
        m, b = load(os.path.join(d, f))
        h1 = re.search(r"<h1[^>]*>(.*?)</h1>", b, re.S)
        name = re.sub(r"<[^>]+>", "", h1.group(1)).strip() if h1 else m["title"].split("—")[0].strip()
        img = re.search(r'<img[^>]*src="([^"]+)"', b)
        desc = m.get("description", "")
        media = (f'      <div class="pc-img"><img src="{img.group(1)}" alt="{name}" '
                 f'loading="lazy" width="1200" height="675"></div>\n' if img else "")
        cards.append(
            f'    <a class="pcard pcard--img" href="{root}industries/{f}">\n'
            f'{media}'
            f'      <div class="pc-body">\n'
            f'        <h3>{name}</h3>\n'
            f'        <p>{desc}</p>\n'
            f'      </div>\n'
            f'    </a>')
    body = (f'  <section class="section" id="industries">\n'
            f'    <div class="wrap">\n'
            f'      <div class="sh">\n'
            f'        <span class="eyebrow">{T["ind_eyebrow"]}</span>\n'
            f'        <h1>{T["ind_h1"]}</h1>\n'
            f'        <p class="lead">{T["ind_lead"]}</p>\n'
            f'      </div>\n'
            f'      <div class="pcard-grid">\n' + "\n".join(cards) + "\n"
            f'      </div>\n'
            f'    </div>\n'
            f'  </section>\n')
    save(os.path.join(d, "index.html"),
         {"title": T["ind_title"], "description": T["ind_desc"],
          "css": ["product"], "type": "page", "crumb": T["ind_eyebrow"],
          "parent": {"href": "/strength.html", "label": T["parent_label"]},
          "backToTop": True, "js": ["back-to-top"]},
         body)
    made.append(f"{lang}/industries/index.html")
    print(f"  {lang}/industries/index.html：{len(files)} 个行业串成索引")

# ── 3. 海狮实力落地页 ───────────────────────────────────────
for lang in ("zh", "en"):
    T = TXT[lang]
    body = (f'  <section class="section prod-hero">\n'
            f'    <div class="wrap">\n'
            f'      <span class="eyebrow">{T["strength_eyebrow"]}</span>\n'
            f'      <h1>{T["strength_h1"]}</h1>\n'
            f'      <p class="lead">{T["strength_lead"]}</p>\n'
            f'    </div>\n'
            f'  </section>\n')
    save(os.path.join(ROOT, "src", "content", lang, "strength.html"),
         {"title": T["strength_title"], "description": T["strength_desc"],
          "css": [], "type": "page"},
         body)
    made.append(f"{lang}/strength.html")
    print(f"  {lang}/strength.html：栏目落地页（子栏目由生成器自动列出）")

# ── 4. 导航改指向 ───────────────────────────────────────────
p = os.path.join(ROOT, "src", "site.json")
d = json.load(io.open(p, encoding="utf-8"))
n = 0
for item in d["nav"]:
    if item["label"]["zh"] != "海狮实力":
        continue
    item["href"] = "/strength.html"
    n += 1
    for c in item.get("children", []):
        if c["label"]["zh"] == "产品应用":
            c["href"] = "/applications.html"; n += 1
        elif c["label"]["zh"] == "应用行业":
            c["href"] = "/industries/"; n += 1
io.open(p, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=2) + "\n")
print(f"\n导航改掉 {n} 个指向；新建 {len(made)} 个页面")
