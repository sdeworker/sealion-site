# -*- coding: utf-8 -*-
"""生成两个事业部入口页（中/英），卡片信息取自各产品页自身的元数据"""
import json, os, re

PIPE = ["gravimetric", "masterbatch", "masterbatch-weighing", "multi-dosing", "ultrasonic-small",
        "cloud-monitoring", "ultrasonic-big", "quality-storage", "intelligent-inspection"]
CABLE = ["gravimetric", "masterbatch", "masterbatch-weighing", "multi-dosing", "laser-caliper",
         "ultrasonic-small", "cloud-monitoring"]

TEXT = {
    "pipe": {
        "zh": {
            "title": "管道挤出事业部 — 海狮科技",
            "desc": "海狮管道挤出事业部：面向 PE 给水管、燃气管、PPR、PVC、波纹管产线，提供米重控制、色母计量、超声波在线测厚、质量安全入库与在线智能检测共 8 套测控系统。",
            "eyebrow": "管道挤出事业部",
            "h1": "管道挤出：从下料口到入库口，全程可测可控",
            "lead": "管子出了模具就定型，壁厚偏了、米重超了，回头再看已是几吨料的事。管道挤出事业部把测量放进产线本身——喂料端控米重、机头后测壁厚、下线前查质量，让每一米管都在你设定的范围里走完全程。",
            "secTitle": "本事业部的 9 套系统",
            "why": [
                ("控在源头", "米重系统装在挤出机进料口，用 PID 闭环实时调主机转速与牵引速度，标准条件下控制精度可达 0.3%，节省 2%–5% 原料。"),
                ("测在机头", "超声波在线测厚在水箱里非接触测量运动中的管材，壁厚、外径、偏心度、椭圆度即时可见，不必等切开才知道。"),
                ("查在下线", "管材质量安全入库与在线智能检测在下线端把壁厚、外径、长度、不圆度逐根核过，不合格的管止步于仓库门口。"),
            ],
            "industries": [("pe-water-pipe", "PE 给水管"), ("pe-gas-pipe", "PE 燃气管"),
                           ("ppr-pipe", "PPR 管"), ("pvc-pipe", "PVC 管"),
                           ("corrugated-pipe", "波纹管 / 缠绕管"), ("plastic-piping", "塑料管道")],
            "indTitle": "典型应用行业",
            "ctaTitle": "把你的产线情况讲给工程师听",
            "ctaBody": "管径范围、材料、产量、现有设备品牌——说清楚这几项，我们才能给出对得上的方案。",
            "ctaBtn": "联系技术工程师",
            "other": "也做线缆挤出？",
            "otherLink": "去线缆挤出事业部",
        },
        "en": {
            "title": "Pipe Extrusion Division — Sealion Tech",
            "desc": "Sealion's Pipe Extrusion Division: eight measurement and control systems for PE water and gas pipe, PPR, PVC and corrugated pipe lines — gravimetric control, masterbatch dosing, ultrasonic wall thickness, inbound quality and online inspection.",
            "eyebrow": "Pipe Extrusion Division",
            "h1": "Pipe extrusion: measurable and controllable from the feed throat to the warehouse door",
            "lead": "A pipe is set the moment it leaves the die. By the time an out-of-tolerance wall shows up, it is measured in tonnes of material. This division puts the measurement inside the line itself — weight controlled at the feed, wall measured after the die, quality checked before it is stored.",
            "secTitle": "The nine systems in this division",
            "why": [
                ("Control at the source", "The gravimetric system sits at the extruder feed throat and closes the loop on screw and haul-off speed, holding 0.3% under standard conditions and saving 2%–5% of material."),
                ("Measure at the die", "Ultrasonic gauging measures moving pipe without contact in the cooling tank — wall, diameter, eccentricity and ovality visible immediately, not after somebody cuts a sample."),
                ("Check before storage", "Inbound quality and online inspection verify wall, diameter, length and ovality on every pipe, so the bad ones stop at the warehouse door."),
            ],
            "industries": [("pe-water-pipe", "PE water pipe"), ("pe-gas-pipe", "PE gas pipe"),
                           ("ppr-pipe", "PPR pipe"), ("pvc-pipe", "PVC pipe"),
                           ("corrugated-pipe", "Corrugated pipe"), ("plastic-piping", "Plastic piping")],
            "indTitle": "Typical industries",
            "ctaTitle": "Tell an engineer about your line",
            "ctaBody": "Diameter range, material, output, and the brands already on the line — with those four we can answer with something that actually fits.",
            "ctaBtn": "Talk to an engineer",
            "other": "Also running cable lines?",
            "otherLink": "Go to the Cable Extrusion Division",
        },
        "ru": {
            "title": "Подразделение экструзии труб — Sealion Tech",
            "desc": "Подразделение экструзии труб Sealion: восемь систем измерения и управления для линий ПЭ труб водоснабжения и газоснабжения, ППР, ПВХ и гофрированных труб — гравиметрический контроль, дозирование суперконцентрата, ультразвуковое измерение толщины, входной контроль качества и контроль в линии.",
            "eyebrow": "Подразделение экструзии труб",
            "h1": "Экструзия труб: измеряемо и управляемо от загрузочной горловины до склада",
            "lead": "Труба принимает форму сразу после фильеры. Когда отклонение стенки становится заметным, оно измеряется уже тоннами сырья. Это подразделение помещает измерение внутрь самой линии: масса контролируется на загрузке, стенка измеряется после фильеры, качество проверяется до склада.",
            "secTitle": "Девять систем подразделения",
            "why": [
                ("Контроль у источника", "Гравиметрическая система устанавливается на загрузочной горловине экструдера и замыкает контур по частоте вращения шнека и скорости тяги, удерживая 0,3% в стандартных условиях и экономя 2–5% сырья."),
                ("Измерение после фильеры", "Ультразвук измеряет движущуюся трубу бесконтактно в ванне охлаждения: стенка, диаметр, эксцентриситет и овальность видны сразу, а не после того, как кто-то отрежет образец."),
                ("Проверка перед складом", "Системы входного контроля и контроля в линии проверяют стенку, диаметр, длину и овальность каждой трубы, чтобы брак останавливался у ворот склада."),
            ],
            "industries": [("pe-water-pipe", "ПЭ труба водоснабжения"), ("pe-gas-pipe", "ПЭ газовая труба"),
                           ("ppr-pipe", "ППР труба"), ("pvc-pipe", "ПВХ труба"),
                           ("corrugated-pipe", "Гофрированная труба"), ("plastic-piping", "Пластиковые трубопроводы")],
            "indTitle": "Типовые отрасли",
            "ctaTitle": "Расскажите инженеру о вашей линии",
            "ctaBody": "Диапазон диаметров, материал, производительность и марки уже установленного оборудования — с этими четырьмя пунктами мы ответим по существу.",
            "ctaBtn": "Связаться с инженером",
            "other": "Также работаете с кабелем?",
            "otherLink": "Перейти в подразделение экструзии кабеля",
        },
    },
    "cable": {
        "zh": {
            "title": "线缆挤出事业部 — 海狮科技",
            "desc": "海狮线缆挤出事业部：面向电缆护套、绝缘层、医疗导管等挤出产线，提供米重控制、色母计量、超声波在线测厚（小管）与挤出云远程监控共 5 套测控系统。",
            "eyebrow": "线缆挤出事业部",
            "h1": "线缆挤出：护套厚一点点，一年就是一笔料钱",
            "lead": "线缆护套和绝缘层没法像管材那样随手切开量。厚了是白送料，薄了是质量事故——差别往往只在零点几毫米之间。线缆挤出事业部用米重与超声波两条线索，把这零点几毫米变成产线上看得见、控得住的数字。",
            "secTitle": "本事业部的 7 套系统",
            "why": [
                ("按米控料", "米重系统实时监测每米重量并闭环调节主机与牵引，把护套厚度稳定在设定值附近，省下的是每一盘都在多送的那点料。"),
                ("按盘算账", "设定每盘收卷长度与计划盘数，系统自动算出需要领取的物料重量；反过来输入已领料重，也能算出这批料能出多少盘。"),
                ("小管测厚", "超声波小管系统面向 Φ2–50mm，非接触测量护套壁厚、外径与偏心度，医疗导管这类细管同样适用。"),
            ],
            "industries": [("cable-sheathing", "电缆护套"), ("medical-catheter", "医疗导管"),
                           ("masterbatch-compounds", "色母与改性料")],
            "indTitle": "典型应用行业",
            "ctaTitle": "把你的线缆规格讲给工程师听",
            "ctaBody": "线径范围、护套材料、产量、收卷方式——说清楚这几项，方案才对得上。",
            "ctaBtn": "联系技术工程师",
            "other": "也做管道挤出？",
            "otherLink": "去管道挤出事业部",
        },
        "en": {
            "title": "Cable Extrusion Division — Sealion Tech",
            "desc": "Sealion's Cable Extrusion Division: five measurement and control systems for cable sheathing, insulation and medical tubing lines — gravimetric control, masterbatch dosing, small-bore ultrasonic gauging and cloud monitoring.",
            "eyebrow": "Cable Extrusion Division",
            "h1": "Cable extrusion: a fraction of a millimetre on the sheath is a year's material bill",
            "lead": "You cannot cut open a sheath the way you can sample a pipe. Too thick and you are giving material away; too thin and it is a quality failure — and the difference is often a few tenths of a millimetre. This division turns those tenths into numbers the line can see and hold.",
            "secTitle": "The seven systems in this division",
            "why": [
                ("Control by the metre", "The gravimetric system tracks weight per metre live and closes the loop on extruder and haul-off, holding sheath thickness near setpoint — what it saves is the material every drum was quietly carrying."),
                ("Plan by the drum", "Set wound length per drum and the number of drums and the system works out the material to draw; enter the weight already drawn and it tells you how many drums it will make."),
                ("Gauge small bores", "The small-bore ultrasonic system covers Φ2–50mm, measuring sheath wall, diameter and eccentricity without contact — medical tubing included."),
            ],
            "industries": [("cable-sheathing", "Cable sheathing"), ("medical-catheter", "Medical catheter"),
                           ("masterbatch-compounds", "Masterbatch & compounds")],
            "indTitle": "Typical industries",
            "ctaTitle": "Tell an engineer about your cable spec",
            "ctaBody": "Diameter range, sheath material, output and how you wind it — with those we can answer with something that fits.",
            "ctaBtn": "Talk to an engineer",
            "other": "Also running pipe lines?",
            "otherLink": "Go to the Pipe Extrusion Division",
        },
        "ru": {
            "title": "Подразделение экструзии кабеля — Sealion Tech",
            "desc": "Подразделение экструзии кабеля Sealion: пять систем измерения и управления для линий кабельной оболочки, изоляции и медицинских катетеров — гравиметрический контроль, дозирование суперконцентрата, ультразвуковое измерение малых диаметров и облачный мониторинг.",
            "eyebrow": "Подразделение экструзии кабеля",
            "h1": "Экструзия кабеля: доля миллиметра на оболочке — это годовой счёт за сырьё",
            "lead": "Оболочку нельзя разрезать так, как отбирают образец трубы. Идёте с запасом — отдаёте сырьё даром; идёте тонко — это уже дефект качества. Разница часто составляет несколько десятых миллиметра. Подразделение превращает эти десятые в цифры, которые линия видит и удерживает.",
            "secTitle": "Семь систем подразделения",
            "why": [
                ("Контроль по метру", "Гравиметрическая система отслеживает массу погонного метра в реальном времени и замыкает контур по экструдеру и тяге, удерживая толщину оболочки у заданного значения — экономится то сырьё, которое каждый барабан тихо уносил с собой."),
                ("Расчёт по барабанам", "Задайте длину намотки на барабан и число барабанов — система рассчитает необходимую массу материала; введите уже полученную массу — получите число барабанов."),
                ("Измерение малых диаметров", "Ультразвуковая система для Φ2–50 мм измеряет толщину оболочки, диаметр и эксцентриситет бесконтактно, включая медицинские трубки."),
            ],
            "industries": [("cable-sheathing", "Кабельная оболочка"), ("medical-catheter", "Медицинский катетер"),
                           ("masterbatch-compounds", "Суперконцентраты и компаунды")],
            "indTitle": "Типовые отрасли",
            "ctaTitle": "Расскажите инженеру о вашей спецификации",
            "ctaBody": "Диапазон диаметров, материал оболочки, производительность и способ намотки — этого достаточно, чтобы ответить по существу.",
            "ctaBtn": "Связаться с инженером",
            "other": "Также работаете с трубой?",
            "otherLink": "Перейти в подразделение экструзии труб",
        },
    },
}


def prod_meta(lang, slug, div):
    """产品卡片信息取自该产品页自身元数据"""
    p = f"src/content/{lang}/{div}/{slug}.html"
    if not os.path.exists(p):
        p = f"src/content/{lang}/pipe/{slug}.html"
    if not os.path.exists(p):                       # 该语种尚未翻译，回退英文
        p = f"src/content/en/{div}/{slug}.html"
    if not os.path.exists(p):
        p = f"src/content/en/pipe/{slug}.html"
    meta = json.loads(open(p, encoding="utf-8").read().split("\n---\n")[0])
    t = re.sub(r"\s*[—-]\s*(海狮科技|Sealion Tech).*$", "", meta["title"]).strip()
    return t, meta.get("description", "")


def build(div, lang):
    T = TEXT[div][lang]
    slugs = PIPE if div == "pipe" else CABLE
    other = "cable" if div == "pipe" else "pipe"
    root = "/" if lang == "zh" else "/en/"

    more_lbl = {"zh": "了解详情", "en": "Read more", "ru": "Подробнее"}[lang]
    cards = []
    for s in slugs:
        t, d = prod_meta(lang, s, div)
        cards.append(
            f'    <a class="pcard" href="{root}{div}/{s}.html">\n'
            f'      <h3>{t}</h3>\n'
            f'      <p>{d}</p>\n'
            f'      <span class="arrow-link">{more_lbl}</span>\n'
            f'    </a>')

    why = "\n".join(
        f'    <div class="func"><b>{a}</b> {b}</div>' for a, b in T["why"])
    inds = "\n".join(
        f'      <a class="ind-tag" href="{root}industries/{slug}.html"><i></i>{label}</a>'
        for slug, label in T["industries"])

    body = f'''<section class="section prod-hero">
  <div class="wrap">
    <span class="eyebrow">{T["eyebrow"]}</span>
    <h1>{T["h1"]}</h1>
    <p class="lead">{T["lead"]}</p>
  </div>
</section>

<section class="section mist"><div class="wrap">
  <div class="grid cols-2 func-grid">
{why}
  </div>
</div></section>

<section class="section"><div class="wrap">
  <div class="sh"><h2>{T["secTitle"]}</h2></div>
  <div class="pcard-grid">
{chr(10).join(cards)}
  </div>
</div></section>

<section class="section apply"><div class="wrap">
  <div class="sh"><h2>{T["indTitle"]}</h2></div>
  <div class="ind-tags">
{inds}
  </div>
  <p class="lead" style="margin-top:2rem"><a class="arrow-link" href="{root}{other}/">{T["other"]} {T["otherLink"]}</a></p>
</div></section>

<section class="section prod-foot-cta on-dark"><div class="wrap narrow">
  <h2>{T["ctaTitle"]}</h2>
  <p class="lead">{T["ctaBody"]}</p>
  <a class="btn" href="{root}#contact">{T["ctaBtn"]}</a>
</div></section>'''

    meta = {"title": T["title"], "description": T["desc"], "css": ["product"], "type": "page"}
    out = f"src/content/{lang}/{div}/index.html"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(
        json.dumps(meta, ensure_ascii=False, indent=1) + "\n---\n" + body + "\n")
    return out


for div in ("pipe", "cable"):
    for lang in ("zh", "en", "ru"):
        print("生成", build(div, lang))
