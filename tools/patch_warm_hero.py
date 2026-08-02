# -*- coding: utf-8 -*-
"""两件事

一、配色：冷灰蓝 → 暖灰空间
   现在的浅底是 #F3F6F8 / #EEF2F6，都是偏冷的灰蓝，和深海蓝同一个色相族，
   整站等于只有一种颜色的明暗变化——这是"没档次"的直接来源：
   不是颜色太少，是没有色温对比。
   改成暖白 #FBFAF8 与暖灰 #F2EFEA，冷蓝与暖灰形成温差，蓝才立得住。
   另加铜色 #8A5326 作第二强调（对白 6.28，可作正文级）。

二、首页 Hero：图文分离
   参考 INOEX：左边整块实景，右边一个纯色块承载标题与说明，界限分明，
   不把文字压在照片上。我们的商标边缘有残缺，这种做法正好不需要它融进画面。
"""
import io, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── 一、配色 ────────────────────────────────────────────────
S = os.path.join(ROOT, "public", "style.css")
s = io.open(S, encoding="utf-8").read()

COLORS = [
    ("--paper:#F3F6F8", "--paper:#FBFAF8", "纸面转暖白"),
    ("--mist:#EEF2F6", "--mist:#F2EFEA", "雾灰转暖灰"),
    ("--line:#D8E0E7", "--line:#DED8CF", "描边跟着转暖"),
]
for a, b, why in COLORS:
    if s.count(a) != 1:
        sys.exit(f"✗ {why}：锚点命中 {s.count(a)} 次")
for a, b, why in COLORS:
    s = s.replace(a, b, 1)

# paper-2 若存在也一并转暖
s = re.sub(r"--paper-2:#[0-9A-Fa-f]{6}", "--paper-2:#FFFDFA", s)

# 新增铜色作第二强调
s = s.replace("  --signal-dk:#8F5D00;",
              "  --signal-dk:#8F5D00;\n"
              "  --copper:#8A5326;      /* 铜：第二强调。对暖白 6.02，可作正文级；\n"
              "                            与品牌蓝形成冷暖对，而不是又一个蓝 */\n"
              "  --copper-lt:#B0703A;", 1)
print("  配色：纸面/雾灰/描边转暖，新增铜色")

# ── 二、Hero 图文分离 ───────────────────────────────────────
HERO_CSS = """/* Hero：图文分离。左边整块实景，右边纯色块承载文字，界限分明——
   文字压在照片上永远要跟画面抢，而且我们的商标边缘有残缺，
   这种做法正好不必让它融进画面。 */
body.home .hero{min-height:calc(100svh - var(--header-h,136px));margin-top:0}
body.home .hero-grid{display:grid;grid-template-columns:1fr;padding:0;width:100%;
  min-height:calc(100svh - var(--header-h,136px))}
body.home .hero-split{display:grid;grid-template-columns:1.25fr .75fr;width:100%;
  min-height:calc(100svh - var(--header-h,136px))}
body.home .hero-figure{position:relative;overflow:hidden;background:var(--ink)}
body.home .hero-figure .hero-video,
body.home .hero-figure video{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
body.home .hero-panel{background:var(--ink);color:#fff;display:flex;flex-direction:column;
  justify-content:center;padding:clamp(2.5rem,4vw,4.5rem) clamp(2rem,3.5vw,3.75rem)}
body.home .hero-panel .eyebrow{color:var(--signal)}
body.home .hero-panel h1{color:#fff;margin-block:.6rem 1rem}
body.home .hero-panel .lead{color:rgba(255,255,255,.84);max-width:34ch}
body.home .hero-cta{display:flex;flex-wrap:wrap;gap:1rem;margin-top:var(--sp-1)}
@media(max-width:1000px){
  body.home .hero-split{grid-template-columns:1fr;min-height:0}
  body.home .hero-figure{min-height:58svh}
  body.home .hero-panel{padding:var(--sp-2) var(--gutter)}
}
/* 图文分离之后，播放键回到画面里，不再压着文字 */
body.home .hero-figure .hero-play{position:absolute;left:50%;top:50%;
  transform:translate(-50%,-50%);z-index:3}
body.home .hero-figure .hero-play:hover{transform:translate(-50%,-50%)}
body.home .hero-figure .hero-play:hover::before{transform:scale(1.07)}

"""
A = "/* a11y + motion */"
assert s.count(A) == 1
s = s.replace(A, HERO_CSS + A, 1)
io.open(S, "w", encoding="utf-8").write(s)
print("  Hero 图文分离样式")

# ── HTML ────────────────────────────────────────────────────
TXT = {
    "zh": dict(eyebrow="称重控制 · 超声波测厚 · 云端监控",
               h1="毫米级管控，每米可测量",
               lead="海狮为塑料挤出产线打造测量与控制系统——从称重、测厚、喂料、配料，到检测与上云，让每米产品稳定在公差之内。",
               b1="浏览产品", b1h="/pipe/", b2="发四个数给工程师"),
    "en": dict(eyebrow="Gravimetric · Ultrasonic · Cloud",
               h1="Millimetre control, every metre measured",
               lead="Measurement and control for plastics extrusion — weighing, wall thickness, feeding, dosing, inspection and the cloud, so every metre stays inside tolerance.",
               b1="Browse systems", b1h="/en/pipe/", b2="Send four numbers"),
}
MAILTO = "mailto:2428582102@qq.com?subject=%E4%BA%A7%E7%BA%BF%E5%8F%82%E6%95%B0%E5%92%A8%E8%AF%A2"

for lang in ("zh", "en"):
    p = os.path.join(ROOT, "src", "content", lang, "index.html")
    src = io.open(p, encoding="utf-8").read()
    h, sep, body = src.partition("\n---\n")
    if "hero-split" in body:
        print(f"  {lang} Hero 已改过，跳过")
        continue
    m = re.search(r'<section class="hero"[^>]*>(.*?)</section>', body, re.S)
    assert m, f"{lang} 找不到 hero 节"
    inner = m.group(1)
    video = re.search(r"<video.*?</video>", inner, re.S)
    lines = re.search(r'<div class="hero-lines".*?</div>', inner, re.S)
    play = re.search(r"<button class=\"hero-play\".*?</button>", inner, re.S)
    T = TXT[lang]
    new = (
        '<section class="hero">\n'
        '  <div class="hero-split">\n'
        '    <div class="hero-figure">\n'
        f'      {video.group(0) if video else ""}\n'
        f'      {lines.group(0) if lines else ""}\n'
        f'      {play.group(0) if play else ""}\n'
        '    </div>\n'
        '    <div class="hero-panel">\n'
        f'      <span class="eyebrow">{T["eyebrow"]}</span>\n'
        f'      <h1>{T["h1"]}</h1>\n'
        f'      <p class="lead">{T["lead"]}</p>\n'
        '      <div class="hero-cta">\n'
        f'        <a class="btn btn--primary" href="{T["b1h"]}">{T["b1"]}</a>\n'
        f'        <a class="btn btn--onDark" href="{MAILTO}">{T["b2"]}</a>\n'
        '      </div>\n'
        '    </div>\n'
        '  </div>\n'
        '</section>'
    )
    body = body[:m.start()] + new + body[m.end():]
    io.open(p, "w", encoding="utf-8").write(h + sep + body)
    print(f"  {lang} Hero 改为图文分离")
