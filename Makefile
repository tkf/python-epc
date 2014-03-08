ifdef ENV
	PYTHON = $(shell pwd)/.tox/${ENV}/bin/python
endif
PYTHON ?= python
CASK ?= cask
EMACS ?= emacs
VIRTUAL_EMACS = EMACS=${EMACS} PYTHON=${PYTHON} ${CASK} exec ${EMACS} -Q
sample_runner = ${VIRTUAL_EMACS} -batch -l

ELPA_DIR = \
	.cask/$(shell ${EMACS} -Q --batch --eval '(princ emacs-version)')/elpa
# See: cask-elpa-dir

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
	EMACS=${EMACS} PYTHON=${PYTHON} CASK=${CASK} examples/epcs/run.sh

run-gtk-sample:
	${VIRTUAL_EMACS} -l examples/gtk/client.el

elpa: ${ELPA_DIR}
${ELPA_DIR}: Cask
	${CASK} install
	touch $@

clean-elpa:
	rm -rf ${ELPA_DIR}

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
