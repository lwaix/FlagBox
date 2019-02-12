from setuptools import setup
from pmorm import VERSION

setup(
    name='Pmorm',
    version=VERSION,
    author='lwaix',
    author_email='1494645263@qq.com',
    packages=['pmorm'],
    install_requires=[
        'PyMySQL'
    ],
    license='MIT',
    test_suite='test'
)
