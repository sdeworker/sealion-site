# -*- coding: utf-8 -*-
"""把 2026 新素材铺到 13 个产品页（中英同步）"""
import json, os, re
from PIL import Image

def dims(rel):
    with Image.open("public" + rel) as im:
        return im.size

def has(rel):
    return os.path.exists("public" + rel)

G = "/assets/2026/gravimetric"
M = "/assets/2026/masterbatch"
U = "/assets/2026/ultrasonic"
Q = "/assets/2026/quality-storage"
C = "/assets/2026/core"
V = "/assets/2026/video"

PLAN = {
 "pipe/gravimetric": dict(
   hero=f"{C}/core-gravimetric.webp",
   gallery=[f"{G}/pipe-{i}.webp" for i in (1,2,3,4,5,6)],
   gtitle={"zh":"管道产线现场","en":"On pipe lines"},
   videos=[(f"{V}/gravimetric-promo.mp4", {"zh":"米重控制系统 2026","en":"Gravimetric Control System 2026"}),
           (f"{V}/gravimetric-pipe-site-1.mp4", {"zh":"车间实拍","en":"Filmed on site"})]),
 "cable/gravimetric": dict(
   hero=f"{C}/core-gravimetric.webp",
   gallery=[f"{G}/cable-site-{i}.webp" for i in (1,2,3)] + [f"{G}/cable-ui-{i}.webp" for i in (1,2,3)],
   gtitle={"zh":"线缆现场与控制界面","en":"Cable line and control screens"},
   videos=[(f"{V}/gravimetric-cable-intro.mp4", {"zh":"线缆米重系统介绍","en":"Cable gravimetric system"})]),
 "pipe/masterbatch": dict(
   hero=f"{C}/core-masterbatch.webp",
   gallery=[f"{M}/volumetric-{i}.webp" for i in (1,2,3)],
   gtitle={"zh":"三共挤产线现场","en":"Three-layer co-extrusion line"},
   videos=[(f"{V}/masterbatch-site-1.mp4", {"zh":"三共挤现场实录","en":"Co-extrusion line, on site"}),
           (f"{V}/masterbatch-ui.mp4", {"zh":"软件控制界面录屏","en":"Control software screen recording"})]),
 "cable/masterbatch": dict(
   hero=f"{C}/core-masterbatch.webp",
   gallery=[f"{M}/volumetric-{i}.webp" for i in (1,2)],
   gtitle={"zh":"共挤产线现场","en":"Co-extrusion line"},
   videos=[(f"{V}/masterbatch-ui.mp4", {"zh":"软件控制界面录屏","en":"Control software screen recording"})]),
 "pipe/masterbatch-weighing": dict(
   hero=f"{C}/core-masterbatch-weighing.webp",
   gallery=[f"{M}/weighing-{i}.webp" for i in (1,2,3)],
   gtitle={"zh":"称重版现场","en":"Weighing edition on site"}, videos=[]),
 "cable/masterbatch-weighing": dict(
   hero=f"{C}/core-masterbatch-weighing.webp",
   gallery=[f"{M}/weighing-{i}.webp" for i in (1,2)],
   gtitle={"zh":"称重版现场","en":"Weighing edition on site"}, videos=[]),
 "pipe/ultrasonic-big": dict(
   hero=f"{C}/core-ultrasonic.webp",
   gallery=[f"{U}/big-{i:02d}.webp" for i in range(1,6)],
   gtitle={"zh":"大管测厚现场","en":"Large-pipe gauging on site"},
   videos=[(f"{V}/ultrasonic-big-promo.mp4", {"zh":"超声波在线测厚系统 2026","en":"Ultrasonic gauging 2026"}),
           (f"{V}/ultrasonic-big-site-1.mp4", {"zh":"1 米巨型测厚系统实拍","en":"One-metre system on site"})]),
 "pipe/ultrasonic-small": dict(
   hero=f"{C}/core-ultrasonic-2.webp",
   gallery=[f"{U}/small-{i}.webp" for i in range(1,7)],
   gtitle={"zh":"小管测厚现场","en":"Small-bore gauging on site"},
   videos=[(f"{V}/ultrasonic-small-site.mp4", {"zh":"现场实拍","en":"Filmed on site"})]),
 "cable/ultrasonic-small": dict(
   hero=f"{C}/core-ultrasonic-2.webp",
   gallery=[f"{U}/small-{i}.webp" for i in range(1,5)],
   gtitle={"zh":"细径测厚现场","en":"Fine-bore gauging on site"},
   videos=[(f"{V}/ultrasonic-small-site.mp4", {"zh":"现场实拍","en":"Filmed on site"})]),
 "pipe/quality-storage": dict(
   hero=f"{C}/core-quality-storage.webp",
   gallery=[f"{Q}/site-{i}.webp" for i in (1,2,3)],
   gtitle={"zh":"入库检测现场","en":"Inbound inspection on site"},
   videos=[(f"{V}/quality-storage-promo.mp4", {"zh":"管材质量安全入库系统 2026","en":"Inbound quality system 2026"}),
           (f"{V}/quality-storage-1.mp4", {"zh":"系统现场运行","en":"Running on site"})]),
 "pipe/intelligent-inspection": dict(
   hero=f"{C}/core-inspection.webp", gallery=[], gtitle={"zh":"","en":""},
   videos=[(f"{V}/inspection-1.mp4", {"zh":"在线智能检测现场","en":"Online inspection on site"}),
           (f"{V}/inspection-2.mp4", {"zh":"检测流程实录","en":"Inspection sequence"})]),
}

ALT = {"zh": {"gravimetric":"米重控制系统","masterbatch":"米重色母控制系统",
              "masterbatch-weighing":"米重色母系统称重版","ultrasonic-big":"超声波在线测厚系统（大管）",
              "ultrasonic-small":"超声波在线测厚系统（小管）","quality-storage":"管材质量安全入库系统",
              "intelligent-inspection":"管材在线智能检测系统"},
       "en": {"gravimetric":"Gravimetric Control System","masterbatch":"Gravimetric Masterbatch Control System",
              "masterbatch-weighing":"Masterbatch Weighing Edition","ultrasonic-big":"Ultrasonic Thickness (large pipe)",
              "ultrasonic-small":"Ultrasonic Thickness (small bore)","quality-storage":"Pipe Quality Safety Storage System",
              "intelligent-inspection":"Online Intelligent Pipe Inspection"}}

VID_LABEL = {"zh": ("现场影像", "你的浏览器不支持视频播放。"),
             "en": ("Video", "Your browser cannot play this video.")}


def build_gallery(paths, title, lang, alt):
    ok = [p for p in paths if has(p)]
    if not ok:
        return ""
    items = []
    for i, p in enumerate(ok, 1):
        w, h = dims(p)
        items.append(f'    <figure class="shot"><img src="{p}" alt="{alt} · {i}" '
                     f'width="{w}" height="{h}" loading="lazy"></figure>')
    return (f'<section class="section"><div class="wrap">\n'
            f'  <div class="sh"><h2>{title}</h2></div>\n'
            f'  <div class="shot-grid">\n' + "\n".join(items) + "\n  </div>\n</div></section>")


def build_videos(vids, lang, alt):
    ok = [(p, cap) for p, cap in vids if has(p)]
    if not ok:
        return ""
    head, fallback = VID_LABEL[lang]
    items = []
    for p, cap in ok:
        items.append(f'    <figure class="vshot">\n'
                     f'      <video controls preload="none" playsinline>\n'
                     f'        <source src="{p}" type="video/mp4">{fallback}\n'
                     f'      </video>\n'
                     f'      <figcaption>{cap[lang]}</figcaption>\n'
                     f'    </figure>')
    return (f'<section class="section mist"><div class="wrap">\n'
            f'  <div class="sh"><h2>{head}</h2></div>\n'
            f'  <div class="vshot-grid">\n' + "\n".join(items) + "\n  </div>\n</div></section>")


changed = 0
for key, plan in PLAN.items():
    div, slug = key.split("/")
    for lang in ("zh", "en"):
        f = f"src/content/{lang}/{div}/{slug}.html"
        if not os.path.exists(f):
            print("  跳过(无此页):", f); continue
        raw = open(f, encoding="utf-8").read()
        meta_s, _, body = raw.partition("\n---\n")
        alt = ALT[lang].get(slug, slug)

        # 1) 主图：有 prod-hero-media 就换，没有就补进 hero
        hero = plan["hero"]
        if hero and has(hero):
            w, h = dims(hero)
            tag = (f'<img src="{hero}" alt="{alt}" width="{w}" height="{h}">')
            if 'class="prod-hero-media"' in body:
                body = re.sub(r'(<div class="prod-hero-media">)<img[^>]*>',
                              lambda m: m.group(1) + tag, body, count=1)
            else:
                # 线缆页：hero 里没有图，插一张
                body = re.sub(r'(<section class="section prod-hero">\s*<div class="wrap">)',
                              lambda m: m.group(1) + f'\n    <div class="prod-hero-media solo">{tag}</div>',
                              body, count=1)

        # 2) 图库 + 视频：插在结尾 CTA 之前
        gal = build_gallery(plan["gallery"], plan["gtitle"][lang], lang, alt)
        vid = build_videos(plan["videos"], lang, alt)
        block = "\n\n".join(x for x in (gal, vid) if x)
        if block:
            m = re.search(r'<section class="section prod-foot-cta on-dark">', body)
            body = (body[:m.start()] + block + "\n\n" + body[m.start():]) if m else body + "\n" + block

        open(f, "w", encoding="utf-8").write(meta_s + "\n---\n" + body.strip("\n") + "\n")
        changed += 1

print(f"铺开 {changed} 个页面")
