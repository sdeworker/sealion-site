# -*- coding: utf-8 -*-
"""把 public/ 的 95 个页面拆成 src/content/<lang>/... （正文 + 元数据）"""
import glob, os, re, json, shutil

SRC = "src/content"

def lang_of(p):
    return "en" if p.startswith("public/en/") else "zh"

def relpath(p):
    r = p[len("public/"):]
    if r.startswith("en/"):
        r = r[3:]
    return r

def grab(h, pat, d=""):
    m = re.search(pat, h, re.S)
    return m.group(1).strip() if m else d

if os.path.exists(SRC):
    shutil.rmtree(SRC)

pages = sorted(glob.glob("public/**/*.html", recursive=True))
stats = {"ok": 0, "special": 0}
for p in pages:
    h = open(p, encoding="utf-8").read()
    lang, rel = lang_of(p), relpath(p)

    # 404 等无 header/footer 的整页，原样留存为 special
    m = re.search(r"<main[^>]*>(.*)</main>", h, re.S)
    if not m:
        out = os.path.join(SRC, lang, rel)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        meta = {"standalone": True}
        open(out, "w", encoding="utf-8").write(
            json.dumps(meta, ensure_ascii=False, indent=1) + "\n---\n" + h)
        stats["special"] += 1
        continue

    content = m.group(1).strip("\n")

    head = h[:h.find("</head>")]
    meta = {
        "title": grab(h, r"<title>(.*?)</title>"),
        "description": grab(h, r'name="description" content="(.*?)"'),
    }
    # 附加样式表（style.css 全站默认，不记）
    css = [c for c in ("product", "manual")
           if f'href="/{c}.css"' in head]
    if css: meta["css"] = css
    # 附加脚本
    js = []
    for name in ("lightbox", "back-to-top", "app"):
        if f'/assets/{name}.js' in h: js.append(name)
    if js: meta["js"] = js
    # 返回顶部按钮
    if "data-back-to-top" in h: meta["backToTop"] = True
    # 结构化数据类型
    if rel == "index.html": meta["type"] = "home"
    elif rel.startswith("products/"): meta["type"] = "product"
    elif rel.startswith("news/"): meta["type"] = "article"
    else: meta["type"] = "page"

    out = os.path.join(SRC, lang, rel)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(
        json.dumps(meta, ensure_ascii=False, indent=1) + "\n---\n" + content + "\n")
    stats["ok"] += 1

print(f"提取完成：正文页 {stats['ok']}，独立页(404等) {stats['special']}")
for lang in ("zh", "en"):
    n = len(glob.glob(f"{SRC}/{lang}/**/*.html", recursive=True))
    print(f"  {lang}: {n} 页")
