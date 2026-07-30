# -*- coding: utf-8 -*-
"""第三批 · 第 1 项 —— 依据《海狮官网改版执行规范 v2.1》§4.1 §4.2
   正文收到 16px/1.75 · --baseline:28px 基线网格 · 1.25 等比字阶 · Hero 独立 58px

单独一次推送，便于四档视口目视验收后再决定其余八项。
每条 assert 锚定，任一条对不上就整体中止。
"""
import sys, io

S = "public/style.css"
P = "public/product.css"
M = "public/manual.css"
E = []
def edit(path, old, new, why, n=1):
    E.append((path, old, new, why, n))

# ── 1. 字阶：1.25 等比链 + Hero 独立 ──────────────────────────
# 16 / 20 / 25 / 31.25 / 39.06 / 48.83，Hero 58 不入链。
# 桌面值取 1280px 视口；手机值取 390px。
edit(S,
"""  --step--1:clamp(0.8rem,0.76rem + 0.2vw,0.9rem);
  --step-0:clamp(1rem,0.95rem + 0.25vw,1.075rem);
  --step-1:clamp(1.2rem,1.1rem + 0.5vw,1.4rem);
  --step-2:clamp(1.25rem,1.15rem + 0.7vw,1.75rem);
  --step-3:clamp(1.75rem,1.5rem + 1.2vw,2.5rem);
  --step-4:clamp(2.25rem,1.75rem + 2.6vw,3.75rem);""",
"""  /* 字阶：以正文 16px 为基准、公比 1.25 的等比链 —— 16 / 20 / 25 / 31 / 39 / 49。
     Hero 不入链（它是广告位不是章节），单独取 58px。
     为什么必须等比：改版前实测 60/39.4/27.4/22.4/17.2，相邻比 1.52/1.44/1.24/1.30，
     在 H3 那一档断了——H2 到 H3 是个大台阶，H3 到卡片标题却几乎分不出来。
     桌面值按 1280px 视口，手机值按 390px。 */
  --step--1:clamp(0.8rem,0.76rem + 0.2vw,0.9rem);        /* 12.8–14.4  表格与说明 */
  --step-0:1rem;                                          /* 16    正文，一行正好 28px */
  --step-1:clamp(1.125rem,1.05rem + 0.35vw,1.25rem);      /* 18–20 导语、卡片标题、正文 h3 */
  --step-2:clamp(1.25rem,1.15rem + 0.7vw,1.5625rem);      /* 20–25 小节标题、正文 h2 */
  --step-3:clamp(1.5rem,1.305rem + 0.8vw,1.9375rem);      /* 24–31 预留：第五批把产品页
                                                              22 个 h2 降级为 5–6 章之后，
                                                              正文 h2 升到这一档 */
  --step-4:clamp(1.75rem,1.5rem + 1.2vw,2.4375rem);       /* 28–39 区块横幅 .sh h2 */
  --step-5:clamp(2rem,1.7rem + 1.6vw,3.0625rem);          /* 32–49 内页 H1 */
  --step-hero:clamp(2.25rem,1.75rem + 2.6vw,3.625rem);    /* 36–58 Hero，独立不入链 */""",
"字阶改公比 1.25 的等比链，补上 31 那一级，区块横幅与内页 H1 分开")

# ── 2. 基线网格：全站纵向的唯一单位 ───────────────────────────
edit(S,
"  --sp:clamp(3.5rem,8vw,6.5rem);",
"""  /* 基线网格：正文 16px × 行高 1.75 = 一行 28px，这是全站纵向的唯一单位。
     纵向留白只准取它的整数倍——用 clamp 做流体留白会落在非整数倍上，
     所以这里改成按断点跳档，保证每个视口都精确对齐。 */
  --baseline:1.75rem;                    /* 28px */
  --sp-1:var(--baseline);                /* 28   组件内 */
  --sp-2:calc(var(--baseline) * 2);      /* 56   子模块 */
  --sp-3:calc(var(--baseline) * 3);      /* 84   章节 */
  --sp-4:calc(var(--baseline) * 4);      /* 112  大分区 */
  --sp:var(--sp-2);                      /* 章节留白：手机 56，≥768px 跳到 84 */""",
"引入基线与 --sp-* 家族，--sp 改为基线倍数")

edit(S,
"h1,h2,h3,h4{font-family:var(--display);line-height:1.25;font-weight:600;letter-spacing:0}",
"""@media(min-width:768px){:root{--sp:var(--sp-3)}}
h1,h2,h3,h4{font-family:var(--display);line-height:1.25;font-weight:600;letter-spacing:0}
/* 正文里的裸标题此前没有任何 font-size 规则，一直吃浏览器默认的 em 倍数
   （h2=1.5em、h3=1.17em），也就是跟着正文字号浮动、不在字阶里。
   收进 token，让它们和带 class 的标题走同一条比例链。 */
h2{font-size:var(--step-2)}
h3{font-size:var(--step-1)}
h4{font-size:var(--step-0)}""",
"把正文裸标题收进字阶，并让 --sp 在 ≥768px 跳到 84px")

# ── 3. 正文行高 1.65 → 1.75，使一行正好等于基线 ────────────────
edit(S,
"body{font-family:var(--body);font-size:var(--step-0);line-height:1.65;",
"body{font-family:var(--body);font-size:var(--step-0);line-height:1.75;",
"一行正好 28px，与基线对齐")

# ── 4. Hero 与内页 H1 分开 ───────────────────────────────────
edit(S, ".hero-copy h1{font-size:var(--step-4);", ".hero-copy h1{font-size:var(--step-hero);",
     "Hero 用独立的 --step-hero（58px）")
edit(S, ".sh h2{font-size:var(--step-3);", ".sh h2{font-size:var(--step-4);",
     "区块横幅仍是 39px，只是换到新的档位名")
edit(S, ".ind-hero h1{font-size:var(--step-3)", ".ind-hero h1{font-size:var(--step-5)",
     "行业页 H1 39→48px，与区块横幅拉开一档")
edit(S, ".ip-hero h1{font-size:var(--step-3)", ".ip-hero h1{font-size:var(--step-5)",
     "海狮实力页 H1 同上")
edit(P,
     ".prod-hero-body h1{font-family:var(--display);font-size:var(--step-3);line-height:1.1;",
     ".prod-hero-body h1{font-family:var(--display);font-size:var(--step-5);",
     "产品页 H1 39→48px；并删掉 line-height:1.1——它会盖掉 h1 的 1.12，"
     "而 1.1 正是 §4.3 判定为过紧的那个值")
edit(M, ".m-hero h1{font-size:var(--step-3)", ".m-hero h1{font-size:var(--step-5)",
     "手册首页 H1 同上")
edit(M, ".m-head h1{font-size:var(--step-3)", ".m-head h1{font-size:var(--step-5)",
     "手册内页 H1 同上")

# ── 5. 基线自检工具（默认关闭，仅为目视验收第 1 项） ────────────
edit(S,
"/* a11y + motion */",
"""/* 开发期基线自检：在 <body> 上加 class="debug-baseline" 铺一张 28px 网格，
   用来目视确认正文、标题与段间距是否都落在同一条基线上。默认不生效。 */
body.debug-baseline{background-image:repeating-linear-gradient(
  to bottom,rgba(0,97,188,.14) 0 1px,transparent 1px var(--baseline))}

/* a11y + motion */""",
"加基线调试网格，默认关闭")

# ── 执行 ─────────────────────────────────────────────────────
cache = {}
for path, old, new, why, n in E:
    if path not in cache:
        cache[path] = io.open(path, encoding="utf-8").read()
    got = cache[path].count(old)
    if got != n:
        sys.exit("✗ 中止：%s 锚点命中 %d 次（期望 %d）— %s\n   %s" % (path, got, n, why, old[:110]))

before = {p: cache[p].count("\n") for p in cache}
for path, old, new, why, n in E:
    cache[path] = cache[path].replace(old, new, n)
for path, text in cache.items():
    io.open(path, "w", encoding="utf-8").write(text)

print("全部 %d 条锚点命中，已写入：" % len(E))
for p in cache:
    print("  %-22s 行数 %d → %d" % (p, before[p], cache[p].count("\n")))
