# -*- coding: utf-8 -*-
"""首页做成「粒子—波—场」样板

按用户给定的三组坐标：
  粒子＝整体性、稳定性、独立性
  波  ＝轨迹、速度、粘度
  场  ＝连接、次序、结构

改动分三类：
  场·次序   首页排成「问题→选择→方案→证据→人→行动」六段，
            并把断掉的连接接上（案例、客户、服务在拆分后都从首页消失了，
            只剩导航能到——首页现在没有一处通往证据与人）
  场·结构   打破全站等宽等高的网格：现场大图与数据卡并排、
            浅色区与深色区交替、局部不对称
  波·速度   信息密度分快慢：证据段慢、选择段快
  粒子·整体性 首页第一次出现人——工程师与服务，冷设备参数之外的另一半
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


# ── 第四段：证据（现场 + 客户）──────────────────────────────
PROOF = {
    "zh": '''  <section data-reveal class="section proof-band">
    <div class="wrap">
      <div class="pb-grid">
        <figure class="pb-media">
          <img src="/assets/cases/sealion-gravimetric-coextrusion-hd.jpg"
               alt="三共挤米重控制系统装在客户产线上" loading="lazy" width="1200" height="800">
          <figcaption>三共挤产线上的米重控制系统 · 客户车间实拍</figcaption>
        </figure>
        <div class="pb-body">
          <span class="eyebrow">装在真实产线上</span>
          <h2>不是展台上的样机</h2>
          <p class="lead">26 组现场记录，6 组带产线运行视频。机器在客户车间里跑着，
            报警灯亮着，屏幕上是当班的实时数据。</p>
          <ul class="pb-list">
            <li><b>18 家</b>长期合作客户，从管道到电缆、从改性料到检测</li>
            <li><b>60 项</b>知识产权，权利人都是海狮自己</li>
            <li><b>2%–5%</b>原料节省，这是客户产线上算出来的区间</li>
          </ul>
          <p class="pb-cta">
            <a class="btn btn--primary" href="/cases.html">看现场记录</a>
            <a class="arrow-link" href="/about/partners.html">他们的产线上装着海狮 &rarr;</a>
          </p>
        </div>
      </div>
    </div>
  </section>

''',
    "en": '''  <section data-reveal class="section proof-band">
    <div class="wrap">
      <div class="pb-grid">
        <figure class="pb-media">
          <img src="/assets/cases/sealion-gravimetric-coextrusion-hd.jpg"
               alt="Gravimetric control on a three-layer coextrusion line" loading="lazy" width="1200" height="800">
          <figcaption>Gravimetric control on a coextrusion line, photographed on site</figcaption>
        </figure>
        <div class="pb-body">
          <span class="eyebrow">On working lines</span>
          <h2>Not a machine on a stand</h2>
          <p class="lead">Twenty-six site records, six of them with footage of the line running.
            The equipment is in a customer's workshop with the shift's own figures on the screen.</p>
          <ul class="pb-list">
            <li><b>18</b> long-term customers, from pipe and cable to compounds and inspection</li>
            <li><b>60</b> patents and copyrights, all held by Sealion</li>
            <li><b>2%&ndash;5%</b> material saved &mdash; a range measured on customers' lines</li>
          </ul>
          <p class="pb-cta">
            <a class="btn btn--primary" href="/en/cases.html">See the site records</a>
            <a class="arrow-link" href="/en/about/partners.html">Who runs Sealion &rarr;</a>
          </p>
        </div>
      </div>
    </div>
  </section>

''',
}

# ── 第五段：人与服务 ────────────────────────────────────────
PEOPLE = {
    "zh": '''  <section data-reveal class="section people on-dark">
    <div class="wrap">
      <div class="sh">
        <span class="eyebrow">装上线，才是开始</span>
        <h2>设备背后是一队人</h2>
        <p class="lead">系统装在产线上会跑很多年。这些年里换过料、换过班、换过工艺，
          真正要一直在的是能接电话、能到现场、能远程接上来看一眼的人。</p>
      </div>
      <div class="ppl-grid">
        <figure class="ppl-i ppl-i--wide">
          <img src="/assets/service/onsite.jpg" alt="工程师在客户现场安装调试"
               loading="lazy" width="550" height="310">
          <figcaption><b>现场安装与调试</b>到产线上装、调、试到出合格品，不是发货了事</figcaption>
        </figure>
        <figure class="ppl-i">
          <img src="/assets/service/training.jpg" alt="操作与维护培训"
               loading="lazy" width="550" height="310">
          <figcaption><b>操作与维护培训</b>把机器交给会用的人</figcaption>
        </figure>
        <figure class="ppl-i">
          <img src="/assets/service/team.jpg" alt="售后服务团队"
               loading="lazy" width="550" height="310">
          <figcaption><b>售后与备件</b>老机型同样有件可换</figcaption>
        </figure>
      </div>
      <p class="ppl-cta"><a class="arrow-link" href="/service.html">售后与服务怎么安排 &rarr;</a></p>
    </div>
  </section>

''',
    "en": '''  <section data-reveal class="section people on-dark">
    <div class="wrap">
      <div class="sh">
        <span class="eyebrow">Commissioning is the start</span>
        <h2>There are people behind the equipment</h2>
        <p class="lead">A system stays on the line for years. Over those years the material
          changes, the shift changes, the process changes &mdash; what has to stay is someone
          who answers the phone, comes to the site, and can dial in and look.</p>
      </div>
      <div class="ppl-grid">
        <figure class="ppl-i ppl-i--wide">
          <img src="/assets/service/onsite.jpg" alt="Engineers commissioning on site"
               loading="lazy" width="550" height="310">
          <figcaption><b>Installation and commissioning</b> on the line, through to good product &mdash; not shipped and forgotten</figcaption>
        </figure>
        <figure class="ppl-i">
          <img src="/assets/service/training.jpg" alt="Operator training"
               loading="lazy" width="550" height="310">
          <figcaption><b>Operator training</b> handing the machine to people who can run it</figcaption>
        </figure>
        <figure class="ppl-i">
          <img src="/assets/service/team.jpg" alt="Service team"
               loading="lazy" width="550" height="310">
          <figcaption><b>Service and spares</b> older models still have parts</figcaption>
        </figure>
      </div>
      <p class="ppl-cta"><a class="arrow-link" href="/en/service.html">How service is arranged &rarr;</a></p>
    </div>
  </section>

''',
}

# ── 第六段：行动号召 ────────────────────────────────────────
CTA = {
    "zh": '''  <section data-reveal class="section endcta">
    <div class="wrap narrow">
      <span class="eyebrow">下一步</span>
      <h2>把四个数发给我们</h2>
      <p class="lead">口径、材料、产量、线速——这四项定了，工程师就能按你的产线给出配置建议，
        以及还需要现场确认哪几项。</p>
      <p class="endcta-act">
        <a class="btn btn--primary" href="mailto:2428582102@qq.com?subject=%E4%BA%A7%E7%BA%BF%E5%8F%82%E6%95%B0%E5%92%A8%E8%AF%A2">发四个数给工程师</a>
        <a class="btn" href="tel:+8640084040800">打 4008-4040-80</a>
      </p>
      <p class="endcta-note">也可以先看 <a href="/manual/">产品手册</a>，
        或按行业挑：<a href="/industries/">十二个应用行业</a>。</p>
    </div>
  </section>

''',
    "en": '''  <section data-reveal class="section endcta">
    <div class="wrap narrow">
      <span class="eyebrow">Next</span>
      <h2>Send us four numbers</h2>
      <p class="lead">Diameter, material, output and line speed. With those four an engineer can
        propose a configuration for your line, and say which points still need confirming on site.</p>
      <p class="endcta-act">
        <a class="btn btn--primary" href="mailto:2428582102@qq.com?subject=Line%20parameter%20enquiry">Send the four numbers</a>
        <a class="btn" href="tel:+8640084040800">Call 4008-4040-80</a>
      </p>
      <p class="endcta-note">Or start with the <a href="/en/manual/">product manual</a>,
        or pick by <a href="/en/industries/">industry</a>.</p>
    </div>
  </section>

''',
}


def cut(body, sid):
    m = re.search(r'<section[^>]*\bid="%s"[^>]*>' % re.escape(sid), body)
    if not m:
        return None, body
    st = m.start()
    depth = 0
    end = None
    for mm in re.finditer(r"</?section\b", body[st:]):
        depth += 1 if mm.group(0) == "<section" else -1
        if depth == 0:
            end = st + mm.end()
            break
    while end < len(body) and body[end] in ">\n":
        end += 1
    return body[st:end], body[:st] + body[end:]


for lang in ("zh", "en"):
    p = os.path.join(ROOT, "src", "content", lang, "index.html")
    meta, body = load(p)
    if "proof-band" in body:
        print(f"  {lang} 已改过，跳过")
        continue
    # 取出五节，按新次序重排
    parts = {}
    for sid in ("stats", "need", "divisions", "products", "calc"):
        blk, body = cut(body, sid)
        parts[sid] = blk or ""
    # 六段：问题 → 数字 → 选择 → 方案 → 证据 → 人 → 行动
    body = (body.rstrip() + "\n\n"
            + parts["need"]          # ① 问题：慢
            + parts["stats"]         # ② 可核数字：快
            + parts["divisions"]     # ③ 选择：快
            + parts["products"]      # ④ 方案
            + parts["calc"]          # ⑤ 价值：慢
            + PROOF[lang]            # ⑥ 证据：慢
            + PEOPLE[lang]           # ⑦ 人
            + CTA[lang])             # ⑧ 行动
    meta.setdefault("js", [])
    if "motion" not in meta["js"]:
        meta["js"].append("motion")
    save(p, meta, body)
    print(f"  {lang} 首页重排为八段，新增 证据 / 人 / 行动号召 三段")

# ── CSS ────────────────────────────────────────────────────
S = os.path.join(ROOT, "public", "style.css")
st = io.open(S, encoding="utf-8").read()
A = "/* a11y + motion */"
CSS = """/* ============ 首页：场·结构 ============ */
/* 打破全站等宽等高的网格。此前每一节都是同宽同高的卡片阵列，
   规整得像一张表格——粒子的稳定性做满了，场的结构却做死了。
   这里让大幅现场照与数据并排、宽窄不等，局部不对称。 */
.proof-band{background:var(--paper-2)}
.pb-grid{display:grid;grid-template-columns:1.15fr .85fr;gap:clamp(1.5rem,3vw,3rem);
  align-items:center}
.pb-media{margin:0;position:relative;border-radius:var(--radius-lg);overflow:hidden;
  box-shadow:0 24px 64px rgba(10,26,38,.18)}
.pb-media img{display:block;width:100%;height:auto}
.pb-media figcaption{position:absolute;left:0;right:0;bottom:0;padding:2.4rem 1.25rem .9rem;
  color:#fff;font-size:1rem;
  background:linear-gradient(180deg,transparent,rgba(10,26,38,.82))}
.pb-list{list-style:none;padding:0;margin:var(--sp-1) 0}
.pb-list li{padding:.55rem 0 .55rem 1.1rem;border-left:2px solid var(--line);color:var(--ink-70)}
.pb-list b{color:var(--blue);font-family:var(--mono);font-size:1.28em;margin-right:.4em}
.pb-cta{display:flex;flex-wrap:wrap;align-items:center;gap:1.25rem;margin-top:var(--sp-1)}
@media(max-width:900px){.pb-grid{grid-template-columns:1fr}}

/* 人与服务：首页第一次出现人。三张不等宽，第一张跨两列。 */
.people{background:var(--ink)}
.ppl-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:1.25rem;margin-top:var(--sp-1)}
.ppl-i{margin:0;border-radius:var(--radius-lg);overflow:hidden;background:var(--panel);
  display:flex;flex-direction:column}
.ppl-i--wide{grid-row:span 2}
.ppl-i img{display:block;width:100%;height:100%;object-fit:cover;flex:1;min-height:180px}
.ppl-i--wide img{min-height:400px}
.ppl-i figcaption{padding:1rem 1.15rem;color:rgba(255,255,255,.82);font-size:1rem;line-height:1.5}
.ppl-i figcaption b{display:block;color:#fff;font-size:1.14em;margin-bottom:.25rem}
.ppl-cta{margin-top:var(--sp-1)}
.people .arrow-link{color:var(--signal)}
@media(max-width:900px){.ppl-grid{grid-template-columns:1fr}.ppl-i--wide{grid-row:auto}
  .ppl-i--wide img{min-height:220px}}

/* 收尾的行动号召 */
.endcta{background:var(--paper-2);text-align:center;border-top:1px solid var(--line)}
.endcta .lead{margin-inline:auto}
.endcta-act{display:flex;flex-wrap:wrap;justify-content:center;gap:1rem;margin-top:var(--sp-1)}
.endcta-note{margin-top:1rem;color:var(--steel)}
.endcta-note a{color:var(--blue);border-bottom:1px solid transparent}
.endcta-note a:hover{border-bottom-color:var(--blue)}

"""
assert st.count(A) == 1
io.open(S, "w", encoding="utf-8").write(st.replace(A, CSS + A, 1))
print("  style.css：证据带 / 人与服务 / 收尾号召")
