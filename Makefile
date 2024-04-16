.PHONY: install, test, format, lint, install-system-packages, all

install:
	pip install --upgrade pip && pip install uv\
		uv pip install .

test:
	pytest || ([ $$? = 5 ] && exit 0 || exit $$?)

format:
	black $(git ls-files '*.py') .

lint:
	pylint --disable=R,C $$(git ls-files '*.py')

all: install test format lint install-system-packages