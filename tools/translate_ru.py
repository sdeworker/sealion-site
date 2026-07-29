# -*- coding: utf-8 -*-
"""
俄语正文翻译：从英文母版逐文本块替换成俄语。
未收录的文本块原样保留，并在结尾报出，便于逐轮补齐。
"""
import json, os, re, glob

# 通用短语（各页共有）
COMMON = {
 'Thickness measurement: upper/lower wall-thickness limits and real-time wall thickness are set; a patented structure lasers the pipe from inside and out while a servo motor rotates one full turn, computing accurate thickness in every direction and marking the max/min positions. The detection point sits 30–50mm from the pipe end to avoid the flared cut edge, and the laser avoids direct reflection off the pipe surface.':
   'Измерение толщины: задаются верхний и нижний пределы и текущее значение толщины стенки; запатентованный узел просвечивает трубу лазером изнутри и снаружи, а серводвигатель делает полный оборот, вычисляя точную толщину по всем направлениям и отмечая места наибольшего и наименьшего значения. Точка измерения находится в 30–50 мм от торца, вне зоны развальцованной кромки реза, а лазер не отражается напрямую от поверхности трубы.',
 "Thickness measurement: upper/lower wall-thickness limits and real-time wall thickness are set; a patented structure lasers the pipe from inside and out while a servo motor rotates one full turn, computing accurate thickness in every direction and marking the max/min positions. The detection point sits 30–50mm from the pipe end to avoid the flared cut edge, and the laser avoids direct reflection off the pipe surface so colour doesn't affect the reading.":
   'Измерение толщины: задаются верхний и нижний пределы и текущее значение толщины стенки; запатентованный узел просвечивает трубу лазером изнутри и снаружи, а серводвигатель делает полный оборот, вычисляя точную толщину по всем направлениям и отмечая места наибольшего и наименьшего значения. Точка измерения находится в 30–50 мм от торца, вне зоны развальцованной кромки реза, а лазер не отражается напрямую от поверхности трубы, поэтому цвет не влияет на результат.',

 'When the system alarms, a code appears on screen. The table below gives what each code means and the checks line staff can make':
   'При срабатывании система выводит код на экран. В таблице ниже указано значение каждого кода и проверки, которые персонал линии может выполнить',
 'without opening the cabinet and without working on live equipment':
   'без вскрытия шкафа и без работ под напряжением',
 '. If the alarm persists after those checks, contact Sealion service — anything involving measurement inside the cabinet, wiring changes or part replacement is for our engineers.':
   '. Если после этих проверок сигнал не исчез, обратитесь в сервис Sealion: всё, что связано с измерениями внутри шкафа, изменением проводки или заменой узлов, выполняют наши инженеры.',
 'Power the display off and on a few times to see if it recovers; check that the display-to-controller communication cable is firmly seated and undamaged.':
   'Выключите и включите дисплей несколько раз и посмотрите, восстановится ли связь; проверьте, надёжно ли посажен кабель связи между дисплеем и контроллером и не повреждён ли он.',
 'Is the silo empty? Is the drop path blocked or bridging? Is air pressure 0.3–0.4MPa? Does the shut-off mechanism move freely, and is anything propping up the cylinder base?':
   'Пуст ли силос? Не забит ли тракт подачи, нет ли зависания материала? Давление воздуха 0,3–0,4 МПа? Свободно ли ходит отсечной механизм и не подпирает ли что-либо основание цилиндра?',
 'Is the hopper filling and discharging normally? Any disturbance near the weighing point (hopper vibration, blockage, excessive throat temperature)? Watch the silo — is the screw taking material unevenly?':
   'Нормально ли наполняется и опорожняется бункер? Нет ли помех рядом с точкой взвешивания (вибрация бункера, забивание, повышенная температура горловины)? Посмотрите на силос — равномерно ли шнек забирает материал?',
 'Is the encoder connector fully seated and the cable undamaged? Is the encoder mounted square and centred? Is the coupling tight? Is the supply healthy?':
   'Надёжно ли посажен разъём энкодера и не повреждён ли кабель? Установлен ли энкодер соосно и по центру? Затянута ли муфта? В порядке ли питание?',
 'The extruder is drawing overload current. Reduce screw speed first, then find the cause — commonly the screw is starved or the melt is too cold.':
   'Экструдер потребляет ток перегрузки. Сначала снизьте обороты шнека, затем найдите причину — обычно это нехватка материала на шнеке или слишком холодный расплав.',
 'Is the cable between the two modules fully seated and undamaged? Any strong source of electrical interference nearby?':
   'Надёжно ли посажен кабель между двумя модулями и не повреждён ли он? Нет ли рядом сильного источника электрических помех?',
 'Check the extruder control cable is firmly seated and undamaged. If it still alarms, an engineer needs to measure on site.':
   'Проверьте, надёжно ли посажен кабель управления экструдером и не повреждён ли он. Если сигнал сохраняется, нужны измерения инженера на месте.',
 'Look at the haul-off and output curves: if the haul-off curve is abnormal see code 03; if the output curve is abnormal see code 02.':
   'Посмотрите кривые тяги и производительности: при отклонении кривой тяги см. код 03, при отклонении кривой производительности — код 02.',
 'Has the extruder breaker tripped? Is the extruder start signal on?':
   'Не сработал ли автомат экструдера? Подан ли сигнал пуска экструдера?',
 'Has the haul-off breaker tripped? Is the haul-off start signal on?':
   'Не сработал ли автомат тяги? Подан ли сигнал пуска тяги?',
 "The haul-off is near the inverter's 50Hz ceiling. Reduce haul-off speed and establish why such a high speed was needed.":
   'Тяга приблизилась к пределу 50 Гц частотного преобразователя. Снизьте скорость тяги и выясните, почему потребовалась такая высокая скорость.',
 'Review the haul-off and output curves and work through the checks for codes 02 and 03.':
   'Просмотрите кривые тяги и производительности и выполните проверки по кодам 02 и 03.',
 'Extruder or haul-off control signal exceeds the read signal by 30%':
   'Управляющий сигнал экструдера или тяги превышает считанный сигнал на 30%',
 'Raised when overshoot occurs in steady state. Check the curves to see whether the extrusion or the haul-off end is causing it.':
   'Появляется при перерегулировании в установившемся режиме. По кривым определите, вызвано ли это стороной экструзии или стороной тяги.',
 'Is the extruder speed curve smooth? If it is, the speed pick-up is the likely cause — check the proximity switch and sensing collar for movement and correct gap. If it is not smooth, check whether output fluctuation is driving the speed.':
   'Гладкая ли кривая оборотов экструдера? Если гладкая, вероятная причина — съём скорости: проверьте индуктивный датчик и чувствительное кольцо на смещение и правильный зазор. Если кривая неровная, проверьте, не вызвано ли изменение оборотов колебаниями производительности.',
 'Is the encoder wheel turning with the pipe, and is the encoder shaft rotating? Is the encoder cable fully seated? If there is still no reading, an engineer must assess the encoder or module.':
   'Вращается ли колесо энкодера вместе с трубой и вращается ли вал энкодера? Надёжно ли посажен кабель энкодера? Если показаний по-прежнему нет, состояние энкодера или модуля должен оценить инженер.',
 'Usually caused by a large change in material density, so a full hopper still falls short of the threshold; output is then neither calculated nor controlled. The hopper thresholds need adjusting — contact service.':
   'Обычно вызвано значительным изменением плотности материала: полный бункер всё равно не достигает порога, и тогда производительность не рассчитывается и не регулируется. Требуется скорректировать пороги бункера — обратитесь в сервис.',
 'Confirm valve auto mode is on; confirm air supply is normal (0.3–0.4MPa); watch whether the shut-off device moves freely or is sticking. If it is still wrong, contact service.':
   'Убедитесь, что включён автоматический режим клапана; проверьте, нормальна ли подача воздуха (0,3–0,4 МПа); посмотрите, свободно ли ходит отсечное устройство или подклинивает. Если неисправность сохраняется, обратитесь в сервис.',
 'Sealion provides lifetime maintenance and a two-year free warranty. Please do not attempt diagnosis that involves live measurement inside the cabinet, wiring changes, or replacing modules and parts — leave those to a Sealion engineer.':
   'Sealion предоставляет пожизненное обслуживание и два года бесплатной гарантии. Пожалуйста, не выполняйте самостоятельно диагностику, связанную с измерениями под напряжением внутри шкафа, изменением проводки или заменой модулей и узлов — это работа инженера Sealion.',

 'It corrects uneven wall — or uneven insulation and sheath on cable — caused by changes in material density or blend ratio.':
   'Устраняет неравномерность стенки — а на кабеле неравномерность изоляции и оболочки — вызванную изменением плотности сырья или соотношения компонентов.',
 'Output accumulates by year, month and day and is presented graphically for management.':
   'Выпуск накапливается по годам, месяцам и дням и представляется руководству в графическом виде.',
 'Production quality is watched around the clock, with alarms for starved feed, weight fluctuation, and extruder or haul-off faults.':
   'Качество производства контролируется круглосуточно, с сигнализацией о нехватке материала, колебаниях массы и неисправностях экструдера или тяги.',
 "The system is not only a controller — it is also the line's production ledger.":
   'Система — не только регулятор, но и производственный журнал линии.',
 'Set the length per piece or coil and anything within ±1 m of target counts as good. Set 21 m, for instance, and a measured 20–22 m passes. The running length resets automatically at each cut; a good piece increments the count, an out-of-tolerance one does not.':
   'Задайте длину изделия или бухты, и всё, что отклоняется не более чем на ±1 м, считается годным. Например, при задании 21 м годным признаётся результат 20–22 м. Накопленная длина автоматически обнуляется при каждом резе; годное изделие увеличивает счётчик, вышедшее из допуска — нет.',
 'The output page records total output, good output, scrap output, piece count and produced length, so pass rate no longer has to be worked out by hand.':
   'Страница выпуска фиксирует общий выпуск, годную и бракованную продукцию, число изделий и произведённую длину, поэтому долю годного больше не нужно считать вручную.',
 'Enter the wound length per coil and the number of coils and the system works out how much material to draw; enter the material weight already drawn and it tells you how many coils it will make.':
   'Введите длину намотки на бухту и число бухт — система рассчитает требуемую массу материала; введите уже полученную массу — она подскажет, сколько бухт из неё выйдет.',
 'Output can be metered per shift, with separate shift and grand-total resets, alongside twelve months of accumulated data and the records of the last 100 pieces.':
   'Выпуск учитывается по сменам, с раздельным обнулением сменного и общего счётчиков, а также хранятся данные за двенадцать месяцев и записи по последним 100 изделиям.',
 'Current output, output since start-up, weight per metre, running time, output from the current batch of material and the running total are shown together.':
   'Текущая производительность, выпуск с момента пуска, масса погонного метра, время работы, выпуск из текущей партии сырья и общий итог выводятся вместе.',
 'Operator actions, commissioning steps, production records and alarm records are all retained for later review and shift handover.':
   'Действия оператора, шаги пусконаладки, производственные записи и журнал аварий сохраняются для последующего разбора и передачи смены.',
 'An alarm is more than a notification. With alarms enabled the system acts, rather than letting a faulty line keep making scrap.':
   'Авария — это не просто уведомление. При включённой сигнализации система действует, а не позволяет неисправной линии продолжать выпускать брак.',
 'If the extruder or haul-off faults during production, the system ramps both down together and stops them, instead of running on in a broken state.':
   'При неисправности экструдера или тяги в ходе производства система синхронно снижает обороты обоих узлов до полной остановки, вместо того чтобы продолжать работу в аварийном состоянии.',
 "If gravimetric control itself becomes unstable, the control signal switches back to the machine's own control line — protection that does not cost you production.":
   'Если само гравиметрическое регулирование становится неустойчивым, управляющий сигнал возвращается на штатную линию управления станка — защита, не оплачиваемая остановкой производства.',
 "Cause, the operator actions at the time, the code's meaning and its remedy, plus the history log, all on one screen; re-enable alarms once the issue has been checked and cleared.":
   'Причина, действия оператора в тот момент, значение кода и способ устранения, а также журнал истории — всё на одном экране; после проверки и устранения сигнализацию включают снова.',
 'Weight per metre, output, haul-off speed, extruder and haul-off voltage readings, extruder and haul-off outputs, screw speed, screw feed rate and hopper weight — switchable at a touch.':
   'Масса погонного метра, производительность, скорость тяги, показания напряжения экструдера и тяги, их выходные сигналы, обороты шнека, подача шнека и масса в бункере — переключаются одним касанием.',
 'The speed and voltage curves reveal how hard the system is correcting, and whether overshoot or clamping is occurring during control.':
   'Кривые скорости и напряжения показывают, насколько сильно система корректирует процесс и возникает ли при этом перерегулирование или ограничение.',
 'Hopper value and screw feed-rate curves sit together, making uneven intake obvious — often the true source of weight fluctuation.':
   'Кривые массы в бункере и подачи шнека выводятся рядом, поэтому неравномерный забор материала виден сразу — а это часто и есть истинная причина колебаний массы.',
 'The interface switches between Chinese and English, with a Russian version also available for the pipe edition — useful for export lines and expatriate teams.':
   'Интерфейс переключается между китайским и английским, а для трубного исполнения доступна и русская версия — это удобно для экспортных линий и иностранных специалистов.',
 ', sending production data straight through for remote viewing and central management.':
   ', передавая производственные данные напрямую для удалённого просмотра и централизованного управления.',
 ', a colour ratio can be set against current output — at 300 kg/h and 1%, masterbatch output is 3 kg/h.':
   ', соотношение цвета задаётся относительно текущей производительности: при 300 кг/ч и 1% подача суперконцентрата составит 3 кг/ч.',
 'The main screen also shows the mean wall thickness derived from weight per metre, as a quick on-line reference.':
   'На главном экране также выводится средняя толщина стенки, полученная из массы погонного метра, — как быстрый ориентир прямо на линии.',
 'The cable edition derives mean cable circumference, outer diameter and sheath thickness from the measured data, for reference on the floor.':
   'Кабельное исполнение вычисляет по измеренным данным среднюю длину окружности кабеля, наружный диаметр и толщину оболочки — для справки в цехе.',
 "Start on the machine's own control, with the extruder driving its own drives, or start under gravimetric control, where the system regulates extruder and haul-off automatically — speeds can also be typed in directly or ramped up and down in step.":
   'Пуск возможен на штатном управлении станка, когда экструдер управляет своими приводами, либо под гравиметрическим контролем, когда система сама регулирует экструдер и тягу; скорости также можно ввести напрямую или изменять синхронно.',
 'The system typically saves 2%–5% of raw material, sometimes more. The figures below assume 2.5% savings at a material price of RMB 9.00/kg.':
   'Система обычно экономит 2–5% сырья, иногда больше. Приведённые ниже расчёты исходят из экономии 2,5% при цене материала 9,00 юаней за кг.',
 'Source: ROI examples in the Sealion cable-gravimetric brochure. Actual savings vary with output, hours, price and saving rate.':
   'Источник: примеры расчёта окупаемости из буклета Sealion по кабельной гравиметрии. Фактическая экономия зависит от производительности, режима работы, цены и доли экономии.',

 'The display mounts on the side of, or above, the extruder control cabinet; the air filter-regulator on the main box takes an external air line set to 0.3–0.4MPa.':
   'Дисплей крепится сбоку или над шкафом управления экструдера; фильтр-регулятор на главном шкафу подключается к внешней линии воздуха с давлением 0,3–0,4 МПа.',
 'Keep the inside of the control box dry and remove dust from the modules periodically.':
   'Внутри шкафа управления должно быть сухо, а модули следует периодически очищать от пыли.',
 "The system installs on top of the extruder's feed port, without altering the existing line layout.":
   'Система устанавливается над загрузочной горловиной экструдера и не требует изменения существующей компоновки линии.',
 'Top: before installation\u3000Bottom: after installing the Sealion gravimetric control system':
   'Сверху — до монтажа; снизу — после установки системы гравиметрического контроля Sealion',
 "On today's popular PE/PPR/PERT high-speed production lines, linear speed reaches 20 m/min. Adjusting that speed makes the tube too thick or too thin — sometimes the pipe breaks outright.":
   'На распространённых сегодня скоростных линиях ПЭ/ППР/PERT линейная скорость достигает 20 м/мин. Изменение этой скорости делает трубу слишком толстой или слишком тонкой, а иногда приводит к обрыву.',
 "The double-output gravimetric control system controls both extrusions from the line's twin haul-off speeds and the host output. It works the same way: automatically regulating screw speed, twin haul-off speed and feed rate in real time to match the weight accuracy we set, so the pipe's weight-per-metre stays constant.":
   'Система с двойным выходом управляет обоими потоками экструзии по скоростям двух тянущих устройств и производительности экструдера. Принцип тот же: частота вращения шнека, скорости обеих тяг и подача регулируются в реальном времени под заданную точность массы, поэтому масса погонного метра остаётся постоянной.',
 'One system, four ways to hand over control — chosen to suit the line and the process goal. Whichever end the system takes over, the other stays available for the operator to trim by hand, which is what matters most on the floor.':
   'Одна система, четыре способа передачи управления — выбираются под линию и задачу процесса. Каким бы концом ни управляла система, второй остаётся доступен оператору для ручной подстройки, а это в цехе важнее всего.',
 'The system takes over screw speed; haul-off speed stays adjustable. To trim the extruder up or down, adjust the haul-off.':
   'Система берёт на себя частоту вращения шнека; скорость тяги остаётся регулируемой. Чтобы подстроить экструдер, изменяют скорость тяги.',
 'The system takes over haul-off speed; screw speed stays adjustable. To trim the haul-off, adjust the extruder.':
   'Система берёт на себя скорость тяги; частота вращения шнека остаётся регулируемой. Чтобы подстроить тягу, изменяют режим экструдера.',
 'The system takes over screw speed; change the output figure and the line speeds up or slows down accordingly.':
   'Система берёт на себя частоту вращения шнека; при изменении заданной производительности линия ускоряется или замедляется соответственно.',
 'Both extruder and haul-off are under system control; changing the output value lets the system accelerate or decelerate on its own.':
   'И экструдер, и тяга находятся под управлением системы; при изменении заданной производительности система сама ускоряется или замедляется.',
 'Under wall-thickness control, if the pipe comes out thin or thick, change the target in the gravimetric or spec setting — no need to touch the extruder. The system raises or lowers the screw or haul-off itself.':
   'В режиме управления толщиной стенки при отклонении толщины достаточно изменить задание в настройках массы или типоразмера — трогать экструдер не нужно. Система сама повысит или понизит обороты шнека либо скорость тяги.',
 'Enter outer diameter, wall thickness and material density and the system derives the weight per metre; set OD, density and weight per metre instead and it derives the wall thickness.':
   'Введите наружный диаметр, толщину стенки и плотность материала — система вычислит массу погонного метра; задайте вместо этого диаметр, плотность и массу погонного метра — она вычислит толщину стенки.',
 'The line can be started four ways, whichever suits the crew: by frequency (Hz), by screw speed, by haul-off speed, or by output. Starting on frequency is usually the clearest right after installation.':
   'Линию можно запускать четырьмя способами — по частоте (Гц), по оборотам шнека, по скорости тяги или по производительности. Сразу после монтажа обычно понятнее всего пуск по частоте.',
 'Once the line is stable, save the current spec as a recipe. Next time you run it, recall the recipe and extruder and haul-off ramp back to the saved speeds within 30 seconds — reaching steady state fast and cutting start-up scrap.':
   'Когда линия вышла на режим, сохраните текущий типоразмер как рецепт. В следующий раз вызов рецепта возвращает экструдер и тягу к сохранённым скоростям за 30 секунд: режим достигается быстро, пусковой брак сокращается.',
 'Four further slots store the screw and haul-off speeds used when splicing, so a changeover is one recall instead of a fresh trial by feel.':
   'Ещё четыре ячейки хранят обороты шнека и скорость тяги для стыковки, поэтому переход выполняется одним вызовом, а не подбором на ощупь.',
 'For pipes that need one thickened end, such as socket ends, set the thickened wall and thickened length and the system switches between thick and thin sections in step with cut length.':
   'Для изделий с утолщённым концом, например раструбом, задаются толщина и длина утолщения, и система переключается между толстым и тонким участком синхронно с длиной реза.',
 'It removes the problem of not being able to correct during start-up and production, so lines come up faster with less waste.':
   'Снимается проблема невозможности скорректировать процесс при пуске и в ходе производства: линия выходит на режим быстрее и с меньшими потерями.',
 'Orders can be created and stored with spec, material and the person responsible, and combined with intelligent ratio setting for a fast, traceable start.':
   'Заказы можно создавать и хранить с указанием типоразмера, материала и ответственного, а вместе с интеллектуальной настройкой соотношения это даёт быстрый и прослеживаемый пуск.',
 'It removes the raw-material waste caused by weight deviation during production, saving 2%–5% of material.':
   'Устраняется перерасход сырья из-за отклонения массы в ходе производства — экономия 2–5% материала.',

 "Meter weight is the weight of one metre of product. It can be calculated from the product's dimensions and the density of the material, and holding it constant during production largely determines how good the product is.":
   'Масса погонного метра — это масса одного метра изделия. Её можно рассчитать по размерам изделия и плотности материала, и от того, насколько стабильно она удерживается в ходе производства, во многом зависит качество продукции.',
 "The Sealion gravimetric control system is installed at the top of the extruder's feed port. Using PID (proportional-integral-derivative) closed-loop control, it automatically and strictly controls the weight per metre, continuously regulating screw speed, haul-off speed and feed rate at any moment of the run.":
   'Система гравиметрического контроля Sealion устанавливается над загрузочной горловиной экструдера. С помощью ПИД-регулирования в замкнутом контуре она автоматически и строго удерживает массу погонного метра, непрерывно управляя частотой вращения шнека, скоростью тяги и подачей материала в любой момент работы.',
 'Weight per metre is unknown; a long length must run out before thickness can be judged, and repeated adjustments waste material, time and labour.':
   'Масса погонного метра неизвестна: чтобы оценить толщину, нужно выпустить значительную длину, а многократные подстройки тратят материал, время и труд.',
 'Weight-per-metre data appears on screen from the first moment, shortening start-up; haul-off and extrusion speed can be trimmed live, saving material and time.':
   'Масса погонного метра выводится на экран с первой секунды, сокращая выход на режим; скорость тяги и экструзии подстраивается на ходу, экономя материал и время.',
 "Depends on the operator's experience; the process can't be monitored and deviation is unpredictable.":
   'Всё зависит от опыта оператора: процесс не контролируется, отклонение непредсказуемо.',
 'Extruder and haul-off are driven automatically from the weight recipe, removing human error; weight is monitored throughout and any deviation raises an alarm.':
   'Экструдер и тяга управляются автоматически по рецепту массы, что исключает человеческую ошибку; масса контролируется постоянно, при отклонении подаётся сигнал.',
 "Every supplier's resin behaves differently; the weight shift is unknown and scrap is unavoidable.":
   'Сырьё каждого поставщика ведёт себя по-своему: сдвиг массы неизвестен, брака не избежать.',
 'However the raw material changes, the system detects and corrects it automatically.':
   'Как бы ни менялось сырьё, система обнаруживает это и корректирует автоматически.',
 'The whole run is recorded and stored, and can be traced afterwards.':
   'Весь ход производства записывается и сохраняется, его можно проследить впоследствии.',
 "These 20 readings come from Sealion's own product manual — not a simulation, but weight-per-metre logged on one line, before and after.":
   'Эти 20 измерений взяты из собственного руководства Sealion: это не моделирование, а записи массы погонного метра на одной линии до и после.',
 'Source: Sealion Technology Product Manual, Gravimetric Control System — Main function. Spread and standard deviation are computed directly from these readings.':
   'Источник: руководство Sealion Technology, раздел «Система гравиметрического контроля — основные функции». Размах и среднеквадратичное отклонение рассчитаны непосредственно по этим данным.',
 'The system carries an intelligent weighing device: the hopper valve opens and closes in a continuous cycle so that every batch falls freely under identical pressure. Each opening and closing is governed by the microcomputer in this sequence:':
   'В системе применён интеллектуальный весовой узел: клапан бункера открывается и закрывается в непрерывном цикле, поэтому каждая порция падает свободно при одинаковом давлении. Каждое открытие и закрытие управляется микроконтроллером по следующей последовательности:',
 'Shortens start-up and removes the blind spot where nothing can be adjusted in time':
   'Сокращает выход на режим и устраняет период, когда ничего нельзя вовремя подстроить',
 'Stops weight deviation wasting resin — saves 2%–5% of raw material':
   'Прекращает перерасход сырья из-за отклонения массы — экономия 2–5%',
 'Handles pipe breaks and re-joins by controlling weight and output':
   'Отрабатывает обрыв и повторный запуск за счёт управления массой и производительностью',
 'Absorbs changes in resin density and ratio that make walls uneven':
   'Компенсирует изменения плотности и соотношения сырья, из-за которых стенка становится неравномерной',
 'Single-weight dual-output control for high-speed PE/PPR/PERT lines with synchronised twin haul-off':
   'Управление с одним весовым узлом и двойным выходом для скоростных линий ПЭ/ППР/PERT с синхронной двойной тягой',
 'Load cell, pneumatic cylinder, hopper, hopper retaining ring, hopper hooks, acrylic sleeve, aluminium feed-throat flange, silicone feed-throat flange, shut-off valve, extruder feed-throat mounting seat, main control box, air filter-regulator and alarm beacon.':
   'Тензодатчик, пневмоцилиндр, бункер, прижимное кольцо бункера, крюки бункера, акриловая обечайка, алюминиевый фланец загрузочной горловины, силиконовый фланец горловины, отсечной клапан, посадочное основание горловины экструдера, главный шкаф управления, фильтр-регулятор воздуха и сигнальный маячок.',
 'The base and transition plate fit at the extruder feed throat, the shut-off valve seats into the base channel, and the weighing unit bolts onto the base; hopper, hooks, acrylic sleeve and cover then assemble in order.':
   'Основание и переходная плита устанавливаются на загрузочной горловине экструдера, отсечной клапан входит в паз основания, весовой узел крепится к основанию болтами; затем по порядку собираются бункер, крюки, акриловая обечайка и крышка.',
 'A wire-reinforced hose is clamped to the silo outlet at one end and sits in the aluminium flange feed-throat channel at the other.':
   'Армированный шланг одним концом крепится хомутом к выходу силоса, другим — входит в паз алюминиевого фланца горловины.',
 'The proximity-switch bracket is fixed beside the extruder screw with the sensing collar on the screw itself; the switch aligns to the sensing point with a clearance gap preserved.':
   'Кронштейн индуктивного датчика закрепляется рядом со шнеком экструдера, а чувствительное кольцо — на самом шнеке; датчик выставляется на точку срабатывания с сохранением зазора.',
 'The encoder mounts either way: on an encoder arm riding the pipe above the water tank, or directly on the haul-off bearing.':
   'Энкодер монтируется двумя способами: на кодирующем рычаге, опирающемся на трубу над ванной, либо непосредственно на подшипник тянущего устройства.',

 'What the gravimetric control system is':
   'Что представляет собой система гравиметрического контроля',
 'Why a conventional line needs it':
   'Зачем это обычной линии',
 'Without a control system':
   'Без системы управления',
 'With Sealion gravimetric control':
   'С гравиметрическим контролем Sealion',
 'Material change':
   'Смена материала',
 'Traceability':
   'Прослеживаемость',
 'Once in the warehouse, nothing can be traced.':
   'После склада проследить уже ничего нельзя.',
 'Measured':
   'Измерено',
 'The same line, recorded before and after control':
   'Одна и та же линия: записи до и после внедрения контроля',
 'Weight/metre':
   'Масса на метр',
 'Without control':
   'Без контроля',
 'With gravimetric control':
   'С гравиметрическим контролем',
 'Weight range, uncontrolled':
   'Разброс массы без контроля',
 'Weight range, controlled':
   'Разброс массы с контролем',
 'Spread narrowed':
   'Разброс сужен',
 'Std. deviation (about 1/7 the swing)':
   'Среднеквадратичное отклонение (около 1/7 размаха)',
 'Show the raw data (20 readings from the manual)':
   'Показать исходные данные (20 измерений из руководства)',
 'Without control system':
   'Без системы управления',
 'Workflow':
   'Рабочий цикл',
 'How the system works':
   'Как работает система',
 'The valve closes once material reaches 80% of the hopper.':
   'Клапан закрывается, когда бункер заполнен на 80%.',
 'Material falls freely, feeding the main screw.':
   'Материал свободно опускается, питая основной шнек.',
 'At 20% the valve opens, refills, and the next cycle begins.':
   'На отметке 20% клапан открывается, бункер пополняется и начинается следующий цикл.',
 'Steadies the process and holds product quality':
   'Стабилизирует процесс и удерживает качество продукции',
 'Prevents scrap pipe caused by a blocked screen pack':
   'Предотвращает брак из-за забитого фильтрующего пакета',
 'Records and stores production data for full traceability':
   'Записывает и хранит производственные данные для полной прослеживаемости',
 'Technical structure':
   'Состав системы',
 'Technical structure of the gravimetric control system':
   'Состав системы гравиметрического контроля',
 'Display control unit':
   'Блок индикации и управления',
 'Hopper weight &amp; sensor unit':
   'Весовой бункер с тензодатчиком',
 'Meter weight data acquisition unit':
   'Блок сбора данных массы погонного метра',
 'Extruder rotating speed acquisition unit':
   'Блок сбора частоты вращения экструдера',
 'Tractor speed acquisition unit':
   'Блок сбора скорости тянущего устройства',
 'Mechanical parts':
   'Механические узлы',
 'Where it mounts':
   'Место установки',
 'Feed connection':
   'Подключение подачи материала',
 'Screw speed pick-up':
   'Съём частоты вращения шнека',
 'Line speed pick-up':
   'Съём скорости линии',
 'Display &amp; air supply':
   'Индикация и подача воздуха',
 'Routine care':
   'Текущее обслуживание',
 'Installation':
   'Монтаж',
 'Double output':
   'Двойной выход',
 'Double-output gravimetric control system':
   'Система гравиметрического контроля с двойным выходом',
 'Power supply':
   'Электропитание',
 'Operating temp.':
   'Рабочая температура',
 'Max. humidity':
   'Макс. влажность',
 '90%R.H, non-condensing':
   '90% отн. вл., без конденсата',
 'Power consumption':
   'Потребляемая мощность',
 'Load cell range':
   'Диапазон тензодатчика',
 'Input sensitivity':
   'Чувствительность входа',
 'Input range':
   'Диапазон входного сигнала',
 'A/D resolution':
   'Разрешение АЦП',
 'D/A resolution':
   'Разрешение ЦАП',
 'Conversion':
   'Преобразование',
 'A/D speed':
   'Быстродействие АЦП',
 'Non-linearity':
   'Нелинейность',
 'Gain drift':
   'Дрейф коэффициента усиления',
 'Max. display accuracy':
   'Макс. точность индикации',
 'Control mode':
   'Режим управления',
 'Extruder or haul-off':
   'Экструдер или тянущее устройство',
 'Control accuracy':
   'Точность управления',
 'Hopper volume':
   'Объём бункера',
 'Total weight':
   'Общая масса',
 'Single-extruder gravimetric control':
   'Гравиметрический контроль одного экструдера',
 'Twin-extruder co-extrusion gravimetric control':
   'Гравиметрический контроль двухслойной соэкструзии',
 'Triple-extruder co-extrusion gravimetric control':
   'Гравиметрический контроль трёхслойной соэкструзии',
 'Control modes':
   'Режимы управления',
 'Four control modes':
   'Четыре режима управления',
 'Extruder wall-thickness control':
   'Управление толщиной стенки по экструдеру',
 'Haul-off wall-thickness control':
   'Управление толщиной стенки по тяге',
 'Output control':
   'Управление производительностью',
 'Dual control':
   'Двойное управление',
 'Calculation':
   'Расчёт',
 'Weight-per-metre calculation &amp; four ways to start':
   'Расчёт массы погонного метра и четыре способа пуска',
 'weight/m = (OD − wall) × wall × 3.14 × density ÷ 1000':
   'масса/м = (наружный Ø − стенка) × стенка × 3,14 × плотность ÷ 1000',
 'Recipes, changeover and thickening':
   'Рецепты, переход и утолщение',
 'Production recipes':
   'Производственные рецепты',
 'Changeover recipes':
   'Рецепты перехода',
 'Thickening':
   'Утолщение',
 'No more starting by trial':
   'Больше не нужно подбирать пуск наугад',
 'Order-based production':
   'Производство по заказам',
 'Closed-loop control in one step':
   'Замкнутый контур за один шаг',
 'Closed-loop, self-adjusting control reaching':
   'Замкнутое самонастраивающееся регулирование обеспечивает',
 '0.3% control accuracy under standard conditions':
   'точность контроля 0,3% в стандартных условиях',
 'Material saved, in cash terms':
   'Экономия сырья в деньгах',
 'Absorbs density and ratio drift':
   'Компенсирует уход плотности и соотношения',
 'Output reporting':
   'Отчётность по выпуску',
 '24-hour quality monitoring':
   'Круглосуточный контроль качества',
 'Statistics':
   'Статистика',
 'Length &amp; pass/fail judgement':
   'Длина и оценка годности',
 'Good and scrap counted separately':
   'Годное и брак учитываются раздельно',
 'Material planning by coil':
   'Расчёт материала по бухтам',
 'Shift and long-period statistics':
   'Статистика по сменам и длительным периодам',
 'One accumulation screen':
   'Единый экран накопленных данных',
 'A full audit trail':
   'Полный журнал действий',
 'Protection':
   'Защита',
 'Coordinated slowdown and stop':
   'Согласованное снижение скорости и остановка',
 'Automatic hand-back of control':
   'Автоматический возврат управления',
 'Self-explaining alarm screen':
   'Понятный экран аварий',
 'Ten performance curves':
   'Десять рабочих кривых',
 'See the quality of control':
   'Видно качество регулирования',
 'See whether feeding is even':
   'Видно, равномерна ли подача',
 'Multilingual interface':
   'Многоязычный интерфейс',
 'Monitoring platform link':
   'Связь с платформой мониторинга',
 'Network settings connect the system to the':
   'Сетевые настройки подключают систему к',
 'Sealion monitoring platform':
   'платформе мониторинга Sealion',
 'Masterbatch ratio':
   'Соотношение суперконцентрата',
 'Working with the':
   'Совместно с',
 'masterbatch dosing system':
   'системой дозирования суперконцентрата',
 'Reference wall thickness':
   'Справочная толщина стенки',
 'Cable-specific conversion':
   'Пересчёт для кабеля',
 'Two ways to take control':
   'Два способа взять управление',
 'Return on investment':
   'Окупаемость',
 'Line output':
   'Производительность линии',
 'Running time':
   'Время работы',
 'Material price':
   'Цена сырья',
 'Annual saving':
   'Годовая экономия',
 '16h/day × 200 days/yr':
   '16 ч/сут × 200 дней/год',
 '12h/day × 200 days/yr':
   '12 ч/сут × 200 дней/год',
 '12h/day × 180 days/yr':
   '12 ч/сут × 180 дней/год',
 'Checks you can make on the line':
   'Проверки, доступные на линии',
 'Module cannot connect to the PC':
   'Модуль не соединяется с компьютером',
 'Hopper starved':
   'Нехватка материала в бункере',
 'Output fluctuating':
   'Колебания производительности',
 'Haul-off speed fluctuating':
   'Колебания скорости тяги',
 'Excessive torque':
   'Избыточный момент',
 'Poor feeding':
   'Плохая подача',
 'Is the silo empty? Is the loader working?':
   'Пуст ли силос? Работает ли загрузчик?',
 'Poor link between gravimetric and haul-off modules':
   'Плохая связь между весовым модулем и модулем тяги',
 'Extruder signal low':
   'Низкий сигнал экструдера',
 'Large deviation between measured and set value':
   'Большое расхождение измеренного и заданного значения',
 'Extruder fault':
   'Неисправность экструдера',
 'Haul-off fault':
   'Неисправность тянущего устройства',
 'Haul-off signal at maximum':
   'Сигнал тяги на максимуме',
 'Measured weight per metre far from setpoint':
   'Измеренная масса погонного метра далека от задания',
 'Abnormal screw speed':
   'Отклонение частоты вращения шнека',
 'No or very low haul-off speed reading':
   'Нет показаний скорости тяги или они очень малы',
 'Hopper value never reaches the set upper limit':
   'Значение бункера не достигает заданного верхнего предела',
 'Hopper stays full and output will not rise':
   'Бункер остаётся полным, производительность не растёт',
 'On pipe lines':
   'На трубных линиях',
 'Gravimetric Control System 2026':
   'Система гравиметрического контроля 2026',
 'Pipe line, filmed on site':
   'Трубная линия, съёмка на объекте',

 "The pipe thickness measurement follows the principle of ultrasonic pulse reflection: when the probe's ultrasonic pulse reaches the inner/outer interface of the pipe through the medium, it is reflected back to the probe, and by precisely timing that travel the ultrasonic processing unit rapidly calculates the material thickness.":
   'Измерение толщины стенки основано на отражении ультразвукового импульса: импульс датчика проходит через среду до внутренней и наружной границ трубы и возвращается обратно, а блок ультразвуковой обработки по точно измеренному времени пробега быстро вычисляет толщину материала.',
 'The system is an independently developed, high-end on-line pipe measurement system built on advanced domestic and international technology, using digital processing and high-precision acquisition chips. It comprises the Sealion ultrasonic processing unit, the ultrasonic probe and the scanning structure; the host circuit covers transmission, reception, and display/control. Theoretical measuring resolution is 0.001mm; due to pipe-surface irregularity and the production environment, practical resolution reaches 0.01mm — an advanced level for the industry.':
   'Система — собственная разработка высокого класса для измерения труб в линии, построенная на передовых отечественных и зарубежных решениях с цифровой обработкой и высокоточными микросхемами сбора данных. В её состав входят блок ультразвуковой обработки Sealion, ультразвуковой преобразователь и сканирующий узел; схема основного блока отвечает за излучение, приём, отображение и управление. Теоретическое разрешение измерения — 0,001 мм; с учётом неровности поверхности трубы и производственных условий практическое разрешение достигает 0,01 мм, что соответствует передовому уровню отрасли.',
 'Scanning box with a built-in auto-tracking ultrasonic probe (patent ZL202121445714.5)':
   'Сканирующая головка со встроенным самоотслеживающим ультразвуковым датчиком (патент ZL202121445714.5)',
 'Laser diameter device: real-time OD measurement at 0.01mm display accuracy (patent 202420005454.7)':
   'Лазерный измеритель диаметра: измерение наружного диаметра в реальном времени с индикацией 0,01 мм (патент 202420005454.7)',
 'The scanning box conforms fully to any pipe curvature, keeping the probe pulse perpendicular to the pipe surface for accuracy, stabilising the ultrasonic medium and the DSP signal, and reducing the effect of medium instability. The structure is simple and easy to operate.':
   'Сканирующая головка полностью повторяет кривизну любой трубы, удерживая импульс датчика перпендикулярно поверхности, что обеспечивает точность, стабилизирует ультразвуковую среду и сигнал DSP и снижает влияние нестабильности среды. Конструкция проста и удобна в работе.',
 'The system works on ultrasonic principles with high-frequency transducers. High-speed DSP acquisition and processing measure moving pipe and cable on the extrusion line':
   'Система работает на ультразвуковом принципе с высокочастотными преобразователями. Скоростной сбор и обработка DSP измеряют движущуюся трубу и кабель на экструзионной линии',
 '; an industrial touch screen presents the cross-section with wall-thickness deviation and eccentricity all round, so thickness, eccentricity, ovality and diameter drift can be corrected early — fewer rejects and a shorter start-up.':
   '; промышленный сенсорный экран показывает сечение с отклонением толщины стенки и эксцентриситетом по всей окружности, поэтому уход по толщине, эксцентриситету, овальности и диаметру исправляется рано — меньше брака и короче выход на режим.',
 'Pipe OD range (mm)':
   'Диапазон наружного диаметра трубы (мм)',
 'The probe emits an ultrasonic pulse. A first echo returns from the pipe surface; a second returns after the pulse crosses the wall. The system measures the interval between them and, with the speed of sound in that medium at that temperature, converts it to a wall thickness.':
   'Датчик излучает ультразвуковой импульс. Первое эхо приходит от поверхности трубы, второе — после прохождения импульса через стенку. Система измеряет интервал между ними и по скорости звука в данной среде при данной температуре пересчитывает его в толщину стенки.',
 'The pipe must sit at the centre of the scanning box with the probe perpendicular to the wall. Off-centre, the pulse travels the hypotenuse and reads thicker than the true wall — or returns no signal at all.':
   'Труба должна находиться по центру сканирующей головки, а датчик — перпендикулярно стенке. При смещении импульс идёт по гипотенузе и показывает завышенную толщину либо вовсе не даёт сигнала.',
 'Before filling, close the main outlet and the spray valve, open the quick-fill valve and connect the hose; once the water covers all probes, open the spray valve (about half travel, adjusted to pressure), then close the quick-fill valve.':
   'Перед заполнением закройте главный слив и вентиль распыла, откройте вентиль быстрого налива и подсоедините шланг; когда вода закроет все датчики, откройте вентиль распыла примерно наполовину (с поправкой на давление) и закройте вентиль быстрого налива.',
 'Switch it off or dim it when idle for long periods; clean the screen with a barely damp soft cloth and never pour water on it; it is a capacitive screen, so avoid pressure and impact; do not open the unit yourself.':
   'При длительном простое выключайте его или снижайте яркость; экран протирайте едва влажной мягкой тканью и никогда не лейте на него воду; экран ёмкостный, поэтому избегайте давления и ударов; не вскрывайте прибор самостоятельно.',
 'Replace as soon as one splits. The flange is heavy, so two people should work together — one supporting it, one removing the bolts. When threading pipe, keep the pipe centre level with the seal centre or the seal can burst and leak.':
   'Заменяйте уплотнение сразу при появлении разрыва. Фланец тяжёлый, поэтому работать следует вдвоём: один поддерживает, второй откручивает болты. При заводе трубы держите её ось на одном уровне с центром уплотнения, иначе уплотнение может прорваться и дать течь.',

 'What the ultrasonic gauge is':
   'Что представляет собой ультразвуковая система',
 "The pipe thickness measurement follows the principle of ultrasonic pulse reflection: when the probe's ultrasonic pulse reaches the inner/outer interface of the pipe through the medium, it is reflected back; the system measures the time difference and computes the wall thickness.":
   'Измерение толщины стенки основано на принципе отражения ультразвукового импульса: импульс датчика проходит через среду до внутренней и наружной границ трубы и отражается обратно; система измеряет разницу во времени и вычисляет толщину стенки.',
 'Why equip it':
   'Зачем это нужно',
 'Why an extrusion line needs it':
   'Зачем экструзионной линии эта система',
 'What it gives you':
   'Что вы получаете',
 'Start-up':
   'Пуск линии',
 "See the pipe's condition directly, cutting waste and defects and shortening start-up.":
   'Состояние трубы видно сразу: меньше отходов и брака, короче выход на режим.',
 'During production':
   'В ходе производства',
 'Real-time monitoring of thickness, eccentricity, ovality and OD; every change is monitored and recorded in full, archived so production can be checked at any time — the pipe stays under your control.':
   'Толщина, эксцентриситет, овальность и наружный диаметр контролируются в реальном времени; каждое изменение фиксируется и сохраняется в архив, поэтому производство можно проверить в любой момент — труба остаётся под контролем.',
 'After warehousing':
   'После отгрузки на склад',
 "Even once shipped to site, the database can trace any batch's production data on demand.":
   'Даже после отправки на объект по базе данных можно поднять производственные данные любой партии.',
 'Real-time OD, ID, wall thickness, eccentricity and ovality measurement':
   'Измерение наружного и внутреннего диаметра, толщины стенки, эксцентриситета и овальности в реальном времени',
 'Alarm tracking and lookup':
   'Отслеживание и поиск аварий',
 'History curves and production data records':
   'Исторические кривые и записи производственных данных',
 'Production parameter and order setup':
   'Настройка производственных параметров и заказов',
 'Recipe storage and management':
   'Хранение рецептов и управление ими',
 "Measures multilayer pipe, with each layer's thickness shown separately":
   'Измеряет многослойную трубу с раздельным выводом толщины каждого слоя',
 'Scanning box':
   'Сканирующая головка',
 'The number of ultrasonic probes is selectable — 1, 2, 3, 4, 6, 8 or 16 depending on the model; probes are IP68-rated and mount directly in the scanning box inside the water tank.':
   'Число ультразвуковых датчиков выбирается — 1, 2, 3, 4, 6, 8 или 16 в зависимости от модели; датчики имеют степень защиты IP68 и устанавливаются прямо в сканирующую головку внутри ванны.',
 'without contact and with automatic centring':
   'бесконтактно и с автоматическим центрированием',
 'Autonomy':
   'Самостоятельность',
 'DSP receives echoes fast and accurately while distinguishing clutter':
   'DSP быстро и точно принимает эхо-сигналы, отделяя помехи',
 'Self-adjusting':
   'Самонастройка',
 'Even if material changes, DSP self-adjusts the capture window to lock the echo per set parameters':
   'Даже при смене материала DSP сам подстраивает окно захвата и удерживает эхо-сигнал по заданным параметрам',
 'High accuracy':
   'Высокая точность',
 'DSP processes captured signals synchronously, ensuring measurement accuracy':
   'DSP обрабатывает принятые сигналы синхронно, обеспечивая точность измерения',
 'Model range (big pipe)':
   'Модельный ряд (большой диаметр)',
 'Industrial tablet PC with built-in ultrasonic measurement software, clean interface.':
   'Промышленный планшетный ПК со встроенной программой ультразвукового измерения и понятным интерфейсом.',
 'PE water pipe, PE gas pipe, PPR and PVC extrusion lines where large-diameter wall thickness has to hold.':
   'Линии ПЭ водоснабжения, ПЭ газоснабжения, ППР и ПВХ, где нужно удерживать толщину стенки большого диаметра.',
 'Principle':
   'Принцип',
 'Measuring principle &amp; the conditions for an accurate reading':
   'Принцип измерения и условия точного результата',
 'wall thickness S = speed V × time difference T':
   'толщина стенки S = скорость V × разница во времени T',
 'The speed of sound in water is about 1470 m/s at room temperature. Because speed depends on both material and temperature, the system compensates for them.':
   'Скорость звука в воде при комнатной температуре составляет около 1470 м/с. Поскольку она зависит и от материала, и от температуры, система вводит соответствующую компенсацию.',
 'Perpendicular centring':
   'Перпендикулярное центрирование',
 'Cooled to temperature':
   'Охлаждение до рабочей температуры',
 'The same material at a different temperature gives a different speed of sound. The larger the temperature gap, the larger the error — a reading is always for this material at this temperature.':
   'Один и тот же материал при другой температуре даёт другую скорость звука. Чем больше разница температур, тем больше погрешность: результат всегда относится к данному материалу при данной температуре.',
 'Water quality &amp; coupling':
   'Качество воды и акустический контакт',
 'Every probe must be filled with water and the box water kept clean; contaminated water prevents measurement.':
   'Каждый датчик должен быть заполнен водой, а вода в головке — чистой; загрязнённая вода делает измерение невозможным.',
 'No trapped bubbles':
   'Отсутствие пузырьков',
 'No air bubbles may cling to the probe face or the pipe surface, or the pulse reflects off the bubble instead.':
   'На поверхности датчика и трубы не должно быть пузырьков воздуха, иначе импульс отразится от пузырька.',
 'Low vibration':
   'Малая вибрация',
 'Relative vibration of the moving pipe must be small, since it jitters the echo timing.':
   'Относительная вибрация движущейся трубы должна быть небольшой, так как она искажает время прихода эхо-сигнала.',
 'Visible signal strength':
   'Видимый уровень сигнала',
 'The software shows echo gain live, so the operator can tell from the gain whether centring is good or needs correcting.':
   'Программа показывает усиление эхо-сигнала в реальном времени, и по нему оператор понимает, хорошо ли выставлено центрирование.',
 'All of these conditions must hold together. Sealion provides on-site training at handover, including how to record the centring-device scale so the line can keep these conditions repeatable.':
   'Все эти условия должны выполняться одновременно. При сдаче Sealion проводит обучение на месте, включая порядок записи шкалы центрирующего устройства, чтобы условия можно было воспроизводить.',
 'Measuring the wall is only the start. The Sealion ultrasonic software turns every reading into production data you can query, export and trace.':
   'Измерение стенки — только начало. Программа Sealion превращает каждое показание в производственные данные, доступные для запроса, выгрузки и прослеживания.',
 'Line data on one screen':
   'Данные линии на одном экране',
 'Measured weight per metre, haul-off speed, accumulated pipe length and cut count sit alongside the thickness readings.':
   'Измеренная масса погонного метра, скорость тяги, накопленная длина трубы и число резов выводятся рядом с показаниями толщины.',
 "Thickness curves per probe and an outer-diameter curve are plotted in real time against the recipe's upper and lower limits, so drift is visible at a glance.":
   'Кривые толщины по каждому датчику и кривая наружного диаметра строятся в реальном времени относительно пределов рецепта, поэтому уход виден сразу.',
 'A full set of measuring parameters is stored per pipe spec and pushed to the controller when recalled; recipes can be added, edited, searched, deleted and read back from the controller.':
   'Полный набор параметров измерения сохраняется под каждый типоразмер трубы и передаётся в контроллер при вызове; рецепты можно добавлять, изменять, искать, удалять и считывать из контроллера.',
 'Choose which alarms are active and at what deviation; breaches are alarmed and logged with time and deviation, searchable by date range, with records kept for a year.':
   'Выбирается, какие аварии активны и при каком отклонении; превышения сигнализируются и записываются с указанием времени и отклонения, доступны по диапазону дат, записи хранятся год.',
 'The logging interval is configurable; thickness and diameter data can be queried by date range and shown as a table or curves, exported to Excel, or copied to a USB stick in one click.':
   'Интервал записи настраивается; данные толщины и диаметра можно запросить по диапазону дат и вывести таблицей или кривыми, выгрузить в Excel или скопировать на USB одним нажатием.',
 'Calibration factors':
   'Калибровочные коэффициенты',
 'Correction factors for both wall and diameter compensate measurement error, and several sets can be saved for later recall.':
   'Поправочные коэффициенты по толщине и диаметру компенсируют погрешность измерения; можно сохранить несколько наборов и вызывать их позднее.',
 'Production data is sent live to a monitoring room over TCP/IP (SOCKET, client-server), so staff off the floor can follow the line.':
   'Производственные данные передаются в диспетчерскую в реальном времени по TCP/IP (SOCKET, клиент-сервер), поэтому за линией можно следить вне цеха.',
 'Chinese / English UI':
   'Интерфейс на китайском и английском',
 'The interface switches between Chinese and English for expatriate teams and export lines.':
   'Интерфейс переключается между китайским и английским — для иностранных специалистов и экспортных линий.',
 'Diagnostics':
   'Диагностика',
 'A built-in debug view shows how the software is running, which shortens fault-finding when something misbehaves.':
   'Встроенный отладочный режим показывает работу программы и ускоряет поиск неисправностей.',
 'Daily use':
   'Ежедневная эксплуатация',
 'Encoder arm — running':
   'Кодирующий рычаг — в работе',
 'In operation the encoder wheel must contact the pipe at its centre line and turn with the pipe as it advances — the basis for accurate haul-off speed and length readings.':
   'В работе колесо энкодера должно касаться трубы по её осевой линии и вращаться вместе с ней — это основа точных показаний скорости тяги и длины.',
 'Encoder arm — stop &amp; restart':
   'Кодирующий рычаг — остановка и пуск',
 'On stop the arm lifts clear; to restart, draw the arm out, lower it gently back onto the pipe and adjust it to the centre.':
   'При остановке рычаг поднимается; для пуска его выдвигают, аккуратно опускают на трубу и выставляют по центру.',
 'Filling procedure':
   'Порядок заполнения водой',
 'If pressure is high':
   'При высоком давлении',
 'If supply pressure is high, throttle the inlet with the supply valve to avoid hitting the probes and seals.':
   'Если давление в сети велико, приток дросселируют подающим вентилем, чтобы не ударить по датчикам и уплотнениям.',
 'Maintenance':
   'Обслуживание',
 'This is a water-coupled instrument: how well it is maintained shows directly in measurement accuracy. These are the standard intervals handed to the line during commissioning training.':
   'Это прибор с водяным акустическим контактом: качество обслуживания напрямую отражается на точности измерения. Ниже — стандартные интервалы, передаваемые линии при пусконаладочном обучении.',
 'Probes · every 6 months':
   'Датчики · каждые 6 месяцев',
 'With the line stopped and power off, drain the tank and wipe the curved probe face with a clean, soft, damp cloth. Avoid removing probes; if you must, keep water away from the probe-to-cable junction.':
   'При остановленной линии и снятом питании слейте воду и протрите изогнутую поверхность датчика чистой мягкой влажной тканью. Датчики по возможности не снимайте; если снимаете — не допускайте попадания воды в место соединения датчика с кабелем.',
 'Water tank · every 6 months':
   'Ванна · каждые 6 месяцев',
 'Close the inlet, open the drain, flush the deposits and inspect the pipework, valves and filter at the same time. Clean sooner if readings drift noticeably.':
   'Закройте подачу, откройте слив, промойте отложения и одновременно осмотрите трубопровод, вентили и фильтр. При заметном уходе показаний очищайте раньше срока.',
 'Control cabinet · every 6 months':
   'Шкаф управления · каждые 6 месяцев',
 'Isolate power, brush dust from components and trunking, tighten every terminal, replace corroded lugs, and check the cooling fan, switches and alarm lamp.':
   'Снимите питание, удалите пыль с элементов и кабель-каналов мягкой кистью, подтяните все клеммы, замените окислившиеся наконечники, проверьте вентилятор охлаждения, выключатели и сигнальную лампу.',
 'Filter · drain every 2 weeks':
   'Фильтр · продувка каждые 2 недели',
 'Close the clean-water outlet and open the drain at the base so mains water flushes the element for 3–5 minutes. After 3–6 months the element itself needs cleaning; replace it if deformed or damaged.':
   'Закройте выход чистой воды и откройте нижний слив, чтобы водопроводная вода промывала элемент 3–5 минут. Через 3–6 месяцев сам элемент требует очистки; при деформации или повреждении — замените.',
 'Industrial PC':
   'Промышленный компьютер',
 'Silicone seals':
   'Силиконовые уплотнения',
 'Silicone seal bore vs pipe diameter':
   'Внутренний диаметр уплотнения и диаметр трубы',
 '2 off each':
   'по 2 шт. каждого',
 'Ten reasons to choose Sealion ultrasonic':
   'Десять причин выбрать ультразвук Sealion',
 'Sixteen years of independent ultrasonic R&amp;D':
   'Шестнадцать лет собственных разработок в области ультразвука',
 'Data can be saved and exported; product quality is traceable':
   'Данные сохраняются и выгружаются, качество продукции прослеживается',
 'Fully in-house, so it can be tailored to each plant':
   'Полностью собственная разработка, поэтому решение адаптируется под каждое производство',
 'Large-pipe gauging on site':
   'Измерение больших диаметров на объекте',
 'Ultrasonic gauging 2026':
   'Ультразвуковое измерение 2026',
 'One-metre system on site':
   'Метровая система на объекте',
 'Your browser cannot play this video.':
   'Ваш браузер не может воспроизвести это видео.',

 "Patents": "Патенты",
 "Invention": "Изобретение",
 "Design": "Промышленный образец",
 "Title": "Наименование",
 "Type": "Тип",
 "Pipe quality inspection equipment and method": "Оборудование и способ контроля качества труб",
 "Pipe diameter/thickness gauge and its measuring method": "Прибор измерения диаметра и толщины трубы и способ измерения",
 "Calibration method and device for pipe wall thickness measurement": "Способ и устройство калибровки измерения толщины стенки трубы",
 "Device for measuring pipe length": "Устройство измерения длины трубы",
 "Pipe inspection equipment": "Оборудование контроля труб",
 "Pipe quality inspection equipment": "Оборудование контроля качества труб",
 "Pipe length measuring device": "Устройство измерения длины трубы",
 "Pipe diameter/thickness gauge": "Прибор измерения диаметра и толщины трубы",
 "Pipe quality inspection system": "Система контроля качества труб",
 "Rotating laser diameter/thickness device": "Вращающееся лазерное устройство измерения диаметра и толщины",
 "Online intelligent pipe inspection equipment": "Оборудование интеллектуального контроля труб в линии",
 "Rotating laser pipe thickness device": "Вращающееся лазерное устройство измерения толщины трубы",
 "Manipulator clamping device": "Захватное устройство манипулятора",
 "Sliding pipe support device": "Скользящее опорное устройство для трубы",
 "Pipe measuring system": "Система измерения трубы",
 "Pipe measuring device": "Устройство измерения трубы",
 "Pipe measuring clamp device": "Зажимное измерительное устройство для трубы",
 "Pipe thickness/diameter measuring device": "Устройство измерения толщины и диаметра трубы",
 "OD measurement: the average OD of the off-line pipe is measured, with average upper/lower limits set; an encoder rotates one full turn to compute the accurate OD, at a detection point 300mm from the pipe end, meeting national standards.":
   "Измерение наружного диаметра: определяется средний диаметр сошедшей с линии трубы при заданных верхнем и нижнем пределах; энкодер совершает полный оборот для точного расчёта, точка измерения — в 300 мм от торца, что соответствует государственным нормам.",

 'The Sealion online intelligent pipe inspection system is fitted at the end of the extruder and can be installed at the end of any line; pipe moves automatically to the inspection platform for measurement, without affecting any production task.':
   'Система интеллектуального контроля труб Sealion устанавливается в конце линии — на любой линии; труба автоматически перемещается на измерительную платформу, не мешая производственным задачам.',
 "It includes laser thickness measurement, encoder diameter measurement, non-roundness detection and qualified-pipe flipping as standard. All test data can be sent to the factory's internal MES system, a production Kanban, or another management system for remote quality monitoring.":
   'В базовой комплектации: лазерное измерение толщины, измерение диаметра энкодером, контроль некруглости и перекладывание годных труб. Все результаты могут передаваться в заводскую MES, на производственную панель или в другую систему управления для удалённого контроля качества.',
 "It includes weight detection, laser thickness measurement, encoder diameter measurement, pipe length detection, non-roundness detection and qualified-pipe flipping as standard. All test data can be sent to the factory's internal MES system, a production Kanban, or another management system for remote quality monitoring.":
   'В базовой комплектации: взвешивание, лазерное измерение толщины, измерение диаметра энкодером, измерение длины трубы, контроль некруглости и перекладывание годных труб. Все результаты могут передаваться в заводскую MES, на производственную панель или в другую систему управления для удалённого контроля качества.',
 'OD measurement: the average OD of the off-line pipe is measured, with average upper/lower limits set; an encoder rotates one full turn to compute the accurate OD. The detection point sits 300mm from the pipe end, meeting national measurement standards.':
   'Измерение наружного диаметра: определяется средний диаметр сошедшей с линии трубы при заданных верхнем и нижнем пределах; энкодер совершает полный оборот для точного расчёта. Точка измерения находится в 300 мм от торца, что соответствует государственным нормам измерений.',
 'The Sealion pipe quality and safety storage system is fitted at the end of the extruder and can be installed at the end of any line, using a smooth sliding mechanism to bring the pipe to the testing platform for measurement, without affecting any production task on the line.':
   'Система приёмочного контроля качества труб Sealion устанавливается в конце линии — на любой линии: труба по плавному скользящему механизму подаётся на измерительную платформу, не мешая производственным задачам.',
 'Data storage and collection: all data is saved in real time to Excel in a specified folder; TCP or MQTT ports are opened for uploading to the company MES or a customer-specified port. Data can be exported by order or by date, in Excel or PDF, to a standard USB drive.':
   'Хранение и сбор данных: все данные в реальном времени сохраняются в Excel в заданную папку; открыты порты TCP или MQTT для передачи в MES предприятия или на указанный заказчиком порт. Выгрузка возможна по заказу или по дате, в Excel или PDF, на обычный USB-накопитель.',

 "The Sealion online intelligent pipe inspection system is fitted at the end of the extruder and can be installed at the end of any line; pipe moves automatically to the inspection platform for measurement, without affecting any production process.":
   "Система интеллектуального контроля труб Sealion устанавливается в конце экструзионной линии — на любой линии; труба автоматически перемещается на измерительную платформу, не влияя на производственный процесс.",
 "Thickness measurement: upper/lower wall-thickness limits and real-time wall thickness are set; a patented structure lasers the pipe from inside and out while a servo motor rotates one full turn, computing accurate thickness in every direction and marking the positions of maximum and minimum. The thickness point sits 30–50mm from the pipe end, clear of the cut flash, and the laser does not shine directly on the pipe surface, so colour does not affect the reading.":
   "Измерение толщины: задаются верхний и нижний пределы и текущее значение толщины стенки; запатентованный узел просвечивает трубу лазером изнутри и снаружи, а серводвигатель делает полный оборот, вычисляя точную толщину по всем направлениям и отмечая места наибольшего и наименьшего значения. Точка измерения находится в 30–50 мм от торца, вне зоны заусенца от реза, а лазер не светит прямо на поверхность трубы, поэтому цвет не влияет на результат.",
 "Data storage and collection: all data saved in real time as Excel; TCP or MQTT ports open for upload to the company MES or a customer-specified port; export by order or date in Excel or PDF.":
   "Хранение и сбор данных: все данные сохраняются в реальном времени в Excel; открыты порты TCP или MQTT для передачи в MES предприятия или на указанный заказчиком порт; выгрузка по заказу или по дате в Excel или PDF.",

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
 "quality-storage": {
  "Ovality (non-roundness): two sets of lasers measure OD at several points to calculate and display non-roundness.":
    "Овальность: два лазерных комплекта измеряют наружный диаметр в нескольких точках, вычисляя и отображая некруглость.",
  "Ellipticity: pipe ovality is calculated from the measured wall thickness and displayed on the interface.":
    "Эллиптичность: овальность трубы вычисляется по измеренной толщине стенки и выводится на экран.",
  "Weight: measured with an imported high-precision load cell.": "Масса: измеряется импортным высокоточным тензодатчиком.",
  "Data display: real-time display of current production quantity, yield, NG count and OK count.":
    "Отображение данных: текущий объём выпуска, доля годного, число забракованных и годных изделий в реальном времени.",
  "Deviation alarms: pass/fail alerts from set upper/lower deviations on OD, weight, thickness, length and roundness, with a defective-product alarm and a quantity-reached reminder.":
    "Сигнализация отклонений: годен/не годен по заданным верхним и нижним пределам наружного диаметра, массы, толщины, длины и круглости, с сигналом о браке и напоминанием о достижении заданного количества.",
  "Data processing: abnormal data is excluded and not linked to the traceability code.":
    "Обработка данных: аномальные значения исключаются и не привязываются к коду прослеживаемости.",
  "Twenty patents cover this system — 3 inventions, 15 utility models and 2 design patents. The wall-thickness measuring arrangement described above is one of them.":
    "Систему защищают двадцать патентов: 3 изобретения, 15 полезных моделей и 2 промышленных образца. Описанный выше узел измерения толщины стенки — один из них.",
  "Utility model": "Полезная модель",
  "Sealion holds 60 patents and software copyrights in total; certificates can be viewed on the":
    "Всего у Sealion 60 патентов и свидетельств на программы; сертификаты доступны на странице",
  "IP portfolio": "Интеллектуальная собственность",
  "Key parts are imported, brand-name components, for build quality and stability.":
    "Ключевые узлы — импортные комплектующие известных марок, что обеспечивает качество сборки и стабильность.",
  "Guangzhou Sealion": "Guangzhou Sealion",
  "Servo motor": "Серводвигатель",
  "Control cabinet": "Шкаф управления",
  "Servo drive": "Сервопривод",
  "Industrial PC / HMI": "Промышленный ПК / панель оператора",
  "High-precision load cell": "Высокоточный тензодатчик",
  "Laser displacement sensor": "Лазерный датчик перемещения",
  "Low-voltage components": "Низковольтная аппаратура",
  "Power supply": "Источник питания",
  "Pneumatics": "Пневматика",
  "Rated voltage": "Номинальное напряжение",
  "approx. 2kW": "около 2 кВт",
  "Air supply": "Подача воздуха",
  "Data storage": "Хранение данных",
  "Pipe OD range": "Диапазон наружного диаметра трубы",
  "φ32–400 (banded by line spec)": "φ32–400 (по типоразмеру линии)",
  "Pipe length": "Длина трубы",
  "6–12m (on request)": "6–12 м (под заказ)",
  "Measurable thickness": "Измеряемая толщина",
  "2–45mm (by pipe spec)": "2–45 мм (по типоразмеру трубы)",
  "buzzer + flashing light": "звуковой сигнал и проблесковый маячок",
  "Wall thickness": "Толщина стенки",
  "display 0.01mm, accuracy ±0.03mm": "индикация 0,01 мм, точность ±0,03 мм",
  "Outer diameter": "Наружный диаметр",
  "display 0.01mm, accuracy ±0.05mm": "индикация 0,01 мм, точность ±0,05 мм",
  "display 0.01kg, accuracy ±0.2%": "индикация 0,01 кг, точность ±0,2%",
  "display 0.001m, accuracy ±1mm": "индикация 0,001 м, точность ±1 мм",
  "Operating environment": "Условия эксплуатации",
  "indoor 5–40℃, IP65, noise &lt;70dBA": "в помещении 5–40 ℃, IP65, шум менее 70 дБА",
  "main unit, laser head, IPC, signal processor &amp; control cabinet — 1 year each free; free software upgrades":
    "основной блок, лазерная головка, промышленный ПК, блок обработки сигнала и шкаф управления — по 1 году бесплатно; обновления ПО бесплатны",
  "End-of-line quality gating and inbound storage on PE water, PE gas and PVC pipe extrusion lines.":
    "Отбраковка на выходе линии и приёмка на склад для линий ПЭ водоснабжения, ПЭ газоснабжения и ПВХ.",
  "Inbound inspection on site": "Приёмочный контроль на объекте",
  "Inbound quality system 2026": "Система приёмочного контроля 2026",
  "Running on site": "Работа на объекте",
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
