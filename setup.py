# -*- coding: utf-8 -*-
import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='deform_extensions',
    version='0.2.3',
    packages=['deform_extensions'],
    include_package_data=True,
    license='GPLv3',
    description='Usefull tools for making grid/accordion layouted forms',
    long_description=README,
    url='https://github.com/majerteam/deform_extensions',
    author='Gaston Tjebbes - Majerti',
    author_email='tech@majerti.fr',
    install_requires=['deform', 'js.deform', 'js.jquery_timepicker_addon'],
    extra_requires={'docs': ['sphinx'], 'test':['pytest']},
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        # Replace these appropriately if you are stuck on Python 2.
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
