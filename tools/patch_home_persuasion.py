# -*- coding: utf-8 -*-
"""首页补两块：数字证据条 + 需求确认

首页删到只剩三节之后，问题从"什么都堆一点"变成了"什么都不太说"。
按规范 §11.1／§11.5，缺的是说服链条的头两环：
  · 第一屏之后立刻用数字说话（沃思首屏底部就是这条）
  · 在给方案之前，先让客户确认自己有这个问题

四个数字全部取自站上已有内容，且每个都链到它的依据页——
规范 §9.7 要求"主张与依据紧邻"，这里做成点得进去。
"""
import io, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(p):
    s = io.open(p, encoding="utf-8").read()
    h, sep, b = s.partition("\n---\n")
    if not sep:
        sys.exit(f"✗ {p} 缺元数据分隔符")
    return json.loads(h), b


def save(p, m, b):
    io.open(p, "w", encoding="utf-8").write(
        json.dumps(m, ensure_ascii=False, indent=1) + "\n---\n" + b)


# 数字与去处：每一条都能在站上找到出处
STATS = {
    "zh": [("18+", "年", "行业经验", "/about.html"),
           ("60", "项", "知识产权", "/ip.html"),
           ("18", "家", "长期合作客户", "/about/partners.html"),
           ("26", "组", "现场记录", "/cases.html")],
    "en": [("18+", "yrs", "in the industry", "/en/about.html"),
           ("60", "", "patents &amp; copyrights", "/en/ip.html"),
           ("18", "", "long-term customers", "/en/about/partners.html"),
           ("26", "", "site records", "/en/cases.html")],
    "ru": [("18+", "лет", "в отрасли", "/ru/about.html"),
           ("60", "", "патентов и свидетельств", "/ru/ip.html"),
           ("18", "", "постоянных клиентов", "/ru/about.html"),
           ("26", "", "объектов", "/ru/cases.html")],
}

NEED = {
    "zh": dict(
        eyebrow="先看你的产线",
        h2="米重偏一点，一年是多少钱",
        lead="管子出了模具就定型。壁厚偏了、米重超了，回头再看已经是几吨料的事——而这段偏差，往往要等一整批跑完才被发现。",
        items=[("开机", "靠经验试料，管子要出来很长一段才看得清厚薄，反复调整，料和时间一起烧。"),
               ("生产", "靠人工抽检，两次抽检之间发生了什么，没人知道。"),
               ("事后", "超了当废料或降级，欠了是质量风险——两头都亏。")],
        cta="你的产线一年在这上面漏多少，填三个数就知道",
        cta_href="#calc"),
    "en": dict(
        eyebrow="Start with your line",
        h2="A little heavy per metre, a year at a time",
        lead="Pipe sets the moment it leaves the die. By the time an off wall thickness or an over-weight metre is noticed, it is already tonnes of material — and the drift usually only shows up once a whole batch has run.",
        items=[("Start-up", "Trial and error on experience: a long length has to come out before the wall can be judged, and material and time burn together through every adjustment."),
               ("Running", "Manual spot checks. What happened between two of them, nobody knows."),
               ("After", "Over-weight goes to scrap or a lower grade; under-weight is a quality risk. Both directions lose.")],
        cta="What your line loses to this in a year — three numbers will tell you",
        cta_href="#calc"),
    "ru": dict(
        eyebrow="Начните со своей линии",
        h2="Небольшой перевес на метре — за год это деньги",
        lead="Труба принимает форму сразу за фильерой. Когда отклонение толщины стенки или перевес заметят, это уже тонны материала.",
        items=[("Пуск", "Подбор по опыту: чтобы оценить стенку, нужно выпустить длинный отрезок."),
               ("Работа", "Выборочный контроль вручную — что происходит между замерами, неизвестно."),
               ("Потом", "Перевес — в брак или в низший сорт, недовес — риск по качеству.")],
        cta="Сколько теряет ваша линия за год",
        cta_href="/ru/#products"),
}


def stats_html(lang):
    L = {"zh": "可核对的四个数字", "en": "Four numbers you can check",
         "ru": "Четыре проверяемых показателя"}[lang]
    out = [f'  <section class="section stats" id="stats" aria-label="{L}">',
           '    <div class="wrap"><div class="stats-row">']
    for num, unit, label, href in STATS[lang]:
        out.append(
            f'      <a class="stat" href="{href}">'
            f'<b class="stat-n">{num}<span class="stat-u">{unit}</span></b>'
            f'<span class="stat-l">{label}</span></a>')
    out += ["    </div></div>", "  </section>", ""]
    return "\n".join(out)


def need_html(lang):
    T = NEED[lang]
    items = "\n".join(
        f'        <div class="need-i"><b>{t}</b><p>{d}</p></div>' for t, d in T["items"])
    return (f'  <section class="section need" id="need">\n'
            f'    <div class="wrap">\n'
            f'      <div class="sh">\n'
            f'        <span class="eyebrow">{T["eyebrow"]}</span>\n'
            f'        <h2>{T["h2"]}</h2>\n'
            f'        <p class="lead">{T["lead"]}</p>\n'
            f'      </div>\n'
            f'      <div class="need-grid">\n{items}\n      </div>\n'
            f'      <p class="need-cta"><a class="arrow-link" href="{T["cta_href"]}">'
            f'{T["cta"]} &rarr;</a></p>\n'
            f'    </div>\n  </section>\n\n')


for lang in ("zh", "en", "ru"):
    p = os.path.join(ROOT, "src", "content", lang, "index.html")
    if not os.path.exists(p):
        continue
    meta, body = load(p)
    if 'id="stats"' in body:
        print(f"  {lang} 已有，跳过")
        continue
    m = re.search(r'<section[^>]*\bid="divisions"', body)
    if not m:
        print(f"  {lang} 找不到 divisions 节，跳过")
        continue
    add = stats_html(lang) + "\n" + need_html(lang)
    body = body[:m.start()] + add + body[m.start():]
    save(p, meta, body)
    print(f"  {lang} 首页补入 数字证据条 + 需求确认（{len(add)} 字符）")

# ── CSS ────────────────────────────────────────────────────
S = os.path.join(ROOT, "public", "style.css")
st = io.open(S, encoding="utf-8").read()
ANCH = "/* a11y + motion */"
CSS = """/* 数字证据条：第一屏之后立刻用数字说话。
   每个数字都链到它的依据页——页面上出现量化主张就得能点进去核。 */
.stats{padding-block:var(--sp-2);background:var(--ink);color:#fff}
.stats-row{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem}
.stat{display:flex;flex-direction:column;align-items:center;gap:.35rem;padding:.75rem .5rem;
  border-radius:var(--radius-lg);color:#fff;text-align:center;transition:background .2s}
.stat:hover{background:rgba(255,255,255,.08)}
.stat-n{font-family:var(--mono);font-size:clamp(2rem,1.5rem+1.6vw,3rem);font-weight:600;
  line-height:1.1;color:var(--signal);font-variant-numeric:tabular-nums}
.stat-u{font-size:.42em;margin-left:.15em;color:rgba(255,255,255,.72)}
.stat-l{font-size:1.0625rem;color:rgba(255,255,255,.82)}
@media(max-width:760px){.stats-row{grid-template-columns:repeat(2,1fr)}}

/* 需求确认：在给方案之前，先把客户此刻的处境说出来 */
.need-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1.25rem;margin-top:var(--sp-1)}
.need-i{padding:1.35rem 1.5rem;border:1px solid var(--line);border-radius:var(--radius-lg);
  background:var(--paper-2);border-left:3px solid var(--signal)}
.need-i b{display:block;margin-bottom:.5rem;color:var(--ink);font-size:var(--step-1)}
.need-i p{color:var(--ink-70);margin:0}
.need-cta{margin-top:var(--sp-1)}
@media(max-width:860px){.need-grid{grid-template-columns:1fr}}

"""
assert st.count(ANCH) == 1
io.open(S, "w", encoding="utf-8").write(st.replace(ANCH, CSS + ANCH, 1))
print("  style.css：数字条与需求确认样式")
