#!/usr/bin/env python3
"""번호 찾기.

ATT&CK 기법·그룹·소프트웨어를 이름이나 번호로 찾고, CVE·KVE 번호의 제목을 조회한다.
발행한 글에 쓴 CVE·KVE 제목은 _data/vulns.json 에 쌓이고, 사이트는 본문에 적힌 번호에
붙이는 자동 출처의 제목으로 이것을 쓴다. 초안에만 쓴 번호와 손으로 조회한 번호는
_reports/_drafts/.vulns.json 에 따로 둔다. 초안 폴더는 git 에 올라가지 않으므로 무엇을
쓰는 중인지가 저장소에 새지 않는다. 미리보기(tools/preview.py)를 켜면 글에 새로 쓴
CVE·KVE는 알아서 받아 온다.

    python tools/lookup.py powershell          # 이름으로 찾기
    python tools/lookup.py spear phishing      # 낱말이 여럿이면 모두 들어간 것만
    python tools/lookup.py T1566               # 번호로 찾기 (하위 기법까지)
    python tools/lookup.py lazarus             # 그룹은 별칭으로도 찾는다
    python tools/lookup.py CVE-2024-3400       # CVE 제목·CVSS
    python tools/lookup.py KVE-2023-6187       # KVE (KISA 사이버 보안 취약점 정보 포털)
    python tools/lookup.py --sync              # 글에 쓴 CVE·KVE를 한꺼번에 받기
"""
import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ATTACK = ROOT / "_data" / "attack.json"
VULNS = ROOT / "_data" / "vulns.json"
REPORTS = ROOT / "_reports"
DRAFTS = REPORTS / "_drafts"
LOCAL = DRAFTS / ".vulns.json"

UA = {"User-Agent": "Mozilla/5.0 (re-versing lookup)"}
VULN_ID = re.compile(r"\b((?:CVE|KVE)-\d{4}-\d{4,7})\b", re.I | re.A)
ATT_ID = re.compile(r"^(TA\d{0,4}|T\d{1,4}(?:\.\d{0,3})?|[GSCM]\d{1,4})$", re.I)
KNVD = "https://knvd.krcert.or.kr"
RECHECK_DAYS = 30


def load_json(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def save_json(path, data):
    text = json.dumps(data, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    try:
        if path.read_text(encoding="utf-8") == text:
            return
    except OSError:
        pass
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def save_vulns(data):
    save_json(VULNS, data)


def merged():
    """발행 글 사전과 초안용 사전을 합친 것. 로컬 미리보기에만 쓴다."""
    data = dict(load_json(LOCAL, {}))
    data.update(load_json(VULNS, {}))
    return data


def get_json(url, body=None, timeout=15):
    headers = dict(UA)
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        headers.update({"Content-Type": "application/json", "Referer": KNVD + "/"})
    with urllib.request.urlopen(urllib.request.Request(url, data=data, headers=headers), timeout=timeout) as r:
        return json.load(r)


def shorten(text, limit=110):
    text = re.sub(r"\s+", " ", text or "").strip()
    first = re.split(r"(?<=[.!?])\s", text, maxsplit=1)[0]
    return first if len(first) <= limit else first[: limit - 1].rstrip() + "…"


def pick_cvss(record):
    blocks = [record.get("containers", {}).get("cna", {})] + record.get("containers", {}).get("adp", [])
    metrics = [m for b in blocks for m in (b.get("metrics") or [])]
    for key in ("cvssV3_1", "cvssV4_0", "cvssV3_0", "cvssV2_0"):
        for m in metrics:
            if key in m and m[key].get("baseScore") is not None:
                return m[key]["baseScore"], m[key].get("baseSeverity", "")
    return None, ""


def fetch_cve(cid, timeout=15):
    today = date.today().isoformat()
    try:
        rec = get_json(f"https://cveawg.mitre.org/api/cve/{cid}", timeout=timeout)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {"title": "", "checked": today}
        raise
    cna = rec.get("containers", {}).get("cna", {})
    title = (cna.get("title") or "").strip()
    if not title:
        descs = cna.get("descriptions") or []
        en = next((d.get("value", "") for d in descs if str(d.get("lang", "")).startswith("en")), "")
        title = shorten(en or (descs[0].get("value", "") if descs else ""))
    score, sev = pick_cvss(rec)
    out = {"title": title, "checked": today}
    if score is not None:
        out["cvss"] = score
        out["severity"] = str(sev).upper()
    pub = (rec.get("cveMetadata", {}).get("datePublished") or "")[:10]
    if pub:
        out["published"] = pub
    return out


def fetch_kve(kid, timeout=15):
    today = date.today().isoformat()
    base = {"id": "", "sortBy": "_id", "order": -1, "skipCount": 0, "limit": 5, "preKey": "", "nextKey": "",
            "changePerpage": False, "content": kid}
    targets = [("vuln-public", "DOMESTICVULINFO", "", "public"), ("vuln-notice", "VULNOTICE", "ko", "notice")]
    for api, coll, tab, route in targets:
        for opt in ("TITLE", "CONTENT"):
            body = dict(base, type="", searchOption=opt, collectionType=coll, tabs=tab)
            res = get_json(f"{KNVD}/api/core/pu/view/{api}/get", body, timeout=timeout)
            for item in res.get("resList") or []:
                blob = f"{item.get('title', '')} {item.get('content', '')}".upper()
                if kid in blob:
                    return {"title": item.get("title", "").strip(),
                            "url": f"{KNVD}/info/vuln/{route}/detail?id={item.get('id')}", "checked": today}
    return {"title": "", "checked": today}


def fetch(vid, timeout=15):
    vid = vid.upper()
    return fetch_cve(vid, timeout) if vid.startswith("CVE-") else fetch_kve(vid, timeout)


def stale(entry):
    if not entry:
        return True
    if entry.get("title"):
        return False
    try:
        return date.fromisoformat(entry.get("checked", "")) < date.today() - timedelta(days=RECHECK_DAYS)
    except ValueError:
        return True


def ids_in(files):
    found = []
    for p in sorted(files):
        for m in VULN_ID.finditer(p.read_text(encoding="utf-8")):
            vid = m.group(1).upper()
            if vid not in found:
                found.append(vid)
    return found


def sync(quiet=False, timeout=10):
    """글에 쓴 CVE·KVE 중 사전에 없는 것만 받아 온다. 새로 채운 건수를 돌려준다."""
    data, local = load_json(VULNS, {}), load_json(LOCAL, {})
    public = ids_in(REPORTS.glob("*.md"))
    private = [v for v in ids_in(DRAFTS.glob("*.md")) if v not in public] if DRAFTS.exists() else []
    added = 0
    for vid, book in [(v, data) for v in public] + [(v, local) for v in private]:
        if book is data and not stale(local.get(vid)) and stale(data.get(vid)):
            data[vid] = local[vid]
        if not stale(book.get(vid)):
            continue
        try:
            book[vid] = fetch(vid, timeout)
        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as e:
            if not quiet:
                print(f"  {vid}: 받지 못했습니다 ({e.__class__.__name__})")
            continue
        if book[vid].get("title"):
            added += 1
        if not quiet:
            print(f"  {vid}: {book[vid].get('title') or '공개된 정보를 찾지 못했습니다'}")
    save_vulns({k: v for k, v in data.items() if k in public})
    if private or LOCAL.exists():
        save_json(LOCAL, local)
    return added


def vuln_url(vid, entry):
    if vid.startswith("CVE-"):
        return f"https://nvd.nist.gov/vuln/detail/{vid}"
    return entry.get("url") or f"{KNVD}/info/vuln/public"


def show_vuln(vid):
    vid = vid.upper()
    data = load_json(LOCAL, {})
    try:
        data[vid] = fetch(vid)
        save_json(LOCAL, data)
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as e:
        print(f"  조회하지 못했습니다 ({e.__class__.__name__}). 번호만 써도 링크와 출처는 붙습니다.")
        return
    e = data[vid]
    print(f"\n  {vid}")
    print(f"  {e.get('title') or '공개된 정보를 찾지 못했습니다. 링크는 취약점 정보 포털 목록으로 갑니다.'}")
    extra = []
    if e.get("cvss") is not None:
        extra.append(f"CVSS {float(e['cvss']):.1f} {e.get('severity', '')}".strip())
    if e.get("published"):
        extra.append(f"공개 {e['published']}")
    if extra:
        print("  " + " · ".join(extra))
    print(f"  {vuln_url(vid, e)}")
    print(f"\n  본문에 {vid} 라고만 쓰면 링크와 출처가 자동으로 붙습니다.\n")


def attack_entries(db):
    kinds = [("techniques", "기법"), ("tactics", "전술"), ("groups", "그룹"),
             ("software", "소프트웨어"), ("campaigns", "캠페인"), ("mitigations", "완화")]
    for key, label in kinds:
        for aid, v in (db.get(key) or {}).items():
            if isinstance(v, dict):
                yield aid, label, v.get("name", ""), v.get("aliases", [])
            else:
                yield aid, label, v, []


def show_attack(terms):
    db = load_json(ATTACK, {})
    if not db:
        sys.exit("  _data/attack.json 이 없습니다. python tools/attack.py 로 먼저 만드세요.")
    q = " ".join(terms).strip()
    rows = []
    if len(terms) == 1 and ATT_ID.match(q):
        up = q.upper()
        rows = [e for e in attack_entries(db) if e[0].startswith(up)]
    else:
        words = [w.lower() for w in terms]
        for e in attack_entries(db):
            hay = " ".join([e[0], e[2]] + list(e[3])).lower()
            if all(w in hay for w in words):
                rows.append(e)
        rows.sort(key=lambda e: (q.lower() not in e[2].lower(), e[1] != "그룹", len(e[2]), e[0]))
    if not rows:
        print(f"\n  '{q}'에 맞는 ATT&CK 항목이 없습니다. 영어 이름으로 찾아 보세요.\n")
        return
    width = max(len(r[0]) for r in rows[:30])
    print()
    for aid, label, name, aka in rows[:30]:
        tail = f"  ({', '.join(aka[:3])})" if aka else ""
        print(f"  {aid:<{width}}  {label:<5} {name}{tail}")
    if len(rows) > 30:
        print(f"  … 외 {len(rows) - 30}건. 낱말을 더 넣어 좁혀 보세요.")
    top = rows[0]
    if top[1] == "기법":
        print(f"\n  attack 표에 넣을 줄:   전술 | {top[0]} | | 근거")
    print(f"  본문에는 {top[0]} 라고만 쓰면 링크와 출처가 자동으로 붙습니다.\n")


def main():
    ap = argparse.ArgumentParser(description="ATT&CK·CVE·KVE 번호 찾기")
    ap.add_argument("query", nargs="*", help="이름, ATT&CK 번호, CVE·KVE 번호")
    ap.add_argument("--sync", action="store_true", help="글에 쓴 CVE·KVE 제목을 한꺼번에 받기")
    args = ap.parse_args()

    if args.sync:
        n = sync()
        print(f"\n  새로 채운 제목 {n}건  ->  {VULNS}\n")
        return
    terms = " ".join(args.query).split()
    if not terms and sys.stdin.isatty():
        try:
            terms = input("\n  찾을 이름이나 번호: ").split()
        except EOFError:
            terms = []
    if not terms:
        ap.print_help()
        return
    if len(terms) == 1 and VULN_ID.fullmatch(terms[0]):
        show_vuln(terms[0])
    else:
        show_attack(terms)


if __name__ == "__main__":
    main()
