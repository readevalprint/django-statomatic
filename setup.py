#!/usr/bin/env python

from distutils.core import setup

setup(
    name='django-statomatic',
    version='0.8.1',
    author='Timothy Watts',
    author_email='tim@readevalprint.com',
    scripts=['statomatic.py'],
    url='http://readevalprint.com/django-statomatic/',
    license='LICENSE.txt',
    description='Pure Django static site generator',
    long_description=open('README.rst').read(),
    requires=[
        'Django (>=1.3)',
    ],
    classifiers=[
        'Topic :: Software Development :: Code Generators',
        'Topic :: Text Processing :: Markup :: HTML',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
    ],
    entry_points={
        'console_scripts': [
            'statomatic = statomatic:main',
        ],
    },
)

