#!/usr/bin/env python3
"""초안 발행과 발행 전 점검.

초안은 _reports/_drafts/ 에 둔다. 이 폴더는 git 에 올라가지 않고 Jekyll 도 읽지 않으므로
공개 사이트에도 저장소에도 나가지 않는다. 로컬 미리보기(tools/preview.py)에서는 「초안」
표시를 달고 보인다. 다 쓰면 이 도구로 점검한 뒤 _reports/ 로 옮긴다.

    python tools/publish.py _reports/_drafts/my-post.md             # 점검 후 발행 (날짜는 오늘로)
    python tools/publish.py _reports/_drafts/my-post.md --keep-date # 앞머리 날짜 그대로
    python tools/publish.py --check _reports/my-post.md             # 고치지 않고 점검만
    python tools/publish.py --list                                  # 초안 목록

점검하는 것
    TLP        CLEAR 가 아니면 발행하지 않는다
    신원       이 컴퓨터의 사용자 이름, git 전역 이름·메일이 본문이나 그림 파일에 있으면 멈춘다
    메일 주소  코드 블록 밖에 example.* 가 아닌 주소가 있으면 알린다
    그림       글이 쓰는 그림의 촬영 정보(EXIF·GPS)·편집 기록을 지운다. 사진 방향은 남긴다
               초안 폴더의 그림은 assets/img/<글 이름>/ 으로 옮기고 경로를 /assets/... 로 고친다
"""
import argparse
import getpass
import os
import re
import shutil
import subprocess
import sys
import urllib.parse
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "_reports"
DRAFTS = REPORTS / "_drafts"
IMG = ROOT / "assets" / "img"
IMG_EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".avif"}
GENERIC = {"user", "users", "admin", "administrator", "root", "runner", "public", "default", "guest",
           "analyst", "owner", "test", "desktop", "home"}

MD_IMG = re.compile(r'(!\[(?:[^\[\]]|\[[^\]]*\])*\]\(\s*)(<[^>]+>|[^)\s]+)((?:\s+"[^"]*")?\s*\))')
HTML_IMG = re.compile(r'(<img\b[^>]*?\bsrc=["\'])([^"\']+)(["\'])', re.I)
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
FENCE = re.compile(r"^([ \t]*)(`{3,}|~{3,}).*?^\1\2[ \t]*$", re.S | re.M)


def say(msg=""):
    print(f"  {msg}" if msg else "")


def mask(v):
    return v[0] + "*" * max(1, len(v) - 2) + v[-1] if len(v) > 2 else "*" * len(v)


def identities():
    found = set()
    for v in (os.environ.get("USERNAME"), os.environ.get("USER"), Path.home().name):
        found.add(v or "")
    try:
        found.add(getpass.getuser())
    except Exception:
        pass
    for key in ("user.name", "user.email"):
        try:
            out = subprocess.run(["git", "config", "--global", key], capture_output=True, text=True,
                                 timeout=5).stdout.strip()
        except (OSError, subprocess.SubprocessError):
            out = ""
        found.add(out)
        if "@" in out:
            found.add(out.split("@")[0])
    allowed = set()
    for key in ("user.name", "user.email"):
        try:
            allowed.add(subprocess.run(["git", "-C", str(ROOT), "config", "--local", key], capture_output=True,
                                       text=True, timeout=5).stdout.strip().lower())
        except (OSError, subprocess.SubprocessError):
            pass
    cfg = ROOT / "_config.yml"
    if cfg.exists():
        m = re.search(r'^author:\s*"?([^"\n]+)"?', cfg.read_text(encoding="utf-8"), re.M)
        if m:
            allowed.add(m.group(1).strip().lower())
    return sorted(v for v in found if v and len(v) >= 3 and v.lower() not in GENERIC and v.lower() not in allowed)


def ident_hits(text, ids):
    hits = []
    for v in ids:
        pat = re.compile(r"(?<![0-9A-Za-z])" + re.escape(v) + r"(?![0-9A-Za-z])", re.I)
        for m in pat.finditer(text):
            hits.append((text.count("\n", 0, m.start()) + 1, v))
    return hits


def ident_in_bytes(data, ids):
    low = data.lower()
    return [v for v in ids if v.lower().encode("utf-8") in low or v.lower().encode("utf-16-le") in low]


def exif_orientation(payload):
    if not payload.startswith(b"Exif\x00\x00"):
        return 1
    t = payload[6:]
    order = {b"II": "little", b"MM": "big"}.get(t[:2])
    if not order or len(t) < 8:
        return 1
    off = int.from_bytes(t[4:8], order)
    if off + 2 > len(t):
        return 1
    for k in range(int.from_bytes(t[off:off + 2], order)):
        p = off + 2 + 12 * k
        if p + 12 > len(t):
            break
        if int.from_bytes(t[p:p + 2], order) == 0x0112:
            v = int.from_bytes(t[p + 8:p + 10], order)
            return v if 1 <= v <= 8 else 1
    return 1


def orientation_segment(v):
    tiff = (b"MM\x00\x2a\x00\x00\x00\x08" + b"\x00\x01" + b"\x01\x12\x00\x03\x00\x00\x00\x01"
            + v.to_bytes(2, "big") + b"\x00\x00" + b"\x00\x00\x00\x00")
    payload = b"Exif\x00\x00" + tiff
    return b"\xff\xe1" + (len(payload) + 2).to_bytes(2, "big") + payload


def scrub_jpeg(data):
    if data[:2] != b"\xff\xd8":
        return data, []
    out, removed, i, kept_orientation = bytearray(b"\xff\xd8"), [], 2, False
    while i + 1 < len(data):
        if data[i] != 0xFF:
            return data, []
        while i + 1 < len(data) and data[i + 1] == 0xFF:
            i += 1
        marker = data[i + 1]
        if marker == 0xDA or marker == 0xD9:
            out += data[i:]
            break
        if 0xD0 <= marker <= 0xD7 or marker == 0x01:
            out += data[i:i + 2]
            i += 2
            continue
        if i + 4 > len(data):
            return data, []
        seg_len = int.from_bytes(data[i + 2:i + 4], "big")
        seg = data[i:i + 2 + seg_len]
        payload = seg[4:]
        name = None
        if marker == 0xE1 and not kept_orientation and seg == orientation_segment(exif_orientation(payload)):
            out += seg
            kept_orientation = True
            i += 2 + seg_len
            continue
        if marker == 0xE1:
            name = "EXIF" if payload.startswith(b"Exif") else "XMP"
        elif marker == 0xED:
            name = "IPTC"
        elif marker == 0xFE:
            name = "주석"
        elif 0xE3 <= marker <= 0xEF and marker != 0xEE:
            name = f"APP{marker - 0xE0}"
        if name:
            removed.append(name)
            if name == "EXIF" and not kept_orientation:
                o = exif_orientation(payload)
                if o != 1:
                    out += orientation_segment(o)
                    kept_orientation = True
        else:
            out += seg
        i += 2 + seg_len
    return (bytes(out), removed) if removed else (data, [])


def scrub_png(data):
    sig = b"\x89PNG\r\n\x1a\n"
    if not data.startswith(sig):
        return data, []
    out, removed, i = bytearray(sig), [], 8
    while i + 8 <= len(data):
        n = int.from_bytes(data[i:i + 4], "big")
        kind = data[i + 4:i + 8]
        if kind in (b"tEXt", b"zTXt", b"iTXt", b"eXIf", b"tIME"):
            removed.append(kind.decode("ascii"))
        else:
            out += data[i:i + 12 + n]
        i += 12 + n
        if kind == b"IEND":
            break
    return (bytes(out), removed) if removed else (data, [])


def scrub_webp(data):
    if data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        return data, []
    chunks, removed, i = [], [], 12
    while i + 8 <= len(data):
        kind = data[i:i + 4]
        n = int.from_bytes(data[i + 4:i + 8], "little")
        chunk = bytearray(data[i:i + 8 + n + (n & 1)])
        if kind in (b"EXIF", b"XMP "):
            removed.append(kind.decode("ascii").strip())
        else:
            chunks.append(chunk)
        i += 8 + n + (n & 1)
    if not removed:
        return data, []
    for c in chunks:
        if c[:4] == b"VP8X" and len(c) > 8:
            c[8] &= 0xF3
    body = b"WEBP" + b"".join(bytes(c) for c in chunks)
    return b"RIFF" + len(body).to_bytes(4, "little") + body, removed


def scrub_svg(data):
    try:
        t = data.decode("utf-8")
    except UnicodeDecodeError:
        return data, []
    removed = []
    for pat, label in ((r"<metadata\b[\s\S]*?</metadata>", "metadata"),
                       (r"<sodipodi:namedview\b[\s\S]*?(?:/>|</sodipodi:namedview>)", "편집기 설정"),
                       (r'\s(?:sodipodi|inkscape):[\w.-]+="[^"]*"', "편집기 속성")):
        t2 = re.sub(pat, "", t)
        if t2 != t:
            removed.append(label)
            t = t2
    return (t.encode("utf-8"), removed) if removed else (data, [])


def scrubbed(path):
    data = path.read_bytes()
    ext = path.suffix.lower()
    fn = {".jpg": scrub_jpeg, ".jpeg": scrub_jpeg, ".png": scrub_png, ".webp": scrub_webp, ".svg": scrub_svg}.get(ext)
    return fn(data) if fn else (data, [])


def scrub_file(path):
    """메타데이터를 지우고 지운 항목 이름을 돌려준다. 바뀐 게 없으면 빈 목록."""
    data, removed = scrubbed(path)
    if removed:
        path.write_bytes(data)
    return removed


def split_doc(text):
    if not text.startswith("---"):
        return None, text
    end = re.search(r"^---[ \t]*$", text[3:], re.M)
    if not end:
        return None, text
    return text[:3 + end.end()], text[3 + end.end():]


def load_fm(head):
    import yaml
    return yaml.safe_load(head.strip().strip("-")) or {}


def resolve_src(src, doc):
    s = src.strip("<>")
    if re.match(r"(?:https?:|data:|//|#)", s, re.I):
        return None
    if re.match(r"file:", s, re.I):
        s = urllib.parse.urlsplit(s).path
        if re.match(r"/[A-Za-z]:", s):
            s = s[1:]
    s = urllib.parse.unquote(s)
    if re.match(r"[A-Za-z]:[\\/]", s) or s.startswith("\\\\"):
        return Path(s)
    if s.startswith("/"):
        return ROOT / s.lstrip("/")
    return (doc.parent / s).resolve()


def safe_name(name, taken):
    stem, ext = os.path.splitext(name)
    stem = re.sub(r"[^a-z0-9._-]+", "-", stem.lower()).strip("-.") or "fig"
    cand, k = f"{stem}{ext.lower()}", 2
    while cand in taken:
        cand, k = f"{stem}-{k}{ext.lower()}", k + 1
    taken.add(cand)
    return cand


def open_in_editor(path):
    if os.environ.get("TERM_PROGRAM") != "vscode":
        return
    exe = shutil.which("code")
    if exe:
        try:
            subprocess.run([exe, "-r", str(path)], capture_output=True, timeout=20)
        except (OSError, subprocess.SubprocessError):
            pass


def plan_images(body, doc, slug, moving):
    """본문의 그림 경로를 모아 옮길 곳과 새 경로를 정한다. 파일은 건드리지 않는다."""
    plan, notes, taken = {}, [], set()
    dest_dir = IMG / slug
    if dest_dir.exists():
        taken.update(p.name for p in dest_dir.iterdir())
    for pat in (MD_IMG, HTML_IMG):
        for m in pat.finditer(body):
            src = m.group(2)
            if src in plan:
                continue
            f = resolve_src(src, doc)
            if f is None:
                continue
            if not f.is_file():
                notes.append(f"그림 파일이 없습니다: {src}")
                continue
            try:
                rel = f.resolve().relative_to(ROOT)
                inside = True
            except ValueError:
                inside = False
            in_drafts = inside and DRAFTS.resolve() in f.resolve().parents
            if not inside or (in_drafts and moving):
                target = dest_dir / safe_name(f.name, taken)
                plan[src] = (f, target, "/" + target.relative_to(ROOT).as_posix())
            else:
                url = "/" + urllib.parse.quote(rel.as_posix())
                plan[src] = (f, f, url)
    return plan, notes


def rewrite(body, plan):
    def fix(m):
        hit = plan.get(m.group(2))
        return m.group(1) + hit[2] + m.group(3) if hit else m.group(0)
    return HTML_IMG.sub(fix, MD_IMG.sub(fix, body))


def prose_only(text):
    return FENCE.sub(lambda m: "\n" * m.group(0).count("\n"), text)


def run(doc, check_only=False, keep_date=False):
    doc = doc.resolve()
    rel = doc.relative_to(ROOT).as_posix() if ROOT in doc.parents else str(doc)
    if doc.suffix.lower() != ".md" or not doc.is_file():
        sys.exit(f"  글 파일이 아닙니다: {doc}")
    is_draft = DRAFTS.resolve() in doc.parents
    moving = is_draft and not check_only
    raw = doc.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    nl = "\r\n" if "\r\n" in text else "\n"
    text = text.replace("\r\n", "\n")
    head, body = split_doc(text)
    if head is None:
        sys.exit("  앞머리(---)가 없습니다.")
    fm = load_fm(head)
    slug = doc.stem

    stop, info = [], []
    tlp = str(fm.get("tlp") or "CLEAR").upper()
    if tlp != "CLEAR":
        stop.append(f"TLP:{tlp} 문서는 공개하지 않습니다. 초안 폴더에 둔 채 미리보기에서 PDF로 뽑으세요.")
    if not fm.get("title"):
        stop.append("앞머리에 title 이 없습니다.")
    if not is_draft and not check_only:
        stop.append("초안 폴더(_reports/_drafts) 밖의 글입니다. 이미 발행한 글은 --check 로 점검만 합니다.")
    target = REPORTS / doc.name
    if moving and target.exists():
        stop.append(f"_reports/{doc.name} 이 이미 있습니다. 초안 파일 이름을 바꾸세요.")

    plan, notes = plan_images(body, doc, slug, moving)
    info += notes
    for m in MD_IMG.finditer(body):
        alt = m.group(1)[2:].split("](")[0].strip()
        if alt.lower() in ("alt text", "image", "이미지"):
            info.append(f"그림 설명이 '{alt}' 그대로입니다. ![설명](...) 의 설명이 그림 번호 옆 캡션이 됩니다.")
    new_body = rewrite(body, plan)
    ids = identities()
    for line, v in ident_hits(head + new_body, ids):
        stop.append(f"{line}번째 줄에 이 컴퓨터의 신원 정보({mask(v)})가 있습니다.")
    for m in EMAIL.finditer(prose_only(head + new_body)):
        addr = m.group(0)
        if not re.search(r"(^|\.)example(\.[a-z]+)?$|users\.noreply\.github\.com$", addr.split("@")[1], re.I):
            info.append(f"메일 주소가 있습니다: {addr}  (공개해도 되는 주소인지 확인)")

    meta_total, images = 0, []
    for src, (f, dst, url) in plan.items():
        data, removed = scrubbed(f)
        bad = ident_in_bytes(data, ids)
        if bad:
            stop.append(f"그림 {f.name} 안에 이 컴퓨터의 신원 정보({', '.join(mask(b) for b in bad)})가 남아 있습니다.")
        if removed:
            meta_total += 1
        images.append((f, dst, data, removed))

    say()
    say(f"점검  {rel}")
    say(f"  TLP        {tlp}")
    say(f"  신원       {'확인할 것 있음' if any('신원' in s for s in stop) else '문제 없음'}")
    say(f"  그림       {len(images)}장" + (f" · 메타데이터 있는 그림 {meta_total}장" if meta_total else ""))
    for s in stop:
        say(f"  [멈춤] {s}")
    for s in info:
        say(f"  [참고] {s}")
    if images:
        say("  [참고] 그림 속 화면(창 제목·경로·계정 이름)은 눈으로 한 번 더 확인하세요.")

    if stop:
        say()
        say("발행하지 않았습니다." if not check_only else "고칠 것이 있습니다.")
        say()
        return 1
    if check_only:
        if meta_total:
            say("  메타데이터는 미리보기(tools/preview.py)를 켜거나 발행할 때 지워집니다.")
        say()
        return 0

    for f, dst, data, removed in images:
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst != f:
            dst.write_bytes(data)
            if DRAFTS.resolve() in f.resolve().parents:
                f.unlink()
        elif removed:
            f.write_bytes(data)
    today = date.today().isoformat()
    if not keep_date:
        if re.search(r"^date:.*$", head, re.M):
            head = re.sub(r"^date:.*$", f"date: {today}", head, count=1, flags=re.M)
        else:
            head = re.sub(r"^(title:.*)$", rf"\1\ndate: {today}", head, count=1, flags=re.M)
    head = re.sub(r"^published:\s*false\b.*\n", "", head, flags=re.M)
    head = re.sub(r"^draft:\s*true\b.*\n", "", head, flags=re.M)
    out = (head + new_body).replace("\n", nl)
    target.write_bytes((b"\xef\xbb\xbf" if bom else b"") + out.encode("utf-8"))
    doc.unlink()
    left = DRAFTS / "img" / slug
    if left.is_dir() and not any(left.iterdir()):
        left.rmdir()

    moved = [dst for f, dst, _, _ in images if dst != f]
    say()
    say(f"발행했습니다  _reports/{doc.name}" + ("" if keep_date else f"  (날짜 {today})"))
    if moved:
        say(f"그림 {len(moved)}장을 assets/img/{slug}/ 로 옮기고 경로를 고쳤습니다.")
    if meta_total:
        say(f"그림 {meta_total}장에서 메타데이터를 지웠습니다.")
    say()
    say("다음")
    say("  python tools/preview.py")
    paths = f"_reports/{doc.name}" + (f" assets/img/{slug}" if moved or (IMG / slug).exists() else "")
    say(f"  git add {paths}")
    say(f'  git commit -m "{fm.get("title", slug)}"')
    say("  git push")
    say()
    open_in_editor(target)
    return 0


def list_drafts():
    files = sorted(DRAFTS.glob("*.md")) if DRAFTS.exists() else []
    say()
    if not files:
        say("초안이 없습니다. 새 글은 tools/new.ps1 로 만들면 초안으로 시작합니다.")
        say()
        return
    say(f"초안 {len(files)}편  (_reports/_drafts · git 에 올라가지 않음)")
    for p in files:
        head, _ = split_doc(p.read_text(encoding="utf-8-sig").replace("\r\n", "\n"))
        fm = load_fm(head) if head else {}
        tlp = str(fm.get("tlp") or "CLEAR").upper()
        tag = "" if tlp == "CLEAR" else f"  TLP:{tlp}"
        say(f"  {str(fm.get('date', '')):<10}  {p.name:<34} {fm.get('title', '')}{tag}")
    say()


def main():
    ap = argparse.ArgumentParser(description="초안 발행과 발행 전 점검")
    ap.add_argument("file", nargs="?", help="초안 파일 (_reports/_drafts/*.md)")
    ap.add_argument("--check", action="store_true", help="고치지 않고 점검만")
    ap.add_argument("--keep-date", action="store_true", help="앞머리 date 를 오늘로 바꾸지 않음")
    ap.add_argument("--list", action="store_true", help="초안 목록")
    args = ap.parse_args()
    if args.list or not args.file:
        list_drafts()
        if not args.file:
            return
    sys.exit(run(Path(args.file), check_only=args.check, keep_date=args.keep_date))


if __name__ == "__main__":
    main()
