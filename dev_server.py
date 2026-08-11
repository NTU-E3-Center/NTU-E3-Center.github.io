"""Watch-rebuild-reload dev loop: `make dev`, then edit and save.

Watches source trees, reruns build.py on change (incremental thanks to the
WebP encode cache), and serves docs/ with livereload's injected refresh
script. Build errors print to this terminal — fix and save to trigger a
rebuild. (A failed build can leave docs/ partially rendered until the next
good build.)"""
import subprocess
import sys

from livereload import Server

WATCHED = ["contents/", "templates/", "static/", "lib/", "build.py", "config.py"]


def rebuild():
    subprocess.run([sys.executable, "build.py"], check=False)


if __name__ == "__main__":
    rebuild()
    server = Server()
    for path in WATCHED:
        server.watch(path, rebuild, delay=0.5)
    server.serve(root="docs", host="0.0.0.0", port=8000)
