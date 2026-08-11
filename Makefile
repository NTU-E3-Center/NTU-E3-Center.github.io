# NTU E3 Center — common tasks.
# Assumes the `E3website` conda env is active (see README).
.PHONY: build serve dev clean clean-cache audit audit-site tokens package-member help

help:
	@echo "make build            - compile contents/ -> docs/"
	@echo "make serve            - build, then serve docs/ at http://localhost:8000"
	@echo "make dev              - watch contents/templates/static, rebuild + live-reload at :8000"
	@echo "make clean            - remove the generated docs/ tree"
	@echo "make clean-cache      - drop the WebP encode cache (forces full re-encode)"
	@echo "make audit            - cross-check publication authors against the roster"
	@echo "make audit-site       - build-output audit: dead links, anchors, h1/meta/alt"
	@echo "make tokens           - validate design tokens + regenerate DESIGN_RULES/tokens.md"
	@echo "make package-member MEMBER=<webId>  - zip a member's folder + template to send them"

build:
	python build.py

# HTTP/1.1 (not http.server's HTTP/1.0 default) so VS Code / SSH port-forwarding
# streams the response instead of buffering it into an infinite spinner.
serve: build
	cd docs && python -c "from http.server import SimpleHTTPRequestHandler as H, ThreadingHTTPServer as S; H.protocol_version='HTTP/1.1'; S(('0.0.0.0',8000),H).serve_forever()"

dev:
	python dev_server.py

clean:
	rm -rf docs

clean-cache:
	rm -rf .webp-cache

audit:
	python audit_authors.py

tokens:
	python validate_design_tokens.py
	python generate_token_reference.py

audit-site:
	python validate_site.py

# e.g. make package-member MEMBER=jianhernyeoh
package-member:
	@test -n "$(MEMBER)" || { echo "Usage: make package-member MEMBER=<webId>"; exit 1; }
	@test -d "contents/members/$(MEMBER)" || { echo "No such member folder: contents/members/$(MEMBER)"; exit 1; }
	zip -r "$(MEMBER).zip" "contents/members/$(MEMBER)" "contents/members/MEMBER_TEMPLATE/README.md"
	@echo "Wrote $(MEMBER).zip"
