from setuptools import setup, find_packages

setup(
    name='posuto',
    version='0.1.1',
    url='https://github.com/polm/posuto.git',
    author="Paul O'Leary McCann",
    author_email='polm@dampfkraft.com',
    description='Japanese Postal Code Data',
    packages=find_packages(),    
    package_data={'posuto':['postaldata.json.gz']},
    install_requires=[],
)
