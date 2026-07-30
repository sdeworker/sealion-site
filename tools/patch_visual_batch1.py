# -*- coding: utf-8 -*-
"""视觉与排版规范第一批落地 —— 依据《海狮官网视觉与排版规范_双AI合稿权威终版》
   §6 字体系统（无争议部分）· §7 字号层级 · §8 颜色治理 · §9 圆角 · §10 组件 · §12 中文排印
   每条改动都用 assert 锚定命中次数，任何一条对不上就整体中止，不留半成品。
"""
import sys

EDITS = []


def edit(path, old, new, n=1, why=""):
    EDITS.append((path, old, new, n, why))


S = "public/style.css"
P = "public/product.css"
B = "tools/build.py"

# ── §6 字体：删掉从未加载的 Space Grotesk，写死中文兜底链 ──────────────
edit(S,
     '  --display:"Space Grotesk","Noto Sans SC",sans-serif;\n'
     '  --body:"Inter","Noto Sans SC",system-ui,sans-serif;',
     '  /* 三语站不引拉丁展示字体：汉字用不了它，双语标题会两套字形并排。\n'
     '     层级靠字号与字重拉开，仪表感由 --mono 的数值与刻度承担。 */\n'
     '  --display:"Inter","Noto Sans SC","PingFang SC","Microsoft YaHei",sans-serif;\n'
     '  --body:"Inter","Noto Sans SC","PingFang SC","Microsoft YaHei","Hiragino Sans GB",system-ui,sans-serif;',
     why="删 Space Grotesk（声明了但从未加载），并写死中文兜底链")

edit(B,
     'family=Barlow+Semi+Condensed:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500'
     '&family=Inter:wght@400;500;600&family=Noto+Sans+SC:wght@300;400;500;700',
     'family=IBM+Plex+Mono:wght@400;500'
     '&family=Inter:wght@400;500;600;700&family=Noto+Sans+SC:wght@400;500;600;700',
     why="删全站零引用的 Barlow；补 Noto Sans SC 600（标题要求 600 但从未加载）；删无人用的 300")

# ── §7 字号层级：把"普遍 48px"的二级标题降到 36–40px，建立次级三档 ──────
edit(S, '  --step-2:clamp(1.5rem,1.3rem + 1vw,2rem);',
        '  --step-2:clamp(1.25rem,1.15rem + 0.7vw,1.75rem);',
     why="子章节 H3：24–28px（原 24–32）")
edit(S, '  --step-3:clamp(2rem,1.6rem + 2vw,3rem);',
        '  --step-3:clamp(1.75rem,1.5rem + 1.2vw,2.5rem);',
     why="章节 H2：桌面 40px / 平板 33px / 手机 29px（原封顶 48px）")
edit(S, '  --step-4:clamp(2.5rem,1.85rem + 3.3vw,4.3rem);',
        '  --step-4:clamp(2.25rem,1.75rem + 2.6vw,3.75rem);',
     why="Hero H1：桌面 60px（原实测 68.8px，且在 533px 窄栏里换行难看）")

# ── §7 + §12 标题排印：行高分档、汉字去负字距 ────────────────────────
edit(S,
     'h1,h2,h3,h4{font-family:var(--display);line-height:1.1;font-weight:600;letter-spacing:-0.01em}',
     'h1,h2,h3,h4{font-family:var(--display);line-height:1.25;font-weight:600;letter-spacing:0}\n'
     'h1{line-height:1.12}h2{line-height:1.2}h3{line-height:1.35}h4{line-height:1.4}\n'
     '/* 负字距是拉丁排印习惯（补大写字母间的空档）；汉字方块本就贴满字身框，'
     '再收就是往一起挤。只给拉丁语种加回去。 */\n'
     ':lang(en) h1,:lang(en) h2,:lang(en) h3,:lang(en) h4{letter-spacing:-0.01em}',
     why="中文标题行高 1.1→按级 1.12/1.2/1.35/1.4；负字距只留给英文")

edit(S, '.hero-copy h1{font-size:var(--step-4);letter-spacing:-0.02em;',
        '.hero-copy h1{font-size:var(--step-4);letter-spacing:0;',
     why="Hero 中文大标题去负字距")
edit(S, '.pcard h3{font-size:var(--step-1);letter-spacing:-0.01em}',
        '.pcard h3{font-size:var(--step-1);letter-spacing:0}',
     why="卡片标题去负字距")

# ── §10 产品卡标题降到 20–22px（原 24–32px，在方卡里折三行吃掉半张）────
edit(S,
     '.pcard--img .pc-body h3{color:#fff;font-size:var(--step-2);line-height:1.22;',
     '.pcard--img .pc-body h3{color:#fff;font-size:var(--step-1);line-height:1.3;',
     why="事业部卡片标题 20–22px")

# ── §12 眉题：中文串套等宽字族会一行两套字，分隔符与空格来自 mono ─────
edit(S,
     '.eyebrow{font-family:var(--mono);font-size:var(--step--1);letter-spacing:0.14em;'
     'text-transform:uppercase;color:var(--blue);font-weight:500;',
     '.eyebrow{font-family:var(--body);font-size:var(--step--1);letter-spacing:0.08em;'
     'color:var(--blue);font-weight:500;',
     why="眉题改正文字族、字距 0.14em→0.08em、去掉对汉字无效的 uppercase")
edit(S, '.arrow-link{font-family:var(--mono);', '.arrow-link{font-family:var(--body);',
     why='「了解详情」这类中文行动链接不走等宽')

# ── §12 中文标签下限 12px：Hero 读数器的「壁厚」「每米克重」原为 10.24px ──
edit(S,
     '.rv-cap{flex-basis:100%;font-family:var(--mono);font-size:0.64rem;letter-spacing:0.1em;'
     'text-transform:uppercase;color:var(--steel-dk);',
     '.rv-cap{flex-basis:100%;font-family:var(--body);font-size:0.75rem;letter-spacing:0.06em;'
     'color:var(--steel-dk);',
     why="10.24px → 12px，改正文字族，去 uppercase")

# ── §10 按钮：三种高度（68/68/43px）统一到 48px，中文 CTA 不走等宽 ────
edit(S,
     '.btn{--bg:var(--ink);--fg:#fff;--bd:var(--ink);display:inline-flex;align-items:center;'
     'gap:0.55em;font-family:var(--mono);font-size:var(--step--1);letter-spacing:0.03em;'
     'padding:0.85em 1.4em;',
     '.btn{--bg:var(--ink);--fg:#fff;--bd:var(--ink);display:inline-flex;align-items:center;'
     'justify-content:center;gap:0.55em;font-family:var(--body);font-size:0.9375rem;'
     'font-weight:500;letter-spacing:0.02em;line-height:1.2;min-height:48px;padding:0 1.4em;',
     why="按钮统一 48px 高、15px/500、改正文字族（中文 CTA 的等宽技术感生硬且依赖回退）")

edit(S,
     '.hero-play{display:inline-flex;align-items:center;gap:.55em;margin-top:1.6rem;padding:.7em 1.2em;\n'
     '  background:rgba(255,255,255,.10);border:1px solid rgba(255,255,255,.30);color:#fff;\n'
     '  border-radius:999px;cursor:pointer;font-size:var(--step--1);transition:background .2s,border-color .2s}\n'
     '.hero-play:hover{background:rgba(255,255,255,.18);border-color:rgba(255,255,255,.55)}',
     '/* 第三动作降级为同高文字按钮：一屏只留一个主按钮，不做第三种高度与第三种形状。 */\n'
     '.hero-play{display:inline-flex;align-items:center;gap:.5em;margin-top:1.2rem;\n'
     '  min-height:48px;padding:0;background:none;border:0;color:rgba(255,255,255,.88);\n'
     '  cursor:pointer;font-family:var(--body);font-size:0.9375rem;font-weight:500;\n'
     '  letter-spacing:0.02em;transition:color .2s}\n'
     '.hero-play:hover{color:#fff;text-decoration:underline;text-underline-offset:4px}',
     why="视频按钮 43px 胶囊 → 48px 同高文字按钮")

# ── §9 圆角三档：控件 6px、卡片/媒体 10px、胶囊 999px ────────────────
edit(S, '  --radius:4px; --radius-lg:8px;', '  --radius:6px; --radius-lg:10px;',
     why="控件 4→6px、卡片 8→10px")
edit(S, 'border-radius:16px', 'border-radius:var(--radius-lg)', n=3, why="删 16px 混用")
edit(S, 'border-radius:14px', 'border-radius:var(--radius-lg)', n=3, why="删 14px 混用")
edit(S, 'border-radius:12px', 'border-radius:var(--radius-lg)', n=2, why="删 12px 混用")
edit(S, 'border-radius:10px', 'border-radius:var(--radius-lg)', n=2, why="收进 token")
edit(S, 'border-radius:6px', 'border-radius:var(--radius)', n=1, why="收进 token")
edit(S, 'border-radius:4px', 'border-radius:var(--radius)', n=1, why="收进 token")
edit(P, 'border-radius:8px', 'border-radius:var(--radius-lg)', n=1, why="收进 token")

# ── §14 触控目标 ≥44px ────────────────────────────────────────────
edit(S, '.langlink{display:inline-flex;align-items:center;justify-content:center;min-height:38px;',
        '.langlink{display:inline-flex;align-items:center;justify-content:center;min-height:44px;',
     why="语言按钮 38→44px")
edit(S, '.hotline{font-family:var(--mono);font-size:0.82rem;color:var(--ink);'
        'display:inline-flex;align-items:center;gap:0.5em;letter-spacing:0.02em;min-height:38px;',
        '.hotline{font-family:var(--mono);font-size:0.82rem;color:var(--ink);'
        'display:inline-flex;align-items:center;gap:0.5em;letter-spacing:0.02em;min-height:44px;',
     why="热线 38→44px")

# ── §8 颜色治理：绕过 token 的第二个暖色收编 + 清死代码 ───────────────
edit(S, '  --signal:#FFB020;       /* amber — measurement / in-spec LED (only) */',
        '  --signal:#FFB020;       /* amber — measurement / in-spec LED (only) */\n'
        '  --signal-dk:#8F5D00;    /* 深琥珀：图表第二线与数据表数值。对白 5.62:1，'
        '同色相族，不再引入第二个暖色 */',
     why="为 #A8480B 建立正式 token")
edit(P, 'stroke:#A8480B', 'stroke:var(--signal-dk)', n=1, why="图表第二线归队")
edit(P, 'fill:#A8480B', 'fill:var(--signal-dk)', n=1, why="图表数据点归队")
edit(P, 'color:#A8480B', 'color:var(--signal-dk)', n=1, why="数据表数值列归队")
edit(S, ".pc-en{font-family:var(--mono);font-size:0.72rem;letter-spacing:0.04em;color:var(--signal);",
        ".pc-en{font-family:var(--mono);font-size:0.72rem;letter-spacing:0.04em;",
     why="清死代码：这里的琥珀在下一行被立即覆盖为品牌蓝，从未生效")

# ── 执行 ─────────────────────────────────────────────────────────
cache = {}
for path, old, new, n, why in EDITS:
    if path not in cache:
        cache[path] = open(path, encoding="utf-8").read()
    got = cache[path].count(old)
    if got != n:
        sys.exit(f"✗ 中止：{path} 锚点命中 {got} 次（期望 {n}）\n   {why}\n   {old[:90]}")

lines_before = {p: cache[p].count("\n") for p in cache}
for path, old, new, n, why in EDITS:
    cache[path] = cache[path].replace(old, new, n)

for path, text in cache.items():
    open(path, "w", encoding="utf-8").write(text)

print("全部锚点命中，已写入：")
for p in cache:
    print(f"  {p}  行数 {lines_before[p]} → {cache[p].count(chr(10))}")
print(f"\n共 {len(EDITS)} 条改动")
