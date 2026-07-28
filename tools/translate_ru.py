# -*- coding: utf-8 -*-
"""
俄语正文翻译：从英文母版逐文本块替换成俄语。
未收录的文本块原样保留，并在结尾报出，便于逐轮补齐。
"""
import json, os, re, glob

# 通用短语（各页共有）
COMMON = {
 "Pipe Extrusion Division": "Подразделение экструзии труб",
 "Cable Extrusion Division": "Подразделение экструзии кабеля",
 "Get a proposal &amp; quote": "Запросить решение и цену",
 "Get a proposal & quote": "Запросить решение и цену",
 "View all products": "Все продукты",
 "Read the manual": "Открыть руководство",
 "Where it is used": "Область применения",
 "Functional characteristics": "Функциональные особенности",
 "Technical data": "Технические характеристики",
 "Technical parameters": "Технические характеристики",
 "Model configurations": "Исполнения и модели",
 "Main functions": "Основные функции",
 "System advantages": "Преимущества системы",
 "On site": "На объекте",
 "Video": "Видео",
 "Overview": "Обзор",
 "Filmed on site": "Съёмка на объекте",
 "Control software screen recording": "Запись экрана управляющей программы",
 "Co-extrusion line, on site": "Линия соэкструзии на объекте",
 "Weighing edition on site": "Весовое исполнение на объекте",
 "Co-extrusion line": "Линия соэкструзии",
 "Small-bore gauging on site": "Измерение малых диаметров на объекте",
 "Fine-bore gauging on site": "Измерение тонких диаметров на объекте",
}

# 各页专属
PAGES = {
 "cloud-monitoring": {
  "Cloud-Based Extrusion Monitoring System": "Система облачного мониторинга экструзии",
  "Products · 08": "Продукция · 08",
  "Connects the company's ERP system with the line's execution system, collecting shop-floor data in real time to a cloud or internal server — giving management full visibility of the process, shortening response time, lifting quality and cutting cost.":
    "Связывает ERP предприятия с системой исполнения на линии, собирая цеховые данные в реальном времени в облако или на внутренний сервер: руководство видит весь процесс, время реакции сокращается, качество растёт, издержки снижаются.",
  "With global competition in manufacturing, enterprises face constant challenges and change. Industrial upgrading, energy saving and emission reduction, management efficiency, production cost, product quality and order delivery time are all powerful links in staying competitive.":
    "В условиях глобальной конкуренции производство сталкивается с постоянными вызовами. Модернизация, энергосбережение, эффективность управления, себестоимость, качество продукции и сроки исполнения заказов — всё это составляющие конкурентоспособности.",
  "The Sealion cloud-based extrusion monitoring system is dedicated to intelligent manufacturing, built specifically for on-line measurement, control and remote monitoring of extrusion lines. It connects the company's ERP system with the line's execution system; by collecting shop-floor data in real time and transmitting it to a cloud server or internal network server, it gives management visualisation and whole-process monitoring of production. Data from every stage is transmitted to the remote monitoring system in real time, and out-of-spec data during production is responded to and corrected immediately — shortening response time, improving product quality, reducing production cost, and lifting the enterprise's core competitiveness.":
    "Система облачного мониторинга Sealion создана для интеллектуального производства и предназначена для измерения, управления и удалённого контроля экструзионных линий. Она связывает ERP предприятия с системой исполнения на линии: цеховые данные в реальном времени передаются на облачный или внутренний сервер, благодаря чему руководство получает наглядную картину и контроль всего процесса. Данные каждого этапа поступают в систему удалённого мониторинга немедленно, а отклонения устраняются сразу — это сокращает время реакции, повышает качество, снижает себестоимость и усиливает конкурентоспособность предприятия.",
  "Equipment management: add/remove equipment, order number, spec/model, raw-material batch, production supervisor, marking content, equipment vendor":
    "Управление оборудованием: добавление и удаление единиц, номер заказа, типоразмер, партия сырья, ответственный за производство, содержание маркировки, поставщик оборудования",
  "Order management: remote task dispatch, target line, order number, spec/model, material batch, order quantity, operator, marking content":
    "Управление заказами: удалённая выдача задания, целевая линия, номер заказа, типоразмер, партия материала, объём заказа, оператор, содержание маркировки",
  "Production curve monitoring: weight-per-metre curve, extrusion-rate curve, feed-rate curve, screw-speed curve, haul-off speed curve":
    "Мониторинг производственных кривых: масса погонного метра, производительность экструзии, подача материала, частота вращения шнека, скорость тяги",
  "Production data statistics: daily / monthly / yearly totals, output quantity, total length, masterbatch consumption, running time, power consumption":
    "Статистика производства: итоги за день, месяц и год, объём выпуска, общая длина, расход суперконцентрата, время работы, энергопотребление",
  "Alarm monitoring: material-shortage alarm, abnormal screw-speed alarm, abnormal weight alarm, abnormal control-signal alarm, extruder/haul-off fault alarm":
    "Мониторинг аварий: нехватка материала, отклонение частоты вращения шнека, отклонение массы, отклонение управляющего сигнала, неисправность экструдера или тяги",
  "Finished-goods monitoring: order number, spec/model, order quantity, material number, operator, completed quantity, product ID code, OD/weight/length":
    "Контроль готовой продукции: номер заказа, типоразмер, объём заказа, номер материала, оператор, выполненное количество, идентификатор изделия, наружный диаметр, масса и длина",
  "Plastic extrusion plants running several lines or workshops, and anywhere production data has to reach ERP.":
    "Производства пластиковой экструзии с несколькими линиями или цехами, а также любые случаи, когда производственные данные должны попадать в ERP.",
  "Put every line on one screen": "Все линии на одном экране",
  "Data stranded on each machine, output reported by hand, and no way back through a problem — this is what we solve daily.":
    "Данные заперты в отдельных станках, выпуск считается вручную, разобрать причину брака невозможно — именно это мы решаем каждый день.",
 },
}

RU_DIR = "src/content/ru"
untranslated = {}


def translate(body, page_map):
    table = dict(COMMON)
    table.update(page_map)
    missing = []

    def repl(m):
        raw = m.group(1)
        key = raw.strip()
        if key in table:
            return ">" + table[key] + "<"
        if len(key) >= 12 and re.search(r"[A-Za-z]{4}", key):
            missing.append(key[:90])
        return m.group(0)

    out = re.sub(r">([^<>]{4,})<", repl, body)
    return out, missing


def run(div, slug):
    src = f"src/content/en/{div}/{slug}.html"
    dst = f"{RU_DIR}/{div}/{slug}.html"
    if not os.path.exists(dst):
        return
    raw = open(dst, encoding="utf-8").read()
    meta_s, _, body = raw.partition("\n---\n")
    body, missing = translate(body, PAGES.get(slug, {}))
    open(dst, "w", encoding="utf-8").write(meta_s + "\n---\n" + body)
    if missing:
        untranslated[f"{div}/{slug}"] = missing


for div in ("pipe", "cable"):
    for f in glob.glob(f"{RU_DIR}/{div}/*.html"):
        slug = os.path.basename(f)[:-5]
        if slug != "index":
            run(div, slug)

for k, v in untranslated.items():
    print(f"\n【{k}】仍未译 {len(v)} 段")
    for t in v[:4]:
        print("   ·", t)
print(f"\n仍有未译文本的页面：{len(untranslated)}")
