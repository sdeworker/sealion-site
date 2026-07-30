# -*- coding: utf-8 -*-
"""把整站的视觉尺度放大一档 —— 对标沃思首页的"大气"

问题不在 1px 的正文，在版面尺度：
  沃思 1440 视口：整屏实景大图，导航压在图上，首屏底部就是数字证据条
  海狮 1440 视口：Hero 只有 615px（80% 首屏），实景被 .92 的遮罩压死，
                  内容夹在 1160px 容器里两边各留 140px，产品图 411px

本批只改尺度，不改结构，全部是 CSS，可整条回滚。
"""
import sys, io

S = "public/style.css"
E = []
def edit(old, new, why, n=1):
    E.append((old, new, why, n))

# ── 1. 容器加宽：1160 → 1320 ──────────────────────────────
edit("  --wrap:1160px; --gutter:clamp(1.1rem,4vw,2.5rem);",
     "  --wrap:1320px; --gutter:clamp(1.1rem,4vw,2.5rem);",
     "内容宽 1160→1320，1440 视口下两侧留白由 140 收到 60")

# ── 2. 正文再放大一档：17 → 18px，基线仍是 28 ─────────────
edit("  --step-0:1.0625rem;                                     /* 17    正文，行高 28px 即基线 */",
     "  --step-0:1.125rem;                                      /* 18    正文，行高 28px 即基线 */",
     "正文 17→18px（18 × 1.5556 = 28，基线不动）")
edit("body{font-family:var(--body);font-size:var(--step-0);line-height:1.647;",
     "body{font-family:var(--body);font-size:var(--step-0);line-height:1.5556;",
     "行高随之收，一行仍是 28px")
edit("  --step-1:clamp(1.1875rem,1.11rem + 0.35vw,1.3125rem);   /* 19–21 导语、卡片标题、正文 h3 */",
     "  --step-1:clamp(1.25rem,1.16rem + 0.4vw,1.40625rem);     /* 20–22.5 导语、卡片标题、正文 h3 */",
     "导语与卡片标题跟着上调，保住与正文的比例")
edit("  --step-2:clamp(1.3125rem,1.2rem + 0.75vw,1.625rem);     /* 21–26 小节标题、正文 h2 */",
     "  --step-2:clamp(1.375rem,1.25rem + 0.85vw,1.75rem);      /* 22–28 小节标题、正文 h2 */",
     "小节标题同上")
edit(".lead{font-size:var(--step-1);line-height:1.334;",
     ".lead{font-size:var(--step-1);line-height:1.245;",
     "导语 22.5 × 1.245 = 28，仍落基线")

# ── 3. 导航放大 ────────────────────────────────────────────
edit(".nav a{display:inline-flex;align-items:center;font-size:0.95rem;",
     ".nav a{display:inline-flex;align-items:center;font-size:1.0625rem;",
     "导航中文 15.2→17px")
edit(".bar{display:flex;align-items:center;gap:1.5rem;min-height:68px}",
     ".bar{display:flex;align-items:center;gap:1.5rem;min-height:76px}",
     "导航条 68→76px，容纳更大的字与 logo")
edit(".brand img{height:42px;width:auto}",
     ".brand img{height:48px;width:auto}",
     "logo 42→48px")
edit(".brand-text strong{font-family:var(--display);font-size:1.12rem;",
     ".brand-text strong{font-family:var(--display);font-size:1.28rem;",
     "品牌名跟着放大")

# ── 4. Hero 铺满首屏 ───────────────────────────────────────
edit(".hero{position:relative;overflow:hidden;background:",
     ".hero{position:relative;overflow:hidden;min-height:calc(100svh - 76px);"
     "display:flex;align-items:center;background:",
     "Hero 由 615px 撑到整屏（减去导航条），实景大图真正占满第一屏")
edit(".hero-grid{display:grid;grid-template-columns:1.05fr 0.95fr;"
     "gap:clamp(2rem,5vw,4.5rem);align-items:center;padding-block:clamp(3.5rem,9vw,7rem);",
     ".hero-grid{display:grid;grid-template-columns:1.05fr 0.95fr;"
     "gap:clamp(2rem,5vw,4.5rem);align-items:center;padding-block:clamp(3rem,7vw,5.5rem);width:100%;",
     "Hero 内容居中，靠 min-height 撑高而不是靠内边距堆高")

# ── 5. 遮罩减淡，让实景显出来 ───────────────────────────────
edit("  background:linear-gradient(90deg,rgba(10,26,38,.92) 0%,rgba(10,26,38,.78) 45%,rgba(10,26,38,.55) 100%)}",
     "  background:linear-gradient(90deg,rgba(10,26,38,.80) 0%,rgba(10,26,38,.58) 45%,"
     "rgba(10,26,38,.26) 100%),\n"
     "             linear-gradient(180deg,rgba(10,26,38,.45) 0%,transparent 28%)}",
     "左侧遮罩 .92→.80、右侧 .55→.26，厂房实景不再被压死；"
     "顶部补一层短渐变，保证导航文字在图上仍读得清")

# ── 6. 产品图放大：三列改两列 ───────────────────────────────
edit(".pcard-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:clamp(1rem,2vw,1.5rem)}",
     ".pcard-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:clamp(1.2rem,2vw,1.75rem)}",
     "事业部产品卡三列→两列，1320 容器下单卡图由 411px 涨到约 645px")
edit(".prod-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:clamp(1rem,2.5vw,1.6rem)}",
     ".prod-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:clamp(1.2rem,2.5vw,1.75rem)}",
     "首页产品区同上")
edit("@media(max-width:900px){.pcard-grid{grid-template-columns:repeat(2,1fr)}}",
     "@media(max-width:900px){.pcard-grid{grid-template-columns:1fr}}",
     "两列在 900px 以下直接落单列，不再挤")
edit("@media(max-width:900px){.prod-grid{grid-template-columns:repeat(2,1fr)}}",
     "@media(max-width:900px){.prod-grid{grid-template-columns:1fr}}",
     "同上")

# ── 执行 ───────────────────────────────────────────────────
s = io.open(S, encoding="utf-8").read()
for old, new, why, n in E:
    got = s.count(old)
    if got != n:
        sys.exit("✗ 中止：锚点命中 %d 次（期望 %d）— %s\n   %s" % (got, n, why, old[:110]))
before = s.count("\n")
for old, new, why, n in E:
    s = s.replace(old, new, n)
io.open(S, "w", encoding="utf-8").write(s)
print("全部 %d 条锚点命中；style.css 行数 %d → %d" % (len(E), before, s.count("\n")))
