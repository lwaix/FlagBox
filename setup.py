from setuptools import setup

setup(
    name='Pmorm',
    version='0.1',
    author='lwaix',
    author_email='1494645263@qq.com',
    packages=['pmorm'],
    install_requires=[
        'PyMySQL'
    ],
    license='MIT',
    test_suite='test'
)