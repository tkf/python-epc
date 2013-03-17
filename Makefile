ifdef ENV
	PYTHON = $(shell pwd)/.tox/${ENV}/bin/python
endif

ifndef PYTHON
	PYTHON = python
endif

ifndef CARTON
	CARTON = carton
endif

ifndef EMACS
	EMACS = emacs
endif

carton_exec = EMACS=${EMACS} PYTHON=${PYTHON} ${CARTON} exec
carton_emacs = ${carton_exec} ${EMACS} -Q
sample_runner = ${carton_emacs} -batch -l

.PHONY : test full-test run-sample elpa clean-elpa cog doc upload


## Tests

test:
	tox

full-test: test elpa
	make run-testable-samples ENV=py26
	make run-testable-samples ENV=py27
	make run-testable-samples ENV=py32

run-testable-samples: run-sample run-quick-launcher-sample run-inprocess
# NOTE: run-inprocess is not added to here as the PORT for this
# example if fixed.

run-sample:
	${sample_runner} examples/echo/client.el

run-quick-launcher-sample:
	${sample_runner} examples/quick-launcher/client.el

run-inprocess:
	${PYTHON} examples/inprocess/echo.py

run-epcs:
	EMACS=${EMACS} PYTHON=${PYTHON} CARTON=${CARTON} examples/epcs/run.sh

run-gtk-sample:
	${carton_emacs} -l examples/gtk/client.el

elpa:
	${CARTON} install

clean-elpa:
	rm -rf elpa

clean-elc:
	rm -f examples/*/*.elc


## Document
doc: cog
	make -C doc html


## Update files using cog.py
cog: epc/__init__.py
epc/__init__.py: README.rst
	cd epc && cog.py -r __init__.py


## Upload to PyPI

upload: epc/__init__.py
	python setup.py register sdist upload
