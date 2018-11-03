ifdef ENV
	PYTHON = $(shell pwd)/.tox/${ENV}/bin/python
endif
PYTHON ?= python
CASK ?= cask
EMACS ?= emacs
VIRTUAL_EMACS = EMACS=${EMACS} PYTHON=${PYTHON} ${CASK} exec ${EMACS} -Q
sample_runner = ${VIRTUAL_EMACS} -batch -l
TOXENVS = $(shell tox -l)
$(info Active tox envs: ${TOXENVS})

ELPA_DIR = \
	.cask/$(shell ${EMACS} -Q --batch --eval '(princ (format "%s.%s" emacs-major-version emacs-minor-version))')/elpa
# See: cask-elpa-dir

.PHONY : test full-test run-sample elpa clean-elpa cog doc upload


## Tests

test:
	tox

full-test: # test elpa .tox
	for toxenv in ${TOXENVS}; do \
		${MAKE} run-testable-samples ENV=$${toxenv}; \
	done

.tox:
	tox --notest

.tox/${ENV}:
# tox-travis plugin is disabled when there is an empty TOXENV envvar, so that
# case must be handled separately.
ifdef ENV
	TOXENV=${ENV} tox --notest
else
	tox --notest
endif
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
	test -d $@
	${MAKE} EMACS=${EMACS} check-elpa
	touch $@

check-elpa:
	${VIRTUAL_EMACS} -batch --eval "(require 'epc)"

clean-elpa:
	rm -rf ${ELPA_DIR}

clean-elc:
	rm -f examples/*/*.elc

print-deps: before-test
	@echo "----------------------- Dependencies -----------------------"
	$(EMACS) --version
	tox --run-command "pip freeze"
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
