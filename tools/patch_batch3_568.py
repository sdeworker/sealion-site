# -*- coding: utf-8 -*-
"""规范 v2.1 第三批 5、6、8 项

5  40 页补可见面包屑（新闻详情 32 + 事业部 6 + reader 2）
6  新闻详情页补上下篇与去处
8  事业部卡片标题拆成中文 h3 + 英文 .pc-en 两级，并做 x-height 补偿
"""
import io, sys

# ── 8. 卡片标题拆两级 ───────────────────────────────────────
p = "tools/make_divisions.py"
s = io.open(p, encoding="utf-8").read()

OLD = """            f'        <h3>{t}</h3>\\n'"""
NEW = """            f'        <h3>{split_title(t)[0]}</h3>\\n'
            + (f'        <span class="pc-en">{split_title(t)[1]}</span>\\n'
               if split_title(t)[1] else '')
            +"""
assert s.count(OLD) == 1, "卡片标题锚点对不上"
s = s.replace(OLD, NEW, 1)

HELPER = '''
def split_title(text):
    """把"米重控制系统 Gravimetric Control System"拆成中文与英文两截。

    此前两种语言压在同一个 h3 里、同号同重，信息层级塌了一层；而且汉字
    字面几乎占满字身框、拉丁小写只占 x-height 那一段，同号并排时英文
    必然显得小一号。拆开之后英文单独一档，可以补回去。
    找第一个拉丁字母，它前面是中文、从它开始是英文。
    """
    for i, ch in enumerate(text):
        if "a" <= ch.lower() <= "z":
            zh, en = text[:i].strip(), text[i:].strip()
            if zh and en:
                return zh, en
            break
    return text.strip(), ""


'''
ANCH = "PROD_IMG = {"
assert s.count(ANCH) == 1
s = s.replace(ANCH, HELPER.lstrip("\n") + ANCH, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("make_divisions.py：卡片标题拆中英两级")

# ── 5 + 6. 面包屑与上下篇 ───────────────────────────────────
b = io.open("tools/build.py", encoding="utf-8").read()

NEWS_HELPERS = '''
# ---------- 面包屑与新闻上下篇 ----------
# 缘由：135 页有 BreadcrumbList 结构化数据（给搜索引擎看），页面上真正
# 看得见的面包屑只有 95 页。缺的 40 页里，32 页是新闻详情——而新闻恰恰
# 是自然流量的第一落点，访客从搜索结果直接落进来，页面上没有任何东西
# 告诉他这是哪个网站的哪一层，读完也只有"返回列表"一条出路。
import re as _re

_NEWS_ORDER = {}


def news_order(lang):
    """从新闻列表页解析出文章顺序与标题，列表页的排序就是权威顺序。"""
    if lang in _NEWS_ORDER:
        return _NEWS_ORDER[lang]
    path = SRC / "content" / lang / "news.html"
    items = []
    if path.exists():
        txt = path.read_text(encoding="utf-8")
        seen = set()
        for m in _re.finditer(r'<h3><a href="([^"]+)">(.*?)</a></h3>', txt, _re.S):
            href, title = m.group(1), _re.sub(r"<[^>]+>", "", m.group(2)).strip()
            if href not in seen:
                seen.add(href)
                items.append((href, title))
    _NEWS_ORDER[lang] = items
    return items


def crumb_for(rel, lang, meta):
    """给没有手写面包屑的页面补一条。产品页等已有的不动。"""
    root = SITE["langRoot"][lang]
    home = t(SITE["ui"]["home"], lang) if "home" in SITE["ui"] else {"zh": "首页", "en": "Home", "ru": "Главная"}[lang]
    parts = rel.split("/")
    label = None
    parent = None
    if parts[0] == "news" and len(parts) > 1:
        parent = (f"{root}news.html", t(SITE["ui"]["newsSection"], lang)
                  if "newsSection" in SITE["ui"] else {"zh": "海狮动态", "en": "News", "ru": "Новости"}[lang])
        label = meta.get("crumb") or _re.sub(r"\\s*[—|]\\s*.*$", "", meta.get("title", "")).strip()
    elif parts[0] in ("pipe", "cable") and parts[-1] == "index.html":
        label = {"pipe": {"zh": "管道挤出事业部", "en": "Pipe Extrusion", "ru": "Экструзия труб"},
                 "cable": {"zh": "线缆挤出事业部", "en": "Cable Extrusion", "ru": "Экструзия кабеля"}}[parts[0]][lang]
    elif parts[0] == "manual":
        parent = (f"{root}manual/", {"zh": "产品手册", "en": "Manual", "ru": "Руководство"}[lang])
        label = meta.get("crumb") or _re.sub(r"\\s*[—|]\\s*.*$", "", meta.get("title", "")).strip()
        if parts[-1] == "index.html":
            parent, label = None, {"zh": "产品手册", "en": "Manual", "ru": "Руководство"}[lang]
    if not label:
        return ""
    mid = f'<a href="{parent[0]}">{H.escape(parent[1])}</a> / ' if parent else ""
    return (f'<nav class="crumb wrap"><a href="{root}">{H.escape(home)}</a> / '
            f'{mid}<span>{H.escape(label)}</span></nav>')


def news_updown(rel, lang):
    """上一篇 / 下一篇 / 回列表，外加两个事业部的去处——读完不能是死胡同。"""
    items = news_order(lang)
    if not items:
        return ""
    href = "/" + rel if not rel.startswith("/") else rel
    root = SITE["langRoot"][lang]
    href = href.replace(root, "/", 1) if root != "/" else href
    idx = next((i for i, (h, _) in enumerate(items) if h.rstrip("/") == href.rstrip("/")), None)
    if idx is None:
        return ""
    L = {"zh": ("上一篇", "下一篇", "全部动态", "看看我们的产品", "管道挤出", "线缆挤出"),
         "en": ("Previous", "Next", "All news", "Browse our systems", "Pipe extrusion", "Cable extrusion"),
         "ru": ("Предыдущая", "Следующая", "Все новости", "Наши системы", "Экструзия труб", "Экструзия кабеля")}[lang]
    out = ['<nav class="artnav wrap" aria-label="' + H.escape(L[2]) + '">']
    if idx > 0:
        h, ti = items[idx - 1]
        out.append(f'  <a class="artnav-i artnav-i--prev" href="{root.rstrip("/")}{h}">'
                   f'<span>{L[0]}</span><b>{H.escape(ti)}</b></a>')
    if idx < len(items) - 1:
        h, ti = items[idx + 1]
        out.append(f'  <a class="artnav-i artnav-i--next" href="{root.rstrip("/")}{h}">'
                   f'<span>{L[1]}</span><b>{H.escape(ti)}</b></a>')
    out.append('</nav>')
    out.append(f'<div class="artmore wrap"><span>{H.escape(L[3])}</span>'
               f'<a href="{root}pipe/">{H.escape(L[4])}</a>'
               f'<a href="{root}cable/">{H.escape(L[5])}</a>'
               f'<a href="{root}news.html">{H.escape(L[2])}</a></div>')
    return "\\n".join(out)


'''

ANCH2 = "def render_header("
assert b.count(ANCH2) == 1
b = b.replace(ANCH2, NEWS_HELPERS.lstrip("\n") + ANCH2, 1)

OLD_MAIN = """<main id="main">
{body}
</main>"""
NEW_MAIN = """<main id="main">
{crumb}
{body}
{updown}
</main>"""
assert b.count(OLD_MAIN) == 1
b = b.replace(OLD_MAIN, NEW_MAIN, 1)

OLD_VARS = '    bodycls = "home" if meta.get("type") == "home" else ""'
NEW_VARS = ('    bodycls = "home" if meta.get("type") == "home" else ""\n'
            '    crumb = "" if \'class="crumb"\' in body else crumb_for(rel, lang, meta)\n'
            '    updown = news_updown(rel, lang) if rel.startswith("news/") else ""')
assert b.count(OLD_VARS) == 1
b = b.replace(OLD_VARS, NEW_VARS, 1)
io.open("tools/build.py", "w", encoding="utf-8").write(b)
print("build.py：面包屑与新闻上下篇")

# ── CSS ────────────────────────────────────────────────────
S = "public/style.css"
st = io.open(S, encoding="utf-8").read()
ANCH3 = "/* a11y + motion */"
CSS = """/* 新闻详情的上下篇与去处：读完不能只有一条"返回列表" */
.artnav{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:1rem;
  margin-block:var(--sp-2) var(--sp-1)}
.artnav-i{display:flex;flex-direction:column;gap:.35rem;padding:1rem 1.15rem;
  border:1px solid var(--line);border-radius:var(--radius-lg);background:var(--paper-2);
  transition:border-color .18s,transform .18s}
.artnav-i:hover{border-color:var(--blue);transform:translateY(-2px)}
.artnav-i span{font-size:0.9375rem;color:var(--steel)}
.artnav-i b{font-weight:600;color:var(--ink);line-height:1.4}
.artnav-i--next{text-align:right}
.artmore{display:flex;flex-wrap:wrap;align-items:center;gap:1rem;margin-bottom:var(--sp-2);
  padding-top:var(--sp-1);border-top:1px solid var(--line)}
.artmore span{color:var(--steel)}
.artmore a{color:var(--blue);border-bottom:1px solid transparent}
.artmore a:hover{border-bottom-color:var(--blue)}
/* 卡片英文名单独一档：汉字占满字身框，拉丁小写只占 x-height，
   同号并排时英文必然显小，这里补回去 */
.pcard--img .pc-en{display:block;margin-top:.15rem;font-size:1.04em;letter-spacing:.01em;
  color:rgba(255,255,255,.78)}

"""
assert st.count(ANCH3) == 1
st = st.replace(ANCH3, CSS + ANCH3, 1)
io.open(S, "w", encoding="utf-8").write(st)
print("style.css：上下篇与卡片英文名样式")
