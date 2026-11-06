"""Sentence-synchronized pH lesson: ions, a true unit scale, and multiplicative change."""
from manim import (
    AnimationGroup, Arrow, Circle, Create, DOWN, FadeIn, FadeOut, Indicate,
    LEFT, Line, Rectangle, RIGHT, Transform, TransformFromCopy, UP, VGroup, Write,
)

from scenes.style import (
    BLUE, GOLD, GREEN, MUTED, PANEL, PINK, asset, card, footer, header,
    particle, require_lines, reveal, say, text,
)

BEAT_COUNTS = {"hydronium": 3, "ph_scale": 3, "logarithmic": 3, "activity_comparison": 3, "ph_recap": 2}


def ph_scale():
    colors = ["#EE6E7C", "#F07A6D", "#EF906B", "#EAA663", "#E8BE70", "#D9CF86", "#AFD99E",
              "#8ADCB2", "#78D8C5", "#74D4DB", "#78BFE4", "#829FE2", "#9A8ADE", "#B186DB", "#C38BD9"]
    blocks = VGroup(*[Rectangle(width=0.66, height=0.52, stroke_width=0,
                                fill_color=color, fill_opacity=1) for color in colors]).arrange(RIGHT, buff=0)
    blocks.move_to(UP * 0.3)
    values = VGroup(*[text(str(i), 17).next_to(block, DOWN, buff=0.16) for i, block in enumerate(blocks)])
    names = VGroup(text("ACIDIC", 23, PINK).move_to(blocks[3].get_center() + UP * 0.95),
                   text("NEUTRAL", 21, GREEN).move_to(blocks[7].get_center() + UP * 0.95),
                   text("BASIC", 23, BLUE).move_to(blocks[11].get_center() + UP * 0.95))
    return VGroup(blocks, values, names)


def comparison():
    one = asset("final_lemon.svg", "lemon", height=0.62)
    ten = VGroup(*[asset("final_lemon.svg", "lemon", height=0.46) for _ in range(10)]).arrange_in_grid(rows=2, cols=5, buff=0.16)
    right = VGroup(text("pH 4", 33, BLUE), one, text("1 × relative activity", 22)).arrange(DOWN, buff=0.32).move_to(LEFT * 3)
    left = VGroup(text("pH 3", 33, PINK), ten, text("10 × relative activity", 22)).arrange(DOWN, buff=0.32).move_to(RIGHT * 3)
    pair = VGroup(left, right)
    notice = VGroup(text("LEMONS = VISUAL METAPHOR ONLY", 21, GOLD),
                    text("Number of lemons does not measure pH", 19, MUTED)).arrange(DOWN, buff=0.13).move_to(DOWN * 2.6)
    return VGroup(pair, notice)


def animate_ph_segment(scene, visual, lines, parameters=None):
    if visual not in BEAT_COUNTS:
        raise ValueError(f"Unsupported pH visual: {visual}")
    require_lines(lines, BEAT_COUNTS[visual], visual)
    if visual == "hydronium":
        head = header("What does pH actually tell us?", "01 / Look inside the water")
        question = card("ACIDIC OR BASIC?", "One number. A molecular explanation.", width=7)
        question.move_to(UP * 0.1)
        waters = VGroup(*[Circle(radius=0.13, fill_color=BLUE, fill_opacity=0.22, stroke_width=0).move_to([x, y, 0])
                          for x, y in [(-4.2, 0.8), (-3.5, -1.3), (-2.7, 0.1), (2.8, 0.6), (3.7, -0.9), (4.5, 0.25)]])
        ion = particle("H₃O⁺", GOLD, 0.8).shift(UP * 0.4)
        name = text("HYDRONIUM", 23, GOLD).next_to(ion, DOWN, buff=0.25)
        activity = card("pH → hydrogen ion activity", "Dilute solution: related to hydronium concentration", BLUE, width=10.7).move_to(DOWN * 1.85)
        say(scene, lines[0], lambda t: scene.play(FadeIn(head), FadeIn(question, shift=UP * 0.15), run_time=t))
        def dissolve(t):
            scene.play(FadeOut(question), FadeIn(ion, scale=0.5), FadeIn(name),
                       AnimationGroup(*[FadeIn(w) for w in waters], lag_ratio=0.12), run_time=t * 0.7)
            scene.play(waters.animate.shift(RIGHT * 0.15), run_time=t * 0.3)
        say(scene, lines[1], dissolve)
        say(scene, lines[2], lambda t: scene.play(FadeIn(activity, shift=UP * 0.15), run_time=t))
        return VGroup(head, waters, ion, name, activity)
    if visual == "ph_scale":
        head = header("Start at neutral, then choose a direction", "02 / Read the scale")
        scale = ph_scale()
        blocks, values, names = scale
        cursor = Arrow(DOWN * 0.48, UP * 0.02, color=GOLD, buff=0).move_to(blocks[7].get_center() + DOWN * 1.13)
        neutral = text("Neutral water ≈ pH 7 at 25°C", 24, GREEN).move_to(DOWN * 1.85)
        note = footer("0–14 is a common classroom range, not a physical limit")
        def establish(t):
            scene.play(FadeIn(head), AnimationGroup(*[FadeIn(block, shift=UP * 0.12) for block in blocks], lag_ratio=0.06),
                       FadeIn(values), FadeIn(names), run_time=t * 0.65)
            scene.play(FadeIn(cursor), FadeIn(neutral), Indicate(blocks[7], color=GREEN), run_time=t * 0.35)
        say(scene, lines[0], establish)
        def directions(t):
            scene.play(cursor.animate.move_to(blocks[2].get_center() + DOWN * 1.13), Indicate(names[0], color=PINK), run_time=t * 0.5)
            scene.play(cursor.animate.move_to(blocks[12].get_center() + DOWN * 1.13), Indicate(names[2], color=BLUE), run_time=t * 0.5)
        say(scene, lines[1], directions)
        say(scene, lines[2], lambda t: scene.play(FadeIn(note), Indicate(VGroup(blocks[0], blocks[-1]), color=GOLD), run_time=t))
        return VGroup(head, scale, cursor, neutral, note)
    if visual == "logarithmic":
        head = header("Equal steps. Multiplying activity.", "03 / The logarithmic surprise")
        formula = text("pH = −log₁₀ a(H⁺)", 36, GOLD).move_to(UP * 1.3)
        cards = VGroup(card("pH 4", "relative activity 1", BLUE, 3), card("pH 3", "relative activity 10", GREEN, 3),
                       card("pH 2", "relative activity 100", PINK, 3)).arrange(RIGHT, buff=0.75).move_to(DOWN * 0.3)
        arrows = VGroup(Arrow(cards[0].get_right(), cards[1].get_left(), buff=0.08, color=GOLD),
                        Arrow(cards[1].get_right(), cards[2].get_left(), buff=0.08, color=GOLD))
        factors = VGroup(*[text("×10", 21, GOLD).next_to(arrow, DOWN, buff=0.2) for arrow in arrows])
        note = footer("a(H⁺) means hydrogen ion activity")
        say(scene, lines[0], lambda t: scene.play(FadeIn(head), Write(formula), FadeIn(cards[0]), FadeIn(note), run_time=t))
        say(scene, lines[1], lambda t: scene.play(Create(arrows[0]), FadeIn(cards[1], shift=LEFT * 0.15), FadeIn(factors[0]), run_time=t))
        say(scene, lines[2], lambda t: scene.play(Create(arrows[1]), FadeIn(cards[2], shift=LEFT * 0.15), FadeIn(factors[1]), run_time=t))
        return VGroup(head, formula, cards, arrows, factors, note)
    if visual == "activity_comparison":
        head = header("Picture the factor of ten", "04 / A visual metaphor")
        pair, notice = comparison()
        ten_side, one_side = pair
        arrow = Arrow(LEFT * 0.85, RIGHT * 0.85, color=GOLD, buff=0)
        multiplier = text("×10", 28, GOLD).next_to(arrow, UP, buff=0.15)
        say(scene, lines[0], lambda t: scene.play(FadeIn(head), FadeIn(notice), FadeIn(one_side), run_time=t))
        def multiply(t):
            scene.play(Create(arrow), FadeIn(multiplier), FadeIn(ten_side[0]), FadeIn(ten_side[2]), run_time=t * 0.35)
            scene.play(AnimationGroup(*[TransformFromCopy(one_side[1], icon) for icon in ten_side[1]], lag_ratio=0.12), run_time=t * 0.65)
        say(scene, lines[1], multiply)
        say(scene, lines[2], lambda t: scene.play(Indicate(notice, color=GOLD, scale_factor=1.02), run_time=t))
        return VGroup(head, pair, notice, arrow, multiplier)
    head = header("Two things to take away", "05 / Keep the idea")
    direction = card("LOWER pH", "higher hydrogen ion activity", BLUE, 5.1).move_to(LEFT * 3 + UP * 0.1)
    jump = card("ONE pH UNIT", "a factor of ten", GOLD, 5.1).move_to(RIGHT * 3 + UP * 0.1)
    say(scene, lines[0], lambda t: scene.play(FadeIn(head), FadeIn(direction, shift=RIGHT * 0.2), run_time=t))
    say(scene, lines[1], lambda t: scene.play(FadeIn(jump, shift=LEFT * 0.2), Indicate(jump[0], color=GOLD), run_time=t))
    return VGroup(head, direction, jump)
