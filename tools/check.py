#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发布前质量闸门 —— 推送前必须跑，任一项 FAIL 就不要推。

    python3 tools/check.py            # 全部检查
    python3 tools/check.py --quick    # 跳过浏览器渲染（快，但覆盖面小）

设计原则：检查那些「看起来没坏、其实已经坏了」的问题。
这些规则多数是踩过坑之后加的，注释里写了缘由。
"""
import glob, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
QUICK = "--quick" in sys.argv
FAILS, WARNS = [], []


def fail(tag, msg):
    FAILS.append(f"[{tag}] {msg}")


def warn(tag, msg):
    WARNS.append(f"[{tag}] {msg}")


PAGES = sorted(glob.glob("public/**/*.html", recursive=True))


# ---------- 1. 样式表体量突变 ----------
# 缘由：曾用字符串查找定位替换区间，锚点没匹配上导致 find 返回 -1，
# 从 .pcard--img 到文件末尾 512 行被整段删除，样式表 873→361 行，
# 导航下拉等 305 个选择器消失。行数突降是最早能发现它的信号。
def check_css_size():
    for name in ("style", "product", "manual"):
        f = f"public/{name}.css"
        if not os.path.exists(f):
            continue
        now = len(open(f, encoding="utf-8").read().splitlines())
        try:
            old_txt = subprocess.check_output(
                ["git", "show", f"HEAD:{f}"], text=True, stderr=subprocess.DEVNULL)
            old = len(old_txt.splitlines())
        except Exception:
            continue
        if old and now < old * 0.9:
            fail("CSS", f"{f} 行数 {old} → {now}，减少超过 10%，疑似被误删")
        elif old and now < old:
            warn("CSS", f"{f} 行数 {old} → {now}（减少 {old-now} 行，确认是有意删除）")


# ---------- 2. 关键样式类是否还在 ----------
# 缘由：同上。样式表被截断时，页面 HTML 完全正常，只有渲染是坏的。
def check_key_selectors():
    css = ""
    for f in glob.glob("public/*.css"):
        css += open(f, encoding="utf-8").read()
    must = ["site-header", "nav-drop-menu", "site-footer", "pcard", "pc-img",
            "case-grid", "ind-tag", "hero", "wrap", "btn", "func-grid", "burger"]
    missing = [m for m in must if m not in css]
    if missing:
        fail("CSS", f"关键样式类缺失：{missing}")


# ---------- 3. 死链与缺资源 ----------
def resolvable(u):
    u = u.split("?")[0]
    p = "public" + u
    if u.endswith("/"):
        return os.path.exists(p + "index.html")
    return (os.path.exists(p) or os.path.exists(p + ".html")
            or os.path.exists(p + "/index.html"))


def check_links():
    miss = {}
    for f in PAGES:
        h = open(f, encoding="utf-8").read()
        for u in re.findall(r'(?:src|href|poster)="(/[^"#]*)"', h):
            if not resolvable(u):
                miss.setdefault(u, []).append(f)
    if miss:
        for u, where in list(miss.items())[:8]:
            fail("链接", f"{u} 不存在（被 {len(where)} 页引用，如 {where[0]}）")


# ---------- 4. 标签配对与 JSON-LD ----------
def check_markup():
    for f in PAGES:
        h = open(f, encoding="utf-8").read()
        for t in ("html", "body", "head", "header", "footer", "main",
                  "nav", "section", "div", "article", "table", "video"):
            o = len(re.findall(r"<%s[\s>]" % t, h))
            c = len(re.findall(r"</%s>" % t, h))
            if o != c:
                fail("标签", f"{f} <{t}> 开 {o} 闭 {c}")
        for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S):
            try:
                json.loads(m)
            except Exception as e:
                fail("JSON-LD", f"{f} 解析失败：{str(e)[:50]}")


# ---------- 5. 越界内容（钥匙类绝不上公开页）----------
# 缘由：授权码、参数代码、带电检修属售后受控内容，见 SKILL.md 第六节红线。
def check_leak():
    BAD = ["3356", "8536", "8856", "pcac-tech", "崖鹰石", "万用表",
           "4A1", "U1RS", "15828128828"]
    P = re.compile(r"\bP(?:0\d|1\d|2\d|3\d|4\d)\b")
    for f in PAGES:
        h = open(f, encoding="utf-8").read()
        for w in BAD:
            if w in h:
                fail("越界", f"{f} 出现受控内容 {w!r}")
        for m in set(P.findall(h)):
            fail("越界", f"{f} 出现参数代码 P{m}")


# ---------- 6. 占位符与未完成痕迹 ----------
def check_placeholder():
    PAT = ["TODO", "FIXME", "lorem ipsum", "单击此处添加", "占位",
           "XXXX", "待补充", "undefined", "[object Object]"]
    for f in PAGES:
        h = open(f, encoding="utf-8").read()
        for w in PAT:
            if w.lower() in h.lower():
                warn("占位", f"{f} 含 {w!r}")


# ---------- 7. 三语一致性 ----------
def check_i18n():
    langs = {}
    for lang in ("zh", "en", "ru"):
        langs[lang] = {f[len(f"src/content/{lang}/"):]
                       for f in glob.glob(f"src/content/{lang}/**/*.html", recursive=True)}
    # 英文页残留中文（专有名词与型号允许）
    for f in glob.glob("public/en/**/*.html", recursive=True):
        h = open(f, encoding="utf-8").read()
        txt = re.sub(r"<[^>]+>", " ", h)
        cjk = len(re.findall(r"[\u4e00-\u9fff]", txt))
        if cjk > 60:
            warn("语种", f"{f} 含 {cjk} 个汉字，可能未翻译完")
    for f in glob.glob("public/ru/**/*.html", recursive=True):
        h = open(f, encoding="utf-8").read()
        body = h[h.find("<main"):h.find("</main>")] if "<main" in h else h
        txt = re.sub(r"<[^>]+>", " ", body)
        ru = len(re.findall(r"[А-Яа-яЁё]", txt))
        lat = len(re.findall(r"[A-Za-z]", txt))
        if ru + lat > 200 and ru / (ru + lat) < 0.9:
            warn("语种", f"{f} 俄语占比 {ru*100//(ru+lat)}%，低于发布线 90%")


# ---------- 8. SEO 资产完整 ----------
def check_seo():
    n = len([p for p in PAGES if not p.endswith("404.html")])
    canon = sum(1 for p in PAGES if 'rel="canonical"' in open(p, encoding="utf-8").read())
    if canon < n:
        fail("SEO", f"{n-canon} 页缺 canonical")
    sm = "public/sitemap.xml"
    if os.path.exists(sm):
        locs = len(re.findall(r"<loc>", open(sm, encoding="utf-8").read()))
        if locs < n:
            fail("SEO", f"sitemap 只有 {locs} 条，站内有 {n} 页")
    # 标题与描述
    for p in PAGES:
        h = open(p, encoding="utf-8").read()
        if "<title>" not in h:
            fail("SEO", f"{p} 缺 title")
        if 'name="description"' not in h and not p.endswith("404.html"):
            warn("SEO", f"{p} 缺 description")


# ---------- 9. 图片属性 ----------
def check_images():
    for p in PAGES:
        h = open(p, encoding="utf-8").read()
        for tag in re.findall(r"<img [^>]*>", h):
            if "alt=" not in tag:
                fail("图片", f"{p} 有 <img> 缺 alt：{tag[:60]}")
            if "width=" not in tag or "height=" not in tag:
                warn("图片", f"{p} 有 <img> 缺宽高（会造成布局跳动）：{tag[:60]}")


# ---------- 10. 部署体积上限 ----------
# 缘由：Cloudflare Workers 单文件上限 25MiB；一次性上传 212MB 曾导致构建失败。
def check_size():
    big = [(f, os.path.getsize(f)) for f in glob.glob("public/**/*", recursive=True)
           if os.path.isfile(f) and os.path.getsize(f) > 25 * 1024 * 1024]
    for f, s in big:
        fail("体积", f"{f} 为 {s/1048576:.1f}MB，超过 Cloudflare 单文件 25MiB 上限")
    total = sum(os.path.getsize(f) for f in glob.glob("public/**/*", recursive=True)
                if os.path.isfile(f))
    if total > 200 * 1024 * 1024:
        warn("体积", f"public/ 共 {total/1048576:.0f}MB，一次性部署过大可能超时")


# ---------- 11. 渲染实测 ----------
# 在渲染实测里顺带做的两项文字体检。缘由：
#  · 白字白底——首页透明头部那条规则把下拉面板里的链接也刷成白色，
#    面板是白底，于是整个语言菜单打开是空的；HTML 与 CSS 都"正常"，肉眼才看得出。
#  · 小字漏网——两轮批量放大用的正则要求 font-size 有前导零，写成 .9rem 的
#    16 处和写死 10/11px 的 3 处全部躲过去了。
# 所以这两项都量渲染后的计算样式，不靠正则、不靠人眼。
TEXT_PROBE = r"""() => {
  const out = {small: [], faint: []};
  const lum = (c) => {
    const f = (v) => { v /= 255; return v <= 0.03928 ? v/12.92 : Math.pow((v+0.055)/1.055, 2.4); };
    return 0.2126*f(c[0]) + 0.7152*f(c[1]) + 0.0722*f(c[2]);
  };
  const parse = (s) => {
    const m = s.match(/rgba?\(([^)]+)\)/); if (!m) return null;
    const p = m[1].split(',').map(x => parseFloat(x));
    return {rgb: [p[0], p[1], p[2]], a: p.length > 3 ? p[3] : 1};
  };
  const over = (fg, bg) => fg.rgb.map((v, i) => v*fg.a + bg[i]*(1-fg.a));
  // 背景取"这一点上真正压在文字底下的东西"：沿命中栈往下走，
  // 碰到图片/视频/背景图就判定为影像底——影像上的对比度算不出来，跳过不误报。
  const bgAt = (el, x, y) => {
    const stack = document.elementsFromPoint(x, y);
    const i = stack.indexOf(el);
    for (const n of (i >= 0 ? stack.slice(i) : [el])) {
      const cs = getComputedStyle(n);
      if (cs.backgroundImage && cs.backgroundImage !== 'none') return null;
      if (n.tagName === 'IMG' || n.tagName === 'VIDEO' || n.tagName === 'CANVAS' || n.tagName === 'SVG') return null;
      const c = parse(cs.backgroundColor);
      if (c && c.a > 0.55) return over(c, [255,255,255]);
    }
    return [255, 255, 255];
  };
  document.querySelectorAll('body *').forEach(el => {
    const txt = [...el.childNodes].filter(n => n.nodeType === 3)
      .map(n => n.textContent.trim()).join('');
    if (txt.length < 2) return;
    const r = el.getBoundingClientRect();
    if (r.width < 4 || r.height < 4) return;
    if (r.bottom < 0 || r.top > innerHeight) return;
    const cs = getComputedStyle(el);
    if (cs.visibility === 'hidden' || cs.display === 'none' || parseFloat(cs.opacity) < 0.15) return;
    const key = (el.className && typeof el.className === 'string'
      ? '.' + el.className.trim().split(/\s+/)[0] : el.tagName);
    const size = parseFloat(cs.fontSize);
    if (size < 14) out.small.push(key + ' ' + size.toFixed(1) + 'px「' + txt.slice(0, 12) + '」');
    // 描边字、渐变字另有着色方式，对比度算不准，跳过
    if (parseFloat(cs.webkitTextStrokeWidth || 0) > 0) return;
    if (cs.webkitBackgroundClip === 'text' || cs.backgroundClip === 'text') return;
    const bg = bgAt(el, Math.min(r.left + 6, innerWidth - 2), Math.min(r.top + r.height/2, innerHeight - 2));
    if (!bg) return;
    const fg = parse(cs.color); if (!fg) return;
    const f = over(fg, bg);
    const l1 = lum(f), l2 = lum(bg);
    const ratio = (Math.max(l1,l2)+0.05) / (Math.min(l1,l2)+0.05);
    if (ratio < 1.5) out.faint.push(key + ' 对比度 ' + ratio.toFixed(2) + '「' + txt.slice(0, 12) + '」');
  });
  out.small = [...new Set(out.small)].slice(0, 6);
  out.faint = [...new Set(out.faint)].slice(0, 6);
  return out;
}"""


def check_render():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        warn("渲染", "未安装 playwright，跳过渲染检查")
        return
    import time
    srv = subprocess.Popen(["python3", "-m", "http.server", "8912"],
                           cwd="public", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2.5)
    try:
        targets = ["/", "/en/", "/ru/", "/pipe/", "/cable/", "/cases.html", "/about.html"]
        with sync_playwright() as p:
            b = p.chromium.launch()
            for u in targets:
                for w in (430, 900, 1440):
                    pg = b.new_page(viewport={"width": w, "height": 800})
                    try:
                        pg.goto("http://localhost:8912" + u, wait_until="networkidle", timeout=15000)
                    except Exception:
                        fail("渲染", f"{u} 加载失败")
                        pg.close(); continue
                    if pg.evaluate("()=>document.documentElement.scrollWidth>window.innerWidth+2"):
                        fail("渲染", f"{u} 在 {w}px 横向溢出")
                    if w == 1440:
                        # 导航下拉必须默认隐藏——样式丢失时它会平铺出来
                        st = pg.evaluate("""()=>{const m=document.querySelector('.nav-drop-menu');
                            if(!m) return 'none';const c=getComputedStyle(m);
                            return c.position+'|'+c.opacity}""")
                        if st != "none" and not st.startswith("absolute"):
                            fail("渲染", f"{u} 导航下拉未正确定位（{st}），样式可能丢失")

                        # 下拉面板要展开着量，否则白字白底藏在 opacity:0 里量不到
                        pg.evaluate("""()=>{const s=document.createElement('style');
                            s.textContent='.nav-drop-menu{opacity:1!important;visibility:visible!important;'
                              +'pointer-events:auto!important;transform:none!important}';
                            document.head.appendChild(s);}""")
                        probe = pg.evaluate(TEXT_PROBE)
                        for it in probe["small"]:
                            fail("字号", f"{u} {it} —— 低于 14px 下限")
                        for it in probe["faint"]:
                            fail("对比度", f"{u} {it} —— 低于 1.5，可能是同色压同色")
                        broken = pg.evaluate("""()=>[...document.querySelectorAll('img')]
                            .filter(i=>i.getAttribute('src')&&i.complete&&i.naturalWidth===0).length""")
                        if broken:
                            fail("渲染", f"{u} 有 {broken} 张图片加载失败")
                    pg.close()
            b.close()
    finally:
        srv.terminate()


# ---------- 12. 脚本钩子 ----------
# 缘由：2026-07-30 发现首页 4 个「问技术工程师」按钮点了完全没反应。
# app.js 是 IIFE，第 5-6 行 querySelector('[data-ai]') 取不到就 return，
# 而给 [data-open-ai] 绑 click 的代码在第 30 行——组件根节点被移除后，
# 按钮永远拿不到事件处理器。HTML 正常、CSS 正常、控制台无报错，只有功能是死的。
# 这类"静默失效"必须由闸门拦，不能靠人点。
JS_HOOKS = [
    # (页面里出现这个触发器, 就必须同页存在这个组件根节点, 说明)
    ("data-open-ai", "data-ai", "咨询按钮没有对应的咨询组件"),
    ("data-lightbox", "data-lightbox", "灯箱触发器"),
    ("data-back-to-top", "data-back-to-top", "回顶按钮"),
]


def check_js_hooks():
    for f in PAGES:
        s = open(f, encoding="utf-8").read()
        for trigger, need, desc in JS_HOOKS:
            if trigger in s and need not in s:
                fail("脚本钩子", f"{f}：{desc}——有 {trigger} 但缺 {need}，交互会静默失效")
    # 反向：加载了 app.js 却没有组件，说明是一次没收尾的移除
    for f in PAGES:
        s = open(f, encoding="utf-8").read()
        if "assets/app.js" in s and "data-ai" not in s:
            fail("脚本钩子", f"{f} 加载了 app.js 但页面没有 [data-ai]，脚本会空跑")


def check_h1():
    """每页必须有 h1。今天发现 about / cases / news / service 一直没有——
       拆栏目时新页也漏了，说明这条只能靠闸门守，不能靠人记。"""
    for f in PAGES:
        s = open(f, encoding="utf-8").read()
        if "<h1" not in s:
            fail("结构", f"{f} 没有 h1")


def main():
    print("发布前自检 —— public/ 共", len(PAGES), "页\n")
    checks = [
        ("样式表体量", check_css_size), ("关键样式类", check_key_selectors),
        ("死链与缺资源", check_links), ("标签与结构化数据", check_markup),
        ("受控内容越界", check_leak), ("占位符", check_placeholder),
        ("三语一致性", check_i18n), ("SEO 资产", check_seo),
        ("图片属性", check_images), ("部署体积", check_size),
        ("脚本钩子", check_js_hooks),
        ("页面结构", check_h1),
    ]
    if not QUICK:
        checks.append(("渲染实测", check_render))
    for name, fn in checks:
        n0, w0 = len(FAILS), len(WARNS)
        fn()
        d_f, d_w = len(FAILS) - n0, len(WARNS) - w0
        mark = "✗" if d_f else ("!" if d_w else "✓")
        extra = f"  {d_f} 项不通过" if d_f else (f"  {d_w} 项提醒" if d_w else "")
        print(f"  {mark} {name}{extra}")

    if WARNS:
        print(f"\n提醒 {len(WARNS)} 条（不阻断发布）：")
        for w in WARNS[:12]:
            print("   ·", w)
        if len(WARNS) > 12:
            print(f"   … 另有 {len(WARNS)-12} 条")
    if FAILS:
        print(f"\n不通过 {len(FAILS)} 条 —— 请勿推送：")
        for f in FAILS[:20]:
            print("   ✗", f)
        if len(FAILS) > 20:
            print(f"   … 另有 {len(FAILS)-20} 条")
        sys.exit(1)
    print("\n全部通过，可以推送。")


if __name__ == "__main__":
    main()
