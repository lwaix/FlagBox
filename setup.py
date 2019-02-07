from setuptools import setup
from pmorm import VERSION, __author__, __email__

setup(
    name='Pmorm',
    version=VERSION,
    author=__email__,
    author_email=__email__,
    packages=['pmorm'],
    install_requires=[
        'PyMySQL'
    ],
    license='MIT',
    test_suite='test'
)