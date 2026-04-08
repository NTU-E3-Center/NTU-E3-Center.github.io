# NTU E3 Center Official Website

Live site: [e3center.caece.net](https://e3center.caece.net)

Project started: Fall 2023

**March 2026 – Present:**
Front-End Development: Jian Hern Yeoh
Maintenance: Jun-Wei Ding (Gary)

**March 2025 – Feb 2026:**
Maintenance: Jun-Wei Ding (Gary)

**Fall 2023 – Fall 2025:**
Design / Development / Maintenance: [Yuan-Hsi Chien (Thomas)](https://github.com/dobahsi)

For bug reports and suggestions, contact Jian Hern or Gary.

---

## How It Works

This site uses a custom Python static site generator. Source files live in `contents/` and `templates/`; the compiled output goes to `docs/`, which GitHub Pages serves.

Pushing to the `source` branch automatically triggers a GitHub Actions workflow that runs `build.py` and deploys the result.

---

## Local Development

### Prerequisites

- Python 3.x
- pip

### Setup (first time)

```bash
python -m venv website
source website/bin/activate        # macOS/Linux
# website\Scripts\activate         # Windows
pip install markdown Pillow jinja2 openpyxl
```

### Build and preview

```bash
# Activate the virtual environment (if not already active)
source website/bin/activate

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
