# NTU E3 Center Official Website

Live site: [e3center.caece.net](https://e3center.caece.net)

Project started: Fall 2023

**March 2026 – Present:**
Front-End Development and Maintenance: Jian Hern Yeoh

**March 2025 – Feb 2026:**
Maintenance: Jun-Wei Ding (Gary)

**Fall 2023 – Fall 2025:**
Design / Development / Maintenance: [Yuan-Hsi Chien (Thomas)](https://github.com/dobahsi)

For bug reports and suggestions, contact Jian Hern or Gary.

---

## How It Works

This site uses a custom Python static site generator. Source files live in `contents/` and `templates/`; `build.py` compiles them into `docs/` (which is gitignored — the build output never lives on the `source` branch).

Pushing to the `source` branch triggers a GitHub Actions workflow (`.github/workflows/deploy.yml`) that runs `build.py` and pushes the generated `docs/` to the `gh-pages` branch via `peaceiris/actions-gh-pages`. GitHub Pages serves the site from `gh-pages`.

---

## Local Development

### Prerequisites

- Conda (Miniconda or Anaconda) with Python 3.9

### Setup (first time)

```bash
conda create -n E3website python=3.9
conda activate E3website
pip install markdown Pillow jinja2 openpyxl
```

### Build and preview

```bash
conda activate E3website

# Build the site
python build.py

# Serve locally
cd docs && python -m http.server 8000
# Open http://localhost:8000
```

> **Note:** `docs/` is overwritten on every build. Never edit files there directly.

---

## Editing Content

See [CONTRIBUTING.md](CONTRIBUTING.md) for step-by-step guides on adding members, publications, news, and group photos.

See [STRUCTURE.md](STRUCTURE.md) for a full breakdown of the directory layout and build process.

---

## Design Rules

[DESIGN_RULES.md](DESIGN_RULES.md) is the canonical reference for typography, color, spacing, and responsive scaling. Consult it before changing CSS or adding any new UI — it defines the type scale, color tokens, breakpoints (desktop / tablet / mobile), and per-component rules (publications, members, news, contact, etc.), plus a list of known drifts to avoid reintroducing.
