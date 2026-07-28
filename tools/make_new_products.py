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
  title="高精度多组份混配系统 High-Precision Multi-Component Dosing System",
  desc="海狮高精度多组份混配系统：失重式计量，每通道独立伺服驱动、独立称重、同步下料，智能闭环算法实时调节下料速度，多组分并行精准配比，配方可存储一键切换、全程可追溯。",
  eyebrow="高精度多组份混配", h1="多路同步下料，每一路各自称重",
  lead="采用失重式计量，每个通道配备高精度伺服电机独立驱动，实现多路物料同步送料、通道独立称重。系统实时采集主料、色母粒与颗粒助剂的流量数据，依靠智能闭环算法动态调节伺服下料速度，多组分并行精准配比，保障混配比例持续稳定。",
  secs=[("产品特点", [
      ("模块化多通道", "各路独立称重、同步下料，互不干扰。"),
      ("伺服驱动", "高精度伺服电机驱动，下料响应快、流量线性稳定。"),
      ("适配颗粒物料", "适配各类颗粒物料，支持多配方存储、一键切换。"),
      ("全自动计量", "生产数据自动留存、全程可追溯，适配长期连续挤出生产。"),
  ]),
  ("核心优势", [
      ("同步送料 + 独立称重", "规避分时下料带来的瞬时配比波动，物料混合更均匀。"),
      ("伺服优于步进", "对比传统步进电机无抖动，计量精度更高，长期运行不易漂移。"),
      ("杜绝人工偏差", "配方数据锁定可追溯，有效减少批次色差与物性差异。"),
  ]),
  ("产品价值", [
      ("从源头稳定品质", "稳定管材、线缆、型材成品的色泽与力学性能，降低不良品率，节约原材料损耗。"),
      ("配料工序标准化", "实现配料工序的自动化标准化管控，提升产线效率与产品一致性，保障稳定量产。"),
  ])],
  ind="应用领域：适用于塑料管材、型材、电线电缆、塑胶板材、软管、薄膜等高分子挤出与注塑行业；满足 PE、PVC、PP、ABS 塑胶颗粒搭配色母粒与各类颗粒助剂的自动化精准混配。"),
 "en": dict(
  title="High-Precision Multi-Component Dosing System",
  desc="Sealion high-precision multi-component dosing: loss-in-weight metering with an independent servo drive and independent weighing on every channel, closed-loop algorithms trimming feed speed live, formulas stored for one-click changeover and fully traceable.",
  eyebrow="High-precision multi-component dosing", h1="Every channel feeds together and weighs on its own",
  lead="Loss-in-weight metering, with a high-precision servo driving each channel independently, so several materials feed simultaneously while each is weighed separately. Flow data from base resin, masterbatch and granular additives is collected in real time, and closed-loop algorithms trim servo feed speed to hold the ratio steady.",
  secs=[("Product features", [
      ("Modular multi-channel", "Each channel weighs independently and feeds simultaneously, without interfering with the others."),
      ("Servo driven", "High-precision servo motors give fast response and a linear, stable flow."),
      ("Suits granular materials", "Handles granular materials generally, with formula storage and one-click changeover."),
      ("Fully automatic metering", "Production data is recorded automatically and stays traceable, which suits long continuous extrusion runs."),
  ]),
  ("Core advantages", [
      ("Simultaneous feed, separate weighing", "This avoids the instantaneous ratio swings that time-shared feeding produces, so the blend is more uniform."),
      ("Servo rather than stepper", "No jitter compared with a stepper drive, higher metering precision, and little drift over long runs."),
      ("No manual batching error", "Locked, traceable formula data reduces batch-to-batch colour and property variation."),
  ]),
  ("Product value", [
      ("Quality settled at source", "Colour and mechanical performance of pipe, cable and profile are stabilised from the start, cutting rejects and material waste."),
      ("Standardised batching", "Batching becomes automatic and standardised, lifting line efficiency and product consistency for steady volume production."),
  ])],
  ind="Applications: plastic pipe, profile, wire and cable, plastic sheet, hose and film — extrusion and injection moulding. For automatic precise blending of PE, PVC, PP and ABS granules with masterbatch and granular additives."),
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
