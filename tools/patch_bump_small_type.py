# -*- coding: utf-8 -*-
"""把全站"还很小"的字一次抬起来。

前两轮只抬了 token（正文、标题、导航），但样式表里有约 50 处组件自己写死的
sub-1rem 字号——按钮 0.9375rem、眉题走 --step--1、热线与语言按钮 0.82rem、
读数器标签 0.75rem、品牌副标 0.6rem……token 抬了它们纹丝不动，
所以整页看下来仍然是"字都很小"。

做法：写死的 sub-1rem 字号统一乘 1.18，下限 13px、上限 18px；
同时抬 --step--1 与容器宽。
"""
import re, sys, io

FILES = ["public/style.css", "public/product.css", "public/manual.css"]
FACTOR, FLOOR, CEIL = 1.18, 0.8125, 1.125   # 13px 起，18px 封顶

# ── 1. 先做点名修改（用户圈出来的三处 + 容器与 token）──────────
NAMED = [
    ("public/style.css",
     "  --step--1:clamp(0.8rem,0.76rem + 0.2vw,0.9rem);        /* 12.8–14.4  表格与说明 */",
     "  --step--1:clamp(0.875rem,0.82rem + 0.25vw,1rem);       /* 14–16  表格、说明、眉题 */",
     "最小一档由 12.8–14.4 抬到 14–16px；眉题走的就是这一档"),
    ("public/style.css",
     "  --wrap:1320px; --gutter:clamp(1.1rem,4vw,2.5rem);",
     "  --wrap:1440px; --gutter:clamp(1.1rem,4vw,2.5rem);",
     "容器 1320→1440，宽屏上内容不再缩在中间一条"),
    ("public/style.css",
     ".nav a{display:inline-flex;align-items:center;font-size:1.0625rem;",
     ".nav a{display:inline-flex;align-items:center;font-size:1.125rem;",
     "导航 17→18px"),
    ("public/style.css",
     "line-height:1.2;min-height:48px;padding:0 1.4em;",
     "line-height:1.2;min-height:52px;padding:0 1.5em;",
     "按钮 48→52px 高，横向内边距同步加大"),
]

cache = {}
for path, old, new, why in NAMED:
    if path not in cache:
        cache[path] = io.open(path, encoding="utf-8").read()
    if cache[path].count(old) != 1:
        sys.exit("✗ 中止：%s 锚点命中 %d 次 — %s" % (path, cache[path].count(old), why))
for path, old, new, why in NAMED:
    cache[path] = cache[path].replace(old, new, 1)

# ── 2. 再做整表扫描：所有写死的 sub-1rem 字号统一上抬 ──────────
changed = []
def bump(m):
    v = float(m.group(1))
    if v >= 1.0:
        return m.group(0)
    nv = min(CEIL, max(FLOOR, round(v * FACTOR, 4)))
    changed.append((v, nv))
    s = ("%.4f" % nv).rstrip("0").rstrip(".")
    return "font-size:%srem" % s

for path in FILES:
    if path not in cache:
        cache[path] = io.open(path, encoding="utf-8").read()
    cache[path] = re.sub(r"font-size:(0\.\d+)rem", bump, cache[path])

for path, text in cache.items():
    io.open(path, "w", encoding="utf-8").write(text)

print("点名修改 %d 条；写死字号上抬 %d 处" % (len(NAMED), len(changed)))
seen = {}
for a, b in changed:
    seen.setdefault((a, b), 0)
    seen[(a, b)] += 1
print("\n%-12s%-12s%-8s%s" % ("原值", "新值", "处数", "px（16 基准）"))
for (a, b), n in sorted(seen.items()):
    print("%-12s%-12s%-8d%.1f → %.1f" % (a, b, n, a * 16, b * 16))
