# -*- coding: utf-8 -*-
"""
产品页分层重排：把「百科全书」改成「决策页」。

内容一条不删，只改顺序与层级：
  销售层（先看到）：价值 → 问题 → 实证 → 选型与参数
  工程层（往下看）：原理与组成 → 功能细节 → 投资回报 → 现场影像
  售后层（默认折叠）：报警代码与现场自查

依据：一个页面同时承担手册、售后知识库与销售页三种任务，
采购者要的选型信息被压在第 10 位之后，价值主张排在第 15 位。
"""
import glob, json, os, re

# 按 eyebrow 归层；数字越小越靠前。未列出的按默认层保持原有相对顺序。
LAYER = {
    # ——— 销售层 ———
    "Value": 10,                # 为产线解决的七件事
    "Why equip it": 12,         # 为什么必须配置
    "The problem": 12,
    "Measured": 14,             # 控制前后实测记录（最强证据）
    "Parameters": 20,           # 技术参数
    "Technical data": 20,
    "Model": 22,                # 产品配置型号
    "Application": 24,          # 适用行业
    # ——— 工程层 ———
    "What is it": 30,
    "Principle": 31,
    "Workflow": 32,
    "Technical structure": 33,
    "Installation": 34,
    "Scanning box": 35,
    "DSP": 35,
    "Hardware": 36,
    "Double output": 37,
    "Control modes": 40,
    "Calculation": 41,
    "Recipes": 42,
    "Functions": 43,
    "Software": 44,
    "Statistics": 45,
    "Protection": 46,
    "More": 47,
    "Cable only": 48,
    "Daily use": 50,
    "Maintenance": 51,
    "Patents": 55,
    "ROI": 60,                  # 投资回报
    # ——— 售后层（默认折叠）———
    "Alarms": 90,
}
DEFAULT = 70          # 无 eyebrow 的（现场图库、视频）排在工程层之后
COLLAPSE = {"Alarms"}  # 折叠的区块

FOLD_LABEL = {
    "zh": ("报警代码与现场自查", "展开查看 18 条报警代码与产线可自查项",
           "以下内容面向已装机客户的产线人员。选型阶段可跳过。"),
    "en": ("Alarm codes & on-line checks", "Show the 18 alarm codes and on-line checks",
           "Written for line staff at sites already running the system. Skip it while selecting."),
    "ru": ("Коды аварий и проверки на линии", "Показать 18 кодов аварий и проверки на линии",
           "Раздел для персонала линий, где система уже работает. При выборе оборудования его можно пропустить."),
}


def split_sections(body):
    idx = [m.start() for m in re.finditer(r"<section\b", body)]
    if not idx:
        return []
    idx.append(len(body))
    return [body[idx[i]:idx[i + 1]] for i in range(len(idx) - 1)]


def eyebrow_of(sec):
    m = re.search(r'<span class="eyebrow">([^<]*)</span>', sec)
    return m.group(1).strip() if m else ""


def reorder(body, lang):
    secs = split_sections(body)
    if len(secs) < 5:
        return body, 0, False

    hero = [s for s in secs if 'class="section prod-hero"' in s]
    cta = [s for s in secs if "prod-foot-cta" in s]
    middle = [s for s in secs if s not in hero and s not in cta]

    ranked = []
    for i, s in enumerate(middle):
        eb = eyebrow_of(s)
        # eyebrow 可能是「产品中心 · 01」这类，取其英文关键词匹配
        rank = LAYER.get(eb, None)
        if rank is None:
            for k, v in LAYER.items():
                if k.lower() in eb.lower():
                    rank = v
                    break
        ranked.append((rank if rank is not None else DEFAULT, i, s, eb))

    ranked.sort(key=lambda x: (x[0], x[1]))
    moved = sum(1 for n, (r, i, s, eb) in enumerate(ranked) if n != i)

    out, folded = [], False
    title, summary, note = FOLD_LABEL.get(lang, FOLD_LABEL["zh"])
    for r, i, s, eb in ranked:
        if eb in COLLAPSE:
            # 折叠：内容一字不删，只是默认收起
            inner = s.strip()
            out.append(
                f'<section class="section svc-fold"><div class="wrap">\n'
                f'  <details class="fold">\n'
                f'    <summary><span class="fold-t">{title}</span>'
                f'<span class="fold-hint">{summary}</span></summary>\n'
                f'    <p class="fold-note">{note}</p>\n'
                f'{inner}\n'
                f'  </details>\n</div></section>\n')
            folded = True
        else:
            out.append(s)

    return "\n".join(hero + out + cta), moved, folded


changed = 0
for f in sorted(glob.glob("src/content/*/pipe/*.html") + glob.glob("src/content/*/cable/*.html")):
    if f.endswith("index.html"):
        continue
    lang = f.split("src/content/")[1].split("/")[0]
    raw = open(f, encoding="utf-8").read()
    meta_s, _, body = raw.partition("\n---\n")
    new, moved, folded = reorder(body, lang)
    if new != body:
        open(f, "w", encoding="utf-8").write(meta_s + "\n---\n" + new.strip("\n") + "\n")
        changed += 1
        print(f"  {f[len('src/content/'):]:36} 调序 {moved} 处" + ("，报警区已折叠" if folded else ""))

print(f"\n重排 {changed} 个产品页")
