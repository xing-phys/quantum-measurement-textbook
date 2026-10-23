# Quantum Measurement, Information Dynamics, and Emergent Criticality

A self-contained, AI-assisted scientific textbook built with Quarto. Research cutoff: 23 October 2026.

The source develops prerequisites, random circuits, measurement-induced transitions, replica statistical mechanics, CFT, mixed-state order and SW-SSB, charge and non-Abelian learnability, monitored hydrodynamics, quantum error correction, and reproducible numerical examples. The source distinguishes exact results, controlled limits, numerical evidence, and conjectures.

## Read and build

Published book: https://xing-phys.github.io/quantum-measurement-textbook/

Install Quarto 1.8.27 or later and a TeX distribution with XeLaTeX. Run:

```sh
quarto render
```

Both the multi-page HTML book and combined `quantum-measurement.pdf` are written under `outputs/site/`. Run `quarto preview --no-browser` for local reading; Quarto prints its local URL. The GitHub Actions workflow builds and deploys both formats automatically on pushes to `main`.

## Layout

- `index.qmd`, numbered chapter sources, `references.qmd`: one source for HTML and PDF.
- `assets/refs-*.bib`: verified primary literature; APS reference formatting, alphabetized with all entries included to maintain consistent numeric labels across chapters.
- `assets/macros.sty` and `assets/mathjax-config.html`: equivalent physics macros in the two formats.
- `assets/mathjax/`: vendored MathJax 3.2.2 runtime and fonts for local equation rendering; upstream Apache 2.0 license retained.
- `figs/`: original scientific illustrations, with PNG and vector PDF siblings.
- `numerics/`: Julia exact-state simulation and Python plotting source.
- `assets/data/`: numerical CSV data used in the book.
- `scripts/check_book.py`: citation, link, image, and fragment validation.

## Reproduce the numerical examples

Julia 1.12.6, standard libraries only:

```sh
julia numerics/monitored_circuit.jl --validate
julia numerics/monitored_circuit.jl
```

Plotting requires NumPy and Matplotlib:

```sh
MPLCONFIGDIR=work/matplotlib python3 numerics/make_figures.py
```

The model is an open chain, two independent Haar-gate layers per time step, then independent on-site projective readouts with probability `p`. Entropies are sampled after readout. The included run uses L=6,8,10, 64 trajectories per parameter, 60 steps, and explicit seeds. These data illustrate finite-size crossover and do not estimate a transition or exponent. Future versions of Julia may use different RNG implementations; use statistical validation rather than requiring bitwise identical output.

## Attribution and licensing

All figures are original; no published research figures are reproduced. Text and original figures: CC BY 4.0 (see LICENSE). Code: MIT (see numerics/LICENSE). Third-party assets retain their licenses. Author metadata follows the owner's Quarto template; the prose is an AI-assisted synthesis and has not undergone independent peer review.
