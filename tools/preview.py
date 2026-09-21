#!/usr/bin/env python3
"""로컬 미리보기.

Ruby/Jekyll 없이 파이썬만으로 사이트 전체를 실제 조판 그대로 빌드하여
localhost 에 띄웁니다. 발행 목록, 각 보고서, 주제별 색인, 소개 페이지가
모두 연결되므로 링크가 실제로 동작합니다. GitHub Pages 로 나갈 결과와
같은 화면을 확인하는 용도이며, 공개 사이트에서 숨긴(published:false) 예시
글도 로컬에서는 표시됩니다.

    python tools/preview.py            # http://localhost:8787 에서 서빙
    python tools/preview.py -p 9000    # 포트 지정
    python tools/preview.py --build    # 서빙 없이 _preview/ 만 생성

필요 패키지: markdown, pyyaml, pygments
    python -m pip install markdown pyyaml pygments
"""
import argparse
import html
import http.server
import re
import socketserver
import sys
import webbrowser
from datetime import date, datetime
from functools import partial
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "_reports"
CSS = ROOT / "assets" / "css" / "report.css"
JS = ROOT / "assets" / "js" / "report.js"
ABOUT = ROOT / "about.md"
OUT = ROOT / "_preview"

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
    for p in sorted(REPORTS.glob("*.md")):
        fm, body = split_front_matter(p.read_text(encoding="utf-8"))
        items.append({"slug": p.stem, "fm": fm, "body": body, "date": as_date(fm.get("date"))})
    items.sort(key=lambda x: x["date"] or date.min)
    return items


def docket_no(item, reports):
    fm = item["fm"]
    if fm.get("docket"):
        return str(fm["docket"])
    d = item["date"]
    if not d:
        return "----"
    seq, n = 0, 0
    for r in reports:
        if r["date"] and r["date"].year == d.year:
            n += 1
            if r["slug"] == item["slug"]:
                seq = n
    return f"{d.year}-{seq:03d}"


# ---- mermaid/chart 펜스는 강조하지 않고 원문 그대로 보존한다 ----
FENCE = re.compile(r"^([ \t]*)```[ \t]*(mermaid|chart)[ \t]*\n(.*?)\n[ \t]*```[ \t]*$",
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
        out = re.sub(rf"<p>\s*RAWFENCE{i}ENDRAW\s*</p>", block, out)
        out = out.replace(f"RAWFENCE{i}ENDRAW", block)
    return out


def esc(s):
    return html.escape(str(s), quote=True)


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
    js = JS.read_text(encoding="utf-8")
    tab = f"{page_title} — {site}" if page_title else site

    def nav(href, label, key):
        cur = ' aria-current="page"' if key == current else ""
        return f'<a href="{href}"{cur}>{label}</a>'

    navbar = (nav("/", "발행 목록", "home") + nav("/labels/", "주제별", "labels")
              + nav("/about/", "이 기록에 대하여", "about"))

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
<header class="masthead">
  <a class="wordmark" href="/">{wordmark(site)}</a>
  <p class="tagline">{esc(tagline)}</p>
</header>
<nav class="site-nav wrap" aria-label="주 메뉴">{navbar}</nav>
<main id="main" class="wrap">
{inner}
</main>
<footer class="colophon wrap">
  <span>© {date.today().year} {esc(cfg.get("author",""))} · {esc(site)}</span>
  <span class="right"><button type="button" id="theme-toggle" aria-label="화면 밝기">◐ 자동</button></span>
</footer>
<script>{js}</script>
</body>
</html>
"""


def docket_dl(item, cfg):
    fm = item["fm"]
    rows = [("발행", f'<time datetime="{item["date"]}">{ko_date(item["date"])}</time>', False)]
    if fm.get("target"):
        rows.append(("분석 대상", esc(fm["target"]), True))
    if fm.get("tools"):
        rows.append(("도구·환경", esc(fm["tools"]), False))
    if fm.get("labels"):
        chips = "".join(f'<a class="label" href="/labels/#{esc(l)}">{esc(l)}</a>' for l in fm["labels"])
        rows.append(("주제", f'<span class="labels">{chips}</span>', False))
    rows.append(("작성", esc(fm.get("analyst") or cfg.get("author", "")), False))
    body = "".join(f'<div><dt>{dt}</dt><dd{" class=\"mono\"" if mono else ""}>{dd}</dd></div>'
                   for dt, dd, mono in rows)
    return f'<dl class="docket">{body}</dl>'


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


def report_inner(item, cfg, no, prev, nxt):
    fm = item["fm"]
    site = cfg.get("title", "re:versing.zip")
    refs_section, refs_button = references_block(fm)
    abstract = ""
    if fm.get("abstract"):
        abstract = ('<section class="abstract"><h2 class="no-number">요지</h2>'
                    + render_body(str(fm["abstract"])) + "</section>")
    subtitle = f'<p class="subtitle">{esc(fm["subtitle"])}</p>' if fm.get("subtitle") else ""
    status = f' · {esc(fm["status"])}' if fm.get("status") else ""

    pn = []
    if prev:
        pn.append(f'<a href="/r/{prev["slug"]}/"><span class="dir">이전</span>{esc(prev["fm"].get("title",""))}</a>')
    if nxt:
        pn.append(f'<a class="next" href="/r/{nxt["slug"]}/"><span class="dir">다음</span>{esc(nxt["fm"].get("title",""))}</a>')
    prevnext = f'<nav class="prevnext" aria-label="다른 보고서">{"".join(pn)}</nav>' if pn else ""

    return f"""<div class="watermark" aria-hidden="true"><span class="wm-mark">{esc(site)} · {no}</span></div>
<article class="report">
  <header class="report-head">
    <p class="docket-no">{no} · {esc(fm.get("kind","심층분석"))}{status}</p>
    <h1>{esc(fm.get("title", item["slug"]))}</h1>
    {subtitle}
    {docket_dl(item, cfg)}
    {abstract}
    <div class="toolbar">
      <button type="button" data-print>PDF 내려받기</button>
      {refs_button}
      <a href="/">목록</a>
    </div>
  </header>
  <nav id="toc" class="toc" aria-label="목차"></nav>
  <div class="report-body">
{render_body(item["body"])}
  </div>
  {refs_section}
  <section id="revisions" class="revisions" data-seeded="false"><h2 class="no-number">개정 이력</h2></section>
  <div class="provenance print-only">
    <div>{esc(site)} · {no} · 발행 {item["date"]} · {esc(fm.get("analyst") or cfg.get("author",""))}</div>
    <div class="src">https://reversing.zip/r/{item["slug"]}/</div>
  </div>
  <div class="pdf-bar">
    <button type="button" data-print>PDF 내려받기</button>
    <span class="hint">인쇄 대화상자에서 대상을 “PDF로 저장”으로 선택하면 됩니다. 워터마크가 함께 표기됩니다.</span>
  </div>
  {prevnext}
</article>"""


def index_inner(reports, cfg):
    lede = ('<p class="lede">바이너리를 직접 뜯어보고, 확인한 것만 적습니다. '
            "도구로 파고든 분석도 있고, 도구 없이 공개된 정보만으로 짚어 본 글도 있어요. "
            "나중에 더 알게 되면 원문은 그대로 두고 날짜를 달아 덧붙입니다.</p>")
    if not reports:
        return lede + "<p>아직 발행한 글이 없습니다.</p>"
    years = {}
    for r in sorted(reports, key=lambda x: x["date"] or date.min, reverse=True):
        years.setdefault(r["date"].year if r["date"] else "?", []).append(r)
    out = [lede]
    for y in sorted(years, reverse=True):
        out.append(f'<div class="section-rule">{y}</div><ul class="ledger">')
        for r in years[y]:
            fm = r["fm"]
            no = docket_no(r, reports)
            nrev = r["body"].count('class="addendum"') + r["body"].count('class="correction"')
            chips = [f'<span class="chip">{esc(fm.get("kind","심층분석"))}</span>']
            if fm.get("status"):
                chips.append(f'<span class="chip chip--open">{esc(fm["status"])}</span>')
            if nrev:
                chips.append(f'<span class="chip chip--rev">개정 {nrev}회</span>')
            if fm.get("published") is False:
                chips.append('<span class="chip">예시</span>')
            for l in fm.get("labels", []):
                chips.append(f'<a class="label" href="/labels/#{esc(l)}">{esc(l)}</a>')
            sub = f'<p class="entry-sub">{esc(fm["subtitle"])}</p>' if fm.get("subtitle") else ""
            out.append(
                f'<li><div class="entry-head"><span class="docket-no">{no}</span>'
                f'<a class="entry-title" href="/r/{r["slug"]}/">{esc(fm.get("title",r["slug"]))}</a></div>'
                f'{sub}<p class="entry-meta"><time datetime="{r["date"]}">'
                f'{r["date"].month:02d}월 {r["date"].day:02d}일</time>{"".join(chips)}</p></li>'
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


def build(cfg):
    reports = load_reports()
    write(OUT / "index.html", shell(index_inner(reports, cfg), cfg, "home"))
    write(OUT / "about" / "index.html",
          shell(about_inner(), cfg, "about", "이 기록에 대하여"))
    write(OUT / "labels" / "index.html",
          shell(labels_inner(reports, cfg), cfg, "labels", "주제별"))
    for i, r in enumerate(reports):
        no = docket_no(r, reports)
        prev = reports[i - 1] if i > 0 else None
        nxt = reports[i + 1] if i + 1 < len(reports) else None
        inner = report_inner(r, cfg, no, prev, nxt)
        write(OUT / "r" / r["slug"] / "index.html",
              shell(inner, cfg, "home", r["fm"].get("title", r["slug"])))
    return reports


def main():
    ap = argparse.ArgumentParser(description="로컬 미리보기 서버")
    ap.add_argument("-p", "--port", type=int, default=8787)
    ap.add_argument("--build", action="store_true", help="서빙 없이 파일만 생성")
    ap.add_argument("--no-open", action="store_true", help="브라우저 자동 실행 안 함")
    args = ap.parse_args()

    cfg = load_config()
    reports = build(cfg)
    print(f"  빌드 완료: 보고서 {len(reports)}편 + 목록·주제별·소개")

    if args.build:
        print(f"  위치: {OUT}")
        return

    handler = partial(http.server.SimpleHTTPRequestHandler, directory=str(OUT))
    socketserver.TCPServer.allow_reuse_address = True
    httpd = None
    for port in range(args.port, args.port + 20):
        try:
            httpd = socketserver.TCPServer(("127.0.0.1", port), handler)
            break
        except OSError:
            continue
    if httpd is None:
        sys.exit("빈 포트를 찾지 못했습니다.")

    url = f"http://localhost:{port}/"
    print("\n  로컬 미리보기가 열렸습니다.")
    print(f"    {url}")
    print("    발행 목록·주제별·소개·각 보고서 링크가 모두 동작합니다.")
    print("    종료: Ctrl+C\n")
    if not args.no_open:
        try:
            webbrowser.open(url)
        except Exception:
            pass
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n  종료했습니다.")
        httpd.server_close()


if __name__ == "__main__":
    main()
