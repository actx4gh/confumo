
from setuptools import setup, find_packages

# Read the contents of requirements.txt
with open('requirements.txt') as f:
    required_packages = f.read().splitlines()

setup(
    name='confumo',
    version='0.1.0',
    description='Platform-aware configuration management for Python applications',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Aaron Colichia',
    url='https://github.com/actx4gh/confumo',
    packages=find_packages(),
    install_requires=required_packages,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
