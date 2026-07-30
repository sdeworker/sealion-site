# -*- coding: utf-8 -*-
"""第 0 批（P0 生产故障）——依据《海狮官网改版执行规范 v2.1》§15.0

0-1  4 个失效的「问技术工程师」按钮改成预填模板 mailto:（用户 2026-07-30 选定方案 A）
0-2  删掉 style.css 里已成孤儿的咨询组件样式（组件早从 HTML 移除）
0-3  check.py 增加「脚本钩子」闸门：有触发器却没有组件根节点 → 阻断发布

每条都 assert 锚定，任一条对不上就整体中止。
"""
import sys, io
from urllib.parse import quote

MAIL = "2428582102@qq.com"

BODY_ZH = """请填下面四项，工程师会按你的产线给出配置建议和需要确认的参数清单。

1. 管材／线缆类型与口径：
2. 原料与配方（含回料比例）：
3. 挤出量（kg/h）：
4. 线速（m/min）：

现有设备（挤出机品牌型号、有无变频、是否已装测厚或称重）：
联系人与电话：
"""

BODY_EN = """Please fill in the four items below. Our engineer will reply with a
suggested configuration and the parameters that still need confirming.

1. Pipe / cable type and diameter:
2. Material and formulation (including regrind ratio):
3. Output (kg/h):
4. Line speed (m/min):

Existing equipment (extruder make and model, VFD, any gauging already fitted):
Contact name and phone:
"""


def mailto(subject, body):
    return "mailto:%s?subject=%s&body=%s" % (MAIL, quote(subject), quote(body))


LINK_ZH = mailto("产线参数咨询", BODY_ZH)
LINK_EN = mailto("Line parameter enquiry", BODY_EN)

E = []
def edit(path, old, new, why, n=1):
    E.append((path, old, new, why, n))


# ── 0-1 四个死按钮 ────────────────────────────────────────────
for path, link, label in [
    ("src/content/zh/index.html", LINK_ZH, "问技术工程师"),
    ("src/content/en/index.html", LINK_EN, "Ask our engineer"),
]:
    edit(path,
         '<button class="btn btn--onDark" type="button" data-open-ai>%s</button>' % label,
         '<a class="btn btn--onDark" href="%s">%s</a>' % (link, label),
         "Hero 按钮改可用的 mailto")
    edit(path,
         '<button class="btn btn--primary" type="button" data-open-ai>%s</button>' % label,
         '<a class="btn btn--primary" href="%s">%s</a>' % (link, label),
         "联系区按钮改可用的 mailto")

# ── 0-2 删孤儿样式 ───────────────────────────────────────────
# 先把 .back-to-top 里那条为已不存在的启动器预留的高度去掉，
# 否则回顶按钮会一直悬在比需要的位置高 46px 的地方。
edit("public/style.css",
     "  bottom:calc(clamp(1rem,3vw,2rem) + var(--ai-launcher-height,2.6875rem) + .875rem);z-index:89;",
     "  bottom:clamp(1rem,3vw,2rem);z-index:89;",
     "回顶按钮不再为已删除的咨询启动器留位")

io_src = io.open("public/style.css", encoding="utf-8").read()
start = io_src.index("/* ============ AI ASSISTANT WIDGET ============ */")
end = io_src.index("/* a11y + motion */")
DEAD = io_src[start:end]
assert ".ai-launcher" in DEAD and ".aip-send" in DEAD and "@keyframes bounce" in DEAD, "死块边界不对"
assert "back-to-top" not in DEAD, "误把回顶样式圈进来了"
edit("public/style.css", DEAD, "",
     "删除咨询组件的孤儿样式（组件已从 HTML 移除，样式还在，违反 §15.2）")

# ── 0-3 check.py 加脚本钩子闸门 ───────────────────────────────
NEW_CHECK = '''
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


'''
edit("tools/check.py", "def main():", NEW_CHECK.lstrip("\n") + "def main():",
     "新增第 12 项检查函数")
edit("tools/check.py",
     '        ("图片属性", check_images), ("部署体积", check_size),',
     '        ("图片属性", check_images), ("部署体积", check_size),\n'
     '        ("脚本钩子", check_js_hooks),',
     "把第 12 项挂进检查表")

# ── 执行 ─────────────────────────────────────────────────────
cache = {}
for path, old, new, why, n in E:
    if path not in cache:
        cache[path] = io.open(path, encoding="utf-8").read()
    got = cache[path].count(old)
    if got != n:
        sys.exit("✗ 中止：%s 锚点命中 %d 次（期望 %d）— %s\n   %s" % (path, got, n, why, old[:100]))

before = {p: cache[p].count("\n") for p in cache}
for path, old, new, why, n in E:
    cache[path] = cache[path].replace(old, new, n)
for path, text in cache.items():
    io.open(path, "w", encoding="utf-8").write(text)

print("全部 %d 条锚点命中，已写入：" % len(E))
for p in cache:
    print("  %-28s 行数 %d → %d" % (p, before[p], cache[p].count("\n")))
print("\nmailto 链接长度：zh %d 字符 / en %d 字符" % (len(LINK_ZH), len(LINK_EN)))
