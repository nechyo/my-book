#!/usr/bin/env python3
"""MITRE ATT&CK 번호 사전을 갱신한다.

MITRE가 공개하는 Enterprise ATT&CK STIX 데이터를 받아 번호와 이름만 추려
_data/attack.json 에 쓴다. 사이트는 이 사전으로 본문·표·표제부에 적힌
ATT&CK 번호(T1566.001, TA0001, G0032, S0584, C0022, M1017)에 링크와 출처를
자동으로 단다. ATT&CK 새 버전이 나오면 한 번 돌리면 된다.

같이 만드는 것
    tools/attack-refs.json.gz      그룹·소프트웨어·캠페인·기법이 인용한 문헌 목록 (tools/find.py 가 쓴다)
    .vscode/attack.code-snippets   VS Code 자동완성 (이름 일부를 치면 번호가 들어간다)

    python tools/attack.py
    python tools/attack.py --file enterprise-attack.json   # 받아 둔 파일로
"""
import argparse
import gzip
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "_data" / "attack.json"
SNIPPETS = ROOT / ".vscode" / "attack.code-snippets"
REFS = ROOT / "tools" / "attack-refs.json.gz"
KINDS = [("techniques", "기법"), ("tactics", "전술"), ("groups", "그룹"),
         ("software", "소프트웨어"), ("campaigns", "캠페인"), ("mitigations", "완화")]
SRC = ("https://raw.githubusercontent.com/mitre-attack/attack-stix-data/"
       "master/enterprise-attack/enterprise-attack.json")


def attack_id(obj):
    for ref in obj.get("external_references", []):
        if ref.get("source_name") == "mitre-attack" and ref.get("external_id"):
            return ref["external_id"]
    return None


def build(bundle):
    objs = [o for o in bundle.get("objects", [])
            if not o.get("revoked") and not o.get("x_mitre_deprecated")]
    version = ""
    tech, tactics, groups, software, campaigns, mitigations = {}, {}, {}, {}, {}, {}

    for o in objs:
        t = o.get("type")
        if t == "x-mitre-collection":
            version = o.get("x_mitre_version", version)
            continue
        aid = attack_id(o)
        if not aid:
            continue
        name = o.get("name", "").strip()
        if t == "attack-pattern" and re.fullmatch(r"T\d{4}(\.\d{3})?", aid):
            tech[aid] = name
        elif t == "x-mitre-tactic" and re.fullmatch(r"TA\d{4}", aid):
            tactics[aid] = name
        elif t == "intrusion-set" and re.fullmatch(r"G\d{4}", aid):
            aka = [a for a in o.get("aliases", []) if a and a != name]
            groups[aid] = {"name": name, "aliases": aka}
        elif t in ("malware", "tool") and re.fullmatch(r"S\d{4}", aid):
            software[aid] = name
        elif t == "campaign" and re.fullmatch(r"C\d{4}", aid):
            campaigns[aid] = name
        elif t == "course-of-action" and re.fullmatch(r"M\d{4}", aid):
            mitigations[aid] = name

    for aid, name in list(tech.items()):
        if "." in aid:
            parent = tech.get(aid.split(".")[0])
            if parent:
                tech[aid] = f"{parent}: {name}"

    def ordered(d):
        return dict(sorted(d.items()))

    return {
        "version": version,
        "techniques": ordered(tech),
        "tactics": ordered(tactics),
        "groups": ordered(groups),
        "software": ordered(software),
        "campaigns": ordered(campaigns),
        "mitigations": ordered(mitigations),
    }


def build_refs(bundle):
    objs = [o for o in bundle.get("objects", [])
            if not o.get("revoked") and not o.get("x_mitre_deprecated")]
    by_stix = {o["id"]: o for o in objs}
    table, seen, by = [], {}, {}

    def add(aid, ref):
        url = (ref.get("url") or "").strip()
        if not url or ref.get("source_name") in ("mitre-attack", "capec"):
            return
        if url not in seen:
            seen[url] = len(table)
            table.append([url, ref.get("source_name", ""), (ref.get("description") or "").strip()])
        bucket = by.setdefault(aid, [])
        if seen[url] not in bucket:
            bucket.append(seen[url])

    owners = ("intrusion-set", "malware", "tool", "campaign")
    for o in objs:
        aid = attack_id(o)
        if aid and o.get("type") in owners + ("attack-pattern",):
            for r in o.get("external_references", []):
                add(aid, r)
    for o in objs:
        kind = o.get("relationship_type")
        if o.get("type") != "relationship" or kind not in ("uses", "attributed-to"):
            continue
        ends = [by_stix.get(o.get("source_ref"))]
        if kind == "attributed-to":
            ends.append(by_stix.get(o.get("target_ref")))
        for end in ends:
            if end and end.get("type") in owners and attack_id(end):
                for r in o.get("external_references", []):
                    add(attack_id(end), r)
    return {"refs": table, "by": dict(sorted(by.items()))}


def write_refs(bundle, version):
    data = build_refs(bundle)
    data["version"] = version
    raw = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    REFS.write_bytes(gzip.compress(raw, mtime=0))
    return len(data["refs"])


def camel(text):
    return "".join(w[:1].upper() + w[1:] for w in re.findall(r"[A-Za-z0-9]+", text))


def write_snippets(data):
    """VS Code 자동완성: 이름 일부를 치면 번호를 넣는다 (powershell -> T1059.001)."""
    out = {}
    for key, label in KINDS:
        for aid, v in (data.get(key) or {}).items():
            name = v["name"] if isinstance(v, dict) else v
            aka = v.get("aliases", []) if isinstance(v, dict) else []
            prefixes = list(dict.fromkeys(p for p in [aid, camel(name)] + [camel(a) for a in aka] if p))
            desc = f"{aid} · {name} ({label})" + (f" · {', '.join(aka[:3])}" if aka else "")
            out[f"{aid} {name}"] = {"scope": "markdown", "prefix": prefixes, "body": aid, "description": desc}
    SNIPPETS.parent.mkdir(parents=True, exist_ok=True)
    SNIPPETS.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return len(out)


def main():
    ap = argparse.ArgumentParser(description="MITRE ATT&CK 번호 사전 갱신")
    ap.add_argument("--file", help="미리 받아 둔 enterprise-attack.json 경로")
    ap.add_argument("--snippets", action="store_true", help="받지 않고 지금 사전으로 VS Code 자동완성만 다시 만들기")
    args = ap.parse_args()

    if args.snippets:
        n = write_snippets(json.loads(OUT.read_text(encoding="utf-8")))
        print(f"  VS Code 자동완성 {n}개  ->  {SNIPPETS}")
        return

    if args.file:
        raw = Path(args.file).read_bytes()
    else:
        print("  ATT&CK 데이터를 받는 중입니다 (수십 MB) ...")
        req = urllib.request.Request(SRC, headers={"User-Agent": "re-versing-attack-sync"})
        with urllib.request.urlopen(req, timeout=180) as r:
            raw = r.read()

    bundle = json.loads(raw)
    data = build(bundle)
    if not data["techniques"] or not data["groups"]:
        sys.exit("  기법이나 그룹을 하나도 찾지 못했습니다. 원본 형식을 확인하세요.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"  ATT&CK v{data['version'] or '?'}  ->  {OUT}")
    print(f"    기법 {len(data['techniques'])} · 전술 {len(data['tactics'])} · 그룹 {len(data['groups'])} · "
          f"소프트웨어 {len(data['software'])} · 캠페인 {len(data['campaigns'])} · 완화 {len(data['mitigations'])}")
    print(f"  인용 문헌 {write_refs(bundle, data['version'])}건  ->  {REFS}")
    print(f"  VS Code 자동완성 {write_snippets(data)}개  ->  {SNIPPETS}")


if __name__ == "__main__":
    main()
