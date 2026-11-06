"""Visual explanations of sharing, energy, transfer, attraction and lattice structure."""
import numpy as np
from manim import (
    AnimationGroup, Arrow, Axes, Circle, Create, DashedLine, Dot, DOWN, Ellipse,
    FadeIn, FadeOut, Indicate, LEFT, Line, RIGHT, SurroundingRectangle, Transform,
    UP, ValueTracker, VGroup, Write,
)

from scenes.style import (
    BLUE, GOLD, GREEN, MUTED, PINK, asset, card, crystal_lattice, electron,
    footer, header, particle, require_lines, reveal, say, text, water_diagram,
)

BEAT_COUNTS = {"hydrogen_atoms": 3, "electron_density": 3, "energy_curve": 3,
               "hydrogen_molecule": 2, "covalent_recap": 2, "salt_and_water": 2,
               "ionic_lattice": 3, "polar_water": 3, "bond_comparison": 2, "bond_recap": 2}


def hydrogen_atom(x):
    cloud = VGroup(*[Circle(radius=r, fill_color=BLUE, fill_opacity=0.035,
                            stroke_width=0) for r in (0.95, 0.8, 0.65, 0.5)])
    nucleus = particle("+", BLUE, 0.19)
    dot = electron(RIGHT * 0.5 + UP * 0.33, radius=0.09)
    name = text("H", 22, BLUE).move_to(DOWN * 1.15)
    return VGroup(cloud, nucleus, dot, name).shift(RIGHT * x)


def shared_cloud():
    return VGroup(*[Ellipse(width=w, height=h, fill_color=GOLD, fill_opacity=0.045,
                            stroke_width=0) for w, h in [(3.6, 1.6), (3.2, 1.35), (2.8, 1.1), (2.4, 0.85)]])


def ion_attraction():
    left = particle("Na⁺", BLUE).shift(LEFT * 1.2)
    right = particle("Cl⁻", PINK).shift(RIGHT * 1.2)
    arrows = VGroup(Arrow(LEFT * 0.72, LEFT * 0.15, buff=0, color=GOLD),
                    Arrow(RIGHT * 0.72, RIGHT * 0.15, buff=0, color=GOLD))
    return VGroup(left, right, arrows)


def water_density(water):
    clouds = VGroup()
    oxygen = water[1]
    for h in (water[2], water[3]):
        center = oxygen.get_center() * 0.64 + h.get_center() * 0.36
        delta = h.get_center() - oxygen.get_center()
        clouds.add(Ellipse(width=0.9, height=0.36, fill_color=GOLD, fill_opacity=0.12,
                           stroke_width=0).rotate(np.arctan2(delta[1], delta[0])).move_to(center))
    return clouds


def animate_bond_segment(scene, visual, lines, parameters=None):
    if visual not in BEAT_COUNTS:
        raise ValueError(f"Unsupported bonding visual: {visual}")
    require_lines(lines, BEAT_COUNTS[visual], visual)
    if visual == "hydrogen_atoms":
        head = header("Why do two hydrogen atoms bond?", "01 / Start with the ingredients")
        left, right = hydrogen_atom(-2.4), hydrogen_atom(2.4)
        note = footer("Gold dot = electron symbol · blue + = proton")
        warning = text("Probability clouds, not planetary orbits", 21, MUTED).move_to(DOWN * 2.25)
        say(scene, lines[0], lambda t: scene.play(FadeIn(head), FadeIn(left), FadeIn(right), run_time=t))
        say(scene, lines[1], lambda t: scene.play(Indicate(VGroup(left[2], right[2]), color=GOLD), FadeIn(note), run_time=t))
        say(scene, lines[2], lambda t: scene.play(FadeIn(warning), left[0].animate.scale(1.06), right[0].animate.scale(1.06), run_time=t))
        return VGroup(head, left, right, note, warning)
    if visual == "electron_density":
        head = header("From two clouds to shared density", "02 / Bring the atoms together")
        left, right = hydrogen_atom(-2.4), hydrogen_atom(2.4)
        cloud = shared_cloud()
        note = footer("Dots track the electron count; their paths are only schematic")
        shared = text("2 electrons · 2 nuclei · shared density", 25, GOLD).move_to(DOWN * 2.1)
        def approach(t):
            scene.play(FadeIn(head), FadeIn(left), FadeIn(right), FadeIn(note), run_time=t * 0.25)
            scene.play(left.animate.shift(RIGHT * 1.55), right.animate.shift(LEFT * 1.55), run_time=t * 0.75)
        say(scene, lines[0], approach)
        def overlap(t):
            scene.play(FadeOut(left[0]), FadeOut(right[0]), FadeIn(cloud),
                       left[2].animate.move_to(LEFT * 0.15), right[2].animate.move_to(RIGHT * 0.15),
                       FadeIn(shared), run_time=t)
        say(scene, lines[1], overlap)
        attraction = VGroup(*[Line(dot, nucleus, color=GOLD, stroke_width=1.2, stroke_opacity=0.5)
                              for dot in (LEFT * 0.15, RIGHT * 0.15)
                              for nucleus in (LEFT * 0.85, RIGHT * 0.85)])
        say(scene, lines[2], lambda t: scene.play(Create(attraction), Indicate(cloud, color=GOLD, scale_factor=1.03), run_time=t))
        return VGroup(head, left, right, cloud, note, shared, attraction)
    if visual == "energy_curve":
        head = header("There is a best distance", "03 / Follow the energy")
        axes = Axes(x_range=[0, 5.2, 1], y_range=[-1.6, 1.6, 1], x_length=6.1, y_length=3.1,
                    axis_config={"include_numbers": False, "include_tip": True, "stroke_width": 1.5}).shift(LEFT * 1.45 + DOWN * 0.15)
        def potential(r):
            return 1.25 * ((1 - np.exp(-(r - 1.7))) ** 2 - 1)
        curve = axes.plot(potential, x_range=[0.9, 5.15], color=GOLD, stroke_width=3)
        baseline = DashedLine(axes.c2p(0, 0), axes.c2p(5.15, 0), color=MUTED, stroke_width=1)
        ylabel = text("Potential\nenergy", 20, BLUE).move_to(LEFT * 5.65 + UP * 0.6)
        xlabel = text("Distance between nuclei →", 22, BLUE).move_to(LEFT * 1.45 + DOWN * 2.2)
        zero = text("Separated atoms: reference energy", 15, MUTED).next_to(baseline, UP, buff=0.1)
        r = ValueTracker(4.7)
        dot = Dot(axes.c2p(r.get_value(), potential(r.get_value())), color=PINK, radius=0.09)
        dot.add_updater(lambda mob: mob.move_to(axes.c2p(r.get_value(), potential(r.get_value()))))
        mini_left = VGroup(particle("+", BLUE, 0.19), electron(UP * 0.4))
        mini_right = mini_left.copy()
        mini_left.add_updater(lambda mob: mob.move_to([4 - 0.35 * r.get_value(), 0.55, 0]))
        mini_right.add_updater(lambda mob: mob.move_to([4 + 0.35 * r.get_value(), 0.55, 0]))
        distance_line = Line([2.4, -0.1, 0], [5.6, -0.1, 0], color=BLUE, stroke_width=2)
        distance_line.add_updater(lambda mob: mob.put_start_and_end_on([4 - 0.35 * r.get_value(), -0.1, 0], [4 + 0.35 * r.get_value(), -0.1, 0]))
        minimum = text("equilibrium", 20, GREEN).move_to(RIGHT * 4 + DOWN * 0.8)
        too_close = text("too close:\nrepulsion", 22, PINK).move_to(RIGHT * 4 + DOWN * 0.8)
        note = footer("Qualitative curve and schematic atoms · not to scale")
        def follow(t):
            scene.play(FadeIn(head), Create(axes), Create(curve), Create(baseline), FadeIn(ylabel), FadeIn(xlabel),
                       FadeIn(zero), FadeIn(dot), FadeIn(mini_left), FadeIn(mini_right), Create(distance_line), FadeIn(note), run_time=t * 0.4)
            scene.play(r.animate.set_value(2.5), run_time=t * 0.6)
        say(scene, lines[0], follow)
        say(scene, lines[1], lambda t: scene.play(r.animate.set_value(1.7), FadeIn(minimum), run_time=t))
        def repel(t):
            scene.play(FadeOut(minimum), FadeIn(too_close), r.animate.set_value(0.95), run_time=t * 0.6)
            scene.play(r.animate.set_value(1.7), FadeOut(too_close), FadeIn(minimum), run_time=t * 0.4)
        say(scene, lines[2], repel)
        for obj in (dot, mini_left, mini_right, distance_line):
            obj.clear_updaters()
        return VGroup(head, axes, curve, baseline, ylabel, xlabel, zero, dot, mini_left, mini_right, distance_line, minimum, note)
    if visual == "hydrogen_molecule":
        head = header("A bond stores an energy difference", "04 / Meet H₂")
        left, right = particle("+", BLUE, 0.25).shift(LEFT * 0.85), particle("+", BLUE, 0.25).shift(RIGHT * 0.85)
        pair = VGroup(electron(LEFT * 0.15), electron(RIGHT * 0.15))
        cloud = shared_cloud()
        molecule = VGroup(cloud, left, right, pair)
        name = text("H₂ · one shared pair", 28, GOLD).move_to(UP * 1.5)
        energy_out = VGroup(Arrow(RIGHT * 2, RIGHT * 4.2, color=GREEN, buff=0), text("energy released", 22, GREEN).move_to(RIGHT * 3.1 + UP * 0.5))
        energy_in = VGroup(Arrow(RIGHT * 4.2, RIGHT * 2, color=PINK, buff=0), text("energy required", 22, PINK).move_to(RIGHT * 3.1 + UP * 0.5))
        note = footer("Electron symbols and energy arrows are schematic")
        say(scene, lines[0], lambda t: scene.play(FadeIn(head), FadeIn(molecule, scale=0.75), FadeIn(name), FadeIn(note), run_time=t))
        def energy(t):
            scene.play(Create(energy_out), run_time=t * 0.45)
            scene.play(FadeOut(energy_out), Create(energy_in), Indicate(pair, color=GOLD), run_time=t * 0.55)
        say(scene, lines[1], energy)
        return VGroup(head, molecule, name, energy_in, note)
    if visual == "covalent_recap":
        head = header("The two-part answer", "05 / Keep the idea")
        left = card("SHARED ELECTRONS", "density around both nuclei", GOLD, 5).move_to(LEFT * 3)
        right = card("LOWER ENERGY", "a favorable bonded state", GREEN, 5).move_to(RIGHT * 3)
        connector = Line(LEFT * 0.5, RIGHT * 0.5, color=BLUE)
        conclusion = text("COVALENT BOND", 31, BLUE).move_to(DOWN * 1.9)
        say(scene, lines[0], lambda t: scene.play(FadeIn(head), FadeIn(left, shift=RIGHT * 0.2), FadeIn(right, shift=LEFT * 0.2), run_time=t))
        say(scene, lines[1], lambda t: scene.play(Create(connector), Write(conclusion), run_time=t))
        return VGroup(head, left, right, connector, conclusion)
    if visual == "salt_and_water":
        head = header("Two materials. Two bonding stories.", "01 / Salt and water")
        salt = VGroup(asset("final_sel.svg", "salt", 1.2), text("NaCl", 31, BLUE)).arrange(DOWN, buff=0.2).move_to(LEFT * 3)
        water = water_diagram().scale(0.9).move_to(RIGHT * 3)
        ionic = text("IONIC", 25, BLUE).move_to(LEFT * 3 + DOWN * 1.8)
        covalent = text("COVALENT", 25, PINK).move_to(RIGHT * 3 + DOWN * 1.8)
        note = footer("Gold dots = valence electron symbols; only bonds within water are compared")
        say(scene, lines[0], lambda t: scene.play(FadeIn(head), FadeIn(salt, shift=RIGHT * 0.2), FadeIn(water, shift=LEFT * 0.2), FadeIn(note), run_time=t))
        say(scene, lines[1], lambda t: scene.play(FadeIn(ionic), FadeIn(covalent), Indicate(water[4], color=GOLD), run_time=t))
        return VGroup(head, salt, water, ionic, covalent, note)
    if visual == "ionic_lattice":
        head = header("Transfer → ions → a crystal", "02 / Ionic bonding")
        sodium = particle("Na", BLUE).shift(LEFT * 2.3)
        chlorine = particle("Cl", PINK).shift(RIGHT * 2.3)
        moving = electron(LEFT * 1.6, radius=0.09)
        transfer = Arrow(LEFT * 1.45 + UP * 0.4, RIGHT * 1.55 + UP * 0.4, color=GOLD, buff=0)
        na_ion = particle("Na⁺", BLUE).move_to(sodium)
        cl_ion = particle("Cl⁻", PINK).move_to(chlorine)
        note_transfer = footer("Simplified transfer model · only the transferred electron is shown")
        def transfer_electron(t):
            scene.play(FadeIn(head), FadeIn(sodium), FadeIn(chlorine), FadeIn(moving), FadeIn(note_transfer), run_time=t * 0.25)
            scene.play(Create(transfer), moving.animate.move_to(RIGHT * 1.65), run_time=t * 0.5)
            scene.play(Transform(sodium, na_ion), Transform(chlorine, cl_ion), run_time=t * 0.25)
        say(scene, lines[0], transfer_electron)
        force = VGroup(Arrow(LEFT * 1.65 + DOWN * 0.7, LEFT * 0.5 + DOWN * 0.7, color=GOLD, buff=0),
                       Arrow(RIGHT * 1.65 + DOWN * 0.7, RIGHT * 0.5 + DOWN * 0.7, color=GOLD, buff=0))
        force_word = text("OPPOSITE CHARGES ATTRACT", 25, GOLD).move_to(DOWN * 1.75)
        def attract(t):
            scene.play(FadeOut(transfer), Create(force), FadeIn(force_word), run_time=t * 0.3)
            scene.play(sodium.animate.shift(RIGHT * 1.25), chlorine.animate.shift(LEFT * 1.25), moving.animate.shift(LEFT * 1.25), run_time=t * 0.7)
        say(scene, lines[1], attract)
        lattice = crystal_lattice().scale(1.12).move_to(LEFT * 1.9 + DOWN * 0.1)
        lattice_name = VGroup(text("SOLID NaCl", 29, GOLD), text("Repeating ion lattice", 23),
                             text("Na⁺  sodium ion", 20, BLUE), text("Cl⁻  chloride ion", 20, PINK)).arrange(DOWN, buff=0.2).move_to(RIGHT * 3.25)
        slice_note = footer("A 2D slice of a 3D crystal · not separate NaCl molecules")
        frame = SurroundingRectangle(lattice, buff=0.2, color=BLUE, stroke_width=1, stroke_opacity=0.35)
        def extend(t):
            scene.play(FadeOut(VGroup(sodium, chlorine, moving, force, force_word, note_transfer)), run_time=t * 0.15)
            scene.play(AnimationGroup(*[FadeIn(ion, scale=0.6) for ion in lattice], lag_ratio=0.12),
                       FadeIn(lattice_name), FadeIn(slice_note), Create(frame), run_time=t * 0.85)
        say(scene, lines[2], extend)
        return VGroup(head, lattice, frame, lattice_name, slice_note)
    if visual == "polar_water":
        head = header("Shared does not always mean equal", "03 / Water's polar covalent bonds")
        water = water_diagram().scale(1.35).move_to(LEFT * 1.7)
        density = water_density(water)
        pair_note = VGroup(text("2 O–H bonds", 29, GOLD), text("1 shared pair per bond", 22),
                           text("Gold dots: 8 valence electrons", 18, MUTED)).arrange(DOWN, buff=0.2).move_to(RIGHT * 3.2 + UP * 0.2)
        note = footer("Two shared pairs + two lone pairs · electron dots are symbols")
        say(scene, lines[0], lambda t: scene.play(FadeIn(head), FadeIn(water), FadeIn(pair_note), FadeIn(note), run_time=t))
        unequal = text("More electron density\nnear oxygen", 24, GOLD).move_to(RIGHT * 3.2 + UP * 0.2)
        def pull(t):
            scene.play(FadeOut(pair_note), FadeIn(unequal), FadeIn(density), run_time=t * 0.5)
            scene.play(Indicate(water[4], color=GOLD, scale_factor=1.1), run_time=t * 0.5)
        say(scene, lines[1], pull)
        charges = VGroup(text("δ−", 24, PINK).next_to(water[1], LEFT, buff=0.14),
                         text("δ+", 22, BLUE).next_to(water[2], LEFT, buff=0.12),
                         text("δ+", 22, BLUE).next_to(water[3], RIGHT, buff=0.12))
        partial = card("δ means PARTIAL", "unequal sharing, not full ion charges", PINK, 5).move_to(RIGHT * 3.2)
        say(scene, lines[2], lambda t: scene.play(FadeIn(charges), FadeOut(unequal), FadeIn(partial), run_time=t))
        return VGroup(head, water, density, note, charges, partial)
    if visual == "bond_comparison":
        head = header("Attraction of ions or shared electrons?", "04 / Compare the mechanism")
        left = ion_attraction().move_to(LEFT * 3)
        right = water_diagram().scale(0.85).move_to(RIGHT * 3)
        separator = Line(UP * 1.6, DOWN * 1.6, color=MUTED, stroke_opacity=0.3)
        ionic = text("IONIC: IONS ATTRACT", 23, BLUE).move_to(LEFT * 3 + DOWN * 1.9)
        covalent = text("COVALENT: ELECTRONS SHARED", 21, PINK).move_to(RIGHT * 3 + DOWN * 1.9)
        def ions(t):
            scene.play(FadeIn(head), Create(separator), FadeIn(left[0]), FadeIn(left[1]), FadeIn(ionic), run_time=t * 0.3)
            scene.play(Create(left[2]), left[0].animate.shift(RIGHT * 0.15), left[1].animate.shift(LEFT * 0.15), run_time=t * 0.7)
        say(scene, lines[0], ions)
        say(scene, lines[1], lambda t: scene.play(FadeIn(right), FadeIn(covalent), run_time=t))
        return VGroup(head, left, right, separator, ionic, covalent)
    head = header("Remember the structure", "05 / Take the idea with you")
    lattice = crystal_lattice().scale(0.8).move_to(LEFT * 3 + UP * 0.15)
    water = water_diagram().scale(0.8).move_to(RIGHT * 3 + UP * 0.15)
    captions = VGroup(text("NaCl: EXTENDED ION LATTICE", 21, BLUE).move_to(LEFT * 3 + DOWN * 1.7),
                      text("H₂O: SHARED ELECTRONS", 21, PINK).move_to(RIGHT * 3 + DOWN * 1.7))
    note = footer("Useful models · real bonds can have mixed ionic and covalent character", GOLD)
    say(scene, lines[0], lambda t: scene.play(FadeIn(head), AnimationGroup(*[FadeIn(ion) for ion in lattice], lag_ratio=0.08),
                                           FadeIn(water), FadeIn(captions), run_time=t))
    say(scene, lines[1], lambda t: scene.play(FadeIn(note), Indicate(captions, color=GOLD, scale_factor=1.02), run_time=t))
    return VGroup(head, lattice, water, captions, note)
