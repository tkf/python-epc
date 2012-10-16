epc/__init__.py: README.rst
	cog.py -r $@

upload: epc/__init__.py
	python setup.py register sdist upload
