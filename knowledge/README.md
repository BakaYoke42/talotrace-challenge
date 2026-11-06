# Scientific storyboard sources

The JSON files contain the narration and visual sequence. Manim diagrams are selected by
the explicit visual identifiers. Each job saves a validated copy of its scenario alongside
its render. The current diagrams use fixed, reviewed examples; parameter values are recorded
for future extensions and are not yet used to configure every diagram.

The provided lemon, salt and water SVG illustrations in `images_pour_videos/` are OpenMoji
artwork: [OpenMoji](https://openmoji.org/), licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
Simple Manim shapes and labels are used as fallbacks if these assets are absent.

Original narration was written with reference to:

- OpenStax, *Chemistry 2e*, [pH and pOH](https://openstax.org/books/chemistry-2e/pages/14-2-ph-and-poh), [covalent bonding](https://openstax.org/books/chemistry-2e/pages/7-2-covalent-bonding), and [ionic bonding](https://openstax.org/books/chemistry-2e/pages/7-1-ionic-bonding).
- IUPAC Gold Book, [pH](https://goldbook.iupac.org/terms/view/P04524), for the hydrogen-ion activity definition. The main page returned HTTP 403 during verification; its indexed definition was available from search.

Adding a concept requires a reviewed JSON file, an explicit entry in `app/scenarios.py`,
and corresponding visual code. The validator checks structure, question, concept, scene
type, ordered visual identifiers and unique segment IDs; it does not prove scientific
accuracy or validate the semantics of arbitrary parameter values.
