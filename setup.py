import os

import requests
import setuptools


def readme():
    if os.path.isfile('README.md'):
        r = requests.post(
            url='http://c.docverter.com/convert',
            data={'from': 'markdown', 'to': 'rst'},
            files={'input_files[]': open('README.md', 'r')}
        )
        if r.ok:
            return r.content.decode()
        else:
            return 'ERROR CONVERTING README!'
    else:
        return 'LOCAL BUILD! NO README!'


setuptools.setup(
    name='enigma',
    version='1.0.0',
    description='Python Enigma-like simulation with historical wirings.',
    long_description=readme(),
    keywords='enigma machine encrypt encryption rotor rotors',
    author='Samuel P. Gillispie II',
    author_email='spgill@vt.edu',
    url='https://github.com/spgill/bitnigma',
    license='MIT',
    packages=['enigma'],
    install_requires=[
        'colorama'
    ],
    classifiers=[
        'Environment :: Console',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3'
    ]
)
