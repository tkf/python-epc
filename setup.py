from distutils.core import setup

import epc

setup(
    name='epc',
    version=epc.__version__,
    packages=['epc', 'epc.tests'],
    author=epc.__author__,
    author_email='aka.tkf@gmail.com',
    url='https://github.com/tkf/python-epc',
    license=epc.__license__,
    description='EPC (RPC stack for Emacs Lisp) implementation in Python',
    long_description=epc.__doc__,
    keywords='Emacs, RPC',
    classifiers=[
        "Development Status :: 3 - Alpha",
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        "Programming Language :: Emacs-Lisp",
        # see: http://pypi.python.org/pypi?%3Aaction=list_classifiers
    ],
    install_requires=[
        'sexpdata',
    ],
)
