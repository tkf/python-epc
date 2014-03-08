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

full-test: test elpa .tox
	${MAKE} run-testable-samples ENV=py26
	${MAKE} run-testable-samples ENV=py27
	${MAKE} run-testable-samples ENV=py32

.tox:
	tox --notest

.tox/${ENV}:
	TOXENV=${ENV} tox --notest
# To make run-testable-samples run-able, .tox and .tox/${ENV} are
# defined separately.

run-testable-samples: .tox/${ENV}
	${MAKE} run-testable-samples-1 ENV=${ENV}

run-testable-samples-1: run-sample run-quick-launcher-sample run-inprocess
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

print-deps: before-test
	@echo "----------------------- Dependencies -----------------------"
	$(EMACS) --version
	ls -d .tox/*/*/python*/site-packages/*egg-info
	@echo "------------------------------------------------------------"

before-test: .tox elpa

travis-ci: print-deps full-test

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
