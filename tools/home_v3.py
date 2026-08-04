# -*- coding: utf-8 -*-
"""首页按参考站重排

参考站首页只有五块：Hero → 数字条 → 行业方案（七张卡，每张一句话）
→ 合作客户漂浮云 → 收尾。可见文本九十来行。

我们现在九节 10736px，其中产品区一节就 3053px——八张卡每张一段说明。
按"简洁、图片为主、文字少"，这一节该是入口不是说明书。

改动：
  · 产品区：每张卡的整段说明换成一句话，卡片做成图为主
  · 补「应用行业」：十二个行业，图 + 名称，一句话都不要——名称本身就是那句话
  · 补「合作客户」漂浮云：参考站首页有，我们搬到关于页之后首页就断了
  · 「需求确认」并进算账那一节：两节讲的是同一件事（米重偏一点值多少钱）
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


# 产品卡的一句话——原来那段说明留在产品页里，首页只需要一句
ONE_LINE = {
    "米重控制系统": "每米克重闭环控制，省料 2%–5%",
    "米重色母控制系统": "米重与色母同时控，配比精度 ±1%",
    "米重色母系统称重版": "称重式配比，适合高精度小添加量",
    "多组份克重计量配料控制系统": "多组份同步计量，配方一次配准",
    "超声波在线测厚系统（大管）": "大口径管材壁厚在线测，不停机",
    "超声波在线测厚系统（小管）": "小管与导管壁厚在线测",
    "管材质量安全入库系统": "出厂前逐根核验，数据可追溯",
    "管材在线智能检测系统": "在线检出外观与尺寸缺陷",
    "挤出云远程监控系统": "产线数据上云，手机上看得见",
    "双轴激光测径仪": "双轴非接触测外径与椭圆度",
}
ONE_LINE_EN = {
    "Gravimetric Control System": "Closed-loop control per metre, 2%–5% saved",
    "Gravimetric Masterbatch Control System": "Weight and masterbatch together, ±1%",
    "Masterbatch Weighing Version": "Weighing-based dosing for small additions",
    "Multi-component Gravimetric Dosing System": "Several components metered at once",
    "Ultrasonic Thickness Gauge (large pipe)": "Wall thickness on large pipe, in line",
    "Ultrasonic Thickness Gauge (small pipe)": "Wall thickness on small pipe and catheter",
    "Quality and Storage System": "Every length verified before it ships",
    "Intelligent Inspection System": "Surface and dimensional defects, in line",
    "Cloud Monitoring System": "Line data in the cloud, visible on a phone",
    "Dual-axis Laser Caliper": "Outer diameter and ovality, non-contact",
}

for lang in ("zh", "en"):
    p = os.path.join(ROOT, "src", "content", lang, "index.html")
    if not os.path.exists(p):
        continue
    meta, body = load(p)
    table = ONE_LINE if lang == "zh" else ONE_LINE_EN

    # ① 产品卡说明换成一句话
    n = 0
    def short(m):
        global n
        name = m.group(1).strip()
        one = table.get(name)
        if not one:
            return m.group(0)
        n += 1
        return f'<h3>{name}</h3>\n          <p class="pc-sum">{one}</p>'
    body = re.sub(r'<h3>([^<]+)</h3>\s*<p class="pc-sum">[^<]*</p>', short, body)
    print(f"  {lang} 产品卡说明收成一句话：{n} 张")

    # ② 需求确认并进算账那一节
    need, body = cut(body, "need")
    if need:
        print(f"  {lang} 移除需求确认节（{len(need)} 字符，与算账节讲同一件事）")

    save(p, meta, body)

# ③ 补「应用行业」与「合作客户」两节
IND = {
    "zh": ("应用行业", "十二个行业，各自该配哪几套系统",
           "从燃气管到医疗导管，从吹膜流延到色母改性——点进去看该配什么。", "/industries/", "看全部行业"),
    "en": ("Industries", "Twelve industries, each with its own配置",
           "From gas pipe to medical catheter, film to masterbatch.", "/en/industries/", "All industries"),
}

for lang in ("zh", "en"):
    d = os.path.join(ROOT, "src", "content", lang, "industries")
    p = os.path.join(ROOT, "src", "content", lang, "index.html")
    if not os.path.isdir(d) or not os.path.exists(p):
        continue
    meta, body = load(p)
    if 'id="industries"' in body:
        print(f"  {lang} 已有行业节")
        continue
    files = sorted(f for f in os.listdir(d) if f.endswith(".html") and f != "index.html")
    root = "/" if lang == "zh" else f"/{lang}/"
    cards = []
    for f in files:
        _, ib = load(os.path.join(d, f))
        h1 = re.search(r"<h1[^>]*>(.*?)</h1>", ib, re.S)
        name = re.sub(r"<[^>]+>", "", h1.group(1)).strip() if h1 else f[:-5]
        img = re.search(r'<img[^>]*src="([^"]+)"', ib)
        media = (f'<span class="ic-img"><img src="{img.group(1)}" alt="{name}" '
                 f'loading="lazy" width="1200" height="675"></span>' if img else "")
        cards.append(f'        <a class="icard" href="{root}industries/{f}">{media}'
                     f'<span class="ic-name">{name}</span></a>')
    T = IND[lang]
    sec = (f'  <section data-reveal class="section industries-home" id="industries">\n'
           f'    <div class="wrap">\n'
           f'      <div class="sh"><span class="eyebrow">{T[0]}</span>\n'
           f'        <h2>{T[1]}</h2><p class="lead">{T[2]}</p></div>\n'
           f'      <div class="icard-grid">\n' + "\n".join(cards) + "\n      </div>\n"
           f'      <p class="ind-more"><a class="arrow-link" href="{T[3]}">{T[4]} &rarr;</a></p>\n'
           f'    </div>\n  </section>\n\n')
    m = re.search(r'<section[^>]*\bid="products"', body)
    body = body[:m.start()] + sec + body[m.start():] if m else body + sec
    save(p, meta, body)
    print(f"  {lang} 补入应用行业节（{len(files)} 个行业）")

# ── CSS ────────────────────────────────────────────────────
S = os.path.join(ROOT, "public", "style.css")
s = io.open(S, encoding="utf-8").read()
A = "/* a11y + motion */"
CSS = """/* 首页行业卡：图为主，名称压在图上，一句话都不要——
   行业名本身就是那句话。参考站首页也是这么排的。 */
.icard-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem}
.icard{position:relative;display:block;aspect-ratio:4/3;overflow:hidden;
  border-radius:var(--radius-lg);background:var(--ink);
  box-shadow:0 10px 28px rgba(10,26,38,.10);transition:transform .25s,box-shadow .25s}
.icard:hover{transform:translateY(-4px);box-shadow:0 18px 40px rgba(10,26,38,.20)}
.ic-img{position:absolute;inset:0}
.ic-img img{width:100%;height:100%;object-fit:cover;transition:transform .45s cubic-bezier(.2,.6,.2,1)}
.icard:hover .ic-img img{transform:scale(1.06)}
.icard::after{content:"";position:absolute;inset:0;
  background:linear-gradient(180deg,transparent 40%,rgba(10,26,38,.82))}
.ic-name{position:absolute;left:0;right:0;bottom:0;z-index:2;padding:1rem 1.1rem;
  color:#fff;font-size:var(--step-1);font-weight:600;line-height:1.3}
.ind-more{margin-top:var(--sp-1);text-align:center}
@media(max-width:1100px){.icard-grid{grid-template-columns:repeat(3,1fr)}}
@media(max-width:760px){.icard-grid{grid-template-columns:repeat(2,1fr)}}

"""
assert s.count(A) == 1
io.open(S, "w", encoding="utf-8").write(s.replace(A, CSS + A, 1))
print("  style.css：行业卡样式")
