# NTU E3 Center — common tasks.
# Assumes the `E3website` conda env is active (see README).
.PHONY: build serve clean audit package-member help

help:
	@echo "make build            - compile contents/ -> docs/"
	@echo "make serve            - build, then serve docs/ at http://localhost:8000"
	@echo "make clean            - remove the generated docs/ tree"
	@echo "make audit            - cross-check publication authors against the roster"
	@echo "make package-member MEMBER=<webId>  - zip a member's folder + template to send them"

build:
	python build.py

serve: build
	cd docs && python -m http.server 8000

clean:
	rm -rf docs

audit:
	python audit_authors.py

# e.g. make package-member MEMBER=jianhernyeoh
package-member:
	@test -n "$(MEMBER)" || { echo "Usage: make package-member MEMBER=<webId>"; exit 1; }
	@test -d "contents/members/$(MEMBER)" || { echo "No such member folder: contents/members/$(MEMBER)"; exit 1; }
	zip -r "$(MEMBER).zip" "contents/members/$(MEMBER)" "contents/members/MEMBER_TEMPLATE/README.md"
	@echo "Wrote $(MEMBER).zip"
