# -*- coding: utf-8 -*-
"""新增两个产品：多组份混配系统（管道+线缆）、双轴激光测径仪（仅线缆）"""
import json, os
from PIL import Image

def wh(rel):
    with Image.open("public" + rel) as im:
        return im.size

MULTI_IMG = "/assets/2026/core/core-multi-dosing.webp"
LASER_IMG = "/assets/2026/core/core-laser-gauge.webp"
LASER_SPEC = "/assets/2026/core/core-laser-gauge-spec.webp"


def page(meta, body, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8").write(
        json.dumps(meta, ensure_ascii=False, indent=1) + "\n---\n" + body.strip("\n") + "\n")


def hero(lang, div, eyebrow, h1, lead, img, alt):
    root = {"zh": "/", "en": "/en/", "ru": "/ru/"}[lang]
    home = {"zh": "首页", "en": "Home", "ru": "Главная"}[lang]
    dname = {"zh": {"pipe": "管道挤出事业部", "cable": "线缆挤出事业部"},
             "en": {"pipe": "Pipe Extrusion Division", "cable": "Cable Extrusion Division"},
             "ru": {"pipe": "Подразделение экструзии труб", "cable": "Подразделение экструзии кабеля"}}[lang][div]
    w, h = wh(img)
    return f'''<section class="section prod-hero">
  <div class="wrap">
    <nav class="crumb"><a href="{root}">{home}</a> / <a href="{root}{div}/">{dname}</a></nav>
    <div class="prod-hero-grid">
      <div class="prod-hero-media"><img src="{img}" alt="{alt}" width="{w}" height="{h}"></div>
      <div class="prod-hero-body">
        <span class="eyebrow">{eyebrow}</span>
        <h1>{h1}</h1>
        <p class="lead">{lead}</p>
      </div>
    </div>
  </div>
</section>'''


def cta(lang, div):
    root = {"zh": "/", "en": "/en/", "ru": "/ru/"}[lang]
    T = {"zh": ("把你的产线情况讲给工程师听", "组份数量、添加比例、产量与现有设备品牌——说清楚这几项，方案才对得上。", "联系技术工程师"),
         "en": ("Tell an engineer about your line", "Number of components, dosing ratio, output and the brands already on the line — with those we can answer with something that fits.", "Talk to an engineer"),
         "ru": ("Расскажите инженеру о вашей линии", "Число компонентов, соотношение дозирования, производительность и марки установленного оборудования — с этими данными мы ответим по существу.", "Связаться с инженером")}[lang]
    return f'''<section class="section prod-foot-cta on-dark"><div class="wrap narrow">
  <h2>{T[0]}</h2>
  <p class="lead">{T[1]}</p>
  <a class="btn" href="{root}#contact">{T[2]}</a>
</div></section>'''


# ---------------- 多组份混配系统 ----------------
MULTI = {
 "zh": dict(
  title="多组份混配系统 Multi-Component Dosing System",
  desc="海狮多组份配色喂料控制系统：西门子 PLC + 伺服马达 + 定制螺杆，2–4 组份按比例连续在线混配，不停机换料，喂料精度可达 0.5%；称重版采用 PID 闭环与托利多传感器，精度 0.2%–0.5%。",
  eyebrow="多组份混配", h1="多组份混配系统",
  lead="按配方把几种原料同时、连续、精准地送进挤出机——而且换料不用停机。系统分体积式与称重式两种，前者靠定制螺杆按转速配比，后者靠称重闭环实时纠偏。",
  secs=[("体积式：多组份配色喂料控制系统", [
      ("硬件构成", "全系采用西门子 PLC 中央处理器、伺服马达与定制螺杆，按预设比例混合，由控制系统换算成转速直接驱动精密螺杆挤出色母原料。"),
      ("不停机换料", "生产不中断即可自由切换色母，保证连续生产，效率显著提高。"),
      ("喂料精度 0.5%", "比普通喂料机更精密稳定；即使在小于 0.5kg/h 的微小产量下，也能保持稳定的喂料精度。"),
      ("组份数量", "可添加 2–4 种组份，可按客户要求定制。"),
  ]),
  ("称重式：多组份称重配色配方喂料控制系统", [
      ("称重闭环", "基于重量检测的闭环控制，采用 PID 方式，配西门子 PLC、伺服马达与托利多高精度称重传感器。"),
      ("实时自适应", "持续称量各物料的挤出消耗量，实时采集挤出螺杆转速形成闭环；设定配方比例后，按自适应算法实时调节螺杆转速，全自动达成配方要求。"),
      ("喂料精度 0.2%–0.5%", "波动范围在 0.3% 以内，喂料稳定可靠；微小产量下同样保持精度。"),
      ("为什么重要", "高精度配色与配方的连续生产中，各物料能否恒定输出，直接决定产品质量与成本控制。"),
  ]),
  ("共同优势", [
      ("在线连续混配", "减少人工耗时费力，落实智能制造与数字化管理。"),
      ("数据永久留存", "具备数据的永久记忆及存储功能，生产用料数据上传，可查询任意时间段的用料量。"),
      ("模块化易清理", "模块化装配结构，拆装方便；采用气动自动清洁料筒内壁，避免残留辅料造成不良产品。"),
      ("自动混料", "自动混料装置按比例输送，保持混料均匀。"),
      ("接口与联网", "可同时满足外部信号输入要求，留有数据传送接口便于信息化采集。"),
      ("远程可选", "可选配远程控制系统，实现远程技术支持与预警售后服务。"),
  ])],
  ind="适用行业：塑料薄膜、电线电缆、塑料改性、化工，以及各种多组份精确配比添加的行业。"),
 "en": dict(
  title="Multi-Component Dosing System",
  desc="Sealion multi-component colour dosing: Siemens PLC, servo motors and custom screws dose 2–4 components continuously to ratio, with colour changes on the run and 0.5% feeding accuracy; the weighing edition closes a PID loop on Mettler-Toledo load cells for 0.2%–0.5%.",
  eyebrow="Multi-component dosing", h1="Multi-Component Dosing System",
  lead="Feed several materials into the extruder at once, continuously and to recipe — and change colour without stopping the line. Two editions: volumetric, which meters by screw speed, and gravimetric, which closes a weighing loop and corrects in real time.",
  secs=[("Volumetric: colour dosing and feeding control", [
      ("What it is built from", "Siemens PLC, servo motors and custom screws throughout. The controller converts the preset ratio into a screw speed and drives the metering screw directly."),
      ("Colour change on the run", "Masterbatch can be switched without stopping production, keeping the line continuous and lifting output."),
      ("0.5% feeding accuracy", "More precise and more stable than a general-purpose feeder, and it holds that accuracy even below 0.5 kg/h."),
      ("Components", "Two to four components, and the count can be built to order."),
  ]),
  ("Gravimetric: weighing, colour and recipe feeding control", [
      ("A weighing loop", "Closed-loop control on measured weight using PID, with Siemens PLC, servo motors and Mettler-Toledo load cells."),
      ("Adaptive in real time", "It weighs what each material actually consumes and reads screw speed to close the loop; once the recipe ratio is set, an adaptive algorithm trims screw speed to hold it automatically."),
      ("0.2%–0.5% accuracy", "Fluctuation stays within 0.3%, and accuracy holds at very low throughput."),
      ("Why it matters", "In continuous production to a tight colour or recipe spec, whether each material comes out at a constant rate is what decides quality and cost."),
  ]),
  ("Shared advantages", [
      ("Continuous in-line blending", "Less manual labour, and a step towards digital production management."),
      ("Data kept permanently", "Consumption data is stored and uploaded, so material use over any period can be queried."),
      ("Modular and easy to clean", "Modular assembly for quick strip-down, with pneumatic cleaning of the barrel wall so no additive is left to spoil the next run."),
      ("Automatic blending", "The blender conveys to ratio and keeps the mix even."),
      ("Interfaces", "External signal inputs are supported and a data interface is provided for plant systems."),
      ("Remote option", "An optional remote system enables remote support and early warning."),
  ])],
  ind="Industries: plastic film, wire and cable, plastic modification, chemicals, and any process needing precise multi-component proportioning."),
}

# ---------------- 双轴激光测径仪 ----------------
LASER = {
 "zh": dict(
  title="双轴激光测径仪 Dual-axis Laser Caliper",
  desc="海狮双轴激光测径仪：双轴激光扫描、非接触检测，实时输出外径与椭圆度数据，精度 ±0.001mm，可高速在线检测并接入 PLC。适用于塑料管材、线缆、金属丝、医疗导管、棒材与丝材。",
  eyebrow="双轴激光测径仪", h1="外径与椭圆度，双轴同步、不碰产品",
  lead="激光从两个轴向同时扫描，产品不必接触任何测量部件。外径与椭圆度实时输出，精度 ±0.001mm，可高速在线检测并把数据交给 PLC 参与闭环。",
  feats=[("双轴同步扫描", "两个轴向同时测量，避免单轴测径遇到椭圆时读数随机的问题。"),
         ("非接触、不损伤", "不接触产品表面，适合软质、高温或表面要求高的产品。"),
         ("精度 ±0.001mm", "适合对尺寸公差要求严格的产线。"),
         ("高速在线检测", "在产线速度下持续输出，不需要停机取样。"),
         ("可接入 PLC", "数据可交给产线控制系统，参与自动调节。"),
         ("输出椭圆度", "同时给出外径与椭圆度，不圆的问题在发生时就能看见。")],
  ind="适用：塑料管材、线缆、金属丝、医疗导管、棒材、丝材等。"),
 "en": dict(
  title="Dual-axis Laser Caliper",
  desc="Sealion dual-axis laser caliper: dual-axis scanning, non-contact measurement, outer diameter and ovality output live at ±0.001mm accuracy, high-speed in-line, connectable to a PLC. For plastic pipe, cable, metal wire, medical catheter, rod and filament.",
  eyebrow="Dual-axis laser caliper", h1="Diameter and ovality, measured on two axes without touching the product",
  lead="Lasers scan on two axes at once, so nothing touches the product. Outer diameter and ovality are output live at ±0.001mm, at line speed, and the data can be handed to a PLC to close a loop.",
  feats=[("Two axes at once", "Measuring on both axes avoids the wandering reading a single-axis gauge gives on an oval product."),
         ("Non-contact", "Nothing touches the surface, which suits soft, hot or finish-critical products."),
         ("±0.001mm", "For lines held to tight dimensional tolerance."),
         ("High-speed in-line", "Continuous output at line speed, with no need to stop and sample."),
         ("PLC connectable", "Data can go to the line controller and take part in automatic correction."),
         ("Ovality as well", "Diameter and ovality together, so out-of-round shows as it happens.")],
  ind="For: plastic pipe, cable, metal wire, medical catheter, rod and filament."),
}


def build_multi(lang, div):
    d = MULTI[lang]
    secs = []
    for i, (title, items) in enumerate(d["secs"]):
        cards = "\n".join(f'    <div class="func"><b>{a}</b> {b}</div>' for a, b in items)
        cls = "section" if i % 2 == 0 else "section mist"
        secs.append(f'<section class="{cls}"><div class="wrap">\n'
                    f'  <div class="sh"><h2>{title}</h2></div>\n'
                    f'  <div class="grid cols-2 func-grid">\n{cards}\n  </div>\n</div></section>')
    body = (hero(lang, div, d["eyebrow"], d["h1"], d["lead"], MULTI_IMG, d["title"]) + "\n\n"
            + "\n\n".join(secs) + "\n\n"
            + f'<section class="section"><div class="wrap narrow">\n  <p class="lead">{d["ind"]}</p>\n</div></section>\n\n'
            + cta(lang, div))
    page({"title": d["title"] + (" — 海狮科技" if lang == "zh" else " — Sealion Tech"),
          "description": d["desc"], "css": ["product"], "type": "product"},
         body, f"src/content/{lang}/{div}/multi-dosing.html")


def build_laser(lang):
    d = LASER[lang]
    cards = "\n".join(f'    <div class="func"><b>{a}</b> {b}</div>' for a, b in d["feats"])
    sw, sh = wh(LASER_SPEC)
    body = (hero(lang, "cable", d["eyebrow"], d["h1"], d["lead"], LASER_IMG, d["title"]) + "\n\n"
            + f'<section class="section mist"><div class="wrap">\n'
              f'  <div class="sh"><h2>{"产品特点" if lang=="zh" else "Features"}</h2></div>\n'
              f'  <div class="grid cols-2 func-grid">\n{cards}\n  </div>\n</div></section>\n\n'
            + f'<section class="section"><div class="wrap">\n'
              f'  <div class="sh"><h2>{"产品说明" if lang=="zh" else "Product sheet"}</h2></div>\n'
              f'  <figure class="shot" style="max-width:900px;margin:1.6rem auto 0">'
              f'<img src="{LASER_SPEC}" alt="{d["title"]}" width="{sw}" height="{sh}" loading="lazy"></figure>\n'
              f'  <p class="lead" style="margin-top:1.4rem">{d["ind"]}</p>\n</div></section>\n\n'
            + cta(lang, "cable"))
    page({"title": d["title"] + (" — 海狮科技" if lang == "zh" else " — Sealion Tech"),
          "description": d["desc"], "css": ["product"], "type": "product"},
         body, f"src/content/{lang}/cable/laser-caliper.html")


for lang in ("zh", "en"):
    for div in ("pipe", "cable"):
        build_multi(lang, div)
    build_laser(lang)
    print(f"  {lang}: multi-dosing ×2（管道/线缆） + laser-caliper ×1（线缆）")
