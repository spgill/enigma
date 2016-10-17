import os
import setuptools


def readme():
    if os.path.isfile('README.md'):
        try:
            import requests
            r = requests.post(
                url='http://c.docverter.com/convert',
                data={'from': 'markdown', 'to': 'rst'},
                files={'input_files[]': open('README.md', 'r')}
            )
            if r.ok:
                return r.content.decode()
            else:
                return 'ERROR CONVERTING README!'
        except ImportError:
            print('No `requests` module. No readme conversion applied.')
            return '!!NO CONVERSION!!\n\n' + open('README.md', 'r').read()
    else:
        return 'No readme for local builds.'


setuptools.setup(
    name='enigma',
    version='1.0.3',
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
