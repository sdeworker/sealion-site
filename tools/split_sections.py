# -*- coding: utf-8 -*-
"""栏目改成独立页面 —— 第一片：关于海狮

现在的毛病：一个长页面塞了六节，导航里三个子栏目全靠 #锚点 跳同一页。
访客点"发展历程"和点"资质证书"落在同一个 URL 上，浏览器前进后退、
分享链接、搜索引擎收录全部分不开，也说不清"我在哪一层"。

改法：一节一页。about.html 只留企业简介，其余各自成页。
这个脚本写成通用的，后面拆"海狮实力""案例展示""联系我们"直接复用。
"""
import io, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(path):
    s = io.open(path, encoding="utf-8").read()
    head, sep, body = s.partition("\n---\n")
    if not sep:
        sys.exit(f"✗ {path} 没有元数据分隔符")
    return json.loads(head), body


def save(path, meta, body):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    io.open(path, "w", encoding="utf-8").write(
        json.dumps(meta, ensure_ascii=False, indent=1) + "\n---\n" + body)


def cut_section(body, sid):
    """按 id 取出整个 <section>…</section>，含嵌套。"""
    m = re.search(r'<section[^>]*id="%s"[^>]*>' % re.escape(sid), body)
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
    # 吃掉紧跟其后的 > 与换行
    while end < len(body) and body[end] in ">\n":
        end += 1
    return body[st:end], body[:st] + body[end:]


# ── 要拆出去的节：(源, 节 id, 新路径, 标题, 描述, 面包屑名) ──────
SPLITS = {
    "zh": [
        ("about.html", "milestones", "about/milestones.html",
         "发展历程 — 海狮科技",
         "海狮科技从一台米重控制系统起步，到覆盖称重、测厚、喂料、配料、检测与上云的完整产线测控体系。",
         "发展历程"),
        ("about.html", "certs", "about/certs.html",
         "资质证书 — 海狮科技",
         "国家高新技术企业、科技创新小巨人、ISO9001 质量管理体系认证、CE 认证与知识产权管理体系认证。",
         "资质证书"),
    ],
    "en": [
        ("about.html", "milestones", "about/milestones.html",
         "Milestones — Sealion Technology",
         "From a single gravimetric control system to a full measurement and control stack for plastics extrusion lines.",
         "Milestones"),
        ("about.html", "certs", "about/certs.html",
         "Certifications — Sealion Technology",
         "National High-Tech Enterprise, ISO9001 quality management, CE marking and IP management certification.",
         "Certifications"),
    ],
}

made = []
for lang, jobs in SPLITS.items():
    for src, sid, dst, title, desc, crumb in jobs:
        sp = os.path.join(ROOT, "src", "content", lang, src)
        if not os.path.exists(sp):
            print(f"  跳过 {lang}/{src}（不存在）")
            continue
        meta, body = load(sp)
        block, rest = cut_section(body, sid)
        if block is None:
            print(f"  跳过 {lang}/{src}#{sid}（找不到这一节）")
            continue
        # 新页面：沿用源页的 css，加上面包屑名
        nmeta = {"title": title, "description": desc,
                 "css": meta.get("css", []), "type": "page", "crumb": crumb,
                 "parent": {"href": "/about.html" if lang == "zh" else f"/{lang}/about.html",
                            "label": {"zh": "关于海狮", "en": "About"}[lang]}}
        if meta.get("js"):
            nmeta["js"] = meta["js"]
        save(os.path.join(ROOT, "src", "content", lang, dst), nmeta, block)
        save(sp, meta, rest)
        made.append(f"{lang}/{dst}")
        print(f"  {lang}/{src}#{sid} → {lang}/{dst}（{len(block)} 字符）")

print(f"\n新建 {len(made)} 个页面")

# ── 导航改指向真实页面 ──────────────────────────────────────
p = os.path.join(ROOT, "src", "site.json")
d = json.load(io.open(p, encoding="utf-8"))
REMAP = {
    "/about.html#about": "/about.html",
    "/about.html#milestones": "/about/milestones.html",
    "/about.html#certs": "/about/certs.html",
}
n = 0
for item in d["nav"]:
    for c in item.get("children", []):
        if c["href"] in REMAP:
            c["href"] = REMAP[c["href"]]
            n += 1
io.open(p, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=2) + "\n")
print(f"导航改掉 {n} 个锚点指向")
