# -*- coding: utf-8 -*-
"""栏目改成独立页面 —— 第三片（案例展示）与第四片（联系我们）

案例这一片是最麻烦的：cases.html 只有一个 <section id="cases">，
四类案例是里面的 <div class="case-cat" id="case-XXX">，不是独立分节，
所以要按 div 层级精确切，不能用切 section 的那套。
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


def cut_tag(body, tag, attr_re):
    """按标签名与属性正则切出一整块，正确处理同名标签嵌套。"""
    m = re.search(r"<%s[^>]*%s[^>]*>" % (tag, attr_re), body)
    if not m:
        return None, body
    st = m.start()
    depth = 0
    end = None
    for mm in re.finditer(r"</?%s\b" % tag, body[st:]):
        depth += 1 if mm.group(0) == "<" + tag else -1
        if depth == 0:
            end = st + mm.end()
            break
    if end is None:
        return None, body
    while end < len(body) and body[end] in ">\n":
        end += 1
    return body[st:end], body[:st] + body[end:]


CASES = {
    "zh": [("case-127", "gravimetric", "米重案例", "米重控制系统装在真实产线上的样子——现场照片与配置。"),
           ("case-204", "masterbatch", "米重色母案例", "米重色母控制系统的现场案例与配置。"),
           ("case-172", "ultrasonic", "超声波案例", "超声波在线测厚系统的现场案例与配置。"),
           ("case-171", "video", "视频案例", "现场运行视频——设备装在产线上真实跑起来的样子。")],
    "en": [("case-127", "gravimetric", "Gravimetric cases", "Gravimetric control systems on real extrusion lines."),
           ("case-204", "masterbatch", "Masterbatch cases", "Gravimetric masterbatch systems on real lines."),
           ("case-172", "ultrasonic", "Ultrasonic cases", "Ultrasonic wall-thickness gauging on real lines."),
           ("case-171", "video", "Video cases", "Footage of the systems running on production lines.")],
}
PARENT = {"zh": ("案例展示", "/cases.html"), "en": ("Cases", "/cases.html")}

made = []
for lang, jobs in CASES.items():
    cp = os.path.join(ROOT, "src", "content", lang, "cases.html")
    if not os.path.exists(cp):
        continue
    meta, body = load(cp)
    for sid, slug, name, desc in jobs:
        blk, body = cut_tag(body, "div", r'id="%s"' % sid)
        if blk is None:
            print(f"  {lang} 找不到 {sid}")
            continue
        # 分类块里的标题是 h3，独立成页要提升为 h1
        blk = re.sub(r"<h3([^>]*)>(.*?)</h3>", r"<h1\1>\2</h1>", blk, count=1, flags=re.S)
        page = ('  <section class="section cases">\n    <div class="wrap">\n'
                + blk + "\n    </div>\n  </section>\n")
        save(os.path.join(ROOT, "src", "content", lang, "cases", slug + ".html"),
             {"title": f"{name} — {'海狮科技' if lang == 'zh' else 'Sealion Technology'}",
              "description": desc, "css": meta.get("css", []), "type": "page",
              "crumb": name, "parent": {"href": PARENT[lang][1], "label": PARENT[lang][0]},
              "backToTop": True, "js": ["back-to-top"]},
             page)
        made.append(f"{lang}/cases/{slug}.html")
        print(f"  {lang}/cases.html#{sid} → {lang}/cases/{slug}.html（{len(blk)} 字符）")
    # 跳转条改成指向新页面
    root = "/" if lang == "zh" else f"/{lang}/"
    for sid, slug, name, desc in jobs:
        body = body.replace(f'href="#{sid}"', f'href="{root}cases/{slug}.html"')
    save(cp, meta, body)

# ── 联系我们 ────────────────────────────────────────────────
CONTACT = {
    "zh": ("联系我们 — 海狮科技", "电话、邮箱、地址与产线参数咨询——把口径、材料、产量、线速发给我们，工程师按你的产线给配置建议。", "联系我们"),
    "en": ("Contact — Sealion Technology", "Phone, email, address and enquiry: send us diameter, material, output and line speed.", "Contact"),
    "ru": ("Контакты — Sealion Technology", "Телефон, почта, адрес и запрос.", "Контакты"),
}
for lang, (title, desc, crumb) in CONTACT.items():
    ip = os.path.join(ROOT, "src", "content", lang, "index.html")
    if not os.path.exists(ip):
        continue
    meta, body = load(ip)
    blk, rest = cut_tag(body, "section", r'id="contact"')
    if blk is None:
        print(f"  {lang}/index.html 没有 contact 节")
        continue
    blk = re.sub(r"<h2([^>]*)>(.*?)</h2>", r"<h1\1>\2</h1>", blk, count=1, flags=re.S)
    save(os.path.join(ROOT, "src", "content", lang, "contact.html"),
         {"title": title, "description": desc, "css": meta.get("css", []),
          "type": "page", "crumb": crumb},
         blk)
    save(ip, meta, rest)
    made.append(f"{lang}/contact.html")
    print(f"  {lang}/index.html#contact → {lang}/contact.html（{len(blk)} 字符）")

# ── 导航与站内残留锚点 ──────────────────────────────────────
p = os.path.join(ROOT, "src", "site.json")
d = json.load(io.open(p, encoding="utf-8"))
SLUG = {"case-127": "gravimetric", "case-204": "masterbatch",
        "case-172": "ultrasonic", "case-171": "video"}
n = 0
for item in d["nav"]:
    if item["label"]["zh"] == "联系我们":
        item["href"] = "/contact.html"; n += 1
    for c in item.get("children", []):
        m = re.search(r"#(case-\d+)$", c["href"])
        if m:
            c["href"] = "/cases/%s.html" % SLUG[m.group(1)]; n += 1
io.open(p, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=2) + "\n")
print(f"\n导航改掉 {n} 个指向；新建 {len(made)} 个页面")

# 站内其余指向 /#contact 的链接一并改掉
fixed = 0
for f in [os.path.join(dp, fn) for dp, _, fns in os.walk(os.path.join(ROOT, "src", "content"))
          for fn in fns if fn.endswith(".html")]:
    s = io.open(f, encoding="utf-8").read()
    lang = f.split(os.sep + "content" + os.sep)[1].split(os.sep)[0]
    root = "/" if lang == "zh" else f"/{lang}/"
    o = s
    s = s.replace(f'href="{root}#contact"', f'href="{root}contact.html"')
    s = s.replace('href="/#contact"', f'href="{root}contact.html"')
    if s != o:
        io.open(f, "w", encoding="utf-8").write(s)
        fixed += 1
print(f"另有 {fixed} 个源文件里的 /#contact 链接改指向新页")
