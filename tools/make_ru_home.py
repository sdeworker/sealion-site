# -*- coding: utf-8 -*-
"""生成俄语首页：核心区块（hero / 分岔 / 产品 / 行业 / 联系）"""
import json, re, os

PRODUCTS = [
    ("gravimetric", "Система гравиметрического контроля",
     "Устанавливается на загрузочной горловине экструдера, ПИД-регулирование в замкнутом контуре, точный контроль массы погонного метра в реальном времени, экономия 2–5% сырья."),
    ("masterbatch", "Система дозирования суперконцентрата",
     "Одновременно с контролем массы автоматически дозирует суперконцентрат: дозатор следует за экструдером, замкнутый контур, точность соотношения ±1%."),
    ("masterbatch-weighing", "Весовая версия системы дозирования",
     "Суперконцентрат дозируется по потере веса, независимое управление несколькими компонентами, рецепты сохраняются и прослеживаются."),
    ("ultrasonic-big", "Ультразвуковое измерение толщины (большой диаметр)",
     "Бесконтактное измерение движущейся трубы в ванне охлаждения: толщина стенки, диаметр, эксцентриситет и овальность в реальном времени."),
    ("ultrasonic-small", "Ультразвуковое измерение толщины (малый диаметр)",
     "Для Φ2–50 мм: толщина оболочки, наружный диаметр и эксцентриситет кабеля, медицинских трубок и тонкостенных изделий."),
    ("quality-storage", "Система входного контроля качества труб",
     "Проверка стенки, диаметра, длины и овальности каждой трубы перед складом; данные передаются в MES."),
    ("intelligent-inspection", "Система контроля труб в линии",
     "Интеллектуальный контроль качества непосредственно на производственной линии."),
    ("cloud-monitoring", "Облачный мониторинг экструзии",
     "Данные всех линий — масса, скорость, производительность, аварии — собираются в облаке и доступны удалённо."),
]

INDUSTRIES = [
    ("pe-water-pipe", "ПЭ труба водоснабжения"), ("pe-gas-pipe", "ПЭ газовая труба"),
    ("ppr-pipe", "ППР труба"), ("pvc-pipe", "ПВХ труба"),
    ("corrugated-pipe", "Гофрированная труба"), ("cable-sheathing", "Кабельная оболочка"),
    ("medical-catheter", "Медицинский катетер"), ("film", "Раздувная и плоскощелевая плёнка"),
    ("sheet-board", "Лист и плита"), ("meltblown", "Мельтблаун"),
    ("masterbatch-compounds", "Суперконцентраты и компаунды"), ("plastic-piping", "Пластиковые трубопроводы"),
]

def img_wh(rel):
    from PIL import Image
    with Image.open("public" + rel) as im:
        return im.size

CORE = {
    "gravimetric": "/assets/2026/core/core-gravimetric.webp",
    "masterbatch": "/assets/2026/core/core-masterbatch.webp",
    "masterbatch-weighing": "/assets/2026/core/core-masterbatch-weighing.webp",
    "ultrasonic-big": "/assets/2026/core/core-ultrasonic.webp",
    "ultrasonic-small": "/assets/2026/core/core-ultrasonic-2.webp",
    "quality-storage": "/assets/2026/core/core-quality-storage.webp",
    "intelligent-inspection": "/assets/2026/core/core-inspection.webp",
    "cloud-monitoring": "/assets/products2/cloud-monitoring.jpg",
}

cards = []
for i, (slug, name, desc) in enumerate(PRODUCTS, 1):
    src = CORE[slug]
    w, h = img_wh(src)
    cards.append(f'''        <article class="pcard">
          <div class="pcard-media"><img src="{src}" alt="{name}" width="{w}" height="{h}" loading="lazy"></div>
          <div class="pcard-body">
            <span class="pcard-n">{i:02d}</span>
            <h3>{name}</h3>
            <p>{desc}</p>
            <a class="arrow-link" href="/ru/pipe/{slug}.html">Подробнее &rarr;</a>
          </div>
        </article>''')

inds = "\n".join(
    f'        <a class="ind-tag" href="/ru/industries/{s}.html"><i></i>{n}</a>'
    for s, n in INDUSTRIES)

body = f'''<section class="hero">
  <div class="hero-video" aria-hidden="true">
    <video autoplay muted loop playsinline preload="auto"
           poster="/assets/2026/video/company-intro-poster.webp">
      <source src="/assets/2026/video/company-intro-bg.mp4" type="video/mp4">
    </video>
  </div>
    <div class="wrap hero-grid">
      <div class="hero-copy">
        <span class="eyebrow">Гравиметрия · Ультразвук · Облачный мониторинг</span>
        <h1>Миллиметровый контроль. Каждый метр измерен.</h1>
        <p class="lead">Sealion создаёт системы измерения и управления для линий экструзии пластмасс — от взвешивания и дозирования до измерения толщины, контроля качества и передачи данных в облако, чтобы каждый метр продукции оставался в пределах допуска.</p>
        <div class="hero-cta">
          <a class="btn btn--primary" href="/ru/pipe/">Экструзия труб</a>
          <a class="btn btn--onDark" href="/ru/cable/">Экструзия кабеля</a>
        </div>
        <button class="hero-play" type="button" data-hero-play aria-label="Смотреть фильм о компании">
          <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path d="M8 5v14l11-7z" fill="currentColor"/></svg>
          <span>Фильм о компании</span>
        </button>
      </div>
    </div>
    <div class="hero-lines" aria-hidden="true"></div>
  </section>

<section class="section divisions" id="divisions"><div class="wrap">
  <div class="sh">
    <span class="eyebrow">Начните отсюда</span>
    <h2>Ваша линия — труба или кабель?</h2>
    <p class="lead">Задача измерения различается. Трубу можно разрезать и проверить стенку — оболочку кабеля нельзя. Труба отгружается метрами, кабель барабанами. Поэтому продукция разделена по подразделениям: переходите сразу в нужное.</p>
  </div>
  <div class="div-grid">
    <a class="div-card" href="/ru/pipe/">
      <img src="/assets/2026/industry/pipe-pe-1.webp" alt="Подразделение экструзии труб" width="1600" height="900" loading="lazy">
      <div class="div-body">
        <h3>Подразделение экструзии труб</h3>
        <p>Линии ПЭ труб водоснабжения и газоснабжения, ППР, ПВХ, гофрированных труб</p>
        <span class="div-meta">8 систем · гравиметрия / суперконцентрат / ультразвук / входной контроль</span>
        <span class="arrow-link">Перейти &rarr;</span>
      </div>
    </a>
    <a class="div-card" href="/ru/cable/">
      <img src="/assets/2026/industry/cable-1.webp" alt="Подразделение экструзии кабеля" width="1600" height="900" loading="lazy">
      <div class="div-body">
        <h3>Подразделение экструзии кабеля</h3>
        <p>Линии кабельной оболочки, изоляции, медицинских катетеров</p>
        <span class="div-meta">5 систем · гравиметрия / суперконцентрат / малые диаметры / облако</span>
        <span class="arrow-link">Перейти &rarr;</span>
      </div>
    </a>
  </div>
</div></section>

<section class="section products" id="products"><div class="wrap">
  <div class="sh">
    <span class="eyebrow">Продукция</span>
    <h2>Системы измерения и управления для линий экструзии</h2>
    <p class="lead">От взвешивания сырья до входного контроля на складе, от отдельной линии до облака — восемь систем, охватывающих весь процесс экструзии пластмасс.</p>
  </div>
  <div class="pcard-grid">
{chr(10).join(cards)}
  </div>
</div></section>

<section class="section apply" id="apply"><div class="wrap">
  <div class="sh">
    <span class="eyebrow">Отрасли применения</span>
    <h2>Создано для вашего процесса экструзии</h2>
  </div>
  <div class="ind-tags">
{inds}
  </div>
</div></section>

<section class="section contact" id="contact"><div class="wrap narrow">
  <div class="sh">
    <span class="eyebrow">Контакты</span>
    <h2>Поговорите с инженером</h2>
    <p class="lead">Диапазон диаметров, материал, производительность и марки установленного оборудования — с этими данными мы ответим по существу, а не общими словами.</p>
  </div>
  <p class="lead">
    Горячая линия: <a href="tel:4008404080">4008-4040-80</a><br>
    Телефон: <a href="tel:+862022109833">+86-20-22109833</a><br>
    Адрес: Гуанчжоу, р-н Хуанпу, ул. Ляньпу 8, Digital Valley, корп. U4, 9 этаж
  </p>
</div></section>
'''

meta = {
    "title": "Sealion Tech — измерение и управление для экструзии пластмасс",
    "description": "Sealion Tech (Гуанчжоу): системы гравиметрического контроля, дозирования суперконцентрата, ультразвукового измерения толщины и контроля качества для линий экструзии труб и кабеля.",
    "css": ["product"],
    "js": ["hero-video"],
    "type": "home",
}
os.makedirs("src/content/ru", exist_ok=True)
open("src/content/ru/index.html", "w", encoding="utf-8").write(
    json.dumps(meta, ensure_ascii=False, indent=1) + "\n---\n" + body)
print("俄语首页已生成:", len(body) / 1024, "KB")
