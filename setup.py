from distutils.core import setup

import epc

setup(
    name='epc',
    version=epc.__version__,
    packages=['epc'],
    author=epc.__author__,
    author_email='aka.tkf@gmail.com',
    url='https://github.com/tkf/python-epc',
    license=epc.__license__,
    description='EPC (RPC stack for Emacs Lisp) server for Python',
    long_description=epc.__doc__,
    keywords='Emacs, RPC',
    classifiers=[
        "Development Status :: 3 - Alpha",
        'License :: OSI Approved :: BSD License',
        "Programming Language :: Emacs-Lisp",
        # see: http://pypi.python.org/pypi?%3Aaction=list_classifiers
    ],
    install_requires=[
        'sexpdata',
    ],
)
