#!/usr/bin/env python3
"""로컬 미리보기.

Ruby/Jekyll 없이 파이썬만으로 사이트 전체를 실제 조판 그대로 빌드하여
localhost 에 띄웁니다. 발행 목록, 각 보고서, 주제별 색인, 소개 페이지가
모두 연결되므로 링크가 실제로 동작합니다. GitHub Pages 로 나갈 결과와
같은 화면을 확인하는 용도이며, 공개 사이트에서 숨긴(published:false) 예시
글과 _reports/_drafts/ 의 초안도 로컬에서는 「초안」 표시를 달고 보입니다.
글이 쓰는 그림은 빌드할 때 촬영 정보(EXIF·GPS) 같은 메타데이터를 지웁니다.

    python tools/preview.py            # http://localhost:8787 에서 서빙
    python tools/preview.py --watch    # 저장할 때마다 다시 빌드하고 브라우저도 새로 고침
    python tools/preview.py -p 9000    # 포트 지정
    python tools/preview.py --build    # 서빙 없이 _preview/ 만 생성

이미 켜진 미리보기가 있으면 새로 띄우지 않고 한 번 빌드한 뒤 브라우저만 연다.
VS Code 에서는 폴더를 열 때 「미리보기 (자동 시작)」 작업이 --watch 로 켜 둔다.

필요 패키지: markdown, pyyaml, pygments
    python -m pip install markdown pyyaml pygments
"""
import argparse
import html
import http.server
import json
import os
import re
import shutil
import sys
import threading
import time
import urllib.parse
import urllib.request
import webbrowser
from datetime import date, datetime
from functools import partial
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "_reports"
DRAFTS = REPORTS / "_drafts"
CSS = ROOT / "assets" / "css" / "report.css"
CURSORS = ROOT / "assets" / "css" / "cursors.css"
JS = ROOT / "assets" / "js" / "report.js"
ABOUT = ROOT / "about.md"
OUT = ROOT / "_preview"
ATTACK = ROOT / "_data" / "attack.json"
VULNS = ROOT / "_data" / "vulns.json"
FONTS = ROOT / "assets" / "fonts"
STAMP = "__build.txt"
LIVE = False
PORT = 8787
IN_VSCODE = os.environ.get("TERM_PROGRAM") == "vscode"
_ATT = None

RELOAD = """<script>
(function () {
  var seen = null;
  function check(t) {
    if (!t) return;
    t = String(t).trim();
    if (seen === null) seen = t;
    else if (t !== seen) location.reload();
  }
  function poll() {
    fetch('/__build.txt', { cache: 'no-store' })
      .then(function (r) { return r.ok ? r.text() : null; })
      .then(check)
      .catch(function () {});
  }
  if (window.EventSource) {
    new EventSource('/__events').onmessage = function (e) { check(e.data); };
  }
  setInterval(poll, 1000);
  document.addEventListener('visibilitychange', function () { if (!document.hidden) poll(); });
  window.addEventListener('focus', poll);
  window.addEventListener('pageshow', poll);
  poll();
})();
</script>"""


def attack_db():
    global _ATT
    if _ATT is None:
        try:
            _ATT = json.loads(ATTACK.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            _ATT = {}
    return _ATT

try:
    import yaml
    import markdown
except ImportError as e:
    sys.exit(f"필요한 패키지가 없습니다 ({e.name}).\n"
             "  python -m pip install markdown pyyaml pygments")


def load_config():
    f = ROOT / "_config.yml"
    return (yaml.safe_load(f.read_text(encoding="utf-8")) or {}) if f.exists() else {}


def split_front_matter(text):
    text = text.lstrip("﻿")
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return (yaml.safe_load(text[3:end]) or {}), text[end + 4:].lstrip("\n")
    return {}, text


def as_date(d):
    if isinstance(d, datetime):
        return d.date()
    if isinstance(d, date):
        return d
    if isinstance(d, str):
        try:
            return datetime.strptime(d.strip()[:10], "%Y-%m-%d").date()
        except ValueError:
            pass
    return None


def load_reports():
    items = []
    for folder, draft in ((REPORTS, False), (DRAFTS, True)):
        for p in sorted(folder.glob("*.md")):
            fm, body = split_front_matter(p.read_text(encoding="utf-8"))
            items.append({"slug": p.stem, "fm": fm, "body": body, "date": as_date(fm.get("date")),
                          "draft": draft, "path": p})
    items.sort(key=lambda x: x["date"] or date.min)
    return items


def local_label(item):
    return "초안" if str(item["fm"].get("tlp") or "CLEAR").upper() == "CLEAR" else "비공개"


def docket_no(item, reports):
    fm = item["fm"]
    if fm.get("docket"):
        return str(fm["docket"])
    if item.get("draft"):
        return local_label(item)
    d = item["date"]
    if not d:
        return "----"
    seq, n = 0, 0
    for r in reports:
        if r.get("draft"):
            continue
        if r["date"] and r["date"].year == d.year:
            n += 1
            if r["slug"] == item["slug"]:
                seq = n
    return f"{d.year}-{seq:03d}"


# ---- mermaid/chart/ioc/timeline/attack 펜스는 강조하지 않고 원문 그대로 보존한다 (report.js가 그림) ----
FENCE = re.compile(r"^([ \t]*)```[ \t]*(mermaid|chart|ioc|timeline|attack)[ \t]*\n(.*?)\n[ \t]*```[ \t]*$",
                   re.DOTALL | re.MULTILINE)


def render_body(md):
    md = re.sub(r'markdown="1"', 'markdown="block"', md)
    slots = []

    def stash(m):
        slots.append((m.group(2), m.group(3)))
        return f"\n\nRAWFENCE{len(slots) - 1}ENDRAW\n\n"

    md = FENCE.sub(stash, md)
    out = markdown.markdown(
        md,
        extensions=["extra", "codehilite", "sane_lists", "attr_list", "md_in_html", "footnotes"],
        extension_configs={"codehilite": {"css_class": "highlight", "guess_lang": False}},
    )
    out = out.replace('<sup id="fnref:', '<sup role="doc-noteref" id="fnref:')
    out = re.sub(r'<div class="footnote">\s*<hr\s*/?>',
                 '<div class="footnotes" role="doc-endnotes">', out)
    out = out.replace('class="footnote-backref"', 'class="reversefootnote"')
    for i, (lang, src) in enumerate(slots):
        block = (f'<div class="language-{lang} highlighter-rouge"><div class="highlight">'
                 f'<pre class="highlight"><code>{html.escape(src)}</code></pre></div></div>')
        out = re.sub(rf"<p>\s*RAWFENCE{i}ENDRAW\s*</p>", lambda m, b=block: b, out)
        out = out.replace(f"RAWFENCE{i}ENDRAW", block)
    return out


def esc(s):
    return html.escape(str(s), quote=True)


IMG_TAG = re.compile(r'(<img\b[^>]*?\bsrc=")([^"]+)(")')


def resolve_images(page, doc, used):
    """그림 경로를 글 파일 기준으로 풀어 미리보기 주소로 바꾸고, 쓰인 파일을 모은다."""
    def fix(m):
        src = html.unescape(m.group(2))
        if re.match(r"(?:[a-z]+:|//|#)", src, re.I):
            return m.group(0)
        path = urllib.parse.unquote(src)
        f = (ROOT / path.lstrip("/")) if path.startswith("/") else (doc.parent / path)
        try:
            rel = f.resolve().relative_to(ROOT)
        except ValueError:
            return m.group(0)
        if f.is_file():
            used.add(f.resolve())
        return m.group(1) + esc("/" + urllib.parse.quote(rel.as_posix())) + m.group(3)
    return IMG_TAG.sub(fix, page)


def ko_date(d):
    return f"{d.year}년 {d.month}월 {d.day}일" if d else ""


def wordmark(title):
    if ".zip" in title:
        base = title.split(".zip")[0]
        return f'{esc(base)}<span class="tld">.zip</span>'
    return esc(title)


def shell(inner, cfg, current, page_title=None):
    site = cfg.get("title", "re:versing.zip")
    tagline = cfg.get("tagline", "")
    css = CSS.read_text(encoding="utf-8")
    if CURSORS.exists():
        css += "\n" + CURSORS.read_text(encoding="utf-8")
    js = JS.read_text(encoding="utf-8")
    tab = f"{page_title} — {site}" if page_title else site

    def nav(href, label, key):
        cur = ' aria-current="page"' if key == current else ""
        return f'<a href="{href}"{cur}>{label}</a>'

    navbar = (nav("/", "발행 목록", "home") + nav("/labels/", "주제별", "labels")
              + nav("/about/", "이 기록에 대하여", "about")
              + '<a href="/feed.xml">구독</a>')

    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(tab)}</title>
<style>{css}</style>
<script>
try {{ var t = localStorage.getItem('rev-theme');
  if (t === 'dark' || t === 'light') document.documentElement.setAttribute('data-theme', t); }} catch (e) {{}}
</script>
</head>
<body>
<a class="skip" href="#main">본문 바로가기</a>
<header class="topbar">
  <div class="masthead">
    <a class="wordmark" href="/">{wordmark(site)}</a>
    <p class="tagline">{esc(tagline)}</p>
    <button type="button" id="theme-toggle" aria-label="화면 밝기">◐ 자동</button>
    <nav class="site-nav" aria-label="주 메뉴">{navbar}</nav>
  </div>
</header>
<main id="main" class="main">
<div class="page">
{inner}
<footer class="colophon"><span>© {date.today().year} {esc(cfg.get("author",""))} · {esc(site)}</span><a href="/feed.xml">구독</a></footer>
</div>
</main>
<script>{js}</script>
{RELOAD if LIVE else ""}
</body>
</html>
"""


SEV = {"긴급": "crit", "critical": "crit", "높음": "high", "high": "high",
       "중간": "mid", "medium": "mid"}


def series_info(item, reports):
    s = item["fm"].get("series")
    if not s:
        return None, 0, []
    same = sorted((r for r in reports if r["fm"].get("series") == s and (not r.get("draft") or r is item)),
                  key=lambda x: x["date"] or date.min)
    no = next((i for i, r in enumerate(same, 1) if r["slug"] == item["slug"]), 0)
    return s, no, same


def tlp_badge(tlp):
    t = str(tlp)
    return f'<span class="tlp tlp--{esc(t.lower().replace("+", "-"))}">TLP:{esc(t.upper())}</span>'


def docket_dl(item, cfg, reports):
    fm = item["fm"]
    rows = [("발행", f'<time datetime="{item["date"]}">{ko_date(item["date"])}</time>', False)]
    s, sno, _ = series_info(item, reports)
    if s:
        rows.append(("시리즈", f"{esc(s)} · 제{sno}호", False))
    if fm.get("period"):
        rows.append(("대상 기간", esc(fm["period"]), False))
    if fm.get("actor"):
        actor = str(fm["actor"])
        aka = fm.get("aliases")
        if isinstance(aka, (list, tuple)):
            aka = ", ".join(str(a) for a in aka)
        grp = attack_db().get("groups", {}).get(actor)
        if grp:
            aka = aka or ", ".join(grp.get("aliases", [])[:5])
            tail = f" · {esc(aka)}" if aka else ""
            cell = (f'<a class="att att--name" data-attack="{esc(actor)}" '
                    f'href="https://attack.mitre.org/groups/{esc(actor)}/" rel="noopener">{esc(grp["name"])}</a> '
                    f'<span class="aka">{esc(actor)}{tail}</span>')
        else:
            cell = esc(actor) + (f' <span class="aka">({esc(aka)})</span>' if aka else "")
        rows.append(("위협 행위자", cell, False))
    if fm.get("target"):
        rows.append(("분석 대상", esc(fm["target"]), True))
    if fm.get("tools"):
        rows.append(("도구·환경", esc(fm["tools"]), False))
    if isinstance(fm.get("meta"), dict):
        for k, v in fm["meta"].items():
            rows.append((esc(k), esc(v), False))
    if fm.get("labels"):
        chips = "".join(f'<a class="label" href="/labels/#{esc(l)}">{esc(l)}</a>' for l in fm["labels"])
        rows.append(("주제", f'<span class="labels">{chips}</span>', False))
    rows.append(("작성", esc(fm.get("analyst") or cfg.get("author", "")), False))
    cells = [f'<div><dt>{dt}</dt><dd{" class=\"mono\"" if mono else ""}>{dd}</dd></div>'
             for dt, dd, mono in rows]
    cells.insert(1, '<div id="revised-row" hidden><dt>최종 개정</dt><dd><span id="revised-slot"></span></dd></div>')
    return f'<dl class="docket">{"".join(cells)}</dl>'


def briefs_block(fm):
    items = fm.get("items")
    if not isinstance(items, list) or not items:
        return ""
    rows, secs = [], []
    for i, it in enumerate(items, 1):
        d = as_date(it.get("date"))
        rows.append(f'<tr><td class="n">{i}</td><td class="d">{f"{d.month:02d}-{d.day:02d}" if d else ""}</td>'
                    f'<td class="g">{esc(it.get("tag", ""))}</td>'
                    f'<td><a href="#brief-{i}">{esc(it.get("title", ""))}</a></td></tr>')
        meta = ""
        if d:
            meta += f'<time datetime="{d}">{d}</time>'
        if it.get("tag"):
            meta += f'<span class="chip">{esc(it["tag"])}</span>'
        refs = it.get("refs") or []
        if not isinstance(refs, list):
            refs = [refs]
        meta += "".join(f'<cite data-ref="{esc(n)}"></cite>' for n in refs)
        note = f'<p class="brief-note"><b>평가</b>{esc(it["note"])}</p>' if it.get("note") else ""
        secs.append(f'<section class="brief" id="brief-{i}"><h2>{esc(it.get("title", ""))}</h2>'
                    f'<p class="brief-meta">{meta}</p>{render_body(str(it.get("summary", "")))}{note}</section>')
    index = ('<div class="brief-index"><table><thead><tr><th>#</th><th>일자</th><th>분류</th>'
             '<th>이번 호 소식</th></tr></thead><tbody>' + "".join(rows) + '</tbody></table></div>')
    return index + "".join(secs)


def series_nav(item, reports):
    s, _, same = series_info(item, reports)
    if not s or len(same) < 2:
        return ""
    lis = []
    for i, r in enumerate(same, 1):
        title = esc(r["fm"].get("title", r["slug"]))
        on = r["slug"] == item["slug"]
        t = f'<span class="t" aria-current="page">{title}</span>' if on else f'<a href="/r/{r["slug"]}/">{title}</a>'
        lis.append(f'<li{" class=\"on\"" if on else ""}><span class="no">제{i}호</span>{t}'
                   f'<time datetime="{r["date"]}">{r["date"]}</time></li>')
    return (f'<nav class="series-nav" aria-label="{esc(s)}"><p class="series-head">{esc(s)} · 전 {len(same)}호</p>'
            f'<ol>{"".join(lis)}</ol></nav>')


def references_block(fm):
    refs = fm.get("references")
    if not refs:
        return "", ""
    lis = []
    for i, r in enumerate(refs, 1):
        url = r.get("url")
        title = esc(r.get("title", ""))
        t = f'<a class="t" href="{esc(url)}" rel="noopener">{title}</a>' if url else f'<span class="t">{title}</span>'
        meta = esc(r.get("source", ""))
        if r.get("date"):
            meta += " · " + str(as_date(r["date"]))
        if r.get("accessed"):
            meta += " · 열람 " + str(as_date(r["accessed"]))
        if r.get("note"):
            meta += " · " + esc(r["note"])
        lis.append(f'<li id="ref-{i}" data-source="{esc(r.get("source",""))}" '
                   f'data-date="{as_date(r.get("date")) or ""}">{t}<span class="meta">{meta}</span></li>')
    section = ('<section id="references" class="references"><h2 class="no-number">참고자료</h2>'
               '<ol class="reflist">' + "".join(lis) + "</ol></section>")
    return section, '<button type="button" id="ref-toggle" aria-expanded="false">참고자료 따로 보기</button>'


def report_inner(item, cfg, no, prev, nxt, reports):
    fm = item["fm"]
    site = cfg.get("title", "re:versing.zip")
    refs_section, refs_button = references_block(fm)
    abstract = ""
    if fm.get("abstract"):
        abstract = ('<section class="abstract"><h2 class="no-number">요지</h2>'
                    + render_body(str(fm["abstract"])) + "</section>")
    subtitle = f'<p class="subtitle">{esc(fm["subtitle"])}</p>' if fm.get("subtitle") else ""
    status = f' · {esc(fm["status"])}' if fm.get("status") else ""
    s, sno, _ = series_info(item, reports)
    series = f" · {esc(s)} 제{sno}호" if s else ""
    tlp = str(fm["tlp"]).upper() if fm.get("tlp") else ""
    tlp_mark = f" · TLP:{esc(tlp)}" if tlp else ""
    flag_parts = [tlp_badge(fm["tlp"])] if tlp else []
    if fm.get("severity"):
        flag_parts.append(f'<span class="sev sev--{SEV.get(str(fm["severity"]), "low")}">'
                          f'심각도 {esc(fm["severity"])}</span>')
    if item.get("draft") and local_label(item) == "초안":
        flag_parts.insert(0, '<span class="draft-flag">초안 · 발행 전</span>')
    flags = f'<p class="flags">{"".join(flag_parts)}</p>' if flag_parts else ""
    briefs = briefs_block(fm)
    art_cls = "report has-briefs" if briefs else "report"

    pn = []
    if prev:
        pn.append(f'<a href="/r/{prev["slug"]}/"><span class="dir">이전</span>{esc(prev["fm"].get("title",""))}</a>')
    if nxt:
        pn.append(f'<a class="next" href="/r/{nxt["slug"]}/"><span class="dir">다음</span>{esc(nxt["fm"].get("title",""))}</a>')
    prevnext = f'<nav class="prevnext" aria-label="다른 보고서">{"".join(pn)}</nav>' if pn else ""

    return f"""<div class="watermark" aria-hidden="true"><span class="wm-mark">{esc(site)} · {no}{tlp_mark}</span></div>
<article class="{art_cls}">
  <header class="report-head">
    <p class="docket-no">{no} · {esc(fm.get("kind","심층분석"))}{series}{status}</p>
    {flags}
    <h1>{esc(fm.get("title", item["slug"]))}</h1>
    {subtitle}
    {docket_dl(item, cfg, reports)}
    {abstract}
    <div class="toolbar">
      <button type="button" data-print title="인쇄 창이 열리면 대상을 ‘PDF로 저장’으로 고르세요. 워터마크가 함께 찍힙니다.">PDF 내려받기</button>
      {refs_button}
      <a href="/">목록</a>
    </div>
  </header>
  <nav id="toc" class="toc" aria-label="목차"></nav>
  <div class="report-body">
{briefs}{render_body(item["body"])}
  </div>
  {refs_section}
  <section id="revisions" class="revisions" data-seeded="false"><h2 class="no-number">개정 이력</h2></section>
  <div class="provenance print-only">
    <div>{esc(site)} · {no}{tlp_mark} · 발행 {item["date"]} · {esc(fm.get("analyst") or cfg.get("author",""))}</div>
    <div class="src">https://reversing.zip/r/{item["slug"]}/</div>
  </div>
  {series_nav(item, reports)}
  {prevnext}
</article>"""


DRAFT_RULE = "초안 · 로컬 전용"


def index_inner(reports, cfg):
    lede = ('<p class="lede">바이너리를 직접 뜯어보고, 확인한 것만 적습니다. '
            "도구로 파고든 분석도 있고, 도구 없이 공개된 정보만으로 짚어 본 글도 있어요. "
            "나중에 더 알게 되면 원문은 그대로 두고 날짜를 달아 덧붙입니다.</p>")
    drafts = sorted((r for r in reports if r.get("draft")), key=lambda x: x["date"] or date.min, reverse=True)
    reports = [r for r in reports if not r.get("draft")]
    if not reports and not drafts:
        return lede + "<p>아직 발행한 글이 없습니다.</p>"
    years = {}
    for r in sorted(reports, key=lambda x: x["date"] or date.min, reverse=True):
        years.setdefault(r["date"].year if r["date"] else "?", []).append(r)
    out = [lede]
    if drafts:
        years[DRAFT_RULE] = drafts
    latest = max((r["date"] for r in reports if r["date"]), default=None)
    labelset = set()
    for r in reports:
        for l in r["fm"].get("labels", []):
            labelset.add(l)
    latest_s = f"{latest.year}.{latest.month:02d}.{latest.day:02d}" if latest else "—"
    out.append(
        '<div class="stats" aria-label="기록 현황">'
        f'<div class="stat"><span class="v">{len(reports)}</span><span class="k">발행</span></div>'
        f'<div class="stat"><span class="v">{len(labelset)}</span><span class="k">주제</span></div>'
        f'<div class="stat"><span class="v">{latest_s}</span><span class="k">최근 발행</span></div>'
        "</div>"
    )
    order = ([DRAFT_RULE] if drafts else []) + sorted((y for y in years if y != DRAFT_RULE), reverse=True)
    for y in order:
        cls = "section-rule section-rule--draft" if y == DRAFT_RULE else "section-rule"
        out.append(f'<div class="{cls}">{y}</div><ul class="ledger">')
        for r in years[y]:
            fm = r["fm"]
            no = docket_no(r, reports + drafts)
            nrev = r["body"].count('class="addendum"') + r["body"].count('class="correction"')
            chips = [f'<span class="chip">{esc(fm.get("kind","심층분석"))}</span>']
            if r.get("draft") and local_label(r) == "초안":
                chips.insert(0, '<span class="chip chip--draft">초안</span>')
            s, sno, _ = series_info(r, reports + drafts)
            if s:
                chips.append(f'<span class="chip chip--series">{esc(s)} 제{sno}호</span>')
            if isinstance(fm.get("items"), list) and fm["items"]:
                chips.append(f'<span class="chip">소식 {len(fm["items"])}건</span>')
            if fm.get("tlp") and str(fm["tlp"]).upper() != "CLEAR":
                chips.append(tlp_badge(fm["tlp"]))
            if fm.get("status"):
                chips.append(f'<span class="chip chip--open">{esc(fm["status"])}</span>')
            if nrev:
                chips.append(f'<span class="chip chip--rev">개정 {nrev}회</span>')
            if fm.get("published") is False and not r.get("draft"):
                chips.append('<span class="chip">예시</span>')
            for l in fm.get("labels", []):
                chips.append(f'<a class="label" href="/labels/#{esc(l)}">{esc(l)}</a>')
            sub = f'<p class="entry-sub">{esc(fm["subtitle"])}</p>' if fm.get("subtitle") else ""
            when = f'{r["date"].month:02d}월 {r["date"].day:02d}일' if r["date"] else "날짜 없음"
            out.append(
                f'<li data-kind="{esc(fm.get("kind","심층분석"))}"><div class="entry-head"><span class="docket-no">{no}</span>'
                f'<a class="entry-title" href="/r/{r["slug"]}/">{esc(fm.get("title",r["slug"]))}</a></div>'
                f'{sub}<p class="entry-meta"><time datetime="{r["date"] or ""}">'
                f'{when}</time>{"".join(chips)}</p></li>'
            )
        out.append("</ul>")
    return "".join(out)


def labels_inner(reports, cfg):
    by = {}
    for r in reports:
        for l in r["fm"].get("labels", []):
            by.setdefault(l, []).append(r)
    if not by:
        return '<h1 style="font-size:1.4rem">주제별 색인</h1><p class="lede">아직 라벨이 없습니다.</p>'
    cloud = " ".join(f'<a href="#{esc(l)}">#{esc(l)} <span class="n">{len(by[l])}</span></a>'
                     for l in sorted(by))
    out = ['<h1 style="font-size:1.4rem;margin:0 0 .4rem">주제별 색인</h1>',
           '<p class="lede">라벨은 각 글 앞머리의 <code>labels:</code>에서 모입니다.</p>',
           f'<div class="label-cloud">{cloud}</div>']
    for l in sorted(by):
        out.append(f'<section class="label-group" id="{esc(l)}"><h2>{esc(l)}</h2><ul class="ledger">')
        for r in sorted(by[l], key=lambda x: x["date"] or date.min, reverse=True):
            out.append(
                f'<li><div class="entry-head"><span class="docket-no">{docket_no(r, reports)}</span>'
                f'<a class="entry-title" href="/r/{r["slug"]}/">{esc(r["fm"].get("title",r["slug"]))}</a></div>'
                f'<p class="entry-meta"><time datetime="{r["date"]}">{r["date"]}</time>'
                f'<span class="chip">{esc(r["fm"].get("kind","심층분석"))}</span></p></li>'
            )
        out.append("</ul></section>")
    return "".join(out)


def about_inner():
    if not ABOUT.exists():
        return "<p>소개 문서가 없습니다.</p>"
    fm, body = split_front_matter(ABOUT.read_text(encoding="utf-8"))
    title = esc(fm.get("title", "이 기록에 대하여"))
    return (f'<article class="report"><header class="report-head"><h1>{title}</h1></header>'
            f'<div class="report-body">{render_body(body)}</div></article>')


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def scrub_images(files):
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import publish
    except Exception:
        return
    n = 0
    for f in sorted(files):
        try:
            if publish.scrub_file(f):
                n += 1
        except OSError as e:
            print(f"  [주의] {f.name}: 메타데이터를 지우지 못했습니다 ({e.__class__.__name__})")
    if n:
        print(f"  그림 {n}장에서 촬영 정보(EXIF·GPS) 같은 메타데이터를 지웠습니다.")


def build(cfg, fresh=True):
    if fresh and OUT.exists():
        shutil.rmtree(OUT, ignore_errors=True)
    reports = load_reports()
    pub = [r for r in reports if not r["draft"]]
    used = set()
    write(OUT / "index.html", shell(index_inner(reports, cfg), cfg, "home"))
    write(OUT / "about" / "index.html",
          shell(resolve_images(about_inner(), ABOUT, used), cfg, "about", "이 기록에 대하여"))
    write(OUT / "labels" / "index.html",
          shell(labels_inner(pub, cfg), cfg, "labels", "주제별"))
    for r in reports:
        if r["draft"] and any(p["slug"] == r["slug"] for p in pub):
            print(f"  [주의] 초안 {r['slug']}.md 와 같은 이름의 발행 글이 있어 초안은 건너뜁니다. 초안 파일 이름을 바꾸세요.")
            continue
        no = docket_no(r, reports)
        prev = nxt = None
        if not r["draft"]:
            i = pub.index(r)
            prev = pub[i - 1] if i > 0 else None
            nxt = pub[i + 1] if i + 1 < len(pub) else None
        inner = resolve_images(report_inner(r, cfg, no, prev, nxt, reports), r["path"], used)
        write(OUT / "r" / r["slug"] / "index.html",
              shell(inner, cfg, "home", r["fm"].get("title", r["slug"])))
    scrub_images(used)
    for f in used:
        dst = OUT / f.relative_to(ROOT)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(f, dst)
    for f in FONTS.glob("*.woff2"):
        dst = OUT / "assets" / "fonts" / f.name
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(f, dst)
    if ATTACK.exists():
        dst = OUT / "assets" / "data" / ATTACK.name
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ATTACK, dst)
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import lookup
        write(OUT / "assets" / "data" / "vulns.json", json.dumps(lookup.merged(), ensure_ascii=False))
    except Exception:
        if VULNS.exists():
            write(OUT / "assets" / "data" / "vulns.json", VULNS.read_text(encoding="utf-8"))
    write(OUT / STAMP, str(time.time_ns()))
    return reports


def sync_vulns():
    """글에 새로 쓴 CVE·KVE 제목을 받아 _data/vulns.json 에 넣는다. 인터넷이 안 되면 건너뛴다."""
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import lookup
        n = lookup.sync(quiet=True, timeout=8)
        if n:
            print(f"  CVE·KVE 제목 {n}건을 새로 받아 _data/vulns.json 에 넣었습니다.")
    except Exception as e:
        print(f"  CVE·KVE 제목은 받지 못했습니다 ({e.__class__.__name__}). 번호와 링크는 그대로 붙습니다.")


def warn_tlp(reports):
    for r in reports:
        t = str(r["fm"].get("tlp", "")).upper()
        if t and t != "CLEAR" and r["fm"].get("published") is not False and not r["draft"]:
            print(f"  [주의] {r['slug']}: TLP:{t} 인데 공개 상태입니다. "
                  "공개 사이트에는 TLP:CLEAR만 올리고, 나머지는 초안 폴더나 published: false 로 두세요.")


def watched():
    files = [ABOUT, ROOT / "_config.yml"]
    files += list(REPORTS.glob("*.md")) + list(DRAFTS.glob("**/*"))
    files += list((ROOT / "assets").glob("**/*")) + list((ROOT / "_data").glob("*.json"))
    sig = {}
    for f in files:
        try:
            if f.is_file():
                st = f.stat()
                sig[f] = (st.st_mtime_ns, st.st_size)
        except OSError:
            pass
    return sig


def watch(args):
    base = watched()
    while True:
        time.sleep(0.4)
        now = watched()
        if now == base:
            continue
        time.sleep(0.15)
        now = watched()
        changed = sorted({f for f in set(now) | set(base) if now.get(f) != base.get(f)})
        names = ", ".join(f.name for f in changed[:3]) + (f" 외 {len(changed) - 3}개" if len(changed) > 3 else "")
        md = [f for f in changed if f.suffix == ".md" and f.parent in (REPORTS, DRAFTS) and f.exists()]
        link = f"  http://localhost:{PORT}/r/{md[0].stem}/" if md else ""
        try:
            if not args.no_sync:
                sync_vulns()
            reports = build(load_config(), fresh=False)
            warn_tlp(reports)
            print(f"  {time.strftime('%H:%M:%S')}  다시 빌드  ({names}){link}")
        except Exception as e:
            print(f"  {time.strftime('%H:%M:%S')}  빌드하지 못했습니다 ({names}): {e.__class__.__name__}: {e}")
        base = watched()


class Server(http.server.ThreadingHTTPServer):
    allow_reuse_address = False
    daemon_threads = True


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_GET(self):
        if self.path.split("?", 1)[0] == "/__events":
            return self.events()
        return super().do_GET()

    def events(self):
        """빌드가 바뀔 때마다 열린 페이지에 알린다. 숨겨진 창에서도 받는다."""
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.end_headers()
        stamp, last, idle = OUT / STAMP, None, 0.0
        try:
            while True:
                try:
                    cur = stamp.read_text(encoding="utf-8").strip()
                except OSError:
                    cur = last
                if cur and cur != last:
                    self.wfile.write(f"data: {cur}\n\n".encode("ascii"))
                    self.wfile.flush()
                    last, idle = cur, 0.0
                elif idle >= 15:
                    self.wfile.write(b": ping\n\n")
                    self.wfile.flush()
                    idle = 0.0
                time.sleep(0.25)
                idle += 0.25
        except OSError:
            return


def latest_report():
    files = [f for f in list(REPORTS.glob("*.md")) + list(DRAFTS.glob("*.md")) if f.is_file()]
    return max(files, key=lambda f: f.stat().st_mtime) if files else None


def show_links(port):
    base = f"http://localhost:{port}/"
    print(f"    목록     {base}")
    f = latest_report()
    if f:
        print(f"    최근 글  {base}r/{f.stem}/")
    if IN_VSCODE:
        print("    주소를 Ctrl+클릭하면 VS Code 안 옆 칸에 열립니다.")
    return f"{base}r/{f.stem}/" if f else base


def open_page(url, args):
    if args.no_open or IN_VSCODE:
        return
    try:
        webbrowser.open(url)
    except Exception:
        pass


def already_running(port):
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/{STAMP}", timeout=0.8) as r:
            return r.status == 200
    except Exception:
        return False


def main():
    global LIVE
    ap = argparse.ArgumentParser(description="로컬 미리보기 서버")
    ap.add_argument("-p", "--port", type=int, default=8787)
    ap.add_argument("--build", action="store_true", help="서빙 없이 파일만 생성")
    ap.add_argument("--watch", action="store_true", help="저장할 때마다 다시 빌드하고 브라우저를 새로 고침")
    ap.add_argument("--no-open", action="store_true", help="브라우저 자동 실행 안 함")
    ap.add_argument("--no-sync", action="store_true", help="CVE·KVE 제목을 받지 않음")
    args = ap.parse_args()

    if not args.build and already_running(args.port):
        LIVE = True
        if not args.no_sync:
            sync_vulns()
        build(load_config(), fresh=False)
        print("\n  미리보기가 이미 켜져 있어 다시 빌드만 했습니다.")
        url = show_links(args.port)
        print()
        open_page(url, args)
        return

    LIVE = args.watch and not args.build
    if not args.no_sync:
        sync_vulns()
    cfg = load_config()
    reports = build(cfg)
    nd = sum(1 for r in reports if r["draft"])
    print(f"  빌드 완료: 보고서 {len(reports) - nd}편" + (f" · 초안 {nd}편" if nd else "") + " + 목록·주제별·소개")
    warn_tlp(reports)

    if args.build:
        print(f"  위치: {OUT}")
        return

    handler = partial(Quiet, directory=str(OUT))
    httpd = None
    for port in range(args.port, args.port + 20):
        try:
            httpd = Server(("127.0.0.1", port), handler)
            break
        except OSError:
            continue
    if httpd is None:
        sys.exit("빈 포트를 찾지 못했습니다.")

    global PORT
    PORT = port
    print("\n  로컬 미리보기가 열렸습니다.")
    url = show_links(port)
    if LIVE:
        print("    글·그림·스타일을 저장하면 다시 빌드하고 열린 브라우저도 새로 고칩니다.")
        threading.Thread(target=watch, args=(args,), daemon=True).start()
    print("    종료: Ctrl+C\n")
    open_page(url, args)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n  종료했습니다.")
        httpd.server_close()


if __name__ == "__main__":
    main()
