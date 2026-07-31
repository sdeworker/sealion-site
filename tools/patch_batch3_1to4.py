# -*- coding: utf-8 -*-
"""规范 v2.1 第三批 1–4 项

1  @media print 打印样式（产品页/案例页/ROI 都能干净打出来）
2  首页视频 preload:auto → metadata，移动端不下载视频只留封面
3  ROI 计算器补状态：初始/空值/无效/超范围 + aria-live + 假设条件
4  长产品页与手册页开启返回页首（每页元数据一行）
"""
import io, json, re, sys, glob, os

# ── 1. 打印样式 ─────────────────────────────────────────────
PRINT_CSS = """/* 打印与内部转发
   客户把页面打出来带进采购会或技术评审，导航、视频、浮动按钮都是噪音；
   折叠起来的参数表必须展开，表格不能跨页截断，页脚要留下网址与日期。 */
@media print {
  :root { --wrap: 100%; }
  html, body { background: #fff !important; color: #000 !important; font-size: 11.5pt; }

  /* 屏幕上的功能件，纸上没有意义 */
  .site-header, .topbar, .nav, .burger, .site-footer nav, .back-to-top,
  .hero-video, video, .hero-play, .ai-launcher, .langlink, .nav-lang,
  .lightbox, .hero-lb, .m-toc, .skip-link, .hero-lines { display: none !important; }

  /* 深色区反白，避免整页吃墨 */
  .on-dark, .hero, .section--dark, .readout, .calc-out, .prod-foot-cta {
    background: #fff !important; color: #000 !important; box-shadow: none !important;
  }
  .on-dark *, .hero *, .readout *, .calc-out * { color: #000 !important; }

  /* 折叠内容一律展开——纸上没有"点开" */
  details { display: block !important; }
  details > summary { font-weight: 600; list-style: none; }
  details:not([open]) > *:not(summary) { display: revert !important; }
  [hidden] { display: revert !important; }
  .is-collapsed, .collapsed { max-height: none !important; overflow: visible !important; }

  /* 分页 */
  h1, h2, h3, h4 { break-after: avoid-page; page-break-after: avoid; }
  table, figure, .pcard, .c-card, .apy-item, .calc-grid { break-inside: avoid; page-break-inside: avoid; }
  thead { display: table-header-group; }
  tfoot { display: table-footer-group; }
  tr { break-inside: avoid; }

  /* 版面 */
  .wrap { max-width: 100% !important; padding-inline: 0 !important; }
  .section { padding-block: 12pt !important; }
  a { color: #000 !important; text-decoration: none !important; }
  /* 正文里的外链把地址打出来，纸上才追得到 */
  .prose a[href^="http"]::after, .apy-body a[href^="http"]::after { content: " (" attr(href) ")"; font-size: 9pt; }
  img { max-width: 100% !important; }

  /* 出处：网址 + 打印日期，由 print.js 填 */
  .print-stamp { display: block !important; margin-top: 14pt; padding-top: 6pt;
    border-top: 1pt solid #999; font-size: 9pt; color: #333; }
}
.print-stamp { display: none; }
"""
io.open("public/print.css", "w", encoding="utf-8").write(PRINT_CSS)
print("已写 public/print.css")

io.open("public/assets/print.js", "w", encoding="utf-8").write(
    """/* 打印时在页脚盖一个出处戳：网址 + 日期。零依赖。 */
(function () {
  var el = document.querySelector('[data-print-stamp]');
  if (!el) return;
  function stamp() {
    var d = new Date();
    el.textContent = location.href + '　·　' + d.getFullYear() + '-' +
      String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
  }
  stamp();
  window.addEventListener('beforeprint', stamp);
})();
""")
print("已写 public/assets/print.js")

b = io.open("tools/build.py", encoding="utf-8").read()

# print.css 全站引入（media=print，不影响屏幕渲染，也不阻塞首屏）
OLD_CSS = '''    skip = t(SITE["ui"]["skip"], lang)'''
NEW_CSS = '''    skip = t(SITE["ui"]["skip"], lang)
    print_css = f'<link rel="stylesheet" href="{ver("/print.css")}" media="print">'
    print_stamp = '<p class="print-stamp" data-print-stamp></p>'''
assert b.count(OLD_CSS) == 1
b = b.replace(OLD_CSS, NEW_CSS, 1)

# 挂进 head 与页脚
OLD_HEADCSS = '<link rel="stylesheet" href="{ver("/style.css")}">'
assert b.count(OLD_HEADCSS) == 1, "style.css 引入锚点对不上"
b = b.replace(OLD_HEADCSS, OLD_HEADCSS + '{print_css}', 1)

OLD_TAILJS = '''    tail = ['<script>document.getElementById(\\'yr\\').textContent=new Date().getFullYear();</script>','''
NEW_TAILJS = '''    tail = [print_stamp,
            f'<script src="{ver("/assets/print.js")}" defer></script>',
            '<script>document.getElementById(\\'yr\\').textContent=new Date().getFullYear();</script>','''
assert b.count(OLD_TAILJS) == 1
b = b.replace(OLD_TAILJS, NEW_TAILJS, 1)
io.open("tools/build.py", "w", encoding="utf-8").write(b)
print("build.py 已引入 print.css 与出处戳")

# ── 2. 首页视频首访负载 ─────────────────────────────────────
for lg in ("zh", "en", "ru"):
    p = f"src/content/{lg}/index.html"
    if not os.path.exists(p):
        continue
    s = io.open(p, encoding="utf-8").read()
    if 'preload="auto"' not in s:
        continue
    s = s.replace('preload="auto"', 'preload="metadata"', 1)
    io.open(p, "w", encoding="utf-8").write(s)
    print(f"{p}：preload auto → metadata")

S = "public/style.css"
st = io.open(S, encoding="utf-8").read()
ANCH = "/* a11y + motion */"
MOBILE = """/* 手机上不下载 13MB 的背景视频，只留封面图。
   preload 已改 metadata，但 autoplay 仍会拉全片——移动流量上不划算。 */
@media(max-width:760px){
  .hero-video video{display:none}
  .hero-video{background-image:url('/assets/2026/video/company-intro-poster.webp');
    background-size:cover;background-position:center}
}

"""
assert st.count(ANCH) == 1
st = st.replace(ANCH, MOBILE + ANCH, 1)
io.open(S, "w", encoding="utf-8").write(st)
print("style.css：移动端改用封面图")

# ── 3. ROI 计算器状态 ───────────────────────────────────────
p = "src/content/zh/index.html"
s = io.open(p, encoding="utf-8").read()

OLD_OUT = '<div class="calc-out">'
NEW_OUT = '<div class="calc-out" aria-live="polite">'
assert s.count(OLD_OUT) == 1
s = s.replace(OLD_OUT, NEW_OUT, 1)

OLD_CTA = '          <a class="btn btn--primary calc-cta" href="/#contact">让工程师按我的产线算一遍</a>'
NEW_CTA = ('          <p class="calc-state" id="c-state">填入上面三项，按 2% 与 5% 两档估算每年省下的原料钱。</p>\n'
           + OLD_CTA)
assert s.count(OLD_CTA) == 1
s = s.replace(OLD_CTA, NEW_CTA, 1)

OLD_NOTE = '<p class="calc-note">测算依据：'
NEW_NOTE = ('<p class="calc-note"><b>假设条件</b>：按 2% 与 5% 两档估算；只算主料，不含安装、培训与停机损失；'
            '原料按到厂价计；年运行小时按你填的数字直接相乘。<br>测算依据：')
assert s.count(OLD_NOTE) == 1
s = s.replace(OLD_NOTE, NEW_NOTE, 1)

OLD_JS = """    function n(id){var v=parseFloat(document.getElementById('c-'+id).value);return isFinite(v)&&v>0?v:0;}"""
NEW_JS = """    var LIMIT={out:20000,price:200,hours:8760};   // 明显越界的上限，用于提醒而非阻断
    function raw(id){return document.getElementById('c-'+id).value.trim();}
    function n(id){var v=parseFloat(raw(id));return isFinite(v)&&v>0?v:0;}
    function state(){
      var el=document.getElementById('c-state'); if(!el) return;
      var empty=['out','price','hours'].filter(function(k){return raw(k)==='';});
      var bad=['out','price','hours'].filter(function(k){var v=parseFloat(raw(k));
        return raw(k)!=='' && (!isFinite(v)||v<=0);});
      var over=['out','price','hours'].filter(function(k){return n(k)>LIMIT[k];});
      var L={out:'挤出量',price:'原料单价',hours:'年运行小时'};
      var msg='', cls='calc-state';
      if(bad.length){msg='「'+bad.map(function(k){return L[k]}).join('、')+'」请填大于 0 的数字。';cls+=' calc-state--warn';}
      else if(empty.length){msg='还差「'+empty.map(function(k){return L[k]}).join('、')+'」没填。';}
      else if(over.length){msg='「'+over.map(function(k){return L[k]}).join('、')+'」看起来偏离常见区间，结果仍按你填的数字算。';cls+=' calc-state--warn';}
      else {msg='按 2% 与 5% 两档估算；只算主料，不含安装、培训与停机损失。';}
      el.textContent=msg; el.className=cls;
    }"""
assert s.count(OLD_JS) == 1
s = s.replace(OLD_JS, NEW_JS, 1)

OLD_CALL = """      document.getElementById('c-hit').textContent=kg?(kg*0.05/1000).toFixed(1):'—';
    }"""
NEW_CALL = """      document.getElementById('c-hit').textContent=kg?(kg*0.05/1000).toFixed(1):'—';
      state();
    }"""
assert s.count(OLD_CALL) == 1
s = s.replace(OLD_CALL, NEW_CALL, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("ROI 计算器：aria-live + 四种状态 + 假设条件")

st = io.open(S, encoding="utf-8").read()
CALCCSS = """.calc-state{margin:.6rem 0 .9rem;font-size:1rem;line-height:1.5;color:var(--steel-dk)}
.calc-state--warn{color:var(--signal)}

"""
st = st.replace(ANCH, CALCCSS + ANCH, 1)
io.open(S, "w", encoding="utf-8").write(st)
print("style.css：计算器状态文案样式")

# ── 4. 长页面开启返回页首 ───────────────────────────────────
n = 0
for f in glob.glob("src/content/*/pipe/*.html") + glob.glob("src/content/*/cable/*.html") \
        + glob.glob("src/content/*/manual/*.html"):
    if f.endswith("/index.html"):
        continue          # 事业部目录页不长，不必加
    s = io.open(f, encoding="utf-8").read()
    head, sep, body = s.partition("\n---\n")
    if not sep:
        continue
    meta = json.loads(head)
    if meta.get("backToTop"):
        continue
    meta["backToTop"] = True
    io.open(f, "w", encoding="utf-8").write(
        json.dumps(meta, ensure_ascii=False, indent=1) + sep + body)
    n += 1
print(f"已为 {n} 个长页面开启返回页首")
