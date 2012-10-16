## Functional test (run sample)
CARTON = carton
EMACS = emacs

run-sample:
	EMACS=${EMACS} ${CARTON} exec ${EMACS} -batch -l client.el

install:
	${CARTON} install

clean-elpa:
	rm -rf elpa


## Update files using cog.py

epc/__init__.py: README.rst
	cog.py -r $@


## Upload to PyPI

upload: epc/__init__.py
	python setup.py register sdist upload
