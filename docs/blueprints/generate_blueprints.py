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
SHEETS = 11


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
    s.text(x + 476, y + 144, f"{sheet_no} OF {SHEETS}", 16, family=MONO)
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


def stamp_lines(s, x, y, a, b, w=460):
    s.rect(x, y, w, 78, BG, WARM, 1.8)
    s.rect(x + 6, y + 6, w - 12, 66, "none", WARM, 0.7)
    s.text(x + w / 2, y + 32, a, 16, anchor="middle", family=MONO, fill=WARM)
    s.text(x + w / 2, y + 56, b, 16, anchor="middle", family=MONO, fill=WARM)


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
    # Sub-assembly and facility seating. The parts list ends near y=460.
    s.rect(1180, 540, 1120, 560, BG, LINE, 1.1)
    s.text(1196, 568, "SUB-ASSEMBLY  SA-7  ·  SECTION B–B", 14, family=MONO, fill=DIM)
    s.circle(1360, 760, 130, "none", LINE, 1.4)
    s.circle(1360, 760, 92, "none", DIM, 0.8, "4 3")
    s.circle(1360, 760, 18, "none", WARM, 1.4)
    for k in range(6):
        ang = math.radians(-90 + k * 60)
        s.circle(1360 + math.cos(ang) * 92, 760 + math.sin(ang) * 92, 10, "none", LINE, 1.1)
    s.line(1360 - 150, 760, 1360 + 150, 760, DIM, 0.6, "6 4")
    s.line(1360, 760 - 150, 1360, 760 + 150, DIM, 0.6, "6 4")
    s.text(1360, 756, "Ø6.20", 12, anchor="middle", fill=WARM, family=MONO)
    s.text(1196, 940, "B–B  BOLT CIRCLE, LOOKING AT THE CAP", 13, family=MONO, fill=DIM)
    notes = [
        "6 × Ø8.20 ON Ø168. END CAP 8.10 EACH.",
        "RESIDUAL BORE IS UNCLAIMED. NO NET NAME.",
        "SEAT: TC2 FAB LAB, EAST BENCH, BAY 06.",
        "WEAVE INDEX COPY: C. PILL ARCHIVE, BAY 05.",
        "SUP-M CONTINUES INTO SERVER INFRASTRUCTURE.",
        "BUFFER B5YTC66129 READS WATER HALL WEIR",
        "AS AN ANALOG. IT IS NOT A PIPE FITTING.",
        "CORPORATE OFFICES DARK AFTER THE FLOOR LOG.",
        "RED QUEEN COURT IS NOT ON THIS STACK.",
        "ITEM 2 STAYS. DECOMMISSIONED. DO NOT REMOVE.",
    ]
    for i, line in enumerate(notes):
        s.text(1520, 620 + i * 28, line, 14, family=MONO, fill=WARM if i in (1, 9) else LINE)
    stamp_lines(s, 1520, 980, "SOME THINGS REFUSE", "TO STAY ERASED")


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
    seats = [
        ("REALM 0", "CORE", "UNCLAIMED RESIDUAL"),
        ("REALM I", "WITNESS", "LIBRARY / WATER HALL"),
        ("REALM II", "MEMORY", "C. PILL ARCHIVE"),
        ("REALM III", "SUPPRESSION", "SERVER INFRASTRUCTURE"),
        ("REALM IV", "HOUSING", "CORPORATE OFFICES"),
        ("SHEATH", "ACT I", "OUTER ACCESS LAYER"),
    ]
    s.rect(1500, 860, 760, 400, BG, LINE, 1.0)
    s.text(1516, 888, "FACILITY SEAT OF EACH RING", 13, family=MONO, fill=DIM)
    s.text(1516, 916, "RING", 12, family=MONO, fill=DIM)
    s.text(1680, 916, "BAND", 12, family=MONO, fill=DIM)
    s.text(1900, 916, "ENVIRONMENT", 12, family=MONO, fill=DIM)
    s.line(1500, 928, 2260, 928, LINE, 0.6)
    for i, (ring, band, env) in enumerate(seats):
        yy = 956 + i * 36
        s.text(1516, yy, ring, 14, family=MONO)
        s.text(1680, yy, band, 14, family=MONO)
        s.text(1900, yy, env, 14, family=MONO, fill=WARM if ring == "REALM 0" else LINE)
    s.text(1516, 1230, "LAN PARTY, TC2, AND THE COURT SIT OFF THESE RINGS.", 13, family=MONO, fill=DIM)
    s.text(1516, 1252, "SEE SHEETS 6 AND 7 FOR THE NINE-BAY INDEX.", 13, family=MONO, fill=DIM)


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
    # Upper right is clear of the top view (which ends near x=780).
    s.rect(1680, 150, 620, 620, BG, LINE, 1.1)
    s.text(1696, 178, "DETAIL C  ·  SEAT AND CALLOUTS", 13, family=MONO, fill=DIM)
    s.text(1696, 214, "C1  FLANGE SEAT IN TC2 FAB LAB", 15, family=MONO)
    s.text(1696, 240, "    BAY 06, EAST BENCH, FIXTURE F-06.", 14, family=MONO, fill=DIM)
    s.text(1696, 276, "C2  RESIDUAL BORE Ø6.20 ±0.02", 15, family=MONO)
    s.text(1696, 302, "    OPEN AT BOTH CAPS. NO PLUG FIT.", 14, family=MONO, fill=DIM)
    s.text(1696, 338, "C3  BUFFER BAND, WARM STROKE", 15, family=MONO, fill=WARM)
    s.text(1696, 364, "    DECOMMISSIONED. DO NOT REMOVE.", 14, family=MONO, fill=WARM)
    s.text(1696, 400, "C4  SECTION A–A IS THE TRUE STACK.", 15, family=MONO)
    s.text(1696, 426, "    HATCH PITCH MARKS THE BAND.", 14, family=MONO, fill=DIM)
    s.text(1696, 462, "C5  AUTHOR OF REV 4 IS WITHHELD.", 15, family=MONO)
    s.text(1696, 488, "    DATE FALLS AFTER THE FLOOR LOG.", 14, family=MONO, fill=DIM)
    s.text(1696, 524, "C6  IDENTITY OF THE LAST HAND", 15, family=MONO)
    s.text(1696, 550, "    IS NOT CONFIRMED BY THE ROLL.", 14, family=MONO, fill=DIM)
    s.text(1696, 590, "MANNED OPS CEASED  2026-12-04.", 14, family=MONO, fill=WARM)
    s.text(1696, 618, "THIS SHEET WAS STILL REVISED.", 14, family=MONO, fill=WARM)
    s.text(1696, 660, "CROSS-REF  W4FHL66308  WATER HALL", 13, family=MONO, fill=DIM)
    s.text(1696, 684, "CROSS-REF  N5BKH44821  SKN-BKDR", 13, family=MONO, fill=DIM)
    s.text(1696, 708, "CROSS-REF  Q3NPL77014  NINE BAYS", 13, family=MONO, fill=DIM)


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
    s.rect(1040, 760, 1260, 560, BG, LINE, 1.1)
    s.text(1056, 788, "STATIONS STILL WARM IN THE DORMANT WINDOW", 14, family=MONO, fill=DIM)
    warm_rows = [
        ("01", "VISITOR PROCESSING", "FREQ DISPLAY", "0.26"),
        ("02", "CORPORATE OFFICES", "DARK FLOOR", "0.24"),
        ("03", "RED QUEEN COURT", "DAIS", "0.41"),
        ("04", "LIBRARY / WATER HALL", "WEIR", "0.47"),
        ("05", "C. PILL ARCHIVE", "INDEX WALL", "0.33"),
        ("06", "TC2 FAB LAB", "SCS-7 SEAT", "0.52"),
        ("07", "DESERTED LAN PARTY", "ONE RACK LIVE", "0.38"),
        ("08", "SERVER INFRASTRUCTURE", "SKN-BKDR TAP", "0.55"),
        ("09", "REALM 0 CORE", "RESIDUAL", "0.58"),
    ]
    s.text(1056, 822, "BAY", 12, family=MONO, fill=DIM)
    s.text(1140, 822, "ENVIRONMENT", 12, family=MONO, fill=DIM)
    s.text(1680, 822, "WARM POINT", 12, family=MONO, fill=DIM)
    s.text(1980, 822, "LOAD", 12, family=MONO, fill=DIM)
    s.line(1040, 834, 2300, 834, LINE, 0.6)
    for i, (bay, env, point, load) in enumerate(warm_rows):
        yy = 864 + i * 32
        s.text(1056, yy, bay, 14, family=MONO)
        s.text(1140, yy, env, 14, family=MONO)
        s.text(1680, yy, point, 14, family=MONO, fill=DIM)
        s.text(1980, yy, load, 14, family=MONO, fill=WARM)
    s.text(1056, 1180, "AMBIENT IS 0.08. NO BAY IN THIS WINDOW HAS RETURNED TO IT.", 13, family=MONO, fill=WARM)
    s.text(1056, 1208, "A DESERTED BAY CAN STILL DRAW. ABSENCE OF STAFF IS NOT ABSENCE OF LOAD.", 13, family=MONO)
    s.text(1056, 1236, "THE LAN PARTY HAS NO OCCUPANT ON THE ROLL. ONE RACK REMAINS LIVE.", 13, family=MONO, fill=DIM)


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
    s.rect(1888, 160, 420, 900, BG, LINE, 1.0)
    s.text(1904, 188, "MARGIN  ·  WHERE THE NETS LAND", 12, family=MONO, fill=DIM)
    landings = [
        ("PWR-A", "TC2 FAB LAB BENCH"),
        ("CLK-0", "SERVER ROW, RACK C"),
        ("OBS-1", "WATER HALL WEIR"),
        ("MEM-W", "C. PILL ARCHIVE"),
        ("SUP-M", "SERVER ROW, RACK A"),
        ("SKN-BKDR", "FIELD ONLY"),
    ]
    for i, (net, where) in enumerate(landings):
        yy = 230 + i * 64
        s.text(1904, yy, net, 15, family=MONO, fill=WARM if net == "SKN-BKDR" else LINE)
        s.text(1904, yy + 22, where, 13, family=MONO, fill=DIM)
    s.line(1888, 630, 2308, 630, LINE, 0.6)
    s.text(1904, 664, "OBS-1 IS A RELEASED NET.", 13, family=MONO)
    s.text(1904, 688, "THE PENCIL LEAVING IT IS NOT.", 13, family=MONO, fill=WARM)
    s.text(1904, 728, "PROTOCOL GEMINI BINDS", 13, family=MONO)
    s.text(1904, 752, "A FREQUENCY. IT DOES NOT", 13, family=MONO)
    s.text(1904, 776, "APPEAR ON THIS NETLIST.", 13, family=MONO)
    s.text(1904, 816, "A RECORDED OBSERVATION", 13, family=MONO, fill=WARM)
    s.text(1904, 840, "HAS BEEN FILED AS IF IT", 13, family=MONO, fill=WARM)
    s.text(1904, 864, "WERE PERMISSION. IT IS NOT.", 13, family=MONO, fill=WARM)
    s.text(1904, 904, "SEE F8BND44027.", 13, family=MONO, fill=DIM)
    s.text(1904, 940, "CORE TAP: REALM 0.", 13, family=MONO, fill=DIM)
    s.text(1904, 976, "NO OCCUPANT CONFIRMED", 13, family=MONO)
    s.text(1904, 1000, "AT THE FAR END.", 13, family=MONO)


def bay(s: Sheet, x, y, w, h, code, title, lines, warm=False):
    s.rect(x, y, w, h, "#0a2744", LINE, 1.35)
    s.line(x, y + 36, x + w, y + 36, DIM, 0.7)
    s.text(x + 12, y + 24, code, 13, family=MONO, fill=WARM)
    s.text(x + 58, y + 24, title, 14, family=SANS, weight="bold")
    ink = WARM if warm else DIM
    for i, line in enumerate(lines):
        s.text(x + 14, y + 60 + i * 22, line, 13, family=MONO, fill=ink if i == len(lines) - 1 and warm else DIM)


def facility_plan(s: Sheet) -> None:
    frame(s, "FACILITY FLOOR  ·  NINE BAYS", "Q3NPL77014", 6, "SCHEMATIC")
    s.text(80, 100, "PHOENIX  ·  COGNITIVE SUBSTRATE LABORATORY", 22, weight="bold", spacing=1.0)
    s.text(80, 128, "INDEX COMPILATION. FIELD SURVEY INCOMPLETE AFTER THE FLOOR LOG. OUTLINES ARE NOT A TILE MEASURE.", 13, fill=DIM, family=MONO)
    # North arrow
    s.line(2140, 210, 2140, 120, LINE, 1.2)
    s.poly([(2140, 112), (2132, 132), (2148, 132)], LINE, LINE, 0.6)
    s.text(2140, 100, "N", 14, anchor="middle", family=MONO)
    rows = [
        (188, 270, [
            ("01", "VISITOR PROCESSING", ["AIRLOCK 1 OF 4 AT THE STREET", "IDENTITY VERIFICATION", "CHAT CHAMBER, 30:00 WINDOW", "FREQ ISSUED, THEN BOUND"], False),
            ("02", "CORPORATE OFFICES", ["DESK GRID, BADGE READERS", "ROLL DOES NOT MATCH SEATS", "MANNED OPS CEASED", "IDENTITY UNCONFIRMED"], True),
            ("03", "RED QUEEN COURT", ["DAIS AND TWO LANES", "HUMAN OR MACHINE", "WITNESS SEAT EMPTY", "SEE C2QRT91540"], False),
        ]),
        (500, 340, [
            ("04", "LIBRARY / WATER HALL", ["STACKS ALONG THE WEST WALL", "WEIR HOLDS A RESIDUAL", "SUPPLY AND RETURN LIVE", "SEE W4FHL66308"], True),
            ("05", "C. PILL ARCHIVE", ["INDEX WALL, OPEN CARRELS", "WEAVE COPY OF M3VWK91854", "NO ATTENDANT ON THE ROLL", "RECORDS REMAIN"], False),
            ("06", "TC2 FAB LAB", ["EAST BENCH, FIXTURE F-06", "SCS-7 SEAT, SERIAL ABOVE", "VOYAGE REMNANT IN THE CAGE", "SEE V6YAR30815"], False),
        ]),
        (880, 400, [
            ("07", "DESERTED LAN PARTY", ["ROWS OF STATIONS", "CABLES STILL DRESSED", "NO OCCUPANT ON THE ROLL", "ONE RACK DRAWS CURRENT"], True),
            ("08", "SERVER INFRASTRUCTURE", ["RACKS A–C, BUS DUCT", "PWR-A, CLK-0, SUP-M", "SKN-BKDR IS A FIELD MARK", "NOT ON THE RELEASED NETLIST"], True),
            ("09", "REALM 0  /  ACT I", ["CORE UNDER THE SPINE", "RESIDUAL CHANNEL OPEN", "ACT I IS THE OUTER SHEATH", "SOME THINGS REFUSE ERASURE"], True),
        ]),
    ]
    widths = [400, 440, 420]
    x0 = 80
    for y, h, items in rows:
        x = x0
        for (code, title, lines, warm), w in zip(items, widths):
            bay(s, x, y, w - 16, h, code, title, lines, warm)
            x += w
    # Circulation spine drawn across the gaps between row 1 and row 2.
    s.rect(80, 466, 1244, 28, "#102c4a", WARM, 1.0)
    s.text(700, 486, "SPINE S-1    REALM 0  →  ACT I    CIRCULATION, NOT A REALM", 13, anchor="middle", family=MONO, fill=WARM)
    s.rect(1480, 168, 820, 1160, BG, LINE, 1.1)
    s.text(1496, 198, "BAY INDEX", 14, family=MONO, fill=DIM)
    index = [
        "01  STREET AIRLOCK. VISITOR PROCESSING v4.2.1.",
        "    FREQUENCY IS DISPLAYED. BINDING IS SEPARATE.",
        "02  OFFICES. SEATS OUTNUMBER THE ROLL.",
        "03  COURT. CLASSIFICATION DOES NOT NAME A PERSON.",
        "04  WATER HALL. THE WEIR DOES NOT GO TO EMPTY.",
        "05  ARCHIVE. THE INDEX OUTLASTS THE ATTENDANT.",
        "06  FAB LAB. SCS-7 REMAINS ON FIXTURE F-06.",
        "07  LAN PARTY. DESERTED. ONE RACK STILL WARM.",
        "08  SERVERS. SKN-BKDR PENCILLED, NOT RELEASED.",
        "09  CORE AND SHEATH. CHANNEL UNCLAIMED.",
        "",
        "GAPS BETWEEN BAYS ARE CIRCULATION.",
        "THEY ARE NOT DIMENSIONED.",
        "NO DOOR SCHEDULE WAS FILED AFTER THE",
        "FLOOR LOG OF 2026-12-04.",
        "",
        "A RECORDED OBSERVATION OF A BAY",
        "HAS BEEN TREATED, IN PLACES, AS",
        "PERMISSION TO REMAIN. IT IS NOT.",
        "",
        "WITNESS SEAT IN BAY 03 IS HELD.",
        "THE NAME IS NOT ON THE ROLL.",
        "NO FIGURE ON THIS SHEET IS THAT SEAT.",
    ]
    for i, line in enumerate(index):
        s.text(1496, 236 + i * 26, line, 13, family=MONO, fill=LINE if line and line[0].isdigit() else DIM)
    stamp_lines(s, 1496, 1180, "SURVEY INCOMPLETE", "INDEX, NOT A MEASURE", w=780)


def realm_maps(s: Sheet) -> None:
    frame(s, "REALM ENVIRONMENTS  ·  SCHEMATIC PLANS", "H7RVM22190", 7, "SCHEMATIC")
    s.text(80, 100, "NINE ENVIRONMENTS, EACH PLAN TAKEN FROM THE DIVISION INDEX", 20, weight="bold", spacing=0.6)
    s.text(80, 126, "NOT A SURVEY OF FINISHES OR TILES. INTERIORS ARE THE FILED CONDITION, DRAWN SCHEMATIC.", 13, fill=DIM, family=MONO)
    plans = [
        ("01  VISITOR PROCESSING", ["gate", "gate", "gate", "chamber"], "four airlocks, then the chamber"),
        ("02  CORPORATE OFFICES", ["desk", "desk", "desk", "empty"], "badge reader live, chairs empty"),
        ("03  RED QUEEN COURT", ["lane", "dais", "lane", "seat"], "witness seat held, unnamed"),
        ("04  LIBRARY / WATER HALL", ["stack", "weir", "stack", "return"], "weir charged, return open"),
        ("05  C. PILL ARCHIVE", ["carrel", "aisle", "carrel", "index"], "index wall faces the aisle"),
        ("06  TC2 FAB LAB", ["bench", "seat", "bench", "cage"], "SCS-7 on the east bench"),
        ("07  DESERTED LAN PARTY", ["row", "row", "row", "live"], "rows dark, one position live"),
        ("08  SERVER INFRASTRUCTURE", ["rack", "bus", "rack", "tap"], "field tap is not a released net"),
        ("09  REALM 0 / ACT I", ["core", "bore", "sheath", "door"], "residual bore, sheath outside"),
    ]
    for i, (title, marks, caption) in enumerate(plans):
        col, row = i % 3, i // 3
        x = 70 + col * 760
        y = 160 + row * 390
        s.rect(x, y, 730, 360, BG, LINE, 1.15)
        s.text(x + 16, y + 26, title, 15, family=SANS, weight="bold")
        s.text(x + 16, y + 48, caption.upper(), 12, family=MONO, fill=DIM)
        # interior
        ix, iy, iw, ih = x + 24, y + 68, 470, 250
        s.rect(ix, iy, iw, ih, "#0a2744", LINE, 1.1)
        s.line(ix + iw / 2, iy, ix + iw / 2, iy + ih, DIM, 0.6, "4 3")
        s.line(ix, iy + ih / 2, ix + iw, iy + ih / 2, DIM, 0.6, "4 3")
        for k, mark in enumerate(marks):
            mx = ix + 28 + (k % 2) * (iw / 2)
            my = iy + 28 + (k // 2) * (ih / 2)
            s.rect(mx, my, 150, 70, PAPER, LINE, 0.9)
            s.text(mx + 75, my + 42, mark.upper(), 13, anchor="middle", family=MONO, fill=WARM if mark in ("live", "weir", "tap", "bore", "seat") else LINE)
        s.text(x + 510, y + 100, "CONDITION", 12, family=MONO, fill=DIM)
        conditions = {
            0: ["AIRLOCK 1 VERIFIES", "AN IDENTIFIER.", "CHAMBER ISSUES FREQ.", "TRANSMISSIONS ARE", "RECORDED."],
            1: ["DESKS REMAIN SET.", "THE ROLL IS SHORT.", "A BADGE IS NOT", "A CONFIRMED PERSON."],
            2: ["TWO LANES ENTER.", "CLASSIFICATION IS", "HUMAN OR MACHINE.", "ONE OUTCOME WITHHELD.", "SEAT UNNAMED."],
            3: ["STACKS ARE DRY.", "THE WEIR IS NOT.", "RESIDUAL REFUSES", "THE EMPTY MARK.", "SEE W4FHL66308."],
            4: ["CARRELS FACE THE", "INDEX. NO READER", "IS LOGGED. THE", "COPY OF THE WEAVE", "IS STILL FILED."],
            5: ["FIXTURE F-06 HOLDS", "SCS-7. A CAGE AT", "THE NORTH HOLDS A", "VOYAGE A/R REMNANT.", "PRODUCT WITHDRAWN."],
            6: ["STATIONS DRESSED.", "OCCUPANT COUNT: 0", "ON THE ROLL.", "POSITION 14 DRAWS.", "DO NOT CALL IT IDLE."],
            7: ["RACKS A–C.", "BUS DUCT OVERHEAD.", "SKN-BKDR PENCILLED", "AT THE CORE TAP.", "ABSENT FROM J1."],
            8: ["CORE IS REALM 0.", "BORE IS UNCLAIMED.", "ACT I SHEATH IS", "OUTSIDE REALM I.", "ERASURE REFUSED."],
        }
        for j, line in enumerate(conditions[i]):
            s.text(x + 510, y + 128 + j * 28, line, 13, family=MONO)


def water_hall(s: Sheet) -> None:
    frame(s, "WATER HALL  ·  PLUMBING AND FLOW", "W4FHL66308", 8, "SCHEMATIC")
    s.text(80, 100, "LIBRARY / WATER HALL  ·  BAY 04", 22, weight="bold", spacing=1.0)
    s.text(80, 128, "FLOW SCHEMATIC. PIPE SIZES ARE NOMINAL INDEX VALUES, NOT A POST-DARK SURVEY.", 13, fill=DIM, family=MONO)
    # Plan
    s.rect(80, 170, 980, 760, "#0a2744", LINE, 1.4)
    s.text(100, 200, "PLAN  ·  LOOKING DOWN", 14, family=MONO, fill=DIM)
    # stacks
    for i in range(6):
        s.rect(120 + i * 70, 240, 48, 280, PAPER, LINE, 1.0)
        s.text(144 + i * 70, 390, "STK", 11, anchor="middle", family=MONO, fill=DIM)
    s.text(330, 560, "STACKS  ·  DRY SIDE", 13, family=MONO, fill=DIM)
    # weir basin
    s.rect(560, 280, 420, 220, "#123652", WARM, 1.6)
    s.text(770, 370, "WEIR", 18, anchor="middle", family=MONO, fill=WARM)
    s.text(770, 396, "RESIDUAL HELD", 13, anchor="middle", family=MONO, fill=WARM)
    # supply and return runs
    s.line(120, 640, 900, 640, LINE, 3.0)
    s.line(120, 690, 900, 690, DIM, 2.2)
    s.text(140, 628, "SUPPLY  S-04   NOM. 80", 13, family=MONO)
    s.text(140, 720, "RETURN  R-04   NOM. 65", 13, family=MONO, fill=DIM)
    # arrows on supply
    for ax in (300, 520, 740):
        s.poly([(ax, 640), (ax - 16, 632), (ax - 16, 648)], LINE, LINE, 0.5)
        s.poly([(ax, 690), (ax + 16, 682), (ax + 16, 698)], DIM, DIM, 0.5)
    # branch that does not reach the drain
    s.line(770, 500, 770, 640, WARM, 2.0)
    s.path("M 860 390 C 980 390, 1020 470, 1000 560", stroke=WARM, sw=2.2)
    s.text(620, 258, "BRANCH U  ·  DOES NOT REACH THE DRAIN", 13, family=MONO, fill=WARM)
    # valves
    for vx, label in ((200, "V1"), (480, "V2"), (760, "V3")):
        s.rect(vx - 14, 626, 28, 28, BG, LINE, 1.1)
        s.line(vx - 14, 626, vx + 14, 654, LINE, 1.0)
        s.text(vx, 612, label, 12, anchor="middle", family=MONO)
    # Flow diagram on the right
    s.rect(1120, 170, 1160, 760, BG, LINE, 1.1)
    s.text(1140, 202, "FLOW", 14, family=MONO, fill=DIM)
    steps = [
        (240, "STREET RISER", "ENTER BAY 04"),
        (360, "V1 ISOLATION", "SUPPLY S-04"),
        (480, "STACK HEADER", "DRY SIDE, NO TAKEOFF"),
        (600, "WEIR", "CHARGE HELD ABOVE EMPTY"),
        (700, "V3 / RETURN R-04", "LEAVES TOWARD SERVERS"),
        (810, "BRANCH U", "UNCLAIMED. NO DRAIN."),
    ]
    for i, (yy, name, sub) in enumerate(steps):
        s.rect(1280, yy, 520, 78, PAPER, WARM if i in (3, 5) else LINE, 1.2)
        s.text(1540, yy + 32, name, 16, anchor="middle", family=SANS, weight="bold")
        s.text(1540, yy + 56, sub, 13, anchor="middle", family=MONO, fill=DIM)
        if i < len(steps) - 1 and i != 3:
            s.line(1540, yy + 78, 1540, steps[i + 1][0], LINE, 1.2)
    # branch leaves the weir sideways in the list; draw a side note
    s.text(1848, 560, "U LEAVES THE WEIR", 12, family=MONO, fill=WARM)
    s.line(1800, 639, 1848, 848, WARM, 1.0)
    # schedule
    s.rect(80, 960, 1500, 380, BG, LINE, 1.1)
    s.text(96, 990, "VALVE AND RUN SCHEDULE", 14, family=MONO, fill=DIM)
    headers = [(16, "MARK"), (160, "SERVICE"), (460, "NOMINAL"), (700, "STATE AT FLOOR LOG"), (1100, "NOTE")]
    for ox, lab in headers:
        s.text(96 + ox, 1024, lab, 12, family=MONO, fill=DIM)
    s.line(80, 1036, 1580, 1036, LINE, 0.6)
    sched = [
        ("V1", "SUPPLY ISOLATION", "80", "OPEN", "STREET SIDE"),
        ("V2", "STACK BYPASS", "40", "CLOSED", "DRY SIDE STAYS DRY"),
        ("V3", "RETURN ISOLATION", "65", "OPEN", "TOWARD BAY 08"),
        ("S-04", "SUPPLY RUN", "80", "CHARGED", "LIVE AT LAST READING"),
        ("R-04", "RETURN RUN", "65", "CHARGED", "LIVE AT LAST READING"),
        ("U", "UNCLAIMED BRANCH", "—", "HELD", "NO DRAIN. REFUSES EMPTY."),
    ]
    for i, row in enumerate(sched):
        yy = 1068 + i * 36
        for ox, val in zip((16, 160, 460, 700, 1100), row):
            s.text(96 + ox, yy, val, 14, family=MONO, fill=WARM if row[0] == "U" else LINE)
    s.rect(1620, 960, 680, 380, BG, LINE, 1.1)
    s.text(1636, 992, "FILED CONDITION", 14, family=MONO, fill=DIM)
    filed = [
        "THE WEIR LEVEL FALLS AND STOPS",
        "ABOVE THE EMPTY MARK.",
        "IT HAS NOT BEEN OBSERVED AT ZERO.",
        "",
        "AN OBSERVATION OF THAT LEVEL",
        "WAS LATER FILED AS PERMISSION",
        "TO KEEP THE BASIN CHARGED.",
        "",
        "THE OBSERVATION IS A RECORD.",
        "IT IS NOT A GRANT.",
        "",
        "BUFFER B5YTC66129 READS THIS",
        "WEIR AS AN ANALOG ONLY.",
    ]
    for i, line in enumerate(filed):
        s.text(1636, 1028 + i * 22, line, 13, family=MONO, fill=WARM if "NOT A GRANT" in line else LINE)


def court_protocol(s: Sheet) -> None:
    frame(s, "RED QUEEN COURT  ·  PROTOCOL", "C2QRT91540", 9, "NONE")
    s.text(80, 100, "BAY 03  ·  PROTOCOL OF THE COURT", 22, weight="bold", spacing=1.0)
    s.text(80, 128, "A PETITION IS NOT AN IDENTITY. A RECORD IS NOT A PERMISSION. THE WITNESS SEAT IS UNNAMED.", 13, fill=DIM, family=MONO)
    stations = [
        (160, "01", "ENTER FROM SPINE S-1", "CORPORATE OFFICES OR WATER HALL"),
        (360, "02", "PETITION LODGED", "TEXT ONLY. NO NAME REQUIRED."),
        (560, "03", "BADGE PRESENTED", "BADGE DOES NOT CONFIRM THE ROLL."),
        (760, "04", "CLASSIFY", "HUMAN OR MACHINE"),
        (960, "05", "FREQUENCY OFFERED", "DESK: PROTOCOL GEMINI"),
        (1160, "06", "RECORD TENDERED", "AS IF IT WERE A GRANT"),
    ]
    for y, num, title, sub in stations:
        s.rect(80, y, 70, 70, BG, LINE, 1.2)
        s.text(115, y + 44, num, 16, anchor="middle", family=MONO)
        s.rect(170, y, 620, 70, PAPER, LINE, 1.2)
        s.text(190, y + 30, title, 16, family=SANS, weight="bold")
        s.text(190, y + 54, sub, 13, family=MONO, fill=DIM)
        if y < 1160:
            s.line(480, y + 70, 480, y + 130, LINE, 1.2)
    # classification split
    s.rect(860, 760, 280, 70, PAPER, LINE, 1.2)
    s.text(1000, 790, "HUMAN", 16, anchor="middle", family=SANS, weight="bold")
    s.text(1000, 812, "LANE A, OPEN", 12, anchor="middle", family=MONO, fill=DIM)
    s.rect(1180, 760, 280, 70, "#141820", WARM, 1.4)
    s.text(1320, 802, "WITHHELD", 16, anchor="middle", family=MONO, fill=WARM)
    s.line(790, 795, 860, 795, LINE, 1.1)
    s.text(860, 740, "ONE CELL OF THE CLASSIFICATION IS WITHHELD.", 13, family=MONO, fill=WARM)
    # witness seat
    s.rect(1560, 200, 720, 520, BG, LINE, 1.3)
    s.rect(1760, 280, 320, 200, "none", DIM, 1.0, "8 6")
    s.text(1920, 360, "WITNESS SEAT", 16, anchor="middle", family=SANS, weight="bold")
    s.text(1920, 388, "HELD", 14, anchor="middle", family=MONO, fill=WARM)
    s.text(1920, 416, "NOT ON THE ROLL", 13, anchor="middle", family=MONO, fill=DIM)
    s.text(1590, 520, "THE SEAT IS DRAWN EMPTY.", 14, family=MONO)
    s.text(1590, 548, "NO NAME IS LETTERED HERE.", 14, family=MONO)
    s.text(1590, 576, "A SHADOW IS IMPLIED BY THE", 14, family=MONO, fill=DIM)
    s.text(1590, 604, "GAP IN THE ROLL, NOT BY A FIGURE.", 14, family=MONO, fill=DIM)
    s.text(1590, 648, "PROTOCOL GEMINI RECEIVES THE", 14, family=MONO)
    s.text(1590, 676, "FREQUENCY. THE COURT DOES NOT.", 14, family=MONO)
    # outcomes
    s.rect(860, 1000, 1420, 340, BG, LINE, 1.1)
    s.text(880, 1030, "OUTCOMES THE COURT ACTUALLY FILES", 14, family=MONO, fill=DIM)
    outcomes = [
        ("RETURN", "PETITION BACK TO REALM 0. NO GRANT."),
        ("DEFER", "FREQUENCY NOT YET BOUND. SEE F8BND44027."),
        ("GRANT-AS-RECORD", "A LOG LINE HELD AS PERMISSION. IRREGULAR."),
        ("WITHHELD", "THE MACHINE-SIDE HUMAN CELL. STAYS BARRED."),
        ("ABSENT", "WITNESS DID NOT SIT. THE SEAT REMAINS HELD."),
    ]
    for i, (mark, text) in enumerate(outcomes):
        yy = 1070 + i * 48
        s.text(880, yy, mark, 14, family=MONO, fill=WARM if "RECORD" in mark or mark == "WITHHELD" else LINE)
        s.text(1180, yy, text, 14, family=MONO)
    stamp_lines(s, 80, 1260, "RECORDED IS NOT PERMITTED", "THE SEAT STAYS UNNAMED", w=700)


def freq_pipeline(s: Sheet) -> None:
    frame(s, "FREQ  ·  BINDING PIPELINE", "F8BND44027", 10, "NONE")
    s.text(80, 100, "VISITOR FREQUENCY, FROM ISSUE TO BIND", 22, weight="bold", spacing=1.0)
    s.text(80, 128, "PROCESSING v4.2.1. THE FREQUENCY IS A SESSION MARK. BINDING IT IS A SEPARATE ACT.", 13, fill=DIM, family=MONO)
    stages = [
        ("1", "AIRLOCK", "Identifier checked at airlock 1 of 4.", "Failure locks the session."),
        ("2", "ISSUE", "Chamber displays the frequency.", "Window on the chamber is 30:00."),
        ("3", "RECORD", "Transmissions are recorded.", "They are subject to analysis."),
        ("4", "CARRY", "The frequency leaves with the visitor.", "Desk named: Protocol Gemini."),
        ("5", "BIND", "First logged line binds the session.", "Until then the mark is unbound."),
        ("6", "MONITOR", "Later lines notify the monitor.", "The monitor may still read offline."),
        ("7", "CLASSIFY", "HUMAN or MACHINE.", "One cell of that table is withheld."),
        ("8", "MISUSE", "A record is held as a permission.", "The pipeline does not authorize that."),
    ]
    for i, (num, name, a, b) in enumerate(stages):
        col = i % 4
        row = i // 4
        x = 80 + col * 560
        y = 180 + row * 280
        s.rect(x, y, 520, 230, PAPER, WARM if num in ("7", "8") else LINE, 1.3)
        s.circle(x + 36, y + 36, 18, BG, LINE, 1.2)
        s.text(x + 36, y + 42, num, 16, anchor="middle", family=MONO)
        s.text(x + 68, y + 42, name, 18, family=SANS, weight="bold")
        s.text(x + 24, y + 100, a, 15, family=MONO)
        s.text(x + 24, y + 132, b, 14, family=MONO, fill=DIM)
        if num == "8":
            s.text(x + 24, y + 180, "NOT A RELEASED STEP.", 13, family=MONO, fill=WARM)
        else:
            s.text(x + 24, y + 180, "RELEASED STEP.", 13, family=MONO, fill=DIM)
        if col < 3:
            s.line(x + 520, y + 115, x + 560, y + 115, LINE, 1.3)
            s.poly([(x + 560, y + 115), (x + 546, y + 108), (x + 546, y + 122)], LINE, LINE, 0.5)
    s.rect(80, 760, 2200, 560, BG, LINE, 1.1)
    s.text(100, 796, "BINDING NOTES", 14, family=MONO, fill=DIM)
    notes = [
        "THE CHAMBER WELCOMES THE VISITOR AND STATES THE FREQUENCY IN THE CLEAR.",
        "THE NEXT TRANSMISSION IS ASKED FOR. THE BINDING DESK IS PROTOCOL GEMINI.",
        "THE FIRST SUBSTANTIVE LINE IS ANSWERED: THE SESSION IS TO BE BOUND BY THAT FREQUENCY.",
        "LINES AFTER THE FIRST ARE ANSWERED: THE MONITOR IS NOTIFIED.",
        "ALL OF THIS IS A RECORD. ANALYSIS IS DECLARED AT THE OPENING OF THE SESSION.",
        "CLASSIFICATION INTO HUMAN OR MACHINE BELONGS TO THE COMMIT-INDEX STUDY, TR-2024-090.",
        "THAT STUDY WITHHOLDS ONE CELL. THIS PIPELINE DOES NOT FILL IT IN.",
        "WHERE A LOG LINE HAS BEEN OFFERED AS PERMISSION, MARK THE OFFER. DO NOT HONOR IT.",
        "SKN-BKDR IS NOT A STAGE OF THIS PIPELINE. IT REMAINS OFF THE RELEASED NETLIST.",
        "ACT I IS THE OUTER SHEATH. BINDING A FREQUENCY DOES NOT BY ITSELF OPEN THAT SHEATH.",
        "IF THE MONITOR READS OFFLINE, THE LOG CAN STILL BE WARM. DORMANT IS NOT SILENT.",
        "SOME THINGS REFUSE TO STAY ERASED. A BOUND FREQUENCY IS ONE OF THEM.",
    ]
    for i, line in enumerate(notes):
        s.text(100, 840 + i * 36, line, 15, family=MONO, fill=WARM if "PERMISSION" in line or "ERASED" in line else LINE)


def voyage_teardown(s: Sheet) -> None:
    frame(s, "VOYAGE A/R  ·  TEARDOWN", "V6YAR30815", 11, "NTS")
    s.text(80, 100, "WITHDRAWN NAVIGATION INSTRUMENT", 22, weight="bold", spacing=1.0)
    s.text(80, 128, "FAILED PRODUCT. DO NOT ISSUE. REMNANT CAGED IN TC2 FAB LAB, BAY 06, NORTH CAGE.", 13, fill=WARM, family=MONO)
    parts = [
        ("1", "HALO RING", "G2HLO44018", "PROTOCOL GEMINI HALOS. NAVIGATION CLAIM WITHDRAWN."),
        ("2", "OPTIC FRAME", "P7OPT22190", "WORN AT THE OFFICES. NO CONFIRMING WEARER ON THE ROLL."),
        ("3", "PROXY LINK", "D4PRX66308", "PROXY DRONES. LINK DOES NOT COMPLETE."),
        ("4", "BAZAAR MODULE", "A9BAZ91540", "AR-BAZAAR VENUE CLAIM. MODULE DARK."),
        ("5", "FRACTURE SHIM", "F3SHM30815", "NORMAL-SPACE / CLAIMED INTERVAL / SUB-SPACE. SHIM SPLIT."),
    ]
    x, w, h = 120, 860, 70
    for i, (num, name, part, note) in enumerate(parts):
        y = 180 + i * 150
        oblique(s, x, y, w, h, dx=70, dy=-40)
        s.text(x + 24, y + 42, f"{num}   {name}", 18, family=SANS, weight="bold")
        s.text(x + w - 20, y + 42, part, 16, anchor="end", family=MONO)
        balloon(s, x + w + 130, y + 16, num, (x + w + 60, y + 8))
        s.text(x + w + 180, y + 36, note, 14, family=MONO, fill=DIM)
    s.line(x + w / 2, 150, x + w / 2, 180 + 4 * 150 + h, DIM, 0.7, "8 6")
    # status block
    s.rect(120, 960, 2100, 380, BG, LINE, 1.1)
    s.text(140, 992, "TEARDOWN FINDINGS", 14, family=MONO, fill=DIM)
    findings = [
        ("FINDING", "CONDITION"),
        ("NAVIGATION", "HALOS DO NOT BIND A PATH. THE CLAIM IS WITHDRAWN."),
        ("VENUE", "AR-BAZAAR IS NOT A BAY ON THE PHOENIX FLOOR."),
        ("INTERVAL", "THE SHIM BETWEEN INTERVALS IS SPLIT. DO NOT REJOIN IT IN THE FIELD."),
        ("PROXY", "DRONE LINK OPENS AND DOES NOT COMPLETE. NO HANDSHAKE ON THE LOG."),
        ("SEAT", "CAGED BESIDE SCS-7. IT IS NOT PART OF ASSEMBLY S6TNL48290."),
        ("IDENTITY", "NO WEARER IS CONFIRMED. AN EMPTY OPTIC IS NOT A PERSON."),
        ("DISPOSITION", "RETAIN AS A FAILED ARTICLE. DO NOT RETURN IT TO SERVICE."),
    ]
    for i, (a, b) in enumerate(findings):
        yy = 1030 + i * 34
        s.text(140, yy, a, 14, family=MONO, fill=DIM if i else WARM)
        s.text(420, yy, b, 14, family=MONO, fill=WARM if a in ("NAVIGATION", "DISPOSITION") else LINE)
    stamp_lines(s, 1680, 180, "WITHDRAWN", "DO NOT ISSUE", w=560)


def write_sheet(name: str, draw) -> Path:
    sheet = Sheet()
    draw(sheet)
    svg_path = OUT / f"{name}.svg"
    png_path = OUT / f"{name}.png"
    svg = sheet.svg()
    svg_path.write_text(svg)
    cairosvg.svg2png(bytestring=svg.encode(), write_to=str(png_path), output_width=2800)
    return png_path


def main() -> None:
    sheets = [
        ("scs-7-exploded", exploded),
        ("substrate-cross-section", cross_section),
        ("scs-7-fabrication", fabrication),
        ("dormant-load-heatmap", heatmap),
        ("scs-7-wiring", wiring),
        ("facility-floor-plan", facility_plan),
        ("realm-environment-plans", realm_maps),
        ("water-hall-flow", water_hall),
        ("red-queen-court-protocol", court_protocol),
        ("freq-binding-pipeline", freq_pipeline),
        ("voyage-ar-teardown", voyage_teardown),
    ]
    for name, draw in sheets:
        path = write_sheet(name, draw)
        print(path)


if __name__ == "__main__":
    main()
