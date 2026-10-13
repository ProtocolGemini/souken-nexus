#!/usr/bin/env python3
"""SCS-7 drawing set for the Cognitive Substrate Laboratory.

Each sheet is an SVG plus a PNG at least 2000 px wide. Re-run from the
repository root or from this directory; paths are resolved from this file.
"""

from __future__ import annotations

import html
import math
import random
from pathlib import Path

import cairosvg

OUT = Path(__file__).resolve().parent
W, H = 2400, 1700
BG = "#071e36"
LINE = "#d7f2fb"
DIM = "#9ecfe2"
FAINT = "#1c4d73"
WARM = "#f4e6c4"
PAPER = "#0c2c4e"
SANS = "Liberation Sans, Helvetica, Arial, sans-serif"
MONO = "Liberation Mono, Courier New, monospace"

# Cartridge geometry, millimetres. Shared by the exploded view and the fabrication sheet.
OD = 186.00
FLANGE = 204.00
HEIGHT = 64.40
BORE = 6.20
LATTICE_T = 14.80
WEAVE_T = 12.40
BUFFER_T = 11.60
MESH_T = 9.40
CAP_T = 8.10  # (HEIGHT - stack) / 2
PCD = 168.00
BOLT = 8.20

ASSEMBLY = "S6TNL48290"
PARTS = [
    ("1", "K8NJF39076", "SUPPRESSION MESH", MESH_T),
    ("2", "B5YTC66129", "OBSERVATION BUFFER", BUFFER_T),
    ("3", "M3VWK91854", "MEMORY WEAVE", WEAVE_T),
    ("4", "L7QHM22041", "LATTICE", LATTICE_T),
]
DARK = "2026-12-04"
REV_LAST = "R8QVN20471"
REV_DATE = "2027-02-17"


def esc(value) -> str:
    return html.escape(str(value), quote=True)


class Sheet:
    def __init__(self):
        self.parts: list[str] = []

    def add(self, fragment: str) -> None:
        self.parts.append(fragment)

    def rect(self, x, y, w, h, fill="none", stroke=LINE, sw=1.25, dash=None):
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(
            f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{extra}/>'
        )

    def line(self, x1, y1, x2, y2, stroke=LINE, sw=1.25, dash=None):
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(
            f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
            f'stroke="{stroke}" stroke-width="{sw}" stroke-linecap="square"{extra}/>'
        )

    def circle(self, cx, cy, r, fill="none", stroke=LINE, sw=1.25, dash=None):
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(
            f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}"{extra}/>'
        )

    def poly(self, pts, fill="none", stroke=LINE, sw=1.25, dash=None):
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        points = " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)
        self.add(
            f'<polygon points="{points}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{extra}/>'
        )

    def path(self, d, fill="none", stroke=LINE, sw=1.5, dash=None, cap="round"):
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(
            f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" '
            f'stroke-linecap="{cap}" stroke-linejoin="round"{extra}/>'
        )

    def text(self, x, y, value, size=16, anchor="start", fill=LINE, family=SANS, weight="normal", spacing=0):
        track = f' letter-spacing="{spacing}"' if spacing else ""
        self.add(
            f'<text x="{x:.2f}" y="{y:.2f}" fill="{fill}" font-size="{size}" '
            f'font-family="{family}" font-weight="{weight}" text-anchor="{anchor}"{track}>'
            f"{esc(value)}</text>"
        )

    def group(self, transform: str, inner: str) -> None:
        self.add(f'<g transform="{transform}">{inner}</g>')

    def svg(self) -> str:
        return (
            f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n'
            + "\n".join(self.parts)
            + "\n</svg>\n"
        )


def frame(s: Sheet, title: str, serial: str, sheet_no: int, scale: str, rev: str = REV_LAST) -> None:
    s.rect(0, 0, W, H, BG, None, 0)
    s.rect(36, 36, W - 72, H - 72, None, LINE, 2.2)
    s.rect(48, 48, W - 96, H - 96, None, LINE, 0.8)
    # Zone ticks along the top and left.
    zones_x = 8
    inner_l, inner_r = 48, W - 48
    span = (inner_r - inner_l) / zones_x
    for i in range(zones_x + 1):
        x = inner_l + i * span
        s.line(x, 36, x, 48, LINE, 0.7)
        if i < zones_x:
            s.text(x + span / 2, 32, str(i + 1), 13, anchor="middle", fill=DIM, family=MONO)
    zones_y = 6
    inner_t, inner_b = 48, H - 48
    span_y = (inner_b - inner_t) / zones_y
    for i in range(zones_y + 1):
        y = inner_t + i * span_y
        s.line(36, y, 48, y, LINE, 0.7)
        if i < zones_y:
            s.text(28, y + span_y / 2 + 4, chr(ord("A") + i), 13, anchor="middle", fill=DIM, family=MONO)
    # Title block
    x, y, w, h = 1460, 1388, 892, 264
    s.rect(x, y, w, h, BG, LINE, 1.4)
    s.line(x, y + 48, x + w, y + 48, LINE, 0.8)
    s.line(x, y + 96, x + w, y + 96, LINE, 0.8)
    s.line(x, y + 156, x + w, y + 156, LINE, 0.8)
    s.line(x + 460, y + 96, x + 460, y + h, LINE, 0.8)
    s.line(x + 680, y + 96, x + 680, y + h, LINE, 0.8)
    s.text(x + 16, y + 32, "SOUKEN INDUSTRIES", 18, family=SANS, weight="bold", spacing=1.4)
    s.text(x + w - 16, y + 32, "COGNITIVE SUBSTRATE LABORATORY", 13, anchor="end", fill=DIM, family=MONO)
    s.text(x + 16, y + 78, title, 20, family=SANS, weight="bold")
    s.text(x + 16, y + 122, "SERIAL", 11, fill=DIM, family=MONO)
    s.text(x + 16, y + 144, serial, 18, family=MONO)
    s.text(x + 476, y + 122, "SHEET", 11, fill=DIM, family=MONO)
    s.text(x + 476, y + 144, f"{sheet_no} OF 5", 16, family=MONO)
    s.text(x + 696, y + 122, "SCALE", 11, fill=DIM, family=MONO)
    s.text(x + 696, y + 144, scale, 16, family=MONO)
    s.text(x + 16, y + 182, "ASSEMBLY", 11, fill=DIM, family=MONO)
    s.text(x + 16, y + 206, ASSEMBLY, 16, family=MONO)
    s.text(x + 16, y + 236, "PHOENIX  ·  UNITS mm  ·  THIRD ANGLE", 13, fill=DIM, family=MONO)
    s.text(x + 476, y + 182, "CURRENT REV", 11, fill=DIM, family=MONO)
    s.text(x + 476, y + 206, rev, 16, family=MONO)
    s.text(x + 476, y + 236, f"REV DATE  {REV_DATE}", 13, fill=DIM, family=MONO)
    s.text(x + 696, y + 182, "FLOOR LOG", 11, fill=DIM, family=MONO)
    s.text(x + 696, y + 206, f"DARK  {DARK}", 16, family=MONO)
    s.text(x + 696, y + 246, "INTERNAL DRAWING", 12, fill=DIM, family=MONO)


def dim_h(s: Sheet, x1, x2, y, label, ext=18):
    s.line(x1, y - ext, x1, y + 6, DIM, 0.8)
    s.line(x2, y - ext, x2, y + 6, DIM, 0.8)
    s.line(x1, y, x2, y, DIM, 0.9)
    # arrowheads
    for x, sign in ((x1, 1), (x2, -1)):
        s.poly([(x, y), (x + sign * 10, y - 3.5), (x + sign * 10, y + 3.5)], DIM, DIM, 0.6)
    s.rect((x1 + x2) / 2 - 70, y - 16, 140, 18, BG, None, 0)
    s.text((x1 + x2) / 2, y - 3, label, 14, anchor="middle", family=MONO, fill=LINE)


def dim_v(s: Sheet, x, y1, y2, label, ext=18):
    s.line(x - 6, y1, x + ext, y1, DIM, 0.8)
    s.line(x - 6, y2, x + ext, y2, DIM, 0.8)
    s.line(x, y1, x, y2, DIM, 0.9)
    for y, sign in ((y1, 1), (y2, -1)):
        s.poly([(x, y), (x - 3.5, y + sign * 10), (x + 3.5, y + sign * 10)], DIM, DIM, 0.6)
    mid = (y1 + y2) / 2
    s.add(
        f'<text x="{x + 14:.2f}" y="{mid:.2f}" fill="{LINE}" font-size="14" '
        f'font-family="{MONO}" text-anchor="middle" transform="rotate(-90 {x + 14:.2f} {mid:.2f})">'
        f"{esc(label)}</text>"
    )


def oblique(s: Sheet, x, y, w, h, dx=86, dy=-52):
    s.poly([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], PAPER, LINE, 1.6)
    s.poly([(x, y), (x + dx, y + dy), (x + w + dx, y + dy), (x + w, y)], "#0e3458", LINE, 1.3)
    s.poly([(x + w, y), (x + w + dx, y + dy), (x + w + dx, y + h + dy), (x + w, y + h)], "#102c4a", LINE, 1.3)
    # centerline tick on the front face
    s.line(x + w / 2, y + 8, x + w / 2, y + h - 8, DIM, 0.6, "6 5")


def balloon(s: Sheet, x, y, n, target):
    s.circle(x, y, 16, BG, LINE, 1.3)
    s.text(x, y + 5, n, 14, anchor="middle", family=MONO)
    s.line(x - 16, y, target[0], target[1], LINE, 0.8)


def exploded(s: Sheet) -> None:
    frame(s, "SCS-7  EXPLODED VIEW", ASSEMBLY, 1, "NTS")
    s.text(80, 100, "SUBSTRATE CARTRIDGE SCS-7", 22, family=SANS, weight="bold", spacing=1.2)
    s.text(80, 128, "LAYER THICKNESS EXAGGERATED. TRUE VALUES PER FABRICATION SHEET F9WDM33462.", 14, fill=DIM, family=MONO)
    layers = [
        ("1", "SUPPRESSION MESH", "K8NJF39076", False),
        ("2", "OBSERVATION BUFFER", "B5YTC66129", True),
        ("3", "MEMORY WEAVE", "M3VWK91854", False),
        ("4", "LATTICE", "L7QHM22041", False),
    ]
    x, w, h = 180, 720, 78
    y0 = 200
    gap = 168
    for i, (num, name, part, dead) in enumerate(layers):
        y = y0 + i * gap
        oblique(s, x, y, w, h)
        s.text(x + 24, y + 46, name, 18, family=SANS, weight="bold")
        s.text(x + w - 24, y + 46, part, 16, anchor="end", family=MONO)
        balloon(s, x + w + 150, y + 20, num, (x + w + 70, y + 10))
        if dead:
            stamp = (
                f'<rect x="-250" y="-28" width="500" height="56" fill="{BG}" stroke="{WARM}" stroke-width="2.2"/>'
                f'<rect x="-242" y="-20" width="484" height="40" fill="none" stroke="{WARM}" stroke-width="0.8"/>'
                f'<text x="0" y="8" fill="{WARM}" font-size="18" font-family="{MONO}" '
                f'text-anchor="middle" letter-spacing="1.4">DECOMMISSIONED — DO NOT REMOVE</text>'
            )
            s.group(f"translate({x + w / 2 + 40} {y + h / 2 + 8}) rotate(-8)", stamp)
    # exploded centerline
    s.line(x + w / 2, 150, x + w / 2, y0 + 3 * gap + h + 40, DIM, 0.7, "10 8")
    s.text(x + w / 2 + 12, 168, "CL", 12, family=MONO, fill=DIM)
    # separation note
    s.text(80, 980, "EXPLODED ALONG THE CARTRIDGE AXIS. GAPS ARE NOT A FIT DIMENSION.", 14, fill=DIM, family=MONO)
    # parts list
    px, py = 1180, 180
    s.rect(px, py, 700, 280, BG, LINE, 1.2)
    s.text(px + 16, py + 28, "PARTS LIST", 14, family=MONO, fill=DIM)
    headers = [(16, "BAL"), (70, "PART NO."), (280, "NOMENCLATURE"), (560, "THK")]
    for ox, lab in headers:
        s.text(px + ox, py + 58, lab, 13, family=MONO, fill=DIM)
    s.line(px, py + 70, px + 700, py + 70, LINE, 0.6)
    for i, (num, part, name, thk) in enumerate(PARTS):
        yy = py + 100 + i * 40
        s.text(px + 16, yy, num, 16, family=MONO)
        s.text(px + 70, yy, part, 16, family=MONO)
        s.text(px + 280, yy, name, 16, family=SANS)
        s.text(px + 560, yy, f"{thk:.2f}", 16, family=MONO)
    s.text(px, py + 320, "ITEM 2 REMAINS IN THE STACK. IT IS DECOMMISSIONED. IT IS NOT TO BE REMOVED.", 14, fill=WARM, family=MONO)
    s.text(80, 1240, "STACK ORDER, BASE TO CAP:  LATTICE  ·  MEMORY WEAVE  ·  OBSERVATION BUFFER  ·  SUPPRESSION MESH", 15, family=MONO)
    s.text(80, 1270, f"ASSEMBLY SERIAL  {ASSEMBLY}", 15, family=MONO)


def cross_section(s: Sheet) -> None:
    frame(s, "SUBSTRATE CROSS-SECTION", "V2HRC55018", 2, "SCHEMATIC")
    s.text(80, 100, "SECTION THROUGH THE SUBSTRATE FIELD", 22, weight="bold", spacing=1.1)
    s.text(80, 128, "REALMS ARE CONCENTRIC. THE RESIDUAL CHANNEL IS NOT ASSIGNED TO A REALM.", 14, fill=DIM, family=MONO)
    cx, cy = 760, 760
    rings = [
        (560, "REALM IV", "HOUSING"),
        (450, "REALM III", "SUPPRESSION"),
        (340, "REALM II", "MEMORY WEAVE"),
        (230, "REALM I", "WITNESS"),
        (120, "REALM 0", "CORE"),
    ]
    # hatch clipped to each annulus
    clips = []
    for i, (r, _name, _sub) in enumerate(rings):
        inner = rings[i + 1][0] if i + 1 < len(rings) else 0
        clips.append(
            f'<clipPath id="ring{i}"><path fill-rule="evenodd" d="'
            f"M {cx} {cy - r} A {r} {r} 0 1 1 {cx - 0.01:.2f} {cy - r} Z "
            f"M {cx} {cy - inner} A {inner} {inner} 0 1 0 {cx - 0.01:.2f} {cy - inner} Z"
            f'"/></clipPath>'
        )
    s.add("<defs>" + "".join(clips) + "</defs>")
    for i, (r, _name, _sub) in enumerate(rings):
        step = 14 + i * 2
        lines = []
        for k in range(-r, r, step):
            lines.append(
                f'<line x1="{cx - r}" y1="{cy + k}" x2="{cx + r}" y2="{cy + k + r}" '
                f'stroke="{DIM}" stroke-width="0.7"/>'
            )
        s.add(f'<g clip-path="url(#ring{i})">' + "".join(lines) + "</g>")
        s.circle(cx, cy, r, "none", LINE, 1.6)
    # residual channel cut through the core — a gap, not a realm
    gap = 16
    s.rect(cx - 620, cy - gap, 1240, gap * 2, BG, None, 0)
    s.line(cx - 620, cy - gap, cx + 620, cy - gap, WARM, 1.4)
    s.line(cx - 620, cy + gap, cx + 620, cy + gap, WARM, 1.4)
    s.line(cx - 600, cy, cx + 600, cy, WARM, 0.6, "8 6")
    # redraw ring strokes over the channel ends so the rings still read, with a break
    for r, _n, _s in rings:
        s.circle(cx, cy, r, "none", LINE, 1.5)
    # break the rings visually where the channel passes: already covered by the BG rect,
    # then circles were redrawn on top. Punch the channel again.
    s.rect(cx - 620, cy - gap + 1.6, 1240, gap * 2 - 3.2, BG, None, 0)
    s.line(cx - 620, cy - gap, cx + 620, cy - gap, WARM, 1.5)
    s.line(cx - 620, cy + gap, cx + 620, cy + gap, WARM, 1.5)
    s.text(cx, cy - 36, "RESIDUAL SIGNAL", 16, anchor="middle", fill=WARM, family=MONO)
    s.text(cx, cy + 52, "UNCLAIMED CHANNEL", 16, anchor="middle", fill=WARM, family=MONO)
    # leaders
    leaders = [
        (560, "REALM IV", "HOUSING", -40),
        (450, "REALM III", "SUPPRESSION MESH", -40),
        (340, "REALM II", "MEMORY WEAVE", 50),
        (230, "REALM I", "WITNESS BAND", 50),
        (120, "REALM 0", "CORE", -70),
    ]
    for r, name, sub, dy in leaders:
        lx = cx + r * 0.72
        ly = cy - r * 0.72
        s.line(lx, ly, 1480, 220 + (560 - r) * 0.55, DIM, 0.8)
        s.circle(lx, ly, 3.5, LINE, LINE, 0.5)
    # callout column
    base_y = 200
    for i, (r, name, sub) in enumerate(rings):
        y = base_y + i * 78
        s.text(1500, y, name, 20, family=SANS, weight="bold")
        s.text(1500, y + 24, sub, 14, fill=DIM, family=MONO)
        s.line(1500, y + 36, 1880, y + 36, FAINT, 0.8)
    s.text(1500, 640, "ACT I ACCESS SHEATH", 16, family=SANS, weight="bold")
    s.text(1500, 664, "LIES OUTSIDE REALM I.", 14, fill=DIM, family=MONO)
    s.text(1500, 686, "SEE TR-2026-093.", 14, fill=DIM, family=MONO)
    s.text(1500, 760, "RESIDUAL BORE", 16, family=SANS, weight="bold")
    s.text(1500, 784, f"Ø{BORE:.2f}  REF. F9WDM33462", 14, fill=DIM, family=MONO)
    s.text(1500, 808, "NO NET NAME. NO REALM.", 14, fill=WARM, family=MONO)
    s.text(80, 1280, "HATCHING DISTINGUISHES REALMS. THE CHANNEL IS LEFT OPEN BECAUSE IT IS UNCLAIMED.", 15, family=MONO)


def hatch_band(s: Sheet, x, y, w, h, step=8):
    lines = []
    for i in range(-int(h), int(w + h), step):
        lines.append(
            f'<line x1="{x + i:.1f}" y1="{y + h:.1f}" x2="{x + i + h:.1f}" y2="{y:.1f}" '
            f'stroke="{DIM}" stroke-width="0.7"/>'
        )
    clip = f"h{int(x)}_{int(y)}"
    s.add(
        f'<clipPath id="{clip}"><rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}"/></clipPath>'
    )
    s.add(f'<g clip-path="url(#{clip})">' + "".join(lines) + "</g>")
    s.rect(x, y, w, h, "none", LINE, 1.1)


def fabrication(s: Sheet) -> None:
    frame(s, "SCS-7  FABRICATION", "F9WDM33462", 3, "1 : 2")
    s.text(80, 96, "ORTHOGRAPHIC  ·  THIRD ANGLE  ·  MILLIMETRES", 16, family=MONO, fill=DIM)
    scale = 3.4  # px per mm at the stated 1:2 once the sheet is printed; the view is to scale with itself
    # The drawing is dimensioned in mm; the view scale is uniform.
    body_w = OD * scale
    flange_w = FLANGE * scale
    body_h = HEIGHT * scale
    cx = 430
    # Top view
    top_c = (cx, 430)
    s.text(top_c[0], 150, "TOP", 16, anchor="middle", family=MONO, fill=DIM)
    s.circle(top_c[0], top_c[1], flange_w / 2, "none", LINE, 1.6)
    s.circle(top_c[0], top_c[1], body_w / 2, "none", LINE, 1.2)
    s.circle(top_c[0], top_c[1], (PCD * scale) / 2, "none", DIM, 0.7, "5 4")
    s.circle(top_c[0], top_c[1], (BORE * scale) / 2, "none", WARM, 1.4)
    s.line(top_c[0] - flange_w / 2 - 16, top_c[1], top_c[0] + flange_w / 2 + 16, top_c[1], DIM, 0.6, "8 6")
    s.line(top_c[0], top_c[1] - flange_w / 2 - 16, top_c[0], top_c[1] + flange_w / 2 + 16, DIM, 0.6, "8 6")
    for k in range(6):
        ang = math.radians(-90 + k * 60)
        bx = top_c[0] + math.cos(ang) * (PCD * scale) / 2
        by = top_c[1] + math.sin(ang) * (PCD * scale) / 2
        s.circle(bx, by, (BOLT * scale) / 2, "none", LINE, 1.1)
    s.text(top_c[0] + 20, top_c[1] - 16, f"Ø{BORE:.2f}", 13, fill=WARM, family=MONO)
    # rev triangle on the bore
    tx, ty = top_c[0] + 70, top_c[1] - 48
    s.poly([(tx, ty - 12), (tx - 11, ty + 8), (tx + 11, ty + 8)], "none", WARM, 1.2)
    s.text(tx, ty + 5, "4", 11, anchor="middle", fill=WARM, family=MONO)
    s.line(tx, ty + 8, top_c[0] + 36, top_c[1] - 8, WARM, 0.7)
    # Front view, aligned under the top view
    front_top = 860
    front_left = cx - flange_w / 2
    s.text(cx, front_top - 24, "FRONT", 16, anchor="middle", family=MONO, fill=DIM)
    # flange
    flange_h = 6.0 * scale
    s.rect(front_left, front_top + body_h - flange_h, flange_w, flange_h, "none", LINE, 1.5)
    body_left = cx - body_w / 2
    s.rect(body_left, front_top, body_w, body_h - flange_h, "none", LINE, 1.5)
    # hidden layer seats
    seat = front_top + CAP_T * scale
    for thk in (LATTICE_T, WEAVE_T, BUFFER_T, MESH_T):
        s.line(body_left, seat, body_left + body_w, seat, DIM, 0.7, "5 4")
        seat += thk * scale
    # bore hidden
    bore_r = (BORE * scale) / 2
    s.line(cx - bore_r, front_top, cx - bore_r, front_top + body_h, WARM, 0.8, "4 3")
    s.line(cx + bore_r, front_top, cx + bore_r, front_top + body_h, WARM, 0.8, "4 3")
    dim_h(s, front_left, front_left + flange_w, front_top + body_h + 46, f"{FLANGE:.2f} ±0.10")
    dim_h(s, body_left, body_left + body_w, front_top + body_h + 86, f"Ø{OD:.2f} ±0.05")
    dim_v(s, front_left - 36, front_top, front_top + body_h, f"{HEIGHT:.2f} ±0.08")
    # Right-side section, heights aligned with the front view
    sec_x = 1280
    s.text(sec_x + body_w / 2, front_top - 24, "SECTION A–A", 16, anchor="middle", family=MONO, fill=DIM)
    s.line(cx, top_c[1] - flange_w / 2 - 30, cx, top_c[1] + 20, DIM, 0.7)
    s.text(cx + 8, top_c[1] - flange_w / 2 - 36, "A", 14, family=MONO, fill=DIM)
    # section stack, true thickness, hatched
    sy = front_top
    bands = [
        (CAP_T, "CAP", False),
        (MESH_T, "K8NJF39076", False),
        (BUFFER_T, "B5YTC66129", True),
        (WEAVE_T, "M3VWK91854", False),
        (LATTICE_T, "L7QHM22041", False),
        (CAP_T, "CAP", False),
    ]
    # The flange is the lower cap region; draw the body width for the section.
    for thk, _name, dead in bands:
        bh = thk * scale
        step = 7 if not dead else 5
        hatch_band(s, sec_x, sy, body_w, bh, step)
        if dead:
            s.rect(sec_x, sy, body_w, bh, "none", WARM, 1.6)
        sy += bh
    # bore void through the section
    s.rect(sec_x + body_w / 2 - bore_r, front_top, bore_r * 2, body_h, BG, WARM, 1.2)
    s.text(sec_x + body_w + 16, front_top + CAP_T * scale + 14, "MESH", 12, family=MONO, fill=DIM)
    buf_y = front_top + (CAP_T + MESH_T) * scale
    s.text(sec_x + body_w + 16, buf_y + 16, "BUFFER", 12, family=MONO, fill=WARM)
    s.text(sec_x + body_w + 16, buf_y + 32, "DO NOT REMOVE", 11, family=MONO, fill=WARM)
    # tolerance block
    s.rect(80, 1188, 520, 160, BG, LINE, 1.0)
    s.text(96, 1214, "UNLESS OTHERWISE SPECIFIED", 13, family=MONO, fill=DIM)
    notes = [
        "LINEAR  ±0.10",
        "ANGULAR  ±0.5°",
        "SURFACE  Ra 1.6",
        "REMOVE BURRS AND BREAK SHARP EDGES",
        f"RESIDUAL BORE  Ø{BORE:.2f} ±0.02",
        f"BOLT CIRCLE  6 × Ø{BOLT:.2f} ON Ø{PCD:.2f}",
    ]
    for i, note in enumerate(notes):
        s.text(96, 1238 + i * 18, note, 13, family=MONO)
    # revision table — last author is a black bar, last date is after the floor went dark
    rx, ry, rw, rh = 80, 1396, 1340, 248
    s.rect(rx, ry, rw, rh, BG, LINE, 1.2)
    s.text(rx + 16, ry + 26, "REVISIONS", 13, family=MONO, fill=DIM)
    cols = [16, 200, 430, 760]
    heads = ["REV", "DATE", "AUTHOR", "DESCRIPTION"]
    for c, htxt in zip(cols, heads):
        s.text(rx + c, ry + 52, htxt, 12, family=MONO, fill=DIM)
    s.line(rx, ry + 62, rx + rw, ry + 62, LINE, 0.6)
    rows = [
        ("H2KLP44018", "2024-06-11", "H. WATANABE", "INITIAL RELEASE OF SCS-7"),
        ("C9DWM11863", "2025-09-02", "K. NAKAMURA", "SEAT DEPTH AND BORE TOLERANCE"),
        ("P4SBR77205", "2026-11-18", "P. MULLER", "PRE-SHUTDOWN INSPECTION RECORD"),
        (REV_LAST, REV_DATE, None, "ENTERED AFTER THE FACILITY WENT DARK"),
    ]
    for i, (rev, date, author, desc) in enumerate(rows):
        yy = ry + 92 + i * 36
        s.text(rx + cols[0], yy, rev, 14, family=MONO)
        s.text(rx + cols[1], yy, date, 14, family=MONO)
        if author is None:
            s.rect(rx + cols[2], yy - 14, 210, 16, "#070b10", None, 0)
        else:
            s.text(rx + cols[2], yy, author, 14, family=MONO)
        s.text(rx + cols[3], yy, desc, 14, family=MONO, fill=WARM if author is None else LINE)
    s.text(620, 1188, f"REV 4  ({REV_LAST})  POSTDATES THE FLOOR LOG OF {DARK}.", 14, fill=WARM, family=MONO)
    s.text(620, 1212, "THE TRIANGLE ON THE TOP VIEW MARKS THAT REVISION.", 14, fill=DIM, family=MONO)


def heat_color(value: float) -> str:
    # 0.18 cold-but-not-ambient → 0.66 still warm. Ambient itself is off this scale.
    t = max(0.0, min(1.0, (value - 0.18) / (0.66 - 0.18)))
    # deep blue -> teal -> pale warm
    stops = [(0.08, 0.24, 0.40), (0.18, 0.55, 0.62), (0.93, 0.86, 0.62)]
    if t < 0.5:
        u = t / 0.5
        a, b = stops[0], stops[1]
    else:
        u = (t - 0.5) / 0.5
        a, b = stops[1], stops[2]
    rgb = tuple(int(round((a[i] + (b[i] - a[i]) * u) * 255)) for i in range(3))
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"


def heatmap(s: Sheet) -> None:
    frame(s, "THERMAL / COGNITION LOAD", "T4PLK88105", 4, "NTS")
    s.text(80, 100, "DORMANT WINDOW", 22, weight="bold", spacing=1.2)
    s.text(80, 128, "THE CARTRIDGE IS LOGGED DORMANT. LOAD DOES NOT RETURN TO AMBIENT.", 14, fill=DIM, family=MONO)
    rows = [
        ("SUPPRESSION MESH", "K8NJF39076", 0.30),
        ("OBSERVATION BUFFER", "B5YTC66129", 0.44),
        ("MEMORY WEAVE", "M3VWK91854", 0.36),
        ("LATTICE", "L7QHM22041", 0.33),
        ("CORE / RESIDUAL", "UNCLAIMED", 0.57),
    ]
    days = list(range(0, 85, 7))
    rng = random.Random(48290)
    x0, y0 = 340, 220
    cw, ch = 118, 86
    for j, day in enumerate(days):
        s.text(x0 + j * cw + cw / 2, y0 - 16, str(day), 13, anchor="middle", family=MONO, fill=DIM)
    s.text(x0 + len(days) * cw / 2, y0 - 42, "DAY OF DORMANCY", 14, anchor="middle", family=MONO)
    for i, (name, part, base) in enumerate(rows):
        s.text(x0 - 16, y0 + i * ch + 36, name, 14, anchor="end", family=SANS)
        s.text(x0 - 16, y0 + i * ch + 56, part, 12, anchor="end", family=MONO, fill=DIM)
        for j, day in enumerate(days):
            # a slow breath that never falls to the ambient floor of 0.08
            wave = 0.04 * math.sin(day / 11.0 + i)
            drift = 0.012 * math.exp(-day / 90.0)
            noise = rng.uniform(-0.015, 0.015)
            value = base + wave - drift + noise
            value = max(value, 0.24)
            color = heat_color(value)
            s.rect(x0 + j * cw + 3, y0 + i * ch + 4, cw - 6, ch - 8, color, LINE, 0.4)
            ink = "#071e36" if value > 0.48 else LINE
            s.text(x0 + j * cw + cw / 2, y0 + i * ch + 50, f"{value:.2f}", 13, anchor="middle", fill=ink, family=MONO)
    # legend
    lx, ly = 340, 760
    s.text(lx, ly, "COGNITION LOAD", 14, family=MONO, fill=DIM)
    for k in range(40):
        v = 0.18 + (0.66 - 0.18) * k / 39
        s.rect(lx + k * 14, ly + 16, 14, 22, heat_color(v), None, 0)
    s.text(lx, ly + 58, "0.18", 12, family=MONO)
    s.text(lx + 40 * 14, ly + 58, "0.66", 12, anchor="end", family=MONO)
    s.text(lx, ly + 90, "AMBIENT REFERENCE  0.08", 14, family=MONO, fill=DIM)
    s.text(lx, ly + 114, "EVERY CELL IN THE DORMANT WINDOW SITS ABOVE 0.24.", 14, family=MONO, fill=WARM)
    s.text(lx, ly + 138, "THE DECOMMISSIONED BUFFER IS STILL WARM. THE CORE IS WARMER.", 14, family=MONO)
    s.text(80, 1100, "LOAD IS A NORMALIZED COGNITION MEASURE RECORDED ON THE CARTRIDGE SEAT.", 14, fill=DIM, family=MONO)
    s.text(80, 1126, "DORMANCY HERE IS THE ABSENCE OF A MANNED SHIFT, NOT THE ABSENCE OF LOAD.", 14, fill=DIM, family=MONO)
    # small time-series of the core, to make the floor obvious
    s.text(80, 1200, "CORE TRACE", 14, family=MONO, fill=DIM)
    xs = days
    core = []
    rng2 = random.Random(7)
    for day in xs:
        core.append(max(0.50, 0.58 + 0.03 * math.sin(day / 9.0) + rng2.uniform(-0.01, 0.01)))
    plot_x, plot_y, plot_w, plot_h = 80, 1230, 900, 120
    s.rect(plot_x, plot_y, plot_w, plot_h, "none", LINE, 0.8)

    def px(day):
        return plot_x + day / 84 * plot_w

    def py(v):
        return plot_y + plot_h - (v - 0.08) / (0.70 - 0.08) * plot_h

    s.line(plot_x, py(0.08), plot_x + plot_w, py(0.08), DIM, 0.8, "5 4")
    s.text(plot_x + plot_w - 8, py(0.08) - 6, "AMBIENT 0.08", 11, anchor="end", fill=DIM, family=MONO)
    d = "M " + " L ".join(f"{px(day):.1f} {py(v):.1f}" for day, v in zip(xs, core))
    s.path(d, stroke=WARM, sw=1.8)
    s.text(plot_x, plot_y - 8, "CORE REMAINS NEAR 0.58 THROUGH DAY 84", 12, family=MONO, fill=WARM)


def wobble(points, seed, amp=7, steps=10):
    rng = random.Random(seed)
    dense = []
    for (x1, y1), (x2, y2) in zip(points, points[1:]):
        for i in range(steps):
            t = i / steps
            x = x1 + (x2 - x1) * t
            y = y1 + (y2 - y1) * t
            if 0 < i < steps:
                x += rng.uniform(-amp, amp)
                y += rng.uniform(-amp, amp)
            dense.append((x, y))
    dense.append(points[-1])
    return dense


def wiring(s: Sheet) -> None:
    frame(s, "SCS-7  WIRING SCHEMATIC", "N5BKH44821", 5, "NONE")
    s.text(80, 100, "RELEASED NETS", 22, weight="bold", spacing=1.2)
    s.text(80, 128, "BUS LINES ARE THE RELEASED NETLIST. THE BYPASS IS A FIELD MARK AND IS NOT ON THAT LIST.", 14, fill=DIM, family=MONO)
    buses = [
        ("PWR-A", "POWER", 240),
        ("CLK-0", "CLOCK", 390),
        ("OBS-1", "OBSERVATION", 540),
        ("MEM-W", "MEMORY WEAVE", 690),
        ("SUP-M", "SUPPRESSION", 840),
    ]
    x1, x2 = 280, 1500
    for name, _sub, y in buses:
        s.line(x1, y, x2, y, LINE, 2.0)
        s.text(x1 - 16, y + 5, name, 16, anchor="end", family=MONO)
        s.circle(x1, y, 5, LINE, LINE, 0.6)
        s.circle(x2, y, 5, LINE, LINE, 0.6)
    # left terminal
    s.rect(80, 200, 70, 700, "none", LINE, 1.3)
    s.text(115, 180, "J1", 14, anchor="middle", family=MONO)
    for _name, _sub, y in buses:
        s.line(150, y, 280, y, LINE, 1.4)
    # right-hand loads
    loads = [
        ("LATTICE DRIVER", "L7QHM22041", 240),
        ("CLOCK FANOUT", "CLK-0", 390),
        ("BUFFER GATE", "B5YTC66129", 540),
        ("WEAVE CONTROLLER", "M3VWK91854", 690),
        ("MESH DRIVER", "K8NJF39076", 840),
    ]
    for name, part, y in loads:
        s.rect(1560, y - 28, 280, 56, PAPER, LINE, 1.2)
        s.line(1500, y, 1560, y, LINE, 1.4)
        s.text(1700, y - 2, name, 14, anchor="middle", family=SANS)
        s.text(1700, y + 16, part, 12, anchor="middle", family=MONO, fill=DIM)
    s.text(1700, 590, "DECOMMISSIONED", 11, anchor="middle", fill=WARM, family=MONO)
    # core tap, not on a released bus
    s.rect(1560, 1040, 280, 70, PAPER, LINE, 1.2)
    s.text(1700, 1070, "CORE TAP", 15, anchor="middle", family=SANS)
    s.text(1700, 1090, "NO RELEASED NET", 12, anchor="middle", family=MONO, fill=DIM)
    # hand-drawn bypass from OBS-1 to the core tap
    pts = wobble(
        [(980, 540), (1040, 560), (1088, 640), (1120, 760), (1090, 900), (1180, 990), (1320, 1040), (1560, 1075)],
        seed=19,
        amp=9,
        steps=8,
    )
    d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    s.path(d, stroke=WARM, sw=2.6)
    # a second, slightly offset stroke so the line looks drawn twice
    pts2 = wobble(
        [(984, 546), (1046, 566), (1094, 646), (1126, 766), (1096, 906), (1186, 996), (1324, 1046), (1560, 1081)],
        seed=23,
        amp=6,
        steps=7,
    )
    d2 = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts2)
    s.path(d2, stroke=WARM, sw=0.9)
    # hand arrowhead
    s.path("M 1560 1075 L 1536 1064", stroke=WARM, sw=2.2)
    s.path("M 1560 1075 L 1538 1092", stroke=WARM, sw=2.2)
    # hand-lettered label
    label = "SKN-BKDR"
    rng = random.Random(4)
    lx, ly = 1140, 820
    for ch in label:
        jx = rng.uniform(-1.5, 1.5)
        jy = rng.uniform(-3.0, 3.0)
        rot = rng.uniform(-7, 7)
        s.add(
            f'<text x="0" y="0" fill="{WARM}" font-size="28" font-family="{SANS}" '
            f'font-weight="bold" transform="translate({lx + jx:.1f} {ly + jy:.1f}) rotate({rot:.1f})">{esc(ch)}</text>'
        )
        lx += 22
    s.text(1140, 858, "field bypass — not on the released netlist", 13, fill=WARM, family=SANS)
    # a rough pencil ring around the tap on OBS-1
    ring = wobble([(960, 520), (1000, 508), (1030, 530), (1020, 566), (980, 574), (958, 548), (960, 522)], seed=11, amp=3, steps=4)
    s.path("M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in ring), stroke=WARM, sw=1.3)
    # netlist
    nx, ny = 80, 1120
    s.rect(nx, ny, 900, 230, BG, LINE, 1.1)
    s.text(nx + 16, ny + 28, "RELEASED NETLIST", 13, family=MONO, fill=DIM)
    s.text(nx + 16, ny + 58, "NET", 13, family=MONO, fill=DIM)
    s.text(nx + 180, ny + 58, "FUNCTION", 13, family=MONO, fill=DIM)
    s.text(nx + 460, ny + 58, "FROM", 13, family=MONO, fill=DIM)
    s.text(nx + 640, ny + 58, "TO", 13, family=MONO, fill=DIM)
    s.line(nx, ny + 70, nx + 900, ny + 70, LINE, 0.6)
    functions = ["POWER", "CLOCK", "OBSERVATION", "MEMORY WEAVE", "SUPPRESSION"]
    for i, ((name, func, _y), _load) in enumerate(zip(buses, loads)):
        yy = ny + 98 + i * 24
        s.text(nx + 16, yy, name, 14, family=MONO)
        s.text(nx + 180, yy, functions[i], 14, family=MONO)
        s.text(nx + 460, yy, "J1", 14, family=MONO)
        s.text(nx + 640, yy, loads[i][0], 14, family=MONO)
    s.text(1020, 1160, "SKN-BKDR IS DRAWN ON THIS SHEET.", 16, fill=WARM, family=MONO)
    s.text(1020, 1188, "IT IS ABSENT FROM THE RELEASED NETLIST.", 16, fill=WARM, family=MONO)
    s.text(1020, 1216, "THE STROKE IS THE FIELD MARK, NOT A CAD NET.", 16, fill=WARM, family=MONO)


def write_sheet(name: str, draw) -> Path:
    sheet = Sheet()
    draw(sheet)
    svg_path = OUT / f"{name}.svg"
    png_path = OUT / f"{name}.png"
    svg = sheet.svg()
    svg_path.write_text(svg)
    cairosvg.svg2png(bytestring=svg.encode(), write_to=str(png_path), output_width=2400)
    return png_path


def main() -> None:
    sheets = [
        ("scs-7-exploded", exploded),
        ("substrate-cross-section", cross_section),
        ("scs-7-fabrication", fabrication),
        ("dormant-load-heatmap", heatmap),
        ("scs-7-wiring", wiring),
    ]
    for name, draw in sheets:
        path = write_sheet(name, draw)
        print(path)


if __name__ == "__main__":
    main()
