test:
	python3.5 -m nose

install:
	python3.5 -m pip install . --upgrade

run-help:
	python3.5 -m viewsparktimeline --help

linter:
	pycodestyle --ignore=E251 --max-line-length=120 .
	python setup.py check --restructuredtext

dist-upload: clean linter test
	python setup.py sdist bdist_wheel
	twine upload dist/*

clean:
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info/
	rm -rf */__pycache__

.PHONY: test linter dist-upload clean
