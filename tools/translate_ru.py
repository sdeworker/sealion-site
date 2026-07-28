# -*- coding: utf-8 -*-
"""
俄语正文翻译：从英文母版逐文本块替换成俄语。
未收录的文本块原样保留，并在结尾报出，便于逐轮补齐。
"""
import json, os, re, glob

# 通用短语（各页共有）
COMMON = {
 "Every product is made from different components, and masterbatch has long been mixed by hand — this can make dosing inaccurate and mixing uneven, leaving product quality unstable, and it adds labour cost and intensity. A moment's carelessness from an operator's sense of responsibility may bring the company a significant, irredeemable loss.":
   "Каждое изделие состоит из разных компонентов, а суперконцентрат долго смешивали вручную: дозирование выходит неточным, смешивание неравномерным, качество продукции нестабильным, а трудозатраты растут. Одна оплошность оператора способна обернуться значительными и невосполнимыми потерями.",
 "Every product has a different formulation, and for years masterbatch has been dosed mainly by hand — inaccurate additions and uneven mixing, which leave product quality unstable and add labour cost and needless effort.":
   "У каждого изделия своя рецептура, а суперконцентрат годами дозировали вручную: неточная добавка и неравномерное смешивание оставляют качество продукции нестабильным и добавляют трудозатрат.",
 "The SL-Ultrascan series is a dedicated product for on-line thickness measurement of small-diameter pipes and cables, applying the same ultrasonic principle to measure OD, thickness, eccentricity and ovality in real time, with data storage and report generation.":
   "Серия SL-Ultrascan предназначена для измерения толщины трубок и кабеля малого диаметра в линии: тот же ультразвуковой принцип позволяет в реальном времени определять наружный диаметр, толщину, эксцентриситет и овальность, сохранять данные и формировать отчёты.",
 "Suitable for medical catheters, wires and cables, pipes and automotive oil pipes. It measures wall thickness of 0.18–10mm across a 2–50mm diameter range. Its original auto-adjusting structure automatically adapts to different pipe sizes, and the probe centres and follows on-line, ensuring accurate, efficient and stable detection.":
   "Подходит для медицинских катетеров, проводов и кабеля, трубок и автомобильных топливных трубок. Измеряет толщину стенки 0,18–10 мм в диапазоне диаметров 2–50 мм. Оригинальная самонастраивающаяся конструкция автоматически подстраивается под типоразмер, а датчик центрируется и следует за изделием, обеспечивая точное, эффективное и стабильное измерение.",
 "Suitable for medical catheters, wires and cables, pipes and automotive oil pipes. It measures wall thickness of 0.18–10mm across a 2–50mm diameter range. Its original auto-adjusting structure automatically adapts to different bore sizes, and the probe centres and follows on-line, ensuring accurate, efficient and stable detection.":
   "Подходит для медицинских катетеров, проводов и кабеля, трубок и автомобильных топливных трубок. Измеряет толщину стенки 0,18–10 мм в диапазоне диаметров 2–50 мм. Оригинальная самонастраивающаяся конструкция автоматически подстраивается под диаметр, а датчик центрируется и следует за изделием, обеспечивая точное, эффективное и стабильное измерение.",

 "What is it": "Что это",
 "Application": "Применение",
 "Advantages": "Преимущества",
 "Parameters": "Параметры",
 "Functions": "Функции",
 "Structure": "Состав",
 "Components": "Компоненты",
 "Mixing": "Смешивание",
 "Isolation": "Разделение",
 "Automatic": "Автоматика",
 "Probes": "Датчики",
 "Software": "Программное обеспечение",
 "Live curves": "Кривые в реальном времени",
 "Why Sealion": "Почему Sealion",
 "The problem": "Задача",
 "Host output": "Производительность экструдера",
 "Masterbatch screw": "Шнек суперконцентрата",
 "OD range (mm)": "Диапазон наружного диаметра (мм)",
 "30s/cycle": "30 с/цикл",
 "DC servo motor, maintenance-free": "Серводвигатель постоянного тока, не требует обслуживания",
 "Configurations can be tailored to your line.": "Конфигурация подбирается под вашу линию.",
 "Wall thickness per probe, plus mean, maximum and minimum wall with the position of the thickest and thinnest points; mean, max and min outer and inner diameter; eccentricity and ovality shown live.":
   "Толщина стенки по каждому датчику, а также средняя, максимальная и минимальная с указанием мест наибольшей и наименьшей толщины; средний, максимальный и минимальный наружный и внутренний диаметр; эксцентриситет и овальность в реальном времени.",
 "Thickness and outer-diameter curves are plotted in real time against the recipe's upper and lower limits.":
   "Кривые толщины и наружного диаметра строятся в реальном времени относительно верхнего и нижнего пределов рецепта.",
 "A full set of measuring parameters is stored per spec and recalled on changeover; recipes can be added, edited, searched, deleted and read back.":
   "Полный набор параметров измерения сохраняется под каждый типоразмер и вызывается при переходе; рецепты можно добавлять, изменять, искать, удалять и считывать обратно.",
 "Alarm items and deviations are user-set; breaches are alarmed and logged, searchable by date range, with records kept for a year.":
   "Перечень аварий и допустимые отклонения задаёт пользователь; превышения сигнализируются и записываются, доступны по диапазону дат, записи хранятся год.",
 "Configurable logging interval, query by date range, table or curve display, Excel export and one-click export to USB.":
   "Настраиваемый интервал записи, запрос по диапазону дат, вывод таблицей или кривыми, выгрузка в Excel и на USB одним нажатием.",
 "Live data to a monitoring room over TCP/IP; the interface switches between Chinese and English.":
   "Данные в реальном времени передаются в диспетчерскую по TCP/IP; интерфейс переключается между китайским и английским.",
 "A dedicated R&amp;D company — recognised as an Innovation Little Giant, a High-Tech Enterprise and a Specialised &amp; Sophisticated (SRDI) enterprise":
   "Компания собственных разработок со статусами «Инновационный малый гигант», «Высокотехнологичное предприятие» и SRDI",
 "China's first ultrasonic online thickness system with fully owned IP and copyright":
   "Первая в Китае система ультразвукового измерения толщины в линии с полностью собственными правами",
 "A second-generation, in-house design with a 250MHz ultrasonic sampling rate — 50MHz higher than others on the market today":
   "Собственная разработка второго поколения с частотой дискретизации 250 МГц — на 50 МГц выше представленных на рынке",
 "Core parts use a US semiconductor chip and a US Olympus ultrasonic probe with a 1-inch receiving diameter":
   "В основе — американский полупроводниковый чип и ультразвуковой преобразователь Olympus с приёмным диаметром 1 дюйм",
 "APCI industrial panel PC with multiple data interfaces": "Промышленный панельный ПК APCI с несколькими интерфейсами данных",
 "Lifetime maintenance, two-year free warranty, free upgrades and free customisation — better value":
   "Пожизненное обслуживание, два года бесплатной гарантии, бесплатные обновления и доработки",
 "Remote monitoring, order placement over WiFi, optional ERP integration":
   "Удалённый мониторинг, выдача заданий по WiFi, опциональная интеграция с ERP",

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
 "masterbatch": {
  "What the masterbatch control system is": "Что представляет собой система дозирования суперконцентрата",
  "The gravimetric masterbatch control system controls the weight per metre and, at the same time, automatically controls masterbatch dosing — the two functions combined into one control system.":
    "Система одновременно удерживает массу погонного метра и автоматически управляет подачей суперконцентрата — две функции объединены в одном контуре управления.",
  "What hand-dosed masterbatch costs": "Во что обходится ручное дозирование",
  "Every product has a different formulation, and for years masterbatch has been dosed mainly by hand — inaccurate additions and uneven mixing, which leave pipe quality unstable and add labour cost and needless effort.":
    "У каждого изделия своя рецептура, а суперконцентрат годами дозировали вручную: неточная добавка и неравномерное смешивание оставляют качество трубы нестабильным и добавляют трудозатрат.",
  "And because it rests on the operator's diligence, a moment's lapse can cost the company dearly.":
    "И поскольку всё держится на внимательности оператора, одна оплошность может дорого обойтись предприятию.",
  "The masterbatch unit follows the extruder dynamically, holding the ratio at every moment":
    "Дозатор динамически следует за экструдером, удерживая соотношение в каждый момент времени",
  "Closed-loop control — intelligent and precise": "Замкнутый контур — интеллектуально и точно",
  "Continuous in-line dosing replaces slow, laborious hand-mixing": "Непрерывное дозирование в линии заменяет медленное ручное смешивание",
  "DC servo motor, maintenance-free": "Серводвигатель постоянного тока, не требует обслуживания",
  "Automatic mixing device keeps the blend even": "Автоматический смеситель поддерживает равномерность смеси",
  "Low-level hardware and software control for reliable running": "Управление на низком аппаратно-программном уровне — надёжная работа",
  "Component range": "Число компонентов",
  "Tailored to requirement": "По требованию заказчика",
  "1–3 (4+ on request)": "1–3 (более 4 — под заказ)",
  "Dosing accuracy": "Точность дозирования",
  "±1% (4‰ with masterbatch weighing)": "±1% (до 4‰ при весовом дозировании)",
  "Automatic separation technology": "Технология автоматического разделения",
  "Configurations can be tailored to your line.": "Конфигурация подбирается под вашу линию.",
  "Masterbatch screw dosing": "Шнековое дозирование суперконцентрата",
  "Extruder output": "Производительность экструдера",
  "Masterbatch screw": "Шнек суперконцентрата",
  "Controllable output": "Регулируемая производительность",
  "1 component, 1–300 Kg/hr": "1 компонент, 1–300 кг/ч",
  "2 components, 1–300 Kg/hr": "2 компонента, 1–300 кг/ч",
  "3 components, 1–300 Kg/hr": "3 компонента, 1–300 кг/ч",
  "Masterbatch gravimetric (weighing) dosing": "Весовое (гравиметрическое) дозирование суперконцентрата",
  "Plastic film, cable, pipe, compounding and chemicals — and any industry that needs several components dosed to an exact ratio.":
    "Плёнка, кабель, труба, компаундирование и химия — а также любые производства, где несколько компонентов нужно дозировать в точном соотношении.",
  "Three-layer co-extrusion line": "Линия трёхслойной соэкструзии",
  "Your browser cannot play this video.": "Ваш браузер не может воспроизвести это видео.",
 },
 "masterbatch-weighing": {
  "What the combined system is": "Что представляет собой объединённая система",
  "The gravimetric masterbatch control system controls masterbatch dosing while controlling the weight per metre, making weight control and masterbatch addition one combined system.":
    "Система управляет подачей суперконцентрата одновременно с контролем массы погонного метра, объединяя обе задачи в один контур.",
  "Every product is made from different components, and masterbatch has long been mixed by hand — this can make dosing inaccurate and mixing uneven, leading to unstable pipe quality, and it adds labour cost and intensity. A moment's carelessness from an operator's sense of responsibility may bring the company a significant, irredeemable loss.":
    "Каждое изделие состоит из разных компонентов, а суперконцентрат долго смешивали вручную: дозирование выходит неточным, смешивание неравномерным, качество трубы нестабильным, а трудозатраты растут. Одна оплошность оператора способна обернуться значительными и невосполнимыми потерями.",
  "The masterbatch machine changes dynamically with the host, strictly controlling the material ratio at every moment":
    "Дозатор динамически следует за экструдером, строго удерживая соотношение материалов в каждый момент",
  "PID closed-loop control — intelligent and highly precise": "ПИД-регулирование в замкнутом контуре — интеллектуально и высокоточно",
  "Continuous on-line mixing, reducing the time and effort of manual mixing, improving efficiency":
    "Непрерывное смешивание в линии сокращает время и трудозатраты ручного смешивания и повышает эффективность",
  "Automatic mixing device keeps the mixture even": "Автоматический смеситель поддерживает равномерность смеси",
  "Control by bottom-level software and hardware for more reliable operation": "Управление на низком аппаратно-программном уровне повышает надёжность",
  "Range of adding component (Kg/h)": "Диапазон подачи компонента (кг/ч)",
  "According to customer": "По требованию заказчика",
  "Quantity of component": "Число компонентов",
  "1–3 (customizing more than 4 for customers)": "1–3 (более 4 — под заказ)",
  "Addition accuracy": "Точность дозирования",
  "±1% (with masterbatch weighing, up to 4‰)": "±1% (при весовом дозировании — до 4‰)",
  "Technical structure": "Состав системы",
  "The system is made of the weighing mechanical section (hopper + load cell), the component-adding control system, the DSP control unit (Sealion data integration system), the extruder control system and the tractor control system, working together.":
    "Система состоит из весового механического узла (бункер и тензодатчик), контура дозирования компонентов, блока DSP (система интеграции данных Sealion), а также контуров управления экструдером и тянущим устройством, работающих совместно.",
  "Masterbatch screw control": "Шнековое управление суперконцентратом",
  "Component controlled": "Управляемые компоненты",
  "Single, 1–300 Kg/hr": "1 компонент, 1–300 кг/ч",
  "Double, 1–300 Kg/hr": "2 компонента, 1–300 кг/ч",
  "Triple, 1–300 Kg/hr": "3 компонента, 1–300 кг/ч",
  "Masterbatch gravimetric (weighing) control": "Весовое (гравиметрическое) управление суперконцентратом",
  "Plastic film, cable, pipe, plastic modification, chemicals, and any industry needing precise multi-component ratio dosing.":
    "Плёнка, кабель, труба, модификация пластмасс, химия и любые производства, где требуется точное многокомпонентное дозирование.",
 },
 "ultrasonic-small": {
  "What the small-tube gauge is": "Что представляет собой система для малых диаметров",
  "Original auto-adjusting structure fits a range of small bores": "Оригинальная самонастраивающаяся конструкция подходит для разных малых диаметров",
  "Probe self-centres and follows on-line — no manual fixture setting": "Датчик самоцентрируется и следует за изделием — без ручной настройки оснастки",
  "Real-time wall, OD, eccentricity and ovality measurement": "Измерение толщины стенки, наружного диаметра, эксцентриситета и овальности в реальном времени",
  "Data saved in real time with report generation": "Данные сохраняются в реальном времени с формированием отчётов",
  "Industrial tablet PC with built-in ultrasonic measurement software": "Промышленный планшетный ПК со встроенной программой ультразвукового измерения",
  "Clean, intuitive interface": "Чистый и понятный интерфейс",
  "Model range (small tube) SL-Ultrascan": "Модельный ряд (малый диаметр) SL-Ultrascan",
  "Pipe OD range (mm)": "Диапазон наружного диаметра (мм)",
  "Thickness (mm)": "Толщина (мм)",
  "Medical catheter, cable, small-bore tubing and automotive oil pipe — extrusion lines where the bore is narrow and wall and geometry have to be exact.":
    "Медицинские катетеры, кабель, тонкостенные трубки и автомобильные топливные трубки — линии, где диаметр мал, а требования к стенке и геометрии высоки.",
  "The same Sealion ultrasonic software as the large-pipe system, turning readings into production data you can query, export and trace.":
    "Та же программа Sealion, что и в системе для больших диаметров: показания превращаются в производственные данные, доступные для запроса, выгрузки и прослеживания.",
  "Live readings": "Показания в реальном времени",
  "Recipe management": "Управление рецептами",
  "Alarm tracking": "Отслеживание аварий",
  "Query &amp; export": "Запрос и выгрузка",
  "Remote monitoring": "Удалённый мониторинг",
  "Ten reasons to choose Sealion ultrasonic": "Десять причин выбрать ультразвук Sealion",
  "Sixteen years of independent ultrasonic R&amp;D": "Шестнадцать лет собственных разработок в области ультразвука",
  "Data can be saved and exported; product quality is traceable": "Данные сохраняются и выгружаются, качество продукции прослеживается",
  "Fully in-house, so it can be tailored to each plant": "Полностью собственная разработка, поэтому решение адаптируется под каждое производство",
  "Your browser cannot play this video.": "Ваш браузер не может воспроизвести это видео.",
 },
 "intelligent-inspection": {
  "Model &amp; parameters": "Модели и параметры",
  "Model & parameters": "Модели и параметры",
  "Pipe OD range (mm)": "Диапазон наружного диаметра (мм)",
  "Pipe length (m)": "Длина трубы (м)",
  "Automatic inspection and quality gating at the end of pipe extrusion lines.": "Автоматический контроль и отбраковка в конце линии экструзии труб.",
  "Ovality (non-roundness): two sets of lasers measure OD at several points to calculate and display non-roundness.":
    "Овальность: два лазерных комплекта измеряют наружный диаметр в нескольких точках, вычисляя и отображая некруглость.",
  "Ellipticity: pipe ovality is calculated from the measured wall thickness and displayed on the interface.":
    "Эллиптичность: овальность трубы вычисляется по измеренной толщине стенки и выводится на экран.",
  "Data display: real-time display of current production quantity, yield, NG count and OK count.":
    "Отображение данных: текущий объём выпуска, доля годного, число забракованных и годных изделий в реальном времени.",
  "Alarm function: a defective-product alarm and a quantity-reached reminder.":
    "Аварийная сигнализация: сигнал о браке и напоминание о достижении заданного количества.",
  "Data processing: abnormal data is excluded and not linked to the traceability code.":
    "Обработка данных: аномальные значения исключаются и не привязываются к коду прослеживаемости.",
  "Online inspection on site": "Контроль в линии на объекте",
  "Inspection sequence": "Последовательность контроля",
  "Your browser cannot play this video.": "Ваш браузер не может воспроизвести это видео.",
 },
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
