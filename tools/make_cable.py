# -*- coding: utf-8 -*-
"""
由管道版产品页派生线缆版：
  · 共用的技术内容（参数表、软件功能、报警自查等）原样保留 —— 是同一套系统
  · 面向客户的框架部分（hero / 价值主张 / 行业链接 / 结尾 CTA）按线缆口径重写
  · 米重页另补电缆版说明书独有内容（周长/外径/护套壁厚换算、按盘计数与领料）
"""
import json, os, re

CABLE = ["gravimetric", "masterbatch", "masterbatch-weighing",
         "ultrasonic-small", "cloud-monitoring"]

# 每个产品的线缆版「开头」——取代管道版的 prod-hero
HERO = {
    "gravimetric": {
        "zh": ("米重控制系统 · 线缆版",
               "护套多包的那零点几毫米，一年是多少料？",
               "线缆护套和绝缘层不像管材可以随手切一段量。厚了看不出来，只是每一盘都在多送料；薄了要到检验环节才暴露。米重控制系统装在挤出机进料口，实时算出每米重量，闭环调节主机转速与牵引速度，把这零点几毫米摁在你设定的范围里。"),
        "en": ("Gravimetric Control System · Cable",
               "What does a fraction of a millimetre of extra sheath cost in a year?",
               "You cannot sample a sheath the way you can cut a pipe. Run thick and nothing looks wrong — every drum is simply carrying material you gave away. Run thin and it surfaces at inspection. The gravimetric system sits at the feed throat, works out weight per metre live, and closes the loop on screw and haul-off speed to hold those tenths where you set them."),
    },
    "masterbatch": {
        "zh": ("米重色母控制系统 · 线缆版",
               "颜色对了，色母也别多加",
               "线缆护套的颜色是识别标准，色母不能少加；但色母单价远高于基料，多加就是白花钱。本系统把色母添加量与实测产量绑定，按比例实时给定，颜色稳定的同时不让色母超投。"),
        "en": ("Gravimetric Masterbatch Control · Cable",
               "Get the colour right without over-dosing",
               "Sheath colour is an identification standard, so masterbatch cannot be skimped. But it costs far more than base resin, and over-dosing is money burned. This system ties masterbatch feed to measured output and doses to ratio in real time — stable colour, no overshoot."),
    },
    "masterbatch-weighing": {
        "zh": ("米重色母系统称重版 · 线缆版",
               "每一份色母都过秤，不靠估",
               "称重版在计量环节加入独立称重单元，色母与基料各自过秤后再混合。对配色要求严、或原料密度批次波动大的线缆产线，这一步把配比从「大致准」变成「有据可查」。"),
        "en": ("Gravimetric Masterbatch, Weighing Edition · Cable",
               "Every dose of masterbatch is weighed, not estimated",
               "The weighing edition adds an independent weighing unit so masterbatch and base resin are each weighed before blending. On cable lines with tight colour requirements, or where resin density drifts between batches, this turns the ratio from roughly right into on the record."),
    },
    "ultrasonic-small": {
        "zh": ("超声波在线测厚系统（小管） · 线缆版",
               "Φ2–50mm，护套厚薄不必等切开",
               "小管超声波系统面向 Φ2–50mm 的细径产品，非接触测量护套壁厚、外径与偏心度。线缆、医疗导管、细管这类没法随时取样的产品，正是它的用场——偏心刚开始跑就能看见，而不是等到成盘之后。"),
        "en": ("Ultrasonic Thickness Online (Small Bore) · Cable",
               "Φ2–50mm — sheath thickness without cutting a sample",
               "The small-bore system covers Φ2–50mm, measuring sheath wall, outer diameter and eccentricity without contact. Cable, medical tubing and fine bore products — things you cannot keep sampling — are exactly its case: drift is visible as it starts, not after the drum is wound."),
    },
    "cloud-monitoring": {
        "zh": ("挤出云远程监控系统 · 线缆版",
               "几条线缆产线，在一块屏上看完",
               "线缆厂常常同时跑十几条挤出线，班组长很难逐台盯。本系统把各线的米重、速度、产量、报警汇到云端，办公室或手机上就能看清哪条线在跑偏、哪条线停了。"),
        "en": ("Cloud-Based Extrusion Monitoring · Cable",
               "A dozen cable lines on one screen",
               "Cable plants often run a dozen extrusion lines at once, and no supervisor can stand at every one. This system collects weight per metre, speed, output and alarms from each line into the cloud, so the office — or a phone — shows which line is drifting and which has stopped."),
    },
}

# 线缆版专属补充段落（追加在正文末、CTA 之前）
EXTRA = {
    "gravimetric": {
        "zh": '''<section class="section"><div class="wrap">
  <div class="sh"><span class="eyebrow">Cable only</span><h2>线缆版专有：按盘生产与护套换算</h2>
  <p class="lead">线缆按盘交货，管材按根交货——计量口径不同，软件也不同。以下是电缆版特有的功能。</p></div>
  <div class="grid cols-2 func-grid">
    <div class="func"><b>周长 · 外径 · 护套壁厚换算</b> 系统由实测数据换算出平均电缆周长、电缆外径与护套壁厚，供生产时快速参照（换算值与真实值存在微弱误差，作参考用）。</div>
    <div class="func"><b>按盘判定合格</b> 设定每盘长度后，实际长度与设定值偏差在 ±1 米内判为合格。例如设定 21 米，实测落在 20–22 米之间即计入合格盘数；切割动作后累计长度自动清零重新计数。</div>
    <div class="func"><b>良品废品分开记账</b> 产量页面分别记录生产产量、良品产量、废品产量、生产盘数与生产长度，合格率不必再靠人工统计。</div>
    <div class="func"><b>按盘测算领料</b> 设定每盘收卷长度与计划盘数，系统算出需领取的物料重量；反过来输入已领料重，可算出这批料能出多少盘。</div>
  </div>
</div></section>''',
        "en": '''<section class="section"><div class="wrap">
  <div class="sh"><span class="eyebrow">Cable only</span><h2>Cable edition: drum-based production and sheath conversion</h2>
  <p class="lead">Cable ships by the drum and pipe ships by the length — different accounting, different software.</p></div>
  <div class="grid cols-2 func-grid">
    <div class="func"><b>Circumference, diameter and sheath thickness</b> The system derives mean cable circumference, outer diameter and sheath wall from the measured data as an on-line reference (derived values carry a small error against the true figure).</div>
    <div class="func"><b>Pass/fail by the drum</b> Set the length per drum and anything within ±1 m counts as good — set 21 m and a measured 20–22 m passes. The running length resets automatically at each cut.</div>
    <div class="func"><b>Good and scrap counted separately</b> The output page records total, good and scrap output along with drum count and produced length, so pass rate is not worked out by hand.</div>
    <div class="func"><b>Material planning by drum</b> Enter wound length per drum and the number of drums and it works out the material to draw; enter the weight drawn and it returns how many drums it will make.</div>
  </div>
</div></section>''',
    }
}

# 结尾 CTA（线缆口径）
CTA = {
    "zh": ('把你的线缆规格讲给工程师听',
           '线径范围、护套材料、产量、收卷方式——说清楚这几项，我们才能给出对得上的方案。',
           '联系技术工程师'),
    "en": ('Tell an engineer about your cable spec',
           'Diameter range, sheath material, output and how you wind it — with those we can answer with something that fits.',
           'Talk to an engineer'),
}

CABLE_INDUSTRIES = {
    "zh": [("cable-sheathing", "电缆护套"), ("medical-catheter", "医疗导管"),
           ("masterbatch-compounds", "色母与改性料")],
    "en": [("cable-sheathing", "Cable sheathing"), ("medical-catheter", "Medical catheter"),
           ("masterbatch-compounds", "Masterbatch & compounds")],
}


def derive(lang, slug):
    src = f"src/content/{lang}/pipe/{slug}.html"
    raw = open(src, encoding="utf-8").read()
    meta_s, _, body = raw.partition("\n---\n")
    meta = json.loads(meta_s)

    eyebrow, h1, lead = HERO[slug][lang]

    # 1) 换掉 hero（第一个 prod-hero section）
    m = re.search(r'<section class="section prod-hero">.*?</section>', body, re.S)
    root = "/" if lang == "zh" else "/en/"
    crumb_home = "首页" if lang == "zh" else "Home"
    crumb_div = "线缆挤出事业部" if lang == "zh" else "Cable Extrusion Division"
    hero = f'''<section class="section prod-hero">
  <div class="wrap">
    <nav class="crumb" aria-label="{'面包屑' if lang=='zh' else 'Breadcrumb'}">
      <a href="{root}">{crumb_home}</a> / <a href="{root}cable/">{crumb_div}</a>
    </nav>
    <span class="eyebrow">{eyebrow}</span>
    <h1>{h1}</h1>
    <p class="lead">{lead}</p>
  </div>
</section>'''
    body = body[:m.start()] + hero + body[m.end():] if m else hero + "\n" + body

    # 2) 追加线缆专属段落（若有）
    extra = EXTRA.get(slug, {}).get(lang)
    if extra:
        f = re.search(r'<section class="section prod-foot-cta on-dark">', body)
        body = body[:f.start()] + extra + "\n\n" + body[f.start():] if f else body + "\n" + extra

    # 3) 换掉结尾 CTA
    t, p_, btn = CTA[lang]
    m2 = re.search(r'<section class="section prod-foot-cta on-dark">.*?</section>', body, re.S)
    cta = f'''<section class="section prod-foot-cta on-dark"><div class="wrap narrow">
  <h2>{t}</h2>
  <p class="lead">{p_}</p>
  <a class="btn" href="{root}#contact">{btn}</a>
</div></section>'''
    body = body[:m2.start()] + cta + body[m2.end():] if m2 else body + "\n" + cta

    # 4) 站内链接改指线缆事业部同类页
    for s2 in CABLE:
        body = body.replace(f'{root}pipe/{s2}.html', f'{root}cable/{s2}.html')

    # 5) 元数据
    title_core = eyebrow
    meta["title"] = f"{title_core} — {'海狮科技' if lang=='zh' else 'Sealion Tech'}"
    meta["description"] = re.sub(r"\s+", " ", lead)[:150]
    meta["type"] = "product"

    out = f"src/content/{lang}/cable/{slug}.html"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(
        json.dumps(meta, ensure_ascii=False, indent=1) + "\n---\n" + body.strip("\n") + "\n")
    return out, len(body)


for lang in ("zh", "en"):
    for slug in CABLE:
        o, n = derive(lang, slug)
        print(f"  {o}  ({n} 字节)")
