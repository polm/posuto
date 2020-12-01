from setuptools import setup, find_packages
import os
import gzip
import shutil
from pathlib import Path

setup(
    name='posuto',
    use_scm_version=True,
    url='https://github.com/polm/posuto.git',
    author="Paul O'Leary McCann",
    author_email='polm@dampfkraft.com',
    description='Japanese Postal Code Data',
    packages=find_packages(),    
    package_data={'posuto':['postaldata.db']},
    install_requires=[],
    setup_requires=['setuptools-scm'],
)

