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


## Update files using cog.py

epc/__init__.py: README.rst
	cog.py -r $@


## Upload to PyPI

upload: epc/__init__.py
	python setup.py register sdist upload
