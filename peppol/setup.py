from setuptools import find_packages, setup

setup(
    name='peppollib',
    packages=find_packages(include=['peppollib']),
    version='0.1.0',
    description=' PEPPOL Access Point library',
    authors='Michiel de Jong,Triantafullenia Doumanni',
    license'MIT',
    url='',
    install_requires=[],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==4.4.1'],
    test_suite='tests',
)
