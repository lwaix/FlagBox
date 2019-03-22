from setuptools import setup
from flagbox import VERSION

with open("README.md", 'r') as f:
    long_description = f.read()

setup(
    name='FlagBox',
    version=VERSION,
    author='lwaix',
    author_email='1494645263@qq.com',
    description='A simple mysql orm for python3',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/lwaix/flagbox',
    packages=['flagbox'],
    install_requires=[
        'PyMySQL'
    ],
    license='MIT',
    test_suite='test'
)
