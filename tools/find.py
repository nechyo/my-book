#!/usr/bin/env python3
"""자료 찾기.

글을 쓰다가 낱말 몇 개로 참고할 자료를 찾는다. 결과 앞의 번호를 고르면 글 앞머리
references: 에 바로 들어가고, 본문에 끼울 <cite> 줄을 알려 준다.

찾는 곳
    ATT&CK 인용 문헌   그룹·소프트웨어·캠페인 이름이 맞으면 MITRE가 그 항목에 인용한 보고서
    KISA 보안공지      KISA 사이버 보안 취약점 정보 포털의 보안 업데이트 권고
    CVE                같은 포털의 CVE 검색. 번호만 본문에 쓰면 출처는 자동으로 붙는다
    웹                 기술 문서를 위로, 뉴스는 아래로. SEARXNG_URL 이 가리키는 검색 엔진이
                       켜져 있으면 그것을, 아니면 DuckDuckGo 를 쓴다

    python tools/find.py lazarus npm
    python tools/find.py dream job --only attack
    python tools/find.py ivanti --into _reports/my-post.md            # 번호를 골라 앞머리에 넣기
    python tools/find.py ivanti --into _reports/my-post.md --pick "1 3"
"""
import argparse
import gzip
import html
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lookup  # noqa: E402

ROOT = lookup.ROOT
REFS = ROOT / "tools" / "attack-refs.json.gz"
REPORTS = ROOT / "_reports"
KNVD = lookup.KNVD
SEARXNG = os.environ.get("SEARXNG_URL", "http://127.0.0.1:8888").rstrip("/")
BROWSER = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                         "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"}
KST = timezone(timedelta(hours=9))
SOURCES = ("attack", "kisa", "cve", "web")

MONTHS = {m: i for i, m in enumerate(
    ("january", "february", "march", "april", "may", "june", "july", "august",
     "september", "october", "november", "december"), 1)}

PUBLISHERS = {
    "attack.mitre.org": "MITRE ATT&CK", "mitre.org": "MITRE",
    "mandiant.com": "Mandiant", "fireeye.com": "FireEye",
    "microsoft.com": "Microsoft", "learn.microsoft.com": "Microsoft Learn", "msrc.microsoft.com": "Microsoft MSRC",
    "securelist.com": "Kaspersky", "kaspersky.com": "Kaspersky",
    "unit42.paloaltonetworks.com": "Unit 42", "paloaltonetworks.com": "Palo Alto Networks",
    "crowdstrike.com": "CrowdStrike", "symantec.com": "Symantec", "security.com": "Symantec",
    "welivesecurity.com": "ESET", "eset.com": "ESET",
    "talosintelligence.com": "Cisco Talos", "cisco.com": "Cisco",
    "trendmicro.com": "Trend Micro", "sentinelone.com": "SentinelOne", "proofpoint.com": "Proofpoint",
    "checkpoint.com": "Check Point", "fortinet.com": "Fortinet", "sophos.com": "Sophos",
    "zscaler.com": "Zscaler", "elastic.co": "Elastic", "volexity.com": "Volexity",
    "recordedfuture.com": "Recorded Future", "group-ib.com": "Group-IB", "intezer.com": "Intezer",
    "reversinglabs.com": "ReversingLabs", "socket.dev": "Socket", "sonatype.com": "Sonatype",
    "phylum.io": "Phylum", "checkmarx.com": "Checkmarx", "jamf.com": "Jamf", "objective-see.org": "Objective-See",
    "huntress.com": "Huntress", "redcanary.com": "Red Canary", "thedfirreport.com": "The DFIR Report",
    "securityintelligence.com": "IBM X-Force", "ibm.com": "IBM", "lookout.com": "Lookout",
    "blog.google": "Google", "googleprojectzero.blogspot.com": "Project Zero",
    "ahnlab.com": "AhnLab", "asec.ahnlab.com": "AhnLab ASEC", "genians.co.kr": "Genians",
    "s2w.inc": "S2W", "estsecurity.com": "ESTsecurity", "alyac.co.kr": "ESTsecurity",
    "krcert.or.kr": "KISA", "boho.or.kr": "KISA", "kisa.or.kr": "KISA",
    "jpcert.or.jp": "JPCERT/CC", "cert.gov.ua": "CERT-UA",
    "cisa.gov": "CISA", "us-cert.gov": "CISA", "fbi.gov": "FBI", "ic3.gov": "FBI IC3", "nsa.gov": "NSA",
    "ncsc.gov.uk": "NCSC", "ncsc.go.kr": "국가사이버안보센터", "nis.go.kr": "국가정보원", "cyber.gov.au": "ASD", "nist.gov": "NIST", "nvd.nist.gov": "NVD", "cve.org": "CVE",
    "github.com": "GitHub", "malpedia.caad.fkie.fraunhofer.de": "Malpedia", "virustotal.com": "VirusTotal",
    "mcafee.com": "McAfee", "trellix.com": "Trellix", "clearskysec.com": "ClearSky", "logpresso.com": "Logpresso",
    "securityscorecard.com": "SecurityScorecard", "nccgroup.com": "NCC Group", "welivesecurity.eu": "ESET",
    "cybereason.com": "Cybereason", "bitdefender.com": "Bitdefender", "avast.com": "Avast", "gendigital.com": "Gen",
    "hp.com": "HP Wolf Security", "threatbook.io": "ThreatBook", "qianxin.com": "QiAnXin", "nsfocus.com": "NSFOCUS",
    "citizenlab.ca": "Citizen Lab", "amnesty.org": "Amnesty Tech", "dragos.com": "Dragos", "claroty.com": "Claroty",
    "rapid7.com": "Rapid7", "tenable.com": "Tenable", "qualys.com": "Qualys", "wiz.io": "Wiz", "datadoghq.com": "Datadog",
    "aquasec.com": "Aqua Security", "sysdig.com": "Sysdig", "cloudflare.com": "Cloudflare", "akamai.com": "Akamai",
}
NEWS = {
    "thehackernews.com", "bleepingcomputer.com", "therecord.media", "securityweek.com", "darkreading.com",
    "cybernoz.com", "gbhackers.com", "cybersecuritynews.com", "infosecurity-magazine.com", "scmagazine.com",
    "zdnet.com", "zdnet.co.kr", "boannews.com", "dailysecu.com", "etnews.com", "yna.co.kr", "hackread.com",
    "securityaffairs.com", "theregister.com", "techcrunch.com", "wired.com", "reuters.com", "bloomberg.com",
    "cyberscoop.com", "helpnetsecurity.com", "dailysecurityreview.com", "bankinfosecurity.com", "csoonline.com",
    "databreaches.net", "redpacketsecurity.com", "cysecurity.news", "teiss.co.uk", "itworld.co.kr",
    "ddaily.co.kr", "digitaltoday.co.kr", "news1.kr", "newsis.com", "hankyung.com", "mk.co.kr", "chosun.com",
    "joongang.co.kr", "donga.com", "hani.co.kr", "khan.co.kr", "nocutnews.co.kr", "kbs.co.kr", "sbs.co.kr",
    "mbc.co.kr", "jtbc.co.kr", "ytn.co.kr", "bloter.net", "inews24.com", "edaily.co.kr", "sedaily.com",
    "wikipedia.org", "namu.wiki", "voakorea.com", "voanews.com", "rfa.org", "nknews.org", "dailynk.com",
    "cnn.com", "bbc.com", "bbc.co.uk", "nytimes.com", "washingtonpost.com", "wsj.com", "forbes.com",
    "arstechnica.com", "theverge.com", "vice.com", "computerweekly.com", "itpro.com", "techradar.com",
}
DROP = {"youtube.com", "facebook.com", "x.com", "twitter.com", "linkedin.com", "reddit.com", "instagram.com",
        "tiktok.com", "pinterest.com", "quora.com", "infosec.exchange", "mastodon.social", "bsky.app",
        "threads.net", "medium.com", "t.me", "telegram.me"}
STOP = {"group", "team", "the", "and", "for", "operation", "campaign", "malware", "attack", "attacks",
        "spider", "panda", "bear", "kitten", "chollima", "typhoon", "blizzard", "sleet", "tempest"}


def tokens(s):
    return re.findall(r"[0-9a-z가-힣]+", str(s).lower())


def host_of(url):
    m = re.match(r"https?://web\.archive\.org/web/[^/]+/(.+)", url)
    u = m.group(1) if m else url
    if not re.match(r"[a-z]+://", u):
        u = "http://" + u
    h = (urllib.parse.urlsplit(u).hostname or "").lower()
    return h[4:] if h.startswith("www.") else h


def domain_in(h, names):
    parts = h.split(".")
    return any(".".join(parts[i:]) in names for i in range(len(parts) - 1))


def publisher(url):
    h = host_of(url)
    if h == "cloud.google.com":
        return "Google Threat Intelligence" if "threat-intelligence" in url else "Google Cloud"
    parts = h.split(".")
    for i in range(len(parts) - 1):
        name = PUBLISHERS.get(".".join(parts[i:]))
        if name:
            return name
    return ""


def when_of(text):
    m = re.search(r"\((\d{4})(?:,\s*([A-Za-z]+)\.?(?:\s+(\d{1,2}))?)?\)", text or "")
    if not m:
        return (0, 0, 0), "", ""
    y, mon, day = int(m.group(1)), MONTHS.get((m.group(2) or "").lower(), 0), int(m.group(3) or 0)
    if mon and day:
        try:
            d = date(y, mon, day).isoformat()
            return (y, mon, day), d, d
        except ValueError:
            pass
    if mon:
        return (y, mon, 0), f"{y}-{mon:02d}", ""
    return (y, 0, 0), str(y), ""


def news(url):
    h = host_of(url)
    return domain_in(h, NEWS) or h.startswith("news.")


def citation(url, source_name, desc):
    m = re.match(r"^(?P<who>.*?)\.?\s*\([^)]*\)\.\s*(?P<title>.+?)(?:\.?\s*Retrieved\b.*)?$", desc or "", re.S)
    who = m.group("who").strip() if m else ""
    title = m.group("title").strip().strip(".").strip() if m else (desc or source_name or url)
    title = re.sub(r"\s+", " ", title)
    org = who if who and "," not in who and len(who) <= 40 and len(who.split()) <= 4 else ""
    key, shown, full = when_of(desc)
    return {"title": title, "source": publisher(url) or org or host_of(url), "url": url,
            "date": full, "when": shown, "key": key, "tag": "뉴스" if news(url) else ""}


def load_refs():
    try:
        return json.loads(gzip.decompress(REFS.read_bytes()).decode("utf-8"))
    except (OSError, ValueError):
        return None


def entity_of(words, db):
    q = set(words)
    best = None
    for key, label in (("groups", "그룹"), ("software", "소프트웨어"), ("campaigns", "캠페인")):
        for aid, v in (db.get(key) or {}).items():
            name = v["name"] if isinstance(v, dict) else v
            aka = v.get("aliases", []) if isinstance(v, dict) else []
            hit = {aid.lower()} & q
            full = False
            for n in [name] + list(aka):
                toks = tokens(n)
                hit |= q & {t for t in toks if len(t) >= 3 and t not in STOP}
                full = full or (bool(toks) and set(toks) <= q)
            if not hit:
                continue
            score = (len(hit), full, label == "그룹", -len(name))
            if best is None or score > best[0]:
                best = (score, aid, label, name, aka, hit)
    return best[1:] if best else None


def src_attack(terms, words, limit):
    db = lookup.load_json(lookup.ATTACK, {})
    refs = load_refs()
    ids = []
    ent = entity_of(words, db) if db else None
    if ent:
        ids.append((ent[0], ent[1], ent[2], ent[3]))
    for aid, label, name, aka in lookup.attack_entries(db):
        hay = " ".join([aid, name] + list(aka)).lower()
        if all(w in hay for w in words) and (not ent or aid != ent[0]):
            ids.append((aid, label, name, aka))
        if len(ids) >= 4:
            break
    if not refs:
        return ids, "MITRE ATT&CK 인용 문헌 (tools/attack.py 를 한 번 돌리면 생긴다)", []
    table = refs["refs"]
    if ent:
        aid, label, name, aka, hit = ent
        rest = [w for w in words if w not in hit]
        pool = refs["by"].get(aid, [])
        head = f"MITRE ATT&CK 인용 문헌 · {name} ({aid}) {len(pool)}건 중"
    else:
        rest, pool, head = words, range(len(table)), "MITRE ATT&CK 인용 문헌"
    rows = []
    for i in pool:
        url, sname, desc = table[i]
        hay = f"{desc} {url}".lower()
        score = sum(1 for w in rest if w in hay)
        if not ent and score < len(rest):
            continue
        rows.append((score, when_of(desc)[0], i))
    rows.sort(key=lambda r: (r[0], r[1]), reverse=True)
    return ids, head, [citation(*table[i]) for _, _, i in rows[:limit]]


def oid_date(oid):
    try:
        return datetime.fromtimestamp(int(str(oid)[:8], 16), KST).date().isoformat()
    except ValueError:
        return ""


def src_kisa(terms, words, limit):
    key = max(terms, key=len)
    rows, seen = [], set()
    for opt in ("TITLE", "CONTENT"):
        body = {"id": "", "sortBy": "_id", "order": -1, "skipCount": 0, "limit": 30, "preKey": "", "nextKey": "",
                "changePerpage": False, "type": "", "searchOption": opt, "content": key,
                "collectionType": "VULNOTICE", "tabs": "ko"}
        res = lookup.get_json(f"{KNVD}/api/core/pu/view/vuln-notice/get", body, timeout=12)
        for it in res.get("resList") or []:
            hay = f"{it.get('title', '')} {it.get('content_text', '')}".lower()
            if it.get("id") in seen or not all(w in hay for w in words):
                continue
            seen.add(it["id"])
            d = oid_date(it["id"])
            rows.append({"title": re.sub(r"\s+", " ", it.get("title", "")).strip(), "source": "KISA",
                         "url": f"{KNVD}/info/vuln/notice/detail?id={it['id']}", "date": d, "when": d})
        if len(rows) >= limit:
            break
    rows.sort(key=lambda r: r["date"], reverse=True)
    return rows[:limit]


def src_cve(terms, words, limit):
    def ask(q):
        body = {"sortBy": "_id", "order": -1, "skipCount": 0, "limit": 30, "preKey": "", "nextKey": "",
                "changePerpage": False, "q": q, "field": "ALL", "cna": [], "severity": [], "highKev": False}
        return lookup.get_json(f"{KNVD}/api/core/pu/view/cve/get", body, timeout=12).get("resList") or []

    found = ask(" ".join(terms))
    if not found and len(terms) > 1:
        found = ask(max(terms, key=len))
    rows = []
    for x in found:
        hay = f"{x.get('cveId', '')} {x.get('title', '')} {x.get('vendorProduct', '')} {x.get('descriptions', '')}".lower()
        if not all(w in hay for w in words):
            continue
        rows.append({"id": x.get("cveId", ""), "title": re.sub(r"\s+", " ", x.get("title") or "").strip(),
                     "cvss": x.get("cvssScore") or "", "sev": x.get("cvssSeverity") or "",
                     "kev": str(x.get("kev")).lower() == "true", "date": (x.get("datePublished") or "")[:10],
                     "product": x.get("vendorProduct") or ""})
        if len(rows) >= limit:
            break
    return rows


def searxng(q):
    u = f"{SEARXNG}/search?" + urllib.parse.urlencode({"q": q, "format": "json", "safesearch": 0})
    with urllib.request.urlopen(urllib.request.Request(u, headers=lookup.UA), timeout=15) as r:
        data = json.load(r)
    return [{"title": x.get("title") or "", "url": x.get("url") or "",
             "date": (x.get("publishedDate") or "")[:10]} for x in data.get("results", [])]


def duckduckgo(q):
    req = urllib.request.Request("https://html.duckduckgo.com/html/",
                                 data=urllib.parse.urlencode({"q": q}).encode(),
                                 headers=dict(BROWSER, **{"Content-Type": "application/x-www-form-urlencoded"}))
    with urllib.request.urlopen(req, timeout=15) as r:
        page = r.read().decode("utf-8", "replace")
    out = []
    for tag, inner in re.findall(r'(<a[^>]*class="result__a"[^>]*>)(.*?)</a>', page, re.S):
        m = re.search(r'href="([^"]+)"', tag)
        if not m:
            continue
        href = html.unescape(m.group(1))
        if "uddg=" in href:
            href = urllib.parse.parse_qs(urllib.parse.urlsplit(href).query).get("uddg", [href])[0]
        if "duckduckgo.com/y.js" in href or not href.startswith("http"):
            continue
        out.append({"title": html.unescape(re.sub(r"<[^>]+>", "", inner)).strip(), "url": href, "date": ""})
    return out


def src_web(terms, words, limit):
    q = " ".join(terms)
    try:
        found, engine = searxng(q), "SearXNG"
    except Exception:
        found, engine = duckduckgo(q), "DuckDuckGo"
    rows, seen = [], set()
    for x in found:
        url = x["url"]
        h = host_of(url)
        norm = re.sub(r"[#?].*$", "", url).rstrip("/").lower()
        if not h or norm in seen or domain_in(h, DROP):
            continue
        seen.add(norm)
        if news(url):
            rank, tag = 2, "뉴스"
        elif publisher(url):
            rank, tag = 0, ""
        else:
            rank, tag = 1, ""
        d = x["date"] if re.fullmatch(r"\d{4}-\d{2}-\d{2}", x["date"] or "") else ""
        rows.append((rank, len(rows), {"title": re.sub(r"\s+", " ", x["title"]).strip() or h,
                                       "source": publisher(url) or h, "url": url, "date": d, "when": d, "tag": tag}))
    rows.sort(key=lambda r: (r[0], r[1]))
    return engine, [r[2] for r in rows[:limit]]


def yq(s):
    s = str(s)
    if not s or re.search(r"[:#\[\]{}&*!|>'\"%@`,]|^[-?\s]|\s$", s):
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return s


def yurl(u):
    return yq(u) if re.search(r"\s|^[\"'\[{&*!|>%@`]", u) else u


def ref_lines(r, indent):
    title = r["title"].replace("\\", "\\\\").replace('"', '\\"')
    lines = [f'{indent}- title: "{title}"',
             f"{indent}  source: {yq(r['source'])}",
             f"{indent}  url: {yurl(r['url'])}"]
    if r.get("date"):
        lines.append(f"{indent}  date: {r['date']}")
    else:
        lines.append(f"{indent}  accessed: {date.today().isoformat()}")
    return lines


def report_path(p):
    if not p:
        return None
    f = Path(p).resolve()
    if f.suffix.lower() != ".md" or REPORTS.resolve() not in f.parents or not f.exists():
        print("\n  지금 연 파일이 _reports 안의 글이 아니라서 목록만 보여 줍니다.")
        return None
    return f


def insert_refs(path, chosen):
    import yaml
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    nl = "\r\n" if "\r\n" in text else "\n"
    lines = text.replace("\r\n", "\n").split("\n")
    if not lines or lines[0].strip() != "---":
        sys.exit("  앞머리(---)가 없는 파일입니다.")
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        sys.exit("  앞머리가 닫히지 않았습니다 (--- 줄이 하나뿐).")
    fm = yaml.safe_load("\n".join(lines[1:end])) or {}
    have = fm.get("references") or []
    urls = {str(r.get("url", "")).rstrip("/") for r in have if isinstance(r, dict)}
    fresh = [r for r in chosen if r["url"].rstrip("/") not in urls]
    if not fresh:
        return len(have), []
    at = next((i for i in range(1, end) if re.match(r"references\s*:", lines[i])), None)
    if at is None:
        lines[end:end] = ["references:"] + [l for r in fresh for l in ref_lines(r, "  ")]
    else:
        j = at + 1
        while j < end and (not lines[j].strip() or lines[j][:1] in (" ", "\t", "-")):
            j += 1
        while j > at + 1 and not lines[j - 1].strip():
            j -= 1
        indent = next((m.group(1) for l in lines[at + 1:j] for m in [re.match(r"(\s*)- ", l)] if m), "  ")
        lines[at] = "references:"
        lines[j:j] = [l for r in fresh for l in ref_lines(r, indent)]
    new_end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    check = yaml.safe_load("\n".join(lines[1:new_end])) or {}
    if len(check.get("references") or []) != len(have) + len(fresh):
        sys.exit("  앞머리를 고치다 형식이 어긋나 저장하지 않았습니다. references: 부분을 확인해 주세요.")
    path.write_bytes((b"\xef\xbb\xbf" if bom else b"") + nl.join(lines).encode("utf-8"))
    return len(have), fresh


def parse_pick(s, n):
    out = []
    for a, b in re.findall(r"(\d+)(?:\s*-\s*(\d+))?", s or ""):
        lo, hi = int(a), int(b or a)
        out += [k for k in range(lo, hi + 1) if 1 <= k <= n and k not in out]
    return out


def main():
    ap = argparse.ArgumentParser(description="참고자료 찾기")
    ap.add_argument("query", nargs="*", help="찾을 낱말")
    ap.add_argument("--into", help="고른 자료를 넣을 글 (_reports 안의 .md)")
    ap.add_argument("--pick", help='묻지 않고 바로 넣을 번호. 예: "1 3 5-7"')
    ap.add_argument("--only", help="찾을 곳만 고르기: " + ",".join(SOURCES))
    ap.add_argument("-n", type=int, default=6, help="한 곳에서 보여 줄 수 (기본 6)")
    args = ap.parse_args()

    terms = " ".join(args.query).split()
    if not terms and sys.stdin.isatty():
        try:
            terms = input("\n  찾을 낱말: ").split()
        except EOFError:
            terms = []
    words = tokens(" ".join(terms))
    if not words:
        ap.print_help()
        return
    only = {s.strip() for s in (args.only or ",".join(SOURCES)).split(",") if s.strip()}
    target = report_path(args.into)
    n = max(1, args.n)

    jobs = {"attack": lambda: src_attack(terms, words, n + 2), "kisa": lambda: src_kisa(terms, words, n),
            "cve": lambda: src_cve(terms, words, n), "web": lambda: src_web(terms, words, n + 4)}
    results = {}
    with ThreadPoolExecutor(max_workers=4) as pool:
        futs = {k: pool.submit(jobs[k]) for k in SOURCES if k in only}
        for k, f in futs.items():
            try:
                results[k] = f.result()
            except Exception as e:
                results[k] = e

    print(f"\n  자료 찾기: {' '.join(terms)}")
    numbered = []

    def section(head, rows):
        if not rows:
            return
        print(f"\n  {head}")
        for r in rows:
            numbered.append(r)
            tag = f"  ({r['tag']})" if r.get("tag") else ""
            print(f"  {len(numbered):>3}  {r['title']}{tag}")
            print("       " + " · ".join(x for x in (r["source"], r.get("when"), r["url"]) if x))

    def failed(label, e):
        print(f"\n  {label}: 받지 못했습니다 ({e.__class__.__name__})")

    ids, cves = [], []
    res = results.get("attack")
    if isinstance(res, Exception):
        failed("ATT&CK", res)
    elif res:
        ids, head, rows = res
        section(head, rows)
    res = results.get("kisa")
    if isinstance(res, Exception):
        failed("KISA 보안공지", res)
    else:
        section("KISA 보안공지", res)
    res = results.get("web")
    if isinstance(res, Exception):
        failed("웹 검색", res)
    elif res:
        section(f"웹 ({res[0]}) · 기술 문서 먼저, 뉴스는 뒤로", res[1])
    res = results.get("cve")
    if isinstance(res, Exception):
        failed("CVE", res)
    elif res:
        cves = res

    if ids or cves:
        print("\n  본문에 번호만 쓰면 링크와 출처가 자동으로 붙는 것")
        for aid, label, name, aka in ids:
            tail = f" ({', '.join(aka[:3])})" if aka else ""
            print(f"       {aid:<10} {label} · {name}{tail}")
        for c in cves:
            score = f"{c['cvss']} {c['sev']}".strip()
            kev = " · KEV" if c["kev"] else ""
            title = c["title"] if len(c["title"]) <= 80 else c["title"][:79].rstrip() + "…"
            print(f"       {c['id']:<16} {score}{kev} · {c['date']} · {title}")
    if not numbered:
        print("\n  넣을 만한 자료를 찾지 못했습니다. 영어 제품명·그룹명으로도 찾아 보세요.\n")
        return

    picks = parse_pick(args.pick, len(numbered)) if args.pick else []
    if target and not args.pick and sys.stdin.isatty():
        try:
            picks = parse_pick(input("\n  글에 넣을 번호 (예: 1 3 5-7, 엔터는 건너뛰기): "), len(numbered))
        except EOFError:
            picks = []
    chosen = [numbered[k - 1] for k in picks]
    if not chosen:
        if not target:
            print("\n  번호를 골라 글에 바로 넣으려면 --into _reports/글.md 를 붙인다. "
                  "VS Code 작업 「자료 찾기」는 지금 연 글에 넣는다.\n")
        else:
            print()
        return
    if not target:
        print("\n  앞머리 references: 에 붙일 줄\n")
        for r in chosen:
            print("\n".join(ref_lines(r, "  ")))
        print()
        return
    before, added = insert_refs(target, chosen)
    rel = target.relative_to(ROOT).as_posix()
    if not added:
        print(f"\n  고른 자료는 이미 {rel} 에 들어 있습니다.\n")
        return
    print(f"\n  {rel} 앞머리 references: 에 {len(added)}건을 넣었습니다.")
    for i, r in enumerate(added, before + 1):
        print(f"    [{i}] {r['title']}")
    print("\n  본문에서 부를 때")
    for i in range(before + 1, before + len(added) + 1):
        print(f'    <cite data-ref="{i}"></cite>')
    print()


if __name__ == "__main__":
    main()
