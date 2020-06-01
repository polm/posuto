from setuptools import setup, find_packages
import os
import gzip
import shutil
from pathlib import Path

def gzip_postal_data():
    # remove the existing file
    curdir = Path(__file__).parent
    jsonfile = curdir / 'posuto/postaldata.json'
    gzfile = curdir / 'posuto/postaldata.json.gz'

    if gzfile.is_file() and not jsonfile.is_file():
        # this is an install that already has the gzip
        return

    if gzfile.is_file() and gzfile.stat().st_mtime > jsonfile.stat().st_mtime:
        # we're up to date, nothing to do.
        return

    # zip the non-compressed file
    with open(jsonfile, 'rb') as f_in:
        with gzip.open(gzfile, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

setup(
    name='posuto',
    version='0.1.9',
    url='https://github.com/polm/posuto.git',
    author="Paul O'Leary McCann",
    author_email='polm@dampfkraft.com',
    description='Japanese Postal Code Data',
    packages=find_packages(),    
    package_data={'posuto':['postaldata.json.gz']},
    install_requires=[],
)

if __name__ == '__main__':
    gzip_postal_data()
