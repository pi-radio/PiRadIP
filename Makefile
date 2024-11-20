build: env
	bash -c "source env/bin/activate ; make do_build"

env: Makefile
	python3 -m venv env

.PHONY: prepare build

ipxact2009:
	bash -c "source env/bin/activate ; xsdata generate -c piradip/build/xsdata-config-2009.xml piradip/build/schema/2009/"

do_prepare:
	git submodule update --init
	pip install anytree pexpect prompt_toolkit bitarray lxml xsdata[cli] click pyEDAA.IPXACT
	pip install -e pirbuild

do_build: do_prepare ipxact2009
	@echo "Building library..."
	./buildlib.py build

build_only:
	bash -c 'source env/bin/activate ; ./buildlib.py build'
