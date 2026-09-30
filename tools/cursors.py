#!/usr/bin/env python3
"""커서 모음을 그려 assets/css/cursors.css 로 쓴다.

조준선 계열 커서를 상태마다 그리고, 라이트·다크 테마용 두 벌을 1x·2x PNG 로 만들어
CSS 에 data URI 로 넣는다. 모양이나 색을 바꾸려면 아래 SHAPES·팔레트를 고치고
다시 돌리면 된다. Pillow 가 필요하다.

    python tools/cursors.py             # assets/css/cursors.css 갱신
    python tools/cursors.py --sheet x.png   # 모든 커서를 한 장에 그려 확인

상태
    default      조준선, 가운데 빨간 점
    pointer      링크·버튼. 빨간 모서리 괄호로 조준이 걸린 모양
    text         글자. 가운데 빨간 점이 있는 I빔
    zoom-in      크게 볼 수 있는 그림. 괄호 안에 +
    zoom-out     크게 본 그림을 닫을 때. 괄호 안에 -
    help         설명이 달린 약어. 조준선 옆 ?
    not-allowed  누를 수 없는 버튼. 조준선 위 금지 표시
    progress     불러오는 중. 조준선을 감싼 끊긴 고리
"""
import argparse
import base64
import io
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "css" / "cursors.css"
S = 16

LIGHT = {"core": (21, 23, 28, 255), "accent": (204, 31, 45, 255), "halo": (255, 255, 255, 255)}
DARK = {"core": (232, 235, 240, 255), "accent": (255, 107, 116, 255), "halo": (16, 18, 22, 255)}

TEXT = "p, li, td, th, dt, dd, h1, h2, h3, h4, blockquote, figcaption, pre, code, input, textarea"
LINK = 'a, a *, button, button *, summary, label, select, [role="button"]'

DOT = [(15, 15, 18, 18, "accent")]
ARMS = [(16, 5, 17, 12), (16, 21, 17, 28), (5, 16, 12, 17), (21, 16, 28, 17)]
SHORT_ARMS = [(16, 9, 17, 12), (16, 21, 17, 24), (9, 16, 12, 17), (21, 16, 24, 17)]
CORNERS = [(4, 4, 10, 6), (4, 4, 6, 10), (22, 4, 28, 6), (26, 4, 28, 10),
           (4, 26, 10, 28), (4, 22, 6, 28), (22, 26, 28, 28), (26, 22, 28, 28)]
QUESTION = ["01110", "10001", "00001", "00010", "00100", "00000", "00100"]


def rects(kind):
    if kind == "default":
        return [(*a, "core") for a in ARMS] + DOT
    if kind == "pointer":
        return [(*c, "accent") for c in CORNERS] + [(*a, "accent") for a in SHORT_ARMS] + DOT
    if kind == "text":
        return [(15, 8, 17, 24, "core"), (12, 6, 20, 8, "core"), (12, 24, 20, 26, "core"), (15, 15, 17, 17, "accent")]
    if kind == "zoom-in":
        return [(*c, "core") for c in CORNERS] + [(10, 16, 23, 17, "accent"), (16, 10, 17, 23, "accent")]
    if kind == "zoom-out":
        return [(*c, "core") for c in CORNERS] + [(10, 16, 23, 17, "accent")]
    if kind == "help":
        glyph = [(22 + x, 21 + y, 23 + x, 22 + y, "accent")
                 for y, row in enumerate(QUESTION) for x, bit in enumerate(row) if bit == "1"]
        return [(*a, "core") for a in ARMS[:3]] + [(21, 16, 25, 17, "core")] + DOT + glyph
    if kind == "not-allowed":
        return [(16, 2, 17, 6, "core"), (16, 27, 17, 31, "core"), (2, 16, 6, 17, "core"), (27, 16, 31, 17, "core")]
    if kind == "progress":
        return [(*a, "core") for a in SHORT_ARMS] + DOT
    raise ValueError(kind)


def extra(kind, d, pal, halo):
    """rects 로 못 그리는 둥근 선. halo 가 참이면 테두리용으로 굵게 그린다."""
    c = 16.5 * S
    grow = S if halo else 0
    color = pal["halo"] if halo else pal["accent"]
    if kind == "not-allowed":
        r = 9 * S
        d.ellipse([c - r - grow, c - r - grow, c + r + grow, c + r + grow], outline=color, width=2 * S + 2 * grow)
        k = r * 0.7071
        d.line([c - k, c - k, c + k, c + k], fill=color, width=2 * S + 2 * grow)
    elif kind == "progress":
        r = 11 * S
        d.arc([c - r - grow, c - r - grow, c + r + grow, c + r + grow], start=0, end=270,
              fill=color, width=2 * S + 2 * grow)


def draw(kind, pal):
    im = Image.new("RGBA", (32 * S, 32 * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    parts = rects(kind)
    extra(kind, d, pal, True)
    for x0, y0, x1, y1, _ in parts:
        d.rectangle([(x0 - 1) * S, (y0 - 1) * S, (x1 + 1) * S - 1, (y1 + 1) * S - 1], fill=pal["halo"])
    extra(kind, d, pal, False)
    for x0, y0, x1, y1, role in parts:
        d.rectangle([x0 * S, y0 * S, x1 * S - 1, y1 * S - 1], fill=pal[role])
    return im


def data_uri(im, px):
    buf = io.BytesIO()
    im.resize((px, px), Image.BOX).save(buf, format="PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


STATES = [
    ("default", "auto", ["&"]),
    ("text", "text", [f"& :is({TEXT})"]),
    ("pointer", "pointer", [f"& :is({LINK})"]),
    ("zoom-in", "zoom-in", ["& img.zoomable"]),
    ("zoom-out", "zoom-out", ["& .zoom", "& .zoom *"]),
    ("help", "help", ["& abbr[title]"]),
    ("not-allowed", "not-allowed", ['& :is(button:disabled, [aria-disabled="true"], [aria-disabled="true"] *)']),
    ("progress", "progress", ['&[aria-busy="true"]', '&[aria-busy="true"] *']),
]


def block(scope, pal, pad):
    out = []
    for kind, fallback, sels in STATES:
        im = draw(kind, pal)
        one, two = data_uri(im, 32), data_uri(im, 64)
        sel = ",\n".join(pad + s.replace("&", scope) for s in sels)
        out.append(f"{sel} {{\n"
                   f'{pad}  cursor: url("{one}") 16 16, {fallback} !important;\n'
                   f'{pad}  cursor: -webkit-image-set(url("{one}") 1x, url("{two}") 2x) 16 16, {fallback} !important;\n'
                   f"{pad}}}\n")
    return "".join(out)


def build_css():
    return (block("html", LIGHT, "")
            + "@media (prefers-color-scheme: dark) {\n"
            + block(':root:not([data-theme="light"])', DARK, "  ")
            + "}\n"
            + block(':root[data-theme="dark"]', DARK, ""))


def sheet(path):
    kinds = [k for k, _, _ in STATES]
    w = 24 + len(kinds) * 80
    im = Image.new("RGBA", (w, 180), (251, 251, 252, 255))
    dark = Image.new("RGBA", (w, 90), (16, 18, 22, 255))
    for i, k in enumerate(kinds):
        im.alpha_composite(draw(k, LIGHT).resize((64, 64), Image.BOX), (16 + i * 80, 13))
        dark.alpha_composite(draw(k, DARK).resize((64, 64), Image.BOX), (16 + i * 80, 13))
    im.alpha_composite(dark, (0, 90))
    im.save(path)


def main():
    ap = argparse.ArgumentParser(description="커서 모음 만들기")
    ap.add_argument("--sheet", help="모든 커서를 한 장에 그려 이 경로에 저장")
    args = ap.parse_args()
    if args.sheet:
        sheet(args.sheet)
        print(f"  확인용 그림  ->  {args.sheet}")
        return
    css = build_css()
    OUT.write_text(css, encoding="utf-8")
    print(f"  커서 {len(STATES)}종 × 라이트·다크  ->  {OUT}  ({len(css.encode()) // 1024} KB)")


if __name__ == "__main__":
    main()
