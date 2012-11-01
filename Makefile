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

.PHONY : test full-test run-sample elpa clean-elpa cog doc upload


## Tests

test:
	tox

full-test: test elpa
	make run-sample ENV=py26
	make run-sample ENV=py27
	make run-sample ENV=py32

run-sample:
	EMACS=${EMACS} PYTHON=${PYTHON} \
		${CARTON} exec ${EMACS} -Q -batch -l client.el

elpa:
	${CARTON} install

clean-elpa:
	rm -rf elpa


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
