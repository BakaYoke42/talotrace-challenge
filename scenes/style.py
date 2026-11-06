"""Shared visual language and sentence-level direction for the chemistry lessons."""
from pathlib import Path

import numpy as np
from manim import (
    AnimationGroup, Circle, Dot, DOWN, FadeIn, LEFT, Line, ORIGIN,
    RIGHT, RoundedRectangle, SVGMobject, Text, UP, VGroup, WHITE,
)

ROOT = Path(__file__).resolve().parent.parent
BG = "#101B2B"
PANEL = "#18283D"
BLUE = "#78D8F0"
PINK = "#FF8C9E"
GOLD = "#FFD379"
GREEN = "#8ADCB2"
MUTED = "#AFBED0"


def text(value, size=27, color=WHITE):
    return Text(value, font="Segoe UI", font_size=size, color=color)


def header(title, section):
    eyebrow = text(section.upper(), 16, GOLD).to_edge(LEFT, buff=0.75).set_y(3.35)
    heading = text(title, 33, WHITE).move_to(UP * 2.8)
    if heading.width > 12:
        heading.scale_to_fit_width(12)
    rule = Line(LEFT * 6 + UP * 2.27, RIGHT * 6 + UP * 2.27, color=BLUE, stroke_width=1.2, stroke_opacity=0.4)
    return VGroup(eyebrow, heading, rule)


def footer(value, color=MUTED):
    result = text(value, 18, color).move_to(DOWN * 3.25)
    if result.width > 12.1:
        result.scale_to_fit_width(12.1)
    return result


def card(title, detail, color=BLUE, width=4.7):
    border = RoundedRectangle(width=width, height=1.55, corner_radius=0.16,
                              stroke_color=color, stroke_width=1.5,
                              fill_color=PANEL, fill_opacity=1)
    words = VGroup(text(title, 29, color), text(detail, 21)).arrange(DOWN, buff=0.2)
    if words.width > width - 0.4:
        words.scale_to_fit_width(width - 0.4)
    return VGroup(border, words)


def particle(symbol, color=BLUE, radius=0.42):
    disk = Circle(radius=radius, color=color, fill_color=PANEL, fill_opacity=1, stroke_width=2.5)
    symbol_text = text(symbol, min(25, radius * 54), WHITE)
    if symbol_text.width > radius * 1.5:
        symbol_text.scale_to_fit_width(radius * 1.5)
    return VGroup(disk, symbol_text)


def electron(point=ORIGIN, radius=0.075):
    return VGroup(Circle(radius=radius * 2.1, fill_color=GOLD, fill_opacity=0.09,
                         stroke_width=0), Dot(radius=radius, color=GOLD)).move_to(point)


def asset(name, fallback, height=0.7):
    path = ROOT / "images_pour_videos" / name
    if path.is_file():
        return SVGMobject(str(path), height=height)
    return VGroup(Circle(radius=height / 2, color=GOLD), text(fallback, 14))


def say(scene, line, action):
    """Each action gets the actual duration of this sentence's Kokoro recording."""
    with scene.voiceover(text=line) as tracker:
        action(max(0.1, tracker.duration * 0.93))


def reveal(scene, objects, duration):
    scene.play(AnimationGroup(*[FadeIn(obj, shift=UP * 0.12) for obj in objects],
                              lag_ratio=0.15), run_time=duration)


def require_lines(lines, count, visual):
    if len(lines) != count:
        raise ValueError(f"{visual} expects {count} narrated sentences, got {len(lines)}")


def water_diagram():
    """Lewis-style teaching model: 4 bonding electrons and 4 lone-pair electrons."""
    oxygen = particle("O", PINK, 0.48).move_to(UP * 0.38)
    left = particle("H", BLUE, 0.32).move_to(LEFT * 1.4 + DOWN * 0.68)
    right = particle("H", BLUE, 0.32).move_to(RIGHT * 1.4 + DOWN * 0.68)
    bonds = VGroup(Line(oxygen.get_center(), left.get_center(), color=GOLD, stroke_width=2),
                   Line(oxygen.get_center(), right.get_center(), color=GOLD, stroke_width=2))
    pairs = VGroup()
    for h in (left, right):
        center = 0.56 * oxygen.get_center() + 0.44 * h.get_center()
        direction = h.get_center() - oxygen.get_center()
        perpendicular = np.array([-direction[1], direction[0], 0])
        perpendicular /= np.linalg.norm(perpendicular)
        pairs.add(electron(center + perpendicular * 0.1), electron(center - perpendicular * 0.1))
    lone = VGroup(*[electron([x, y, 0], radius=0.065)
                    for x, y in [(-0.25, 1.09), (-0.08, 1.09), (0.25, 1.09), (0.42, 1.09)]])
    return VGroup(bonds, oxygen, left, right, pairs, lone)


def crystal_lattice():
    return VGroup(*[particle("Na⁺" if (row + col) % 2 == 0 else "Cl⁻",
                             BLUE if (row + col) % 2 == 0 else PINK, 0.3)
                    .move_to([col * 0.8 - 1.2, 0.8 - row * 0.8, 0])
                    for row in range(3) for col in range(4)])
