build: env
	bash -c "source env/bin/activate ; make do_build"

env: Makefile
	python3 -m venv env

.PHONY: prepare build

do_prepare:
	pip install anytree pexpect prompt_toolkit bitarray lxml xsdata click
	pip install -e pirbuild

do_build: do_prepare
	@echo "Building library..."
	./buildlib.py build
