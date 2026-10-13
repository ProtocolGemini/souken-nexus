#!/usr/bin/env python3
"""Generate Souken technical-report plates for docs/papers/.

Writes an SVG and a PNG for each figure under docs/papers/figures/<paper-id>/
and inserts figure references into the report markdown. Re-running is safe:
existing figure paths are left in place.

PNG export uses cairosvg (Cairo). Fonts: Liberation Serif, Sans, and Mono.
"""

from __future__ import annotations

import math
import random
import html
from pathlib import Path

import cairosvg

ROOT = Path(__file__).resolve().parents[3]
PAPERS = ROOT / "docs" / "papers"
OUT = PAPERS / "figures"

W, H = 920, 580
BG = "#f3efe4"
INK = "#1c1c1c"
MUTED = "#3e4a54"
UMBER = "#6b4c38"
OLIVE = "#3e5146"
SLATE = "#3c4f5f"
GRID = "#ddd6c8"
HAIR = "#b7afA2".lower()
SERIF = "Liberation Serif, Times New Roman, serif"
SANS = "Liberation Sans, Helvetica, Arial, sans-serif"
MONO = "Liberation Mono, Courier New, monospace"


def esc(value) -> str:
    return html.escape(str(value), quote=True)


class Plate:
    def __init__(self, report: str, date: str, number: int, title: str):
        self.report = report
        self.date = date
        self.number = number
        self.title = title
        self.parts: list[str] = []

    def add(self, fragment: str) -> None:
        self.parts.append(fragment)

    def rect(self, x, y, w, h, fill="none", stroke=INK, sw=1, dash=None, rx=0):
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        radius = f' rx="{rx}"' if rx else ""
        fill_attr = "none" if fill is None else fill
        stroke_attr = "none" if stroke is None else stroke
        self.add(
            f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" '
            f'fill="{fill_attr}" stroke="{stroke_attr}" stroke-width="{sw}"{extra}{radius}/>'
        )

    def line(self, x1, y1, x2, y2, stroke=INK, sw=1, dash=None):
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(
            f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
            f'stroke="{stroke}" stroke-width="{sw}"{extra}/>'
        )

    def circle(self, cx, cy, r, fill="none", stroke=INK, sw=1):
        self.add(
            f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}"/>'
        )

    def path(self, d, fill="none", stroke=INK, sw=1.2, dash=None, marker=True):
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        end = ' marker-end="url(#arrow)"' if marker else ""
        self.add(
            f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" '
            f'stroke-linejoin="miter" stroke-linecap="square"{extra}{end}/>'
        )

    def poly(self, pts, fill="none", stroke=INK, sw=1):
        points = " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)
        self.add(
            f'<polygon points="{points}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
        )

    def text(self, x, y, value, size=12, anchor="start", family=SANS, fill=INK, style="normal", weight="normal"):
        self.add(
            f'<text x="{x:.2f}" y="{y:.2f}" fill="{fill}" font-size="{size}" '
            f'font-family="{family}" font-style="{style}" font-weight="{weight}" '
            f'text-anchor="{anchor}">{esc(value)}</text>'
        )

    def frame(self):
        self.rect(0, 0, W, H, BG, None)
        self.rect(12, 12, W - 24, H - 24, None, INK, 1.15)
        self.rect(16, 16, W - 32, H - 32, None, INK, 0.45)
        for dx, dy, sx, sy in (
            (12, 12, -8, 0),
            (12, 12, 0, -8),
            (W - 12, 12, 8, 0),
            (W - 12, 12, 0, -8),
            (12, H - 12, -8, 0),
            (12, H - 12, 0, 8),
            (W - 12, H - 12, 8, 0),
            (W - 12, H - 12, 0, 8),
        ):
            self.line(dx, dy, dx + sx, dy + sy, INK, 0.7)
        self.text(28, 34, "SOUKEN INDUSTRIES  ·  RESEARCH DIVISION", 10, family=MONO, fill=INK)
        self.text(W - 28, 34, f"{self.report}  ·  {self.date}", 10, anchor="end", family=MONO)
        self.line(28, 42, W - 28, 42, INK, 0.6)
        self.text(28, 58, self.title, 13, family=SERIF, style="italic")
        self.line(28, H - 36, W - 28, H - 36, INK, 0.5)
        self.text(28, H - 22, f"FIG. {self.number}", 10, family=MONO)
        self.text(
            W - 28,
            H - 22,
            "COGNITIVE SUBSTRATE LABORATORY  ·  INTERNAL",
            10,
            anchor="end",
            family=MONO,
            fill=MUTED,
        )

    def svg(self) -> str:
        body = "\n".join(self.parts)
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">
    <path d="M0 0 L10 5 L0 10 Z" fill="{INK}"/>
  </marker>
  <pattern id="hatch" patternUnits="userSpaceOnUse" width="6" height="6" patternTransform="rotate(45)">
    <line x1="0" y1="0" x2="0" y2="6" stroke="{INK}" stroke-width="0.7"/>
  </pattern>
</defs>
{body}
</svg>
'''


def wrap(text: str, max_chars: int) -> list[str]:
    if not text:
        return []
    words = text.split()
    lines: list[str] = []
    cur = ""
    for word in words:
        trial = word if not cur else f"{cur} {word}"
        if len(trial) <= max_chars:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_node(plate: Plate, node: dict) -> None:
    x, y, w, h = node["x"], node["y"], node["w"], node["h"]
    kind = node.get("kind", "normal")
    fill = "#e6d9c8" if kind == "emphasis" else "#f7f4ec"
    sw = 1.35 if kind == "emphasis" else 1.0
    dash = "5 3" if kind == "ghost" else None
    plate.rect(x, y, w, h, fill, INK, sw, dash)
    if kind == "emphasis":
        plate.rect(x + 3.5, y + 3.5, w - 7, h - 7, None, INK, 0.55)
    cells = node.get("cells") or []
    title = node["title"]
    if cells:
        plate.text(x + w / 2, y + 18, title, 12, anchor="middle", family=SERIF, weight="bold")
        kicker = node.get("kicker")
        top = 26
        if kicker:
            plate.text(x + w / 2, y + 32, kicker, 8, anchor="middle", family=MONO, fill=UMBER)
            top = 40
        gap = 6
        cw = (w - 16 - gap * (len(cells) - 1)) / len(cells)
        ch = h - top - 10
        cy = y + top
        for i, cell in enumerate(cells):
            cx = x + 8 + i * (cw + gap)
            plate.rect(cx, cy, cw, ch, "#f7f4ec", INK, 0.75)
            lines = wrap(cell, max(6, int(cw / 6.4)))
            ty = cy + ch / 2 - (len(lines) - 1) * 6 + 3
            for line in lines:
                plate.text(cx + cw / 2, ty, line, 9, anchor="middle", family=SANS)
                ty += 12
        return
    max_chars = max(8, int((w - 14) / 6.7))
    lines = wrap(title, max_chars)
    sub_lines = wrap(node.get("sub") or "", max(10, int((w - 14) / 5.9)))
    block = len(lines) * 14 + len(sub_lines) * 12
    ty = y + (h - block) / 2 + 11
    for line in lines:
        plate.text(x + w / 2, ty, line, 12, anchor="middle", family=SERIF)
        ty += 14
    for line in sub_lines:
        plate.text(x + w / 2, ty, line, 9, anchor="middle", family=MONO, fill=MUTED)
        ty += 12


def port(node, side):
    x, y, w, h = node["x"], node["y"], node["w"], node["h"]
    if side == "e":
        return x + w, y + h / 2
    if side == "w":
        return x, y + h / 2
    if side == "n":
        return x + w / 2, y
    return x + w / 2, y + h


def route(a, b, mode=None):
    if mode == "under":
        x1, y1 = port(a, "s")
        x2, y2 = port(b, "s")
        low = max(a["y"] + a["h"], b["y"] + b["h"]) + 32
        return [(x1, y1), (x1, low), (x2, low), (x2, y2)]
    if mode == "over":
        x1, y1 = port(a, "n")
        x2, y2 = port(b, "n")
        high = min(a["y"], b["y"]) - 26
        return [(x1, y1), (x1, high), (x2, high), (x2, y2)]
    acx = a["x"] + a["w"] / 2
    acy = a["y"] + a["h"] / 2
    bcx = b["x"] + b["w"] / 2
    bcy = b["y"] + b["h"] / 2
    dx, dy = bcx - acx, bcy - acy
    if abs(dx) >= abs(dy) and abs(acy - bcy) < 22:
        side_a, side_b = ("e", "w") if dx >= 0 else ("w", "e")
        return [port(a, side_a), port(b, side_b)]
    if abs(dy) > abs(dx) and abs(acx - bcx) < 22:
        side_a, side_b = ("s", "n") if dy >= 0 else ("n", "s")
        return [port(a, side_a), port(b, side_b)]
    if abs(dx) >= abs(dy):
        side_a, side_b = ("e", "w") if dx >= 0 else ("w", "e")
        x1, y1 = port(a, side_a)
        x2, y2 = port(b, side_b)
        mid = (x1 + x2) / 2
        return [(x1, y1), (mid, y1), (mid, y2), (x2, y2)]
    side_a, side_b = ("s", "n") if dy >= 0 else ("n", "s")
    x1, y1 = port(a, side_a)
    x2, y2 = port(b, side_b)
    mid = (y1 + y2) / 2
    return [(x1, y1), (x1, mid), (x2, mid), (x2, y2)]


def draw_edge(plate: Plate, a, b, label=None, dash=False, route_mode=None):
    pts = route(a, b, route_mode)
    d = "M " + " L ".join(f"{x:.2f} {y:.2f}" for x, y in pts)
    plate.path(d, stroke=INK, sw=1.05, dash="4 3" if dash else None, marker=True)
    if not label:
        return
    # Place the label on the longest segment.
    best = max(
        ((pts[i], pts[i + 1]) for i in range(len(pts) - 1)),
        key=lambda seg: math.hypot(seg[1][0] - seg[0][0], seg[1][1] - seg[0][1]),
    )
    (x1, y1), (x2, y2) = best
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    length = math.hypot(x2 - x1, y2 - y1) or 1
    ox = -(y2 - y1) / length * 11
    oy = (x2 - x1) / length * 11
    lx, ly = mx + ox, my + oy
    width = len(label) * 5.6 + 10
    plate.rect(lx - width / 2, ly - 9, width, 13, BG, None)
    plate.text(lx, ly + 1, label, 9, anchor="middle", family=MONO, fill=MUTED)


def draw_diagram(plate: Plate, nodes: list[dict], edges: list[dict]) -> None:
    by_id = {n["id"]: n for n in nodes}
    for node in nodes:
        draw_node(plate, node)
    for edge in edges:
        draw_edge(
            plate,
            by_id[edge["src"]],
            by_id[edge["dst"]],
            edge.get("label"),
            edge.get("dash", False),
            edge.get("route"),
        )


def nice_step(span, count):
    if span <= 0:
        return 1
    raw = span / max(count - 1, 1)
    mag = 10 ** math.floor(math.log10(raw))
    for mult in (1, 2, 2.5, 5, 10):
        if mult * mag >= raw * 0.75:
            return mult * mag
    return 10 * mag


def ticks(lo, hi, count=5):
    step = nice_step(hi - lo, count)
    start = math.ceil((lo - 1e-9) / step) * step
    values = []
    v = start
    while v <= hi + step * 0.01:
        values.append(v)
        v += step
    if not values:
        values = [lo, hi]
    return values


def fmt_bar(value):
    if abs(value - round(value)) < 1e-6:
        return str(int(round(value)))
    if abs(value) >= 10:
        return f"{value:.1f}"
    return f"{value:.2f}"


def fmt_tick(value):
    if abs(value) < 1e-9:
        return "0"
    if abs(value - round(value)) < 1e-6:
        return str(int(round(value)))
    return f"{value:.1f}"


def draw_axes(plate, box, xlim, ylim, xlabel, ylabel):
    x0, y0, x1, y1 = box

    def px(x):
        return x0 + (x - xlim[0]) / (xlim[1] - xlim[0]) * (x1 - x0)

    def py(y):
        return y1 - (y - ylim[0]) / (ylim[1] - ylim[0]) * (y1 - y0)

    for xv in ticks(xlim[0], xlim[1]):
        if xv < xlim[0] - 1e-6 or xv > xlim[1] + 1e-6:
            continue
        xx = px(xv)
        plate.line(xx, y0, xx, y1, GRID, 0.6)
        plate.line(xx, y1, xx, y1 + 4, INK, 0.8)
        plate.text(xx, y1 + 16, fmt_tick(xv), 9, anchor="middle", family=MONO, fill=MUTED)
    for yv in ticks(ylim[0], ylim[1]):
        if yv < ylim[0] - 1e-6 or yv > ylim[1] + 1e-6:
            continue
        yy = py(yv)
        plate.line(x0, yy, x1, yy, GRID, 0.6)
        plate.line(x0 - 4, yy, x0, yy, INK, 0.8)
        plate.text(x0 - 8, yy + 3, fmt_tick(yv), 9, anchor="end", family=MONO, fill=MUTED)
    plate.line(x0, y0, x0, y1, INK, 1)
    plate.line(x0, y1, x1, y1, INK, 1)
    plate.text((x0 + x1) / 2, y1 + 34, xlabel, 11, anchor="middle", family=SERIF)
    plate.text(18, (y0 + y1) / 2, ylabel, 11, anchor="middle", family=SERIF, style="italic")
    # Rotate the y label by redrawing with a transform snippet.
    plate.parts[-1] = (
        f'<text x="18" y="{(y0 + y1) / 2:.2f}" fill="{INK}" font-size="11" '
        f'font-family="{SERIF}" font-style="italic" text-anchor="middle" '
        f'transform="rotate(-90 18 {(y0 + y1) / 2:.2f})">{esc(ylabel)}</text>'
    )
    return px, py


SHAPES = ("circle", "square", "diamond", "triangle", "plus", "cross")


def draw_marker(plate, x, y, r, shape, filled):
    fill = INK if filled else BG
    if shape == "circle":
        plate.circle(x, y, r, fill, INK, 1.1)
    elif shape == "square":
        plate.rect(x - r, y - r, 2 * r, 2 * r, fill, INK, 1.1)
    elif shape == "diamond":
        plate.poly([(x, y - r - 1), (x + r + 1, y), (x, y + r + 1), (x - r - 1, y)], fill, INK, 1.1)
    elif shape == "triangle":
        plate.poly([(x, y - r - 1), (x + r + 1, y + r), (x - r - 1, y + r)], fill, INK, 1.1)
    elif shape == "plus":
        plate.line(x - r, y, x + r, y, INK, 1.4)
        plate.line(x, y - r, x, y + r, INK, 1.4)
    else:
        plate.line(x - r, y - r, x + r, y + r, INK, 1.3)
        plate.line(x - r, y + r, x + r, y - r, INK, 1.3)


def benchmark(plate: Plate, rows: list[tuple]):
    """rows: (name, throughput_k, latency_ms, memory_mb) taken from the report table."""
    lats = [r[2] for r in rows]
    thr = [r[1] for r in rows]
    mem = [r[3] for r in rows]
    xlim = (0, max(lats) * 1.12)
    ylim = (0, max(thr) * 1.16)
    px, py = draw_axes(
        plate,
        (78, 86, 600, 470),
        xlim,
        ylim,
        "p99 latency (ms)",
        "throughput (k ops/s)",
    )
    max_mem = max(mem)
    plate.text(78, 80, "Marker area proportional to resident memory.", 9, family=MONO, fill=MUTED)
    for i, (name, tput, lat, memory) in enumerate(rows):
        radius = 5.5 + 8.5 * math.sqrt(memory / max_mem)
        draw_marker(plate, px(lat), py(tput), radius, SHAPES[i % len(SHAPES)], i % 2 == 0)
    legend_x = 628
    plate.line(616, 86, 616, 490, HAIR, 0.6)
    plate.text(legend_x, 96, "CONFIGURATION", 9, family=MONO, fill=MUTED)
    for i, (name, tput, lat, memory) in enumerate(rows):
        y = 118 + i * 58
        draw_marker(plate, legend_x + 8, y - 2, 5.2, SHAPES[i % len(SHAPES)], i % 2 == 0)
        plate.text(legend_x + 20, y + 2, name, 10, family=MONO)
        plate.text(legend_x, y + 18, f"{tput:g}k ops/s", 9, family=MONO, fill=MUTED)
        plate.text(legend_x, y + 32, f"{lat:g} ms    {memory:g} MB", 9, family=MONO, fill=MUTED)


def series_chart(plate, series, xlabel, ylabel, xlim, ylim, hlines=None, note=None):
    px, py = draw_axes(plate, (78, 84, 860, 468), xlim, ylim, xlabel, ylabel)
    if hlines:
        for y, label in hlines:
            yy = py(y)
            plate.line(78, yy, 860, yy, UMBER, 0.9, "5 4")
            plate.rect(620, yy - 16, 230, 14, BG, None)
            plate.text(848, yy - 5, label, 9, anchor="end", family=MONO, fill=UMBER)
    colors = (INK, UMBER, SLATE, OLIVE)
    for i, item in enumerate(series):
        color = colors[i % len(colors)]
        xs = [px(x) for x in item["x"]]
        ys = [py(y) for y in item["y"]]
        style = item.get("style", "line")
        if style in ("line", "both"):
            d = "M " + " L ".join(f"{x:.2f} {y:.2f}" for x, y in zip(xs, ys))
            plate.path(d, stroke=color, sw=1.45, marker=False)
        if style in ("points", "both"):
            for x, y in zip(xs, ys):
                plate.circle(x, y, 3.2, BG, color, 1.15)
        if len(series) > 1:
            ly = 100 + i * 16
            plate.line(620, ly - 3, 648, ly - 3, color, 1.5)
            plate.text(654, ly, item["name"], 10, family=MONO, fill=INK)
    if note:
        plate.text(78, 78, note, 9, family=MONO, fill=MUTED)


def bar_chart(plate, labels, values, xlabel, ylabel, note=None):
    n = len(labels)
    x0, y0, x1, y1 = 150, 86, 860, 455
    ymax = max(values) * 1.18
    px_span = x1 - x0
    slot = px_span / n
    py = lambda v: y1 - (v / ymax) * (y1 - y0)
    for yv in ticks(0, ymax):
        if yv < -1e-6 or yv > ymax + 1e-6:
            continue
        yy = py(yv)
        plate.line(x0, yy, x1, yy, GRID, 0.6)
        plate.text(x0 - 8, yy + 3, fmt_tick(yv), 9, anchor="end", family=MONO, fill=MUTED)
    plate.line(x0, y0, x0, y1, INK, 1)
    plate.line(x0, y1, x1, y1, INK, 1)
    for i, (label, value) in enumerate(zip(labels, values)):
        bw = slot * 0.62
        cx = x0 + slot * (i + 0.5)
        top = py(value)
        fill = "#d9d0c2" if i % 2 == 0 else "url(#hatch)"
        plate.rect(cx - bw / 2, top, bw, y1 - top, fill, INK, 0.9)
        plate.text(cx, top - 6, fmt_bar(value), 9, anchor="middle", family=MONO)
        plate.text(cx, y1 + 16, label, 9, anchor="middle", family=MONO, fill=MUTED)
    plate.text((x0 + x1) / 2, y1 + 36, xlabel, 11, anchor="middle", family=SERIF)
    plate.text(18, (y0 + y1) / 2, ylabel, 11, anchor="middle", family=SERIF)
    plate.parts[-1] = (
        f'<text x="18" y="{(y0 + y1) / 2:.2f}" fill="{INK}" font-size="11" '
        f'font-family="{SERIF}" font-style="italic" text-anchor="middle" '
        f'transform="rotate(-90 18 {(y0 + y1) / 2:.2f})">{esc(ylabel)}</text>'
    )
    if note:
        plate.text(150, 78, note, 9, family=MONO, fill=MUTED)


def hbar_chart(plate, labels, values, xlabel, value_fmt):
    n = len(labels)
    x0, y0, x1, y1 = 230, 90, 820, 500
    xmax = max(values) * 1.12
    slot = (y1 - y0) / n

    def px(v):
        return x0 + v / xmax * (x1 - x0)

    for xv in ticks(0, xmax):
        if xv < -1e-9 or xv > xmax + 1e-6:
            continue
        xx = px(xv)
        plate.line(xx, y0, xx, y1, GRID, 0.6)
        plate.text(xx, y1 + 16, fmt_tick(xv), 9, anchor="middle", family=MONO, fill=MUTED)
    plate.line(x0, y0, x0, y1, INK, 1)
    plate.line(x0, y1, x1, y1, INK, 1)
    for i, (label, value) in enumerate(zip(labels, values)):
        cy = y0 + slot * (i + 0.5)
        bh = slot * 0.55
        plate.rect(x0, cy - bh / 2, px(value) - x0, bh, "#d9d0c2" if i % 2 == 0 else "url(#hatch)", INK, 0.8)
        plate.text(x0 - 10, cy + 3, label, 10, anchor="end", family=MONO)
        plate.text(px(value) + 6, cy + 3, value_fmt(value), 9, family=MONO, fill=MUTED)
    plate.text((x0 + x1) / 2, y1 + 34, xlabel, 11, anchor="middle", family=SERIF)


def confusion(plate):
    labels = ["human", "machine"]
    # The machine→human cell is withheld. No marginal total is printed.
    cells = {
        (0, 0): "1,406",
        (0, 1): "88",
        (1, 0): None,
        (1, 1): "1,573",
    }
    x0, y0 = 250, 130
    cw, ch = 180, 110
    plate.text(x0 + cw, 100, "predicted class", 12, anchor="middle", family=SERIF, style="italic")
    plate.text(150, y0 + ch, "actual class", 12, anchor="middle", family=SERIF, style="italic")
    plate.parts[-1] = (
        f'<text x="150" y="{y0 + ch:.2f}" fill="{INK}" font-size="12" font-family="{SERIF}" '
        f'font-style="italic" text-anchor="middle" transform="rotate(-90 150 {y0 + ch:.2f})">actual class</text>'
    )
    for j, lab in enumerate(labels):
        plate.text(x0 + j * cw + cw / 2, y0 - 12, lab, 12, anchor="middle", family=MONO)
    for i, lab in enumerate(labels):
        plate.text(x0 - 12, y0 + i * ch + ch / 2 + 4, lab, 12, anchor="end", family=MONO)
    for i in range(2):
        for j in range(2):
            x = x0 + j * cw
            y = y0 + i * ch
            plate.rect(x, y, cw, ch, "#f7f4ec", INK, 1)
            value = cells[(i, j)]
            if value is None:
                plate.rect(x + 22, y + ch / 2 - 11, cw - 44, 22, "#141414", None)
            else:
                plate.text(x + cw / 2, y + ch / 2 + 8, value, 22, anchor="middle", family=SERIF)
    plate.text(250, 400, "Counts are held-out commit-index traces.", 10, family=MONO, fill=MUTED)
    plate.text(250, 418, "One cell is withheld. No row or column total is given.", 10, family=MONO, fill=MUTED)


def stem_spectrum(plate, freqs, mags, xlabel, ylabel, note):
    xlim = (0, max(freqs) * 1.08)
    ylim = (0, max(mags) * 1.18)
    px, py = draw_axes(plate, (78, 90, 860, 470), xlim, ylim, xlabel, ylabel)
    base = py(0)
    for f, m in zip(freqs, mags):
        x, y = px(f), py(m)
        plate.line(x, base, x, y, INK, 1.15)
        plate.circle(x, y, 3.1, INK, INK, 0.6)
    plate.text(78, 80, note, 9, family=MONO, fill=MUTED)


def node(i, x, y, w, h, title, sub=None, kind="normal", cells=None, kicker=None):
    item = {"id": i, "x": x, "y": y, "w": w, "h": h, "title": title, "kind": kind}
    if sub:
        item["sub"] = sub
    if cells:
        item["cells"] = cells
    if kicker:
        item["kicker"] = kicker
    return item


def edge(src, dst, label=None, dash=False, route_mode=None):
    item = {"src": src, "dst": dst}
    if label:
        item["label"] = label
    if dash:
        item["dash"] = True
    if route_mode:
        item["route"] = route_mode
    return item


def row_nodes(ids_titles, y, x0=40, w=190, h=62, gap=28, kind="normal"):
    nodes = []
    x = x0
    for ident, title in ids_titles:
        sub = None
        k = kind
        if isinstance(title, tuple):
            title, sub = title
        nodes.append(node(ident, x, y, w, h, title, sub, k))
        x += w + gap
    return nodes


def chain(ids):
    return [edge(a, b) for a, b in zip(ids, ids[1:])]


# ---------------------------------------------------------------------------
# Diagrams. Coordinates sit inside the plate between the header and footer.
# ---------------------------------------------------------------------------

def diag_019_flow():
    steps = [
        ("s1", "1  Lease revocation", "propagates the context switch"),
        ("s2", "2  Syscall table", "encrypts the billing meter"),
        ("s3", "3  Load balancer", "resolves the blue-green deployment"),
        ("s4", "4  Candidate release", "releases the elevator algorithm"),
    ]
    nodes = []
    y = 90
    for ident, title, sub in steps:
        nodes.append(node(ident, 250, y, 420, 70, title, sub))
        y += 100
    return nodes, chain(["s1", "s2", "s3", "s4"])


def diag_019_bkdr():
    nodes = [
        node("rq", 36, 84, 150, 50, "Run queue"),
        node("sem", 230, 84, 210, 50, "Distributed semaphore"),
        node(
            "bk",
            36,
            176,
            600,
            118,
            "SKN-BKDR",
            kind="emphasis",
            kicker="SUBSYSTEM",
            cells=["marker latch", "witness tap", "retention floor", "partition relay"],
        ),
        node("en", 690, 209, 190, 52, "Secure enclave"),
        node("cg", 690, 330, 190, 50, "Computation graph"),
        node("pk", 36, 420, 180, 50, "Partition key"),
        node("rp", 250, 420, 190, 50, "Range partition"),
        node("jc", 474, 420, 180, 50, "Joint consensus"),
    ]
    edges = [
        edge("rq", "sem"),
        edge("sem", "bk"),
        edge("bk", "en"),
        edge("en", "cg", "gossip"),
        edge("bk", "pk", "relay"),
        edge("pk", "rp"),
        edge("rp", "jc"),
        edge("cg", "jc"),
    ]
    return nodes, edges


def diag_018():
    nodes = [
        node("tw", 36, 110, 160, 58, "Timer wheel"),
        node("hb", 230, 110, 180, 58, "Heartbeat interval"),
        node("ck", 444, 110, 200, 58, "Clock event device"),
        node("to", 678, 110, 200, 58, "Timeout policy"),
        node("tp", 120, 250, 200, 58, "Two-phase commit"),
        node("sw", 444, 250, 200, 58, "Swim protocol"),
        node("dma", 230, 390, 190, 58, "DMA descriptor"),
        node("mk", 520, 390, 180, 58, "Merkle tree"),
    ]
    edges = [
        edge("tw", "hb"),
        edge("hb", "ck"),
        edge("ck", "to"),
        edge("hb", "tp"),
        edge("ck", "sw"),
        edge("tp", "dma"),
        edge("sw", "mk", "sign"),
        edge("dma", "mk"),
    ]
    return nodes, edges


def diag_017():
    nodes = [
        node("cm", 36, 140, 180, 64, "Compaction marker"),
        node("sm", 250, 140, 170, 64, "State machine"),
        node("mt", 454, 140, 160, 64, "Merkle tree"),
        node("cr", 650, 140, 190, 64, "Consensus round"),
        node("gt", 250, 310, 190, 64, "Gating mechanism"),
        node("sc", 490, 310, 180, 64, "Scheduler class"),
        node("ob", 36, 310, 180, 64, "Observation record"),
    ]
    edges = [
        edge("cm", "sm"),
        edge("sm", "mt"),
        edge("mt", "cr"),
        edge("sm", "gt"),
        edge("gt", "sc"),
        edge("cm", "ob", "record"),
    ]
    return nodes, edges


def diag_053():
    nodes = [
        node("rq", 36, 120, 150, 58, "Run queue"),
        node("rb", 220, 120, 160, 58, "Role binding"),
        node("sg", 420, 110, 200, 78, "Saga coordinator"),
        node("rp", 680, 120, 150, 58, "Replica"),
        node("bp", 220, 290, 180, 58, "Backpressure"),
        node("cn", 460, 290, 170, 58, "Canary"),
        node("mr", 680, 290, 170, 58, "Memory region"),
    ]
    edges = [
        edge("rq", "rb"),
        edge("rb", "sg"),
        edge("sg", "rp", "forward"),
        edge("sg", "bp"),
        edge("bp", "cn"),
        edge("rp", "mr"),
        edge("cn", "sg", "compensate", dash=True),
    ]
    return nodes, edges


def diag_093():
    columns = [
        ("c0", 40, "REALM 0", "substrate core", ["cognitive frame", "dma buffer", "heartbeat interval", "recovery point"]),
        ("c1", 330, "MEDIATION", "access gate", ["role binding", "isolation boundary", "metric collector", "optimizer state"]),
        ("c2", 620, "ACT I", "access layer", ["plan tier", "entitlement", "operator surface", "usage record"]),
    ]
    nodes = []
    for ident, x, title, sub, _cells in columns:
        nodes.append(node(ident, x, 110, 250, 300, title, sub))
    # cells drawn manually after the column shells, so leave shells and overlay labels
    edges = [
        edge("c0", "c1", "Realm 0"),
        edge("c1", "c2", "Act I"),
    ]
    return nodes, edges, columns


def draw_realm_map(plate: Plate):
    columns = [
        (40, "REALM 0", "substrate core", ["cognitive frame", "dma buffer", "heartbeat interval", "recovery point"]),
        (330, "MEDIATION", "access gate", ["role binding", "isolation boundary", "metric collector", "optimizer state"]),
        (620, "ACT I", "access layer", ["plan tier", "entitlement", "operator surface", "usage record"]),
    ]
    boxes = []
    for x, title, sub, cells in columns:
        plate.rect(x, 100, 250, 360, "#f7f4ec", INK, 1.15)
        plate.rect(x + 4, 104, 242, 352, None, INK, 0.4)
        plate.text(x + 125, 128, title, 14, anchor="middle", family=SERIF, weight="bold")
        plate.text(x + 125, 146, sub, 10, anchor="middle", family=MONO, fill=MUTED)
        for i, cell in enumerate(cells):
            cy = 168 + i * 66
            plate.rect(x + 18, cy, 214, 48, BG, INK, 0.75)
            plate.text(x + 125, cy + 29, cell, 12, anchor="middle", family=SANS)
        boxes.append({"x": x, "y": 100, "w": 250, "h": 360})
    draw_edge(plate, boxes[0], boxes[1], "Realm 0")
    draw_edge(plate, boxes[1], boxes[2], "Act I")


def diag_063():
    layers = [
        ("l1", "Secure enclave", "throttles the state machine"),
        ("l2", "Memory bank", "elects the tenant context"),
        ("l3", "Commit message", "encrypts the hyperloglog"),
        ("l4", "Latent space", "threshold-signs the range partition"),
        ("l5", "Superblock", "decoder and configuration entry"),
    ]
    nodes = []
    y = 86
    for ident, title, sub in layers:
        nodes.append(node(ident, 230, y, 460, 62, title, sub))
        y += 78
    edges = chain(["l5", "l4", "l3", "l2", "l1"])
    # chain() follows list order, but visually superblock is the base.
    # Redraw edges from base upward: l5 is last drawn at the bottom.
    edges = [edge("l5", "l4"), edge("l4", "l3"), edge("l3", "l2"), edge("l2", "l1")]
    return nodes, edges


def diag_004():
    nodes = [
        node("ap", 36, 150, 150, 58, "Append"),
        node("cp", 220, 150, 180, 58, "Checkpoint record"),
        node("wal", 440, 140, 200, 78, "Write-ahead log"),
        node("rp", 690, 150, 150, 58, "Replay"),
        node("nu", 220, 320, 160, 58, "Nullifier"),
        node("hb", 440, 320, 160, 58, "Heartbeat"),
        node("co", 680, 320, 180, 58, "Compensation"),
    ]
    edges = [
        edge("ap", "cp"),
        edge("cp", "wal"),
        edge("wal", "rp"),
        edge("cp", "nu"),
        edge("wal", "hb"),
        edge("rp", "co", "compensate", dash=True),
        edge("co", "wal", "restore", dash=True),
    ]
    return nodes, edges


def diag_092():
    nodes = [
        node("ci", 36, 160, 160, 58, "Correlation id"),
        node("cs", 230, 160, 180, 58, "Constraint system"),
        node("np", 450, 145, 200, 88, "Neural pathway"),
        node("ar", 700, 160, 180, 58, "Adaptation rate"),
        node("dma", 80, 340, 180, 58, "DMA descriptor"),
        node("bf", 360, 340, 160, 58, "Bloom filter"),
        node("lt", 600, 340, 200, 58, "Lamport timestamp"),
    ]
    edges = [
        edge("ci", "cs"),
        edge("cs", "np"),
        edge("np", "ar"),
        edge("cs", "dma"),
        edge("np", "bf"),
        edge("np", "lt"),
    ]
    return nodes, edges


def diag_002_action():
    nodes = [
        node("eb", 36, 160, 160, 64, "Event bus"),
        node("iv", 240, 160, 180, 64, "Interrupt vector"),
        node("as", 470, 145, 190, 94, "Action space"),
        node("io", 710, 160, 170, 64, "IOMMU mapping"),
        node("bio", 470, 340, 190, 64, "Bio request"),
    ]
    edges = [edge("eb", "iv"), edge("iv", "as"), edge("as", "io"), edge("as", "bio")]
    return nodes, edges


def diag_090():
    nodes = [
        node("ra", 36, 120, 190, 58, "Remote attestation"),
        node("qm", 260, 120, 170, 58, "Query matrix"),
        node("ci", 470, 110, 190, 78, "Commit index"),
        node("ss", 700, 120, 180, 58, "Session store"),
        node("fm", 80, 280, 210, 58, "Federation metadata"),
        node("us", 360, 280, 160, 58, "User stack"),
        node("pr", 590, 280, 180, 58, "Priority level"),
    ]
    edges = [
        edge("ra", "qm"),
        edge("qm", "ci"),
        edge("ci", "ss"),
        edge("qm", "fm"),
        edge("ci", "us"),
        edge("us", "pr"),
    ]
    return nodes, edges


def diag_067():
    nodes = [
        node(
            "bk",
            150,
            78,
            620,
            112,
            "SKN-BKDR",
            kind="emphasis",
            kicker="INSTRUMENTED SUBSYSTEM",
            cells=["marker latch", "witness tap", "retention floor", "partition relay"],
        ),
        node("mc", 310, 220, 300, 50, "Metric collector", "differentiable"),
        node("g", 70, 310, 170, 48, "Gauge"),
        node("c", 375, 310, 170, 48, "Counter"),
        node("h", 680, 310, 170, 48, "Histogram"),
        node("op", 310, 400, 300, 48, "Observability pipeline"),
        node("cf", 650, 400, 210, 48, "Credit-based flow"),
    ]
    edges = [
        edge("bk", "mc", "telemetry"),
        edge("mc", "g"),
        edge("mc", "c"),
        edge("mc", "h"),
        edge("c", "op"),
        edge("op", "cf"),
    ]
    return nodes, edges


def diag_zk():
    nodes = [
        node("sem", 36, 170, 150, 64, "Semaphore"),
        node("lc", 220, 170, 150, 64, "Latent code"),
        node("pr", 410, 155, 160, 94, "Prover"),
        node("zk", 620, 155, 250, 70, "ZK-STARK proof"),
        node("ae", 220, 360, 200, 58, "Anti-entropy session"),
        node("cb", 470, 360, 210, 58, "Circuit breaker state"),
        node("vf", 720, 300, 160, 58, "Verifier"),
    ]
    edges = [
        edge("sem", "lc"),
        edge("lc", "pr"),
        edge("pr", "zk"),
        edge("pr", "ae"),
        edge("ae", "cb"),
        edge("zk", "vf", "check"),
        edge("cb", "vf"),
    ]
    return nodes, edges


def diag_025():
    nodes = [
        node("wt", 36, 150, 140, 58, "Waiter"),
        node("fx", 220, 140, 160, 78, "Futex"),
        node("wq", 440, 150, 170, 58, "Wait queue"),
        node("wk", 680, 150, 140, 58, "Wake"),
        node("rc", 220, 310, 190, 58, "RCU grace period"),
        node("hr", 460, 310, 150, 58, "Hrtimer"),
        node("sb", 680, 310, 170, 58, "Superblock"),
    ]
    edges = [
        edge("wt", "fx"),
        edge("fx", "wq"),
        edge("wq", "wk"),
        edge("fx", "rc"),
        edge("rc", "hr"),
        edge("hr", "sb"),
        edge("wk", "fx", "requeue", dash=True, route_mode="over"),
    ]
    return nodes, edges


def diag_078():
    nodes = [
        node("a", 50, 120, 180, 70, "Process A", "local state"),
        node("b", 370, 120, 180, 70, "Process B", "local state"),
        node("c", 690, 120, 180, 70, "Process C", "local state"),
        node("m1", 230, 250, 120, 48, "Marker"),
        node("m2", 540, 250, 120, 48, "Marker"),
        node("gs", 300, 390, 320, 64, "Global snapshot", "Chandy-Lamport record"),
    ]
    edges = [
        edge("a", "m1", "channel"),
        edge("m1", "b"),
        edge("b", "m2", "channel"),
        edge("m2", "c"),
        edge("a", "gs"),
        edge("b", "gs"),
        edge("c", "gs"),
    ]
    return nodes, edges


def diag_024():
    nodes = [
        node("rq", 40, 180, 160, 64, "Request id"),
        node("qm", 280, 165, 200, 94, "Quota manager"),
        node("ok", 580, 110, 250, 58, "Admit", "service discovery"),
        node("no", 580, 250, 250, 58, "Reject", "clock source"),
        node("hb", 280, 360, 200, 58, "Heartbeat interval"),
    ]
    edges = [
        edge("rq", "qm"),
        edge("qm", "ok", "within quota"),
        edge("qm", "no", "over quota"),
        edge("qm", "hb"),
    ]
    return nodes, edges


def diag_072():
    nodes = [
        node("g", 40, 180, 150, 64, "Gradient"),
        node("w", 240, 165, 190, 94, "Weight matrix"),
        node("s", 490, 165, 180, 94, "Spectral norm"),
        node("u", 720, 180, 160, 64, "Clipped update"),
        node("sv", 240, 370, 190, 58, "Singular values"),
        node("hn", 490, 370, 180, 58, "Hard negative"),
    ]
    edges = [
        edge("g", "w"),
        edge("w", "s", "bound"),
        edge("s", "u"),
        edge("w", "sv"),
        edge("s", "hn"),
    ]
    return nodes, edges


def diag_010():
    nodes = [
        node("a", 50, 120, 230, 64, "Writer A", "earlier timestamp"),
        node("b", 50, 250, 230, 64, "Writer B", "later timestamp"),
        node("lww", 420, 170, 220, 90, "LWW register", "last writer wins"),
        node("gs", 700, 185, 180, 64, "Global snapshot"),
    ]
    edges = [
        edge("a", "lww"),
        edge("b", "lww", "wins"),
        edge("lww", "gs"),
    ]
    return nodes, edges


def diag_062():
    nodes = [
        node("req", 40, 180, 140, 58, "Request"),
        node("gr", 230, 165, 160, 88, "Grant"),
        node("rn", 450, 165, 160, 88, "Renew"),
        node("ex", 680, 180, 160, 58, "Expire"),
        node("co", 230, 360, 160, 52, "Cohort"),
        node("to", 450, 360, 180, 52, "Timeout policy"),
        node("ra", 680, 340, 190, 58, "Remote attestation"),
    ]
    edges = [
        edge("req", "gr"),
        edge("gr", "rn"),
        edge("rn", "ex"),
        edge("rn", "gr", "extend", dash=True),
        edge("gr", "co"),
        edge("rn", "to"),
        edge("ex", "ra"),
    ]
    return nodes, edges


def diag_ff():
    nodes = [
        node("in", 36, 180, 120, 58, "Input"),
        node("ln", 190, 180, 150, 58, "Layer norm"),
        node("ff", 380, 160, 200, 98, "Feed-forward block"),
        node("rs", 630, 180, 140, 58, "Residual add"),
        node("out", 800, 180, 90, 58, "Output"),
        node("ac", 400, 360, 160, 52, "Activation"),
    ]
    edges = [
        edge("in", "ln"),
        edge("ln", "ff"),
        edge("ff", "rs"),
        edge("rs", "out"),
        edge("ff", "ac"),
        edge("in", "rs", "skip", dash=True, route_mode="under"),
    ]
    return nodes, edges


def measured_decay():
    floor = 0.190
    amp = 0.740
    tau = 18.0
    rng = random.Random(2017)
    xs, fit, obs_x, obs_y = [], [], [], []
    t = 0.0
    while t <= 60.001:
        y = floor + amp * math.exp(-t / tau)
        xs.append(t)
        fit.append(y)
        if abs(t - round(t / 4) * 4) < 1e-6:
            noisy = y + rng.uniform(-0.012, 0.012)
            obs_x.append(t)
            obs_y.append(max(noisy, floor + 0.012))
        t += 1.0
    return xs, fit, obs_x, obs_y, floor


def spectrum_018():
    # Clock-event residual. Arbitrary units; no benchmark figure is reused as a frequency.
    freqs = [0.4, 0.8, 1.2, 1.6, 2.0, 2.4, 2.8, 3.6, 4.4, 5.2, 6.0]
    mags = [0.18, 1.00, 0.42, 0.22, 0.55, 0.16, 0.11, 0.27, 0.09, 0.14, 0.05]
    return freqs, mags


def adaptation_019():
    xs = [1, 2, 4, 8, 16, 32, 64]
    ys = [0.22, 0.35, 0.49, 0.62, 0.71, 0.76, 0.78]
    return xs, ys


PAPERS_SPEC = []


def add_paper(**kwargs):
    PAPERS_SPEC.append(kwargs)


def bench_caption(n, what):
    return (
        f"Figure {n}. {what} Throughput against p99 latency. "
        "Marker area is resident memory. Every value is the benchmark table of this report."
    )


# Paper entries. Figure numbers follow order of appearance.
add_paper(
    paper_id="souken-tr-2026-019",
    report="TR-2026-019",
    date="2022-03",
    filename="souken-tr-2026-019.md",
    figures=[
        dict(
            n=1, slug="lease-flow", title="Lease revocation through the elevator algorithm",
            alt="Lease revocation procedure",
            caption="Figure 1. Lease revocation through the elevator algorithm. Revocation propagates the context switch, the syscall table encrypts the billing meter, the load balancer resolves the blue-green deployment, and the candidate releases the elevator algorithm.",
            anchor="## Architecture",
            draw="diagram", diagram=diag_019_flow,
        ),
        dict(
            n=2, slug="skn-bkdr", title="SKN-BKDR on the hierarchical compaction path",
            alt="SKN-BKDR subsystem block diagram",
            caption="Figure 2. SKN-BKDR subsystem on the hierarchical compaction path. The run queue enters at the distributed semaphore. SKN-BKDR — marker latch, witness tap, retention floor, partition relay — sits ahead of the hierarchical secure enclave, which gossips the computation graph. The partition relay feeds the partition key, the range partition, and joint consensus.",
            anchor="## Evaluation",
            draw="diagram", diagram=diag_019_bkdr,
        ),
        dict(
            n=3, slug="benchmarks", title="Benchmark configurations",
            alt="Throughput against p99 latency for the reported configurations",
            caption=bench_caption(3, "Reported configurations of the hierarchical compaction marker."),
            anchor="## Results",
            draw="bench",
            rows=[
                ("bidirectional-8x", 453, 15.7, 3405),
                ("transformer-based-1x", 31, 20.8, 154),
                ("calibrated-1x", 419, 29.1, 708),
                ("cross-modal-2x", 112, 19.4, 3319),
                ("helpful-1x", 371, 38.0, 3914),
            ],
        ),
        dict(
            n=4, slug="adaptation", title="Adaptation rate against query-set size",
            alt="Adaptation rate rising with query-set size",
            caption="Figure 4. Adaptation rate against query-set size. The deterministic adaptation rate reflects the query set and levels off near 0.78 under the largest set exercised here.",
            replace="![Figure 1: Experimental Overview](figures/test_figure.png)",
            draw="adapt",
        ),
    ],
)

add_paper(
    paper_id="souken-tr-2026-018",
    report="TR-2026-018",
    date="2023-04",
    filename="souken-tr-2026-018.md",
    figures=[
        dict(
            n=1, slug="clock-device", title="Differentiable clock event device",
            alt="Clock event device block diagram",
            caption="Figure 1. Differentiable clock event device. The timer wheel feeds the heartbeat interval and the clock event device, which sets the timeout policy. Two-phase commit and the swim protocol meet at the merkle tree; the DMA descriptor joins that path.",
            anchor="## Evaluation",
            draw="diagram", diagram=diag_018,
        ),
        dict(
            n=2, slug="benchmarks", title="Benchmark configurations",
            alt="Throughput against p99 latency for the clock event device",
            caption=bench_caption(2, "Reported configurations of the clock event device."),
            anchor="## Results",
            draw="bench",
            rows=[
                ("dense-8x", 31, 24.3, 3998),
                ("deterministic-4x", 202, 34.7, 1822),
                ("aligned-8x", 233, 47.7, 1814),
                ("data-efficient-1x", 457, 0.9, 2075),
                ("adversarial-8x", 156, 43.3, 314),
            ],
        ),
        dict(
            n=3, slug="heartbeat-spectrum", title="Clock-event residual spectrum",
            alt="Spectrum of the clock-event residual",
            caption="Figure 3. Spectrum of the clock-event residual after the heartbeat interval is attended. Magnitude is normalized to the fundamental. The trace is independent of the latency column in the benchmark table.",
            replace="![Figure 1: Factual vote request — Experimental Results](figures/tr-2026-018-fig1.png)",
            draw="spectrum",
        ),
    ],
)

add_paper(
    paper_id="souken-tr-2026-017",
    report="TR-2026-017",
    date="2024-12",
    filename="souken-tr-2026-017.md",
    figures=[
        dict(
            n=1, slug="observation-path", title="Deterministic observation path",
            alt="Deterministic observation architecture",
            caption="Figure 1. Deterministic observation path. The compaction marker coordinates the state machine, the merkle tree, and the consensus round. The gating mechanism reaches the scheduler class. An observation record is retained beside the marker.",
            anchor="## Evaluation",
            draw="diagram", diagram=diag_017,
        ),
        dict(
            n=2, slug="benchmarks", title="Benchmark configurations",
            alt="Throughput against p99 latency for deterministic observation",
            caption=bench_caption(2, "Reported configurations for deterministic observation."),
            anchor="## Results",
            draw="bench",
            rows=[
                ("calibrated-2x", 358, 44.9, 659),
                ("composable-8x", 270, 23.0, 1164),
                ("hierarchical-8x", 352, 46.1, 620),
            ],
        ),
        dict(
            n=3, slug="retention-decay", title="Observation retention",
            alt="Observation retention decay curve above a positive floor",
            caption="Figure 3. Observation retention. The fitted record falls toward a floor of 0.190 and remains above it through epoch 60. The curve does not attain zero.",
            anchor="## Discussion",
            draw="retention",
        ),
        dict(
            n=4, slug="observation-frequency", title="Observation frequency by record class",
            alt="Observation frequency by record class",
            caption="Figure 4. Observation frequency by record class over the same held-out window as Figure 3. Counts are records retained, not the throughput column of the benchmark table.",
            anchor="## Discussion",
            draw="bars",
            labels=["marker", "merkle", "consensus", "gating", "page cache"],
            values=[1840, 1210, 960, 640, 410],
            xlabel="record class",
            ylabel="observations retained",
            note="Held-out window, deterministic observation.",
        ),
    ],
)

add_paper(
    paper_id="souken-tr-2026-053",
    report="TR-2026-053",
    date="2022-07",
    filename="souken-tr-2026-053.md",
    figures=[
        dict(n=1, slug="saga", title="Composable saga coordinator",
             alt="Saga coordinator with a compensation return",
             caption="Figure 1. Composable saga coordinator. The forward path runs from the run queue through role binding to the replica. Backpressure reaches the canary. The dashed return is the compensation path.",
             anchor="## Evaluation", draw="diagram", diagram=diag_053),
        dict(n=2, slug="benchmarks", title="Benchmark configurations",
             alt="Throughput against p99 latency for the saga coordinator",
             caption=bench_caption(2, "Reported configurations of the saga coordinator."),
             anchor="## Results", draw="bench",
             rows=[
                 ("dense-8x", 429, 20.9, 3428),
                 ("few-shot-4x", 113, 5.3, 577),
                 ("bidirectional-2x", 101, 4.6, 2938),
                 ("compute-optimal-1x", 165, 42.3, 3793),
             ]),
        dict(n=3, slug="saga-outcomes", title="Saga outcomes",
             alt="Frequency of saga outcomes",
             caption="Figure 3. Saga outcomes on the held-out run. Forward commit, compensation, and abort are counted separately from the benchmark table.",
             anchor="## Discussion", draw="bars",
             labels=["commit", "compensate", "abort", "retry"],
             values=[612, 147, 38, 54],
             xlabel="outcome", ylabel="sagas", note="Held-out saga log."),
    ],
)

add_paper(
    paper_id="souken-tr-2026-093",
    report="TR-2026-093",
    date="2025-05",
    filename="souken-tr-2026-093.md",
    figures=[
        dict(n=1, slug="realm-act-access", title="Realm 0 to Act I access layer",
             alt="Realm 0 to Act I access-layer map",
             caption="Figure 1. Access layer from Realm 0 to Act I. Realm 0 holds the substrate core. Mediation carries role binding and the isolation boundary. Act I is the operator-facing entitlement surface.",
             anchor="## Evaluation", draw="realm"),
        dict(n=2, slug="benchmarks", title="Benchmark configurations",
             alt="Throughput against p99 latency for differentiable entitlement",
             caption=bench_caption(2, "Reported configurations of differentiable entitlement."),
             anchor="## Results", draw="bench",
             rows=[
                 ("harmless-1x", 250, 26.3, 4007),
                 ("cross-modal-4x", 219, 12.3, 3120),
                 ("dense-4x", 173, 19.9, 2563),
                 ("multi-objective-8x", 235, 28.1, 1732),
                 ("memory-efficient-2x", 163, 19.1, 138),
             ]),
        dict(n=3, slug="grant-rate", title="Entitlement decisions along the access layer",
             alt="Entitlement grant, defer, and deny counts",
             caption="Figure 3. Entitlement decisions recorded on the Act I side of the access layer. Grant, defer, and deny are counts of decisions, not operations per second.",
             anchor="## Discussion", draw="bars",
             labels=["grant", "defer", "deny", "revoke"],
             values=[980, 214, 76, 41],
             xlabel="decision", ylabel="count", note="Act I access layer, held-out window."),
    ],
)

add_paper(
    paper_id="souken-tr-2027-063",
    report="TR-2027-063",
    date="2020-01",
    filename="souken-tr-2027-063.md",
    figures=[
        dict(n=1, slug="superblock", title="Memory-efficient superblock",
             alt="Superblock stack",
             caption="Figure 1. Memory-efficient superblock. The superblock seats the latent space, the commit message, the memory bank, and the secure enclave above the decoder path described in the architecture section.",
             anchor="## Evaluation", draw="diagram", diagram=diag_063),
        dict(n=2, slug="benchmarks", title="Benchmark configurations",
             alt="Throughput against p99 latency for the superblock",
             caption=bench_caption(2, "Reported configurations of the memory-efficient superblock."),
             anchor="## Results", draw="bench",
             rows=[
                 ("variational-8x", 138, 23.5, 2486),
                 ("adversarial-2x", 91, 31.8, 1231),
                 ("recurrent-4x", 194, 7.2, 1175),
                 ("recursive-2x", 440, 32.6, 3679),
                 ("few-shot-2x", 215, 37.7, 495),
                 ("autoregressive-2x", 69, 21.7, 3036),
             ]),
        dict(n=3, slug="resident-memory", title="Resident memory by configuration",
             alt="Resident memory taken from the benchmark table",
             caption="Figure 3. Resident memory by configuration, transcribed from the benchmark table. The recursive-2x seat is the largest; few-shot-2x is the smallest.",
             anchor="## Discussion", draw="hbars",
             labels=["variational-8x", "adversarial-2x", "recurrent-4x", "recursive-2x", "few-shot-2x", "autoregressive-2x"],
             values=[2486, 1231, 1175, 3679, 495, 3036],
             xlabel="resident memory (MB)",
             value_fmt=lambda v: f"{v:g} MB"),
    ],
)

add_paper(
    paper_id="souken-tr-2027-004",
    report="TR-2027-004",
    date="2022-08",
    filename="souken-tr-2027-004.md",
    figures=[
        dict(n=1, slug="wal", title="Adversarial write-ahead log",
             alt="Write-ahead log with replay and compensation",
             caption="Figure 1. Adversarial write-ahead log. Appends pass the checkpoint record into the log and on to replay. Heartbeat and nullifier sit beside the log. The dashed path is compensation back into the log.",
             anchor="## Evaluation", draw="diagram", diagram=diag_004),
        dict(n=2, slug="benchmarks", title="Benchmark configurations",
             alt="Throughput against p99 latency for the write-ahead log",
             caption=bench_caption(2, "Reported configurations of the adversarial write-ahead log."),
             anchor="## Results", draw="bench",
             rows=[
                 ("sparse-4x", 324, 10.0, 307),
                 ("deterministic-8x", 492, 29.0, 136),
                 ("recurrent-2x", 186, 38.6, 2129),
                 ("semi-supervised-1x", 495, 1.5, 2092),
             ]),
        dict(n=3, slug="record-classes", title="Write-ahead record classes",
             alt="Frequency of write-ahead record classes",
             caption="Figure 3. Write-ahead record classes in the results window. Append, checkpoint, replay, and compensate are record counts.",
             anchor="## Discussion", draw="bars",
             labels=["append", "checkpoint", "replay", "compensate"],
             values=[2400, 310, 860, 140],
             xlabel="record class", ylabel="records", note="Results window."),
    ],
)

add_paper(
    paper_id="souken-tr-2025-092",
    report="TR-2025-092",
    date="2021-07",
    filename="souken-tr-2025-092.md",
    figures=[
        dict(n=1, slug="pathway", title="Multi-objective neural pathway",
             alt="Neural pathway block diagram",
             caption="Figure 1. Multi-objective neural pathway. Correlation id and the constraint system enter the pathway; adaptation rate leaves it. The DMA descriptor, bloom filter, and Lamport timestamp are the side paths named in the architecture section.",
             anchor="## Evaluation", draw="diagram", diagram=diag_092),
        dict(n=2, slug="benchmarks", title="Benchmark configurations",
             alt="Throughput against p99 latency for the neural pathway",
             caption=bench_caption(2, "Reported configurations of the multi-objective neural pathway."),
             anchor="## Results", draw="bench",
             rows=[
                 ("aligned-1x", 112, 43.5, 3268),
                 ("explainable-4x", 300, 45.6, 1142),
                 ("modular-8x", 14, 31.0, 3740),
             ]),
        dict(n=3, slug="objectives", title="Objective losses",
             alt="Three objective loss curves",
             caption="Figure 3. Training loss on three objectives carried by the pathway: spectral norm, variational gap, and aggregate signature. The curves are training traces, not the benchmark table.",
             anchor="## Discussion", draw="losses"),
    ],
)

add_paper(
    paper_id="souken-tr-2025-002",
    report="TR-2025-002",
    date="2023-05",
    filename="souken-tr-2025-002.md",
    figures=[
        dict(n=1, slug="action-space", title="Grounded action space",
             alt="Action space architecture",
             caption="Figure 1. Grounded action space. The event bus reaches the interrupt vector and the action space, which signs the IOMMU mapping and seats the bio request.",
             anchor="## Evaluation", draw="diagram", diagram=diag_002_action),
        dict(n=2, slug="benchmarks", title="Benchmark configurations",
             alt="Throughput against p99 latency for the action space",
             caption=bench_caption(2, "Reported configurations of the grounded action space."),
             anchor="## Results", draw="bench",
             rows=[
                 ("stochastic-1x", 176, 20.1, 2276),
                 ("adversarial-4x", 80, 44.7, 1361),
                 ("differentiable-8x", 418, 13.9, 814),
                 ("subquadratic-8x", 369, 48.6, 230),
                 ("semi-supervised-1x", 487, 22.0, 164),
                 ("multi-task-4x", 310, 17.5, 269),
             ]),
        dict(n=3, slug="action-frequency", title="Action frequency",
             alt="Frequency of grounded actions",
             caption="Figure 4. Action counts on the held-out trace: commit, rollback, merge, throttle, and attest.".replace("Figure 4", "Figure 3"),
             anchor="## Discussion", draw="bars",
             labels=["commit", "rollback", "merge", "throttle", "attest"],
             values=[540, 120, 210, 95, 160],
             xlabel="action", ylabel="count", note="Held-out action trace."),
    ],
)

add_paper(
    paper_id="souken-tr-2024-090",
    report="TR-2024-090",
    date="2020-11",
    filename="souken-tr-2024-090.md",
    figures=[
        dict(n=1, slug="commit-index", title="Robust commit index",
             alt="Commit index architecture",
             caption="Figure 1. Robust commit index. Remote attestation and the query matrix enter the index, which writes the session store. Federation metadata, the user stack, and priority level sit on the side path.",
             anchor="## Evaluation", draw="diagram", diagram=diag_090),
        dict(n=2, slug="benchmarks", title="Benchmark configurations",
             alt="Throughput against p99 latency for the commit index",
             caption=bench_caption(2, "Reported configurations of the robust commit index."),
             anchor="## Results", draw="bench",
             rows=[
                 ("zero-shot-4x", 52, 16.1, 3783),
                 ("interpretable-4x", 453, 39.2, 359),
                 ("cross-modal-8x", 142, 31.1, 3453),
                 ("causal-2x", 18, 49.2, 1310),
                 ("explainable-4x", 201, 49.7, 1724),
                 ("variational-2x", 63, 34.3, 3410),
             ]),
        dict(n=3, slug="human-machine", title="Human versus machine classification",
             alt="Human versus machine confusion matrix with one cell redacted",
             caption="Figure 3. Human-versus-machine classification on held-out commit-index traces. Rows are the actual class and columns are the predicted class. One cell is redacted.",
             anchor="## Discussion", draw="confusion"),
    ],
)

add_paper(
    paper_id="souken-tr-2024-067",
    report="TR-2024-067",
    date="2023-02",
    filename="souken-tr-2024-067.md",
    figures=[
        dict(n=1, slug="skn-bkdr-metrics", title="SKN-BKDR under the metric collector",
             alt="SKN-BKDR subsystem instrumented by the metric collector",
             caption="Figure 1. SKN-BKDR under the differentiable metric collector. Telemetry leaves the subsystem (marker latch, witness tap, retention floor, partition relay) and is split into gauge, counter, and histogram. The observability pipeline continues into credit-based flow.",
             anchor="## Evaluation", draw="diagram", diagram=diag_067),
        dict(n=2, slug="benchmarks", title="Benchmark configurations",
             alt="Throughput against p99 latency for the metric collector",
             caption=bench_caption(2, "Reported configurations of the differentiable metric collector."),
             anchor="## Results", draw="bench",
             rows=[
                 ("parameter-efficient-1x", 290, 8.7, 432),
                 ("subquadratic-2x", 280, 36.0, 3566),
                 ("grounded-4x", 470, 27.3, 1423),
             ]),
        dict(n=3, slug="metric-series", title="Collector series during evaluation",
             alt="Gauge, counter rate, and histogram mean",
             caption="Figure 3. Three series from the collector during the evaluation window: gauge level, counter rate, and histogram mean. The vertical scale is normalized within each series to its own start, so the traces can share a frame.",
             anchor="## Discussion", draw="metrics"),
    ],
)

add_paper(
    paper_id="souken-tr-2023-053",
    report="TR-2023-053",
    date="2025-02",
    filename="souken-tr-2023-053.md",
    figures=[
        dict(n=1, slug="zk-stark", title="Factual ZK-STARK path",
             alt="ZK-STARK proving path",
             caption="Figure 1. Factual ZK-STARK path. The semaphore and latent code enter the prover. The proof is checked by the verifier. The anti-entropy session and the circuit breaker state join that check.",
             anchor="## Evaluation", draw="diagram", diagram=diag_zk),
        dict(n=2, slug="benchmarks", title="Benchmark configurations",
             alt="Throughput against p99 latency for the ZK-STARK path",
             caption=bench_caption(2, "Reported configurations of the factual ZK-STARK path."),
             anchor="## Results", draw="bench",
             rows=[
                 ("recursive-8x", 209, 29.6, 3869),
                 ("helpful-2x", 364, 12.8, 2122),
                 ("explainable-4x", 219, 30.1, 2048),
                 ("harmless-8x", 214, 45.7, 1019),
                 ("linear-complexity-4x", 43, 26.1, 1954),
             ]),
        dict(n=3, slug="calibration", title="Contrastive calibration curve",
             alt="Calibration curve of predicted probability against observed frequency",
             caption="Figure 3. Contrastive calibration curve. Predicted probability is plotted against observed frequency on the held-out proof set. The dashed line is perfect calibration.",
             anchor="## Discussion", draw="calibration"),
    ],
)

add_paper(
    paper_id="souken-tr-2023-025",
    report="TR-2023-025",
    date="2024-01",
    filename="souken-tr-2023-025.md",
    figures=[
        dict(n=1, slug="futex", title="Explainable futex",
             alt="Futex wait and wake path",
             caption="Figure 1. Explainable futex. A waiter enters the futex, the wait queue, and wake. The RCU grace period, hrtimer, and superblock sit under the futex. The dashed arrow is a requeue back onto the futex.",
             anchor="## Evaluation", draw="diagram", diagram=diag_025),
        dict(n=2, slug="benchmarks", title="Benchmark configurations",
             alt="Throughput against p99 latency for the futex",
             caption=bench_caption(2, "Reported configurations of the explainable futex."),
             anchor="## Results", draw="bench",
             rows=[
                 ("semi-supervised-1x", 280, 45.5, 3486),
                 ("calibrated-1x", 321, 28.6, 927),
                 ("adversarial-2x", 156, 45.9, 166),
                 ("grounded-8x", 186, 9.8, 2974),
             ]),
        dict(n=3, slug="wake-latency", title="Wake-interval histogram",
             alt="Histogram of futex wake intervals",
             caption="Figure 3. Wake-interval histogram for the calibrated-1x configuration. Bins are interval counts. The p99 of 28.6 ms in the benchmark table is not a bin of this histogram.",
             anchor="## Discussion", draw="bars",
             labels=["0–4", "4–8", "8–12", "12–16", "16–24", "24–40"],
             values=[420, 610, 540, 260, 140, 45],
             xlabel="wake interval (ms)", ylabel="wakes", note="Calibrated-1x, held-out wakes."),
    ],
)

add_paper(
    paper_id="souken-tr-2022-078",
    report="TR-2022-078",
    date="2020-10",
    filename="souken-tr-2022-078.md",
    figures=[
        dict(n=1, slug="marker-propagation", title="Chandy-Lamport marker propagation",
             alt="Marker propagation across three processes",
             caption="Figure 1. Few-shot Chandy-Lamport marker. Markers move on the channels from process A to B to C. Each process contributes its local state to the global snapshot.",
             anchor="## Evaluation", draw="diagram", diagram=diag_078),
        dict(n=2, slug="benchmarks", title="Benchmark configurations",
             alt="Throughput against p99 latency for the marker",
             caption=bench_caption(2, "Reported configurations of the Chandy-Lamport marker."),
             anchor="## Results", draw="bench",
             rows=[
                 ("semi-supervised-2x", 481, 23.6, 3287),
                 ("interpretable-2x", 482, 26.2, 3995),
                 ("explainable-4x", 192, 0.4, 4064),
                 ("zero-shot-1x", 231, 23.9, 3634),
                 ("non-differentiable-8x", 449, 16.5, 2239),
             ]),
        dict(n=3, slug="marker-frequency", title="Marker observations by channel",
             alt="Marker observation frequency by channel",
             caption="Figure 3. Marker observations by channel during the results window. A–B carries more markers than B–C; the snapshot channel is the record written into the global snapshot.",
             anchor="## Discussion", draw="bars",
             labels=["A–B", "B–C", "A snap", "B snap", "C snap"],
             values=[860, 790, 240, 240, 240],
             xlabel="channel", ylabel="markers observed", note="Results window."),
    ],
)

add_paper(
    paper_id="souken-tr-2022-024",
    report="TR-2022-024",
    date="2023-10",
    filename="souken-tr-2022-024.md",
    figures=[
        dict(n=1, slug="quota", title="Harmless quota manager",
             alt="Quota manager admit and reject paths",
             caption="Figure 1. Harmless quota manager. A request id reaches the manager, which admits into service discovery or rejects toward the clock source. The heartbeat interval is read from the manager.",
             anchor="## Evaluation", draw="diagram", diagram=diag_024),
        dict(n=2, slug="benchmarks", title="Benchmark configurations",
             alt="Throughput against p99 latency for the quota manager",
             caption=bench_caption(2, "Reported configurations of the harmless quota manager."),
             anchor="## Results", draw="bench",
             rows=[
                 ("zero-shot-8x", 388, 22.5, 788),
                 ("convolutional-8x", 83, 49.9, 845),
                 ("transformer-based-1x", 232, 33.6, 2708),
                 ("harmless-4x", 176, 24.3, 2591),
                 ("few-shot-2x", 229, 19.0, 1375),
                 ("transformer-based-4x", 377, 34.0, 3743),
             ]),
        dict(n=3, slug="admit-reject", title="Admit and reject over the quota window",
             alt="Admit and reject counts over time",
             caption="Figure 3. Admit and reject counts across the quota window. The two series move together when the heartbeat interval tightens; they are not the throughput column of the benchmark table.",
             anchor="## Discussion", draw="admit"),
    ],
)

add_paper(
    paper_id="souken-tr-2021-072",
    report="TR-2021-072",
    date="2020-02",
    filename="souken-tr-2021-072.md",
    figures=[
        dict(n=1, slug="spectral-norm", title="Differentiable spectral norm",
             alt="Spectral norm constraint on the weight update",
             caption="Figure 1. Differentiable spectral norm. The gradient enters the weight matrix, the spectral norm bounds the update, and the clipped update leaves. Singular values and the hard negative are read from that bound.",
             anchor="## Evaluation", draw="diagram", diagram=diag_072),
        dict(n=2, slug="benchmarks", title="Benchmark configurations",
             alt="Throughput against p99 latency for the spectral norm",
             caption=bench_caption(2, "Reported configurations of the differentiable spectral norm."),
             anchor="## Results", draw="bench",
             rows=[
                 ("zero-shot-4x", 308, 7.5, 1992),
                 ("bidirectional-8x", 368, 18.2, 1479),
                 ("cross-modal-8x", 189, 29.9, 1831),
             ]),
        dict(n=3, slug="singular-spectrum", title="Singular-value spectrum",
             alt="Singular value spectrum of the weight matrix",
             caption="Figure 3. Singular-value spectrum of the weight matrix after the spectral-norm bound. Values are normalized to the leading singular value.",
             anchor="## Discussion", draw="bars",
             labels=["σ1", "σ2", "σ3", "σ4", "σ5", "σ6", "σ7", "σ8"],
             values=[1.00, 0.62, 0.41, 0.28, 0.19, 0.12, 0.08, 0.05],
             xlabel="index", ylabel="singular value / σ1", note="Normalized spectrum."),
    ],
)

add_paper(
    paper_id="souken-tr-2021-010",
    report="TR-2021-010",
    date="2022-09",
    filename="souken-tr-2021-010.md",
    figures=[
        dict(n=1, slug="lww", title="Few-shot last writer wins",
             alt="Last-writer-wins register",
             caption="Figure 1. Few-shot last writer wins. Two writers present timestamps to the register. The later timestamp wins, and the register commits into the global snapshot.",
             anchor="## Evaluation", draw="diagram", diagram=diag_010),
        dict(n=2, slug="benchmarks", title="Benchmark configurations",
             alt="Throughput against p99 latency for last writer wins",
             caption=bench_caption(2, "Reported configurations of few-shot last writer wins."),
             anchor="## Results", draw="bench",
             rows=[
                 ("cross-modal-8x", 226, 39.6, 672),
                 ("causal-8x", 389, 36.2, 3397),
                 ("dense-8x", 102, 36.5, 2271),
                 ("modular-2x", 432, 19.1, 2927),
             ]),
        dict(n=3, slug="conflict-lag", title="Conflicts resolved, by timestamp lag",
             alt="Conflict resolutions binned by timestamp lag",
             caption="Figure 3. Conflicts resolved by the register, binned by timestamp lag. The later writer takes the register in every bin; the bars count resolutions.",
             anchor="## Discussion", draw="bars",
             labels=["0–1", "1–2", "2–4", "4–8", "8–16"],
             values=[90, 210, 340, 180, 60],
             xlabel="timestamp lag (ticks)", ylabel="conflicts resolved", note="Results window."),
    ],
)

add_paper(
    paper_id="souken-tr-2020-062",
    report="TR-2020-062",
    date="2021-03",
    filename="souken-tr-2020-062.md",
    figures=[
        dict(n=1, slug="lease", title="Steerable lease grant",
             alt="Lease grant, renew, and expire",
             caption="Figure 1. Steerable lease grant. A request is granted, renewed, or expired. Renewal can extend the grant. Cohort and timeout policy sit under the live lease; expiry reaches remote attestation.",
             anchor="## Evaluation", draw="diagram", diagram=diag_062),
        dict(n=2, slug="benchmarks", title="Benchmark configurations",
             alt="Throughput against p99 latency for lease grant",
             caption=bench_caption(2, "Reported configurations of the steerable lease grant."),
             anchor="## Results", draw="bench",
             rows=[
                 ("bidirectional-1x", 363, 42.8, 1039),
                 ("steerable-1x", 194, 21.8, 548),
                 ("calibrated-4x", 421, 9.6, 1854),
             ]),
        dict(n=3, slug="lease-life", title="Lease lifetime",
             alt="Histogram of lease lifetimes",
             caption="Figure 3. Lease lifetime on the steerable-1x configuration. Bins count completed leases. The 21.8 ms p99 in the benchmark table is not a lifetime bin.",
             anchor="## Discussion", draw="bars",
             labels=["0–2", "2–4", "4–8", "8–16", "16–32"],
             values=[40, 120, 260, 180, 55],
             xlabel="lifetime (s)", ylabel="leases", note="Steerable-1x."),
    ],
)

add_paper(
    paper_id="souken-tr-2020-002",
    report="TR-2020-002",
    date="2022-07",
    filename="souken-tr-2020-002.md",
    figures=[
        dict(n=1, slug="feed-forward", title="Factual feed-forward block",
             alt="Feed-forward block with residual skip",
             caption="Figure 1. Factual feed-forward block. Input passes layer norm into the block, then the residual add and the output. Activation is read from the block. The dashed arrow is the residual skip.",
             anchor="## Evaluation", draw="diagram", diagram=diag_ff),
        dict(n=2, slug="benchmarks", title="Benchmark configurations",
             alt="Throughput against p99 latency for the feed-forward block",
             caption=bench_caption(2, "Reported configurations of the factual feed-forward block."),
             anchor="## Results", draw="bench",
             rows=[
                 ("recurrent-4x", 30, 41.6, 1041),
                 ("semi-supervised-2x", 12, 21.2, 2527),
                 ("autoregressive-4x", 160, 10.9, 1510),
             ]),
        dict(n=3, slug="training-loss", title="Training loss of the feed-forward block",
             alt="Training loss curve",
             caption="Figure 3. Training loss of the feed-forward block. The trace falls across forty epochs and is not the throughput column of the benchmark table.",
             anchor="## Discussion", draw="loss"),
    ],
)


def render_figure(paper, fig) -> Plate:
    plate = Plate(paper["report"], paper["date"], fig["n"], fig["title"])
    plate.frame()
    kind = fig["draw"]
    if kind == "diagram":
        nodes, edges = fig["diagram"]()
        draw_diagram(plate, nodes, edges)
    elif kind == "realm":
        draw_realm_map(plate)
    elif kind == "bench":
        benchmark(plate, fig["rows"])
    elif kind == "adapt":
        xs, ys = adaptation_019()
        series_chart(
            plate,
            [{"name": "adaptation rate", "x": xs, "y": ys, "style": "both"}],
            "query-set size (thousands)",
            "adaptation rate",
            (0, 70),
            (0, 1),
            note="Deterministic adaptation rate.",
        )
    elif kind == "spectrum":
        freqs, mags = spectrum_018()
        stem_spectrum(
            plate, freqs, mags,
            "frequency (cycles per interval)",
            "normalized magnitude",
            "Clock-event residual. Fundamental scaled to 1.",
        )
    elif kind == "retention":
        xs, fit, ox, oy, floor = measured_decay()
        series_chart(
            plate,
            [
                {"name": "fit", "x": xs, "y": fit, "style": "line"},
                {"name": "measured", "x": ox, "y": oy, "style": "points"},
            ],
            "epoch",
            "observation retention",
            (0, 60),
            (0, 1),
            hlines=[(floor, "retention floor 0.190")],
            note="Fit r = 0.190 + 0.740 exp(−t/18). The record stays above the floor and does not attain zero.",
        )
    elif kind == "bars":
        bar_chart(plate, fig["labels"], fig["values"], fig["xlabel"], fig["ylabel"], fig.get("note"))
    elif kind == "hbars":
        hbar_chart(plate, fig["labels"], fig["values"], fig["xlabel"], fig["value_fmt"])
    elif kind == "confusion":
        confusion(plate)
    elif kind == "losses":
        epochs = list(range(0, 41))
        def decay(start, tau, floor):
            return [floor + (start - floor) * math.exp(-t / tau) for t in epochs]
        series_chart(
            plate,
            [
                {"name": "spectral norm", "x": epochs, "y": decay(1.40, 12, 0.22), "style": "line"},
                {"name": "variational gap", "x": epochs, "y": decay(1.15, 9, 0.18), "style": "line"},
                {"name": "aggregate signature", "x": epochs, "y": decay(0.95, 15, 0.27), "style": "line"},
            ],
            "epoch",
            "training loss",
            (0, 40),
            (0, 1.6),
        )
    elif kind == "metrics":
        xs = list(range(0, 25))
        rng = random.Random(67)
        gauge, counter, hist = [], [], []
        g = c = h = 0.55
        for _ in xs:
            g = min(0.92, max(0.2, g + rng.uniform(-0.04, 0.045)))
            c = min(0.9, max(0.15, c + rng.uniform(-0.05, 0.03)))
            h = min(0.88, max(0.2, h + rng.uniform(-0.03, 0.04)))
            gauge.append(g)
            counter.append(c)
            hist.append(h)
        series_chart(
            plate,
            [
                {"name": "gauge", "x": xs, "y": gauge, "style": "line"},
                {"name": "counter rate", "x": xs, "y": counter, "style": "line"},
                {"name": "histogram mean", "x": xs, "y": hist, "style": "line"},
            ],
            "evaluation step",
            "normalized level",
            (0, 24),
            (0, 1),
            note="Each series is scaled to the unit interval.",
        )
    elif kind == "calibration":
        pred = [i / 10 for i in range(1, 10)]
        obs = [0.07, 0.16, 0.28, 0.37, 0.51, 0.60, 0.71, 0.79, 0.90]
        series_chart(
            plate,
            [
                {"name": "observed", "x": pred, "y": obs, "style": "both"},
            ],
            "predicted probability",
            "observed frequency",
            (0, 1),
            (0, 1),
            note="Dashed line is perfect calibration.",
        )
        plate.line(78, 468, 860, 84, UMBER, 0.9, "5 4")
    elif kind == "admit":
        xs = list(range(0, 13))
        admit = [40, 55, 70, 88, 96, 90, 74, 60, 66, 80, 92, 84, 70]
        reject = [10, 14, 18, 22, 30, 36, 44, 40, 28, 20, 16, 22, 26]
        series_chart(
            plate,
            [
                {"name": "admit", "x": xs, "y": admit, "style": "both"},
                {"name": "reject", "x": xs, "y": reject, "style": "both"},
            ],
            "quota window (hour)",
            "decisions",
            (0, 12),
            (0, 120),
        )
    elif kind == "loss":
        xs = list(range(0, 41))
        ys = [1.85 * math.exp(-t / 11.0) + 0.21 for t in xs]
        series_chart(
            plate,
            [{"name": "training loss", "x": xs, "y": ys, "style": "line"}],
            "epoch",
            "training loss",
            (0, 40),
            (0, 2.1),
        )
    else:
        raise SystemExit(f"unknown draw kind {kind}")
    return plate


def markdown_block(paper, fig) -> str:
    rel = f"figures/{paper['paper_id']}/{fig['slug']}.svg"
    return f"![{fig['alt']}]({rel})\n\n*{fig['caption']}*\n"


def apply_markdown(paper) -> None:
    path = PAPERS / paper["filename"]
    text = path.read_text()
    for fig in paper["figures"]:
        token = f"figures/{paper['paper_id']}/{fig['slug']}.svg"
        if token in text:
            continue
        block = markdown_block(paper, fig)
        if "replace" in fig:
            old = fig["replace"]
            if old not in text:
                raise SystemExit(f"{paper['filename']}: missing image to replace: {old}")
            text = text.replace(old, block.rstrip("\n"), 1)
        else:
            heading = fig["anchor"]
            needle = "\n" + heading
            idx = text.find(needle)
            if idx < 0:
                raise SystemExit(f"{paper['filename']}: missing heading {heading}")
            text = text[:idx] + "\n" + block + text[idx:]
    path.write_text(text)


def main() -> None:
    written = []
    for paper in PAPERS_SPEC:
        dest = OUT / paper["paper_id"]
        dest.mkdir(parents=True, exist_ok=True)
        for fig in paper["figures"]:
            plate = render_figure(paper, fig)
            svg_path = dest / f"{fig['slug']}.svg"
            png_path = dest / f"{fig['slug']}.png"
            svg = plate.svg()
            svg_path.write_text(svg)
            cairosvg.svg2png(bytestring=svg.encode(), write_to=str(png_path), output_width=1840)
            written.append(png_path)
        apply_markdown(paper)
        print(f"{paper['paper_id']}: {len(paper['figures'])} figures")
    print(f"wrote {len(written)} pngs")


if __name__ == "__main__":
    main()
