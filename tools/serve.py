import argparse
import html
import http.server
import re
import sys
import threading
import webbrowser
from datetime import date, datetime
from pathlib import Path

try:
    import markdown
    import yaml
    from pygments import highlight
    from pygments.formatters import HtmlFormatter
    from pygments.lexers import get_lexer_by_name
    from pygments.util import ClassNotFound
except ImportError as e:
    sys.exit(f"필요한 패키지가 없습니다 ({e.name}).  실행:  python -m pip install markdown pyyaml pygments")

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "_reports"
ASSETS = ROOT / "assets"

FRONT = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)
FENCE = re.compile(r'<pre><code class="language-([\w+.-]+)">(.*?)</code></pre>', re.S)
RAW_LANGS = {"chart", "mermaid", "text", "txt", "plain"}

MD = markdown.Markdown(
    extensions=["fenced_code", "tables", "footnotes", "attr_list", "md_in_html", "sane_lists"],
    extension_configs={"footnotes": {"BACKLINK_TEXT": "↩︎", "BACKLINK_TITLE": ""}},
)


def load_config():
    with open(ROOT / "_config.yml", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def to_date(v):
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    if isinstance(v, str):
        try:
            return date.fromisoformat(v[:10])
        except ValueError:
            return None
    return None


def fmt(v, style="%Y-%m-%d"):
    d = to_date(v)
    if d:
        return d.strftime(style)
    return str(v) if v else ""


def korean_date(v):
    d = to_date(v)
    return f"{d.year}년 {d.month}월 {d.day}일" if d else fmt(v)


def load_reports():
    out = []
    for p in sorted(REPORTS.glob("*.md")):
        text = p.read_text(encoding="utf-8")
        m = FRONT.match(text)
        meta = (yaml.safe_load(m.group(1)) if m else None) or {}
        meta.setdefault("kind", "심층분석")
        out.append({"slug": p.stem, "path": f"_reports/{p.name}", "meta": meta,
                    "body": text[m.end():] if m else text})
    out.sort(key=lambda r: (to_date(r["meta"].get("date")) or date.min, r["slug"]))
    return out


def docket_no(report, reports):
    if report["meta"].get("docket"):
        return str(report["meta"]["docket"])
    d = to_date(report["meta"].get("date")) or date.today()
    n = 0
    for r in reports:
        rd = to_date(r["meta"].get("date")) or date.today()
        if rd.year == d.year:
            n += 1
            if r is report:
                break
    return f"{d.year}-{n:03d}"


def fence_repl(m):
    lang, code = m.group(1), html.unescape(m.group(2))
    inner = None
    if lang not in RAW_LANGS:
        try:
            inner = highlight(code, get_lexer_by_name(lang), HtmlFormatter(nowrap=True))
        except ClassNotFound:
            inner = None
    if inner is None:
        inner = html.escape(code)
    return (f'<div class="language-{lang} highlighter-rouge"><div class="highlight">'
            f'<pre class="highlight"><code>{inner}</code></pre></div></div>')


def render_md(src):
    MD.reset()
    out = MD.convert(src)
    out = out.replace('<div class="footnote">', '<div class="footnotes" role="doc-endnotes">')
    out = re.sub(r'(<div class="footnotes" role="doc-endnotes">)\s*<hr\s*/?>', r"\1", out)
    out = re.sub(r'<sup id="fnref:([^"]+)"><a class="footnote-ref"',
                 r'<sup id="fnref:\1" role="doc-noteref"><a class="footnote" rel="footnote"', out)
    out = out.replace('class="footnote-backref"', 'class="reversefootnote" role="doc-backlink"')
    out = FENCE.sub(fence_repl, out)
    return out


def esc(s):
    return html.escape(str(s), quote=True)


def slugify(s):
    s = re.sub(r"[^\w\s-]", "", str(s).lower()).strip()
    return re.sub(r"[\s_]+", "-", s)


def strip_tags(s):
    return re.sub(r"<[^>]+>", "", s).strip()


def render_report(report, reports, cfg, export=False):
    meta = report["meta"]
    no = docket_no(report, reports)
    title = cfg.get("title", "")
    author = meta.get("analyst") or cfg.get("author", "")
    body = render_md(report["body"])

    abstract_html = render_md(str(meta["abstract"])) if meta.get("abstract") else ""
    desc = strip_tags(abstract_html) or cfg.get("description", "")
    desc = (desc[:177] + "...") if len(desc) > 180 else desc

    css_href = "/assets/css/report.css"
    js_src = "/assets/js/report.js"
    if export:
        css_tag = "<style>\n" + (ASSETS / "css" / "report.css").read_text(encoding="utf-8") + "\n</style>"
        js_tag = "<script>\n" + (ASSETS / "js" / "report.js").read_text(encoding="utf-8") + "\n</script>"
    else:
        css_tag = f'<link rel="stylesheet" href="{css_href}">'
        js_tag = f'<script src="{js_src}" defer></script>'

    rows = [f'<div><dt>발행</dt><dd><time datetime="{fmt(meta.get("date"))}">{korean_date(meta.get("date"))}</time></dd></div>']
    revised = meta.get("revised")
    rows.append(f'<div id="revised-row"{"" if revised else " hidden"}><dt>최종 개정</dt>'
                f'<dd><span id="revised-slot">{fmt(revised) if revised else ""}</span></dd></div>')
    if meta.get("target"):
        rows.append(f'<div><dt>분석 대상</dt><dd class="mono">{esc(meta["target"])}</dd></div>')
    if meta.get("tools"):
        rows.append(f'<div><dt>도구·환경</dt><dd>{esc(meta["tools"])}</dd></div>')
    if meta.get("labels"):
        labels = "".join(f'<a class="label" href="#labels-{slugify(l)}">{esc(l)}</a>' for l in meta["labels"])
        rows.append(f'<div><dt>주제</dt><dd class="labels">{labels}</dd></div>')
    rows.append(f'<div><dt>작성</dt><dd>{esc(author)}</dd></div>')

    refs = meta.get("references") or []
    ref_html = ""
    if refs:
        items = []
        for i, r in enumerate(refs, 1):
            t = esc(r.get("title", ""))
            head = f'<a class="t" href="{esc(r["url"])}" rel="noopener">{t}</a>' if r.get("url") else f'<span class="t">{t}</span>'
            bits = [esc(r.get("source", ""))]
            if r.get("date"):
                bits.append(fmt(r["date"]))
            if r.get("accessed"):
                bits.append("열람 " + fmt(r["accessed"]))
            if r.get("note"):
                bits.append(esc(r["note"]))
            items.append(f'<li id="ref-{i}" data-source="{esc(r.get("source", ""))}" data-date="{fmt(r.get("date"))}">'
                         f'{head}<span class="meta">{" · ".join(b for b in bits if b)}</span></li>')
        ref_html = ('<section id="references" class="references"><h2 class="no-number">참고자료</h2>'
                    '<ol class="reflist">' + "".join(items) + "</ol></section>")

    status = f' · {esc(meta["status"])}' if meta.get("status") else ""
    subtitle = f'<p class="subtitle">{esc(meta["subtitle"])}</p>' if meta.get("subtitle") else ""
    abstract = f'<section class="abstract"><h2 class="no-number">요지</h2>{abstract_html}</section>' if abstract_html else ""
    ref_btn = '<button type="button" id="ref-toggle" aria-expanded="false">참고자료 따로 보기</button>' if refs else ""

    if export:
        nav = ""
        toolbar_tail = ""
        prevnext = ""
        canonical = ""
    else:
        nav = ('<nav class="site-nav wrap" aria-label="주 메뉴">'
               '<a href="/" aria-current="page">보고서</a>'
               '<a href="/labels/">주제별</a><a href="/about/">이 기록에 대하여</a><a href="/feed.xml">구독</a></nav>')
        toolbar_tail = '<a href="/">목록</a>'
        idx = reports.index(report)
        links = []
        if idx > 0:
            p = reports[idx - 1]
            links.append(f'<a href="/r/{p["slug"]}/"><span class="dir">이전</span>{esc(p["meta"].get("title", ""))}</a>')
        if idx < len(reports) - 1:
            n = reports[idx + 1]
            links.append(f'<a class="next" href="/r/{n["slug"]}/"><span class="dir">다음</span>{esc(n["meta"].get("title", ""))}</a>')
        prevnext = f'<nav class="prevnext" aria-label="다른 보고서">{"".join(links)}</nav>' if links else ""
        canonical = f'<link rel="canonical" href="/r/{report["slug"]}/">'

    return f"""<!doctype html>
<html lang="{cfg.get('lang', 'ko')}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(meta.get('title', ''))} — {esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="author" content="{esc(author)}">
{canonical}
{css_tag}
<script>
try {{
  var t = localStorage.getItem('rev-theme');
  if (t === 'dark' || t === 'light') document.documentElement.setAttribute('data-theme', t);
}} catch (e) {{}}
</script>
</head>
<body>
<a class="skip" href="#main">본문 바로가기</a>
<header class="masthead">
  <a class="wordmark" href="/">{esc(title)}</a>
  {f'<p class="tagline">{esc(cfg["tagline"])}</p>' if cfg.get("tagline") else ""}
</header>
{nav}
<main id="main" class="wrap">
<div class="watermark" aria-hidden="true"><span class="wm-mark">{esc(title)} · {no}</span></div>
<article class="report">
  <header class="report-head">
    <p class="docket-no">{no} · {esc(meta.get('kind', '심층분석'))}{status}</p>
    <h1>{esc(meta.get('title', ''))}</h1>
    {subtitle}
    <dl class="docket">{"".join(rows)}</dl>
    {abstract}
    <div class="toolbar">
      <button type="button" data-print>PDF 내려받기</button>
      {ref_btn}
      {toolbar_tail}
    </div>
  </header>
  <nav id="toc" class="toc" aria-label="목차"></nav>
  <div class="report-body">
{body}
  </div>
  {ref_html}
  <section id="revisions" class="revisions" data-seeded="false"><h2 class="no-number">개정 이력</h2></section>
  <div class="provenance print-only">
    <div>{esc(title)} · {no} · 발행 {fmt(meta.get('date'))} · {esc(author)}</div>
    <div class="src">/r/{report['slug']}/</div>
  </div>
  <div class="pdf-bar">
    <button type="button" data-print>PDF 내려받기</button>
    <span class="hint">인쇄 대화상자에서 대상을 “PDF로 저장”으로 고르면 됩니다. 워터마크가 함께 찍힙니다.</span>
  </div>
  {prevnext}
</article>
</main>
<footer class="colophon wrap">
  <span>© {date.today().year} {esc(cfg.get('author', ''))} · {esc(title)}</span>
  <span class="right"><button type="button" id="theme-toggle" aria-label="화면 밝기">◐ 자동</button></span>
</footer>
{js_tag}
</body>
</html>
"""


def not_found(cfg, msg):
    return f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>{esc(cfg.get('title',''))}</title>
<link rel="stylesheet" href="/assets/css/report.css"></head><body>
<header class="masthead"><a class="wordmark" href="/">{esc(cfg.get('title',''))}</a></header>
<main class="wrap"><p class="lede" style="margin-top:3rem">{msg}</p></main></body></html>"""


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(ROOT), **kw)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt_, *args):
        sys.stdout.write("  %s\n" % (fmt_ % args))

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path.startswith("/assets/"):
            return super().do_GET()

        cfg = load_config()
        reports = load_reports()
        target = None
        if path == "/":
            target = reports[-1] if reports else None
        else:
            m = re.fullmatch(r"/r/([\w.-]+)/?", path)
            if m:
                target = next((r for r in reports if r["slug"] == m.group(1)), None)

        if target is None:
            if path == "/":
                page, status = not_found(cfg, "_reports/ 에 보고서가 없습니다."), 404
            else:
                page, status = not_found(cfg, "로컬 미리보기는 보고서 페이지만 렌더합니다. 목록·주제별·소개는 GitHub Pages 배포본에서 확인하세요."), 404
        else:
            try:
                page, status = render_report(target, reports, cfg), 200
            except Exception as e:
                page, status = not_found(cfg, f"렌더 중 오류: {esc(e)}"), 500

        data = page.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main():
    ap = argparse.ArgumentParser(description="보고서 하나를 로컬에서 렌더해 보여 준다.")
    ap.add_argument("slug", nargs="?", help="_reports/ 파일 이름(확장자 제외). 없으면 최신 글")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--no-open", action="store_true", help="브라우저를 자동으로 열지 않는다")
    ap.add_argument("--export", metavar="FILE", help="서버를 띄우지 않고 단일 HTML 파일로 내보낸다 (CSS/JS 포함)")
    args = ap.parse_args()

    cfg = load_config()
    reports = load_reports()
    if not reports:
        sys.exit("_reports/ 에 .md 파일이 없습니다.")

    target = reports[-1]
    if args.slug:
        target = next((r for r in reports if r["slug"] == args.slug), None)
        if target is None:
            sys.exit(f"'{args.slug}' 을(를) 찾을 수 없습니다. 있는 글: " + ", ".join(r["slug"] for r in reports))

    if args.export:
        out = Path(args.export)
        out.write_text(render_report(target, reports, cfg, export=True), encoding="utf-8")
        print(f"내보냈습니다: {out}  ({out.stat().st_size:,} bytes)")
        return

    url = f"http://127.0.0.1:{args.port}/r/{target['slug']}/"
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"\n  {url}\n  Ctrl+C 로 종료. 마크다운을 고치고 새로고침하면 바로 반영됩니다.\n")
    if not args.no_open:
        threading.Timer(0.4, webbrowser.open, args=(url,)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.server_close()


if __name__ == "__main__":
    main()
