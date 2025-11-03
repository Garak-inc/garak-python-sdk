"""
Garak Security SDK - Setup

Python client library for the Garak AI Security Platform.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename), encoding='utf-8') as f:
        return f.read()

# Read version from __init__.py
def get_version():
    with open(os.path.join('garak_sdk', '__init__.py'), 'r') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"').strip("'")
    return '1.0.0'

setup(
    name='garak-sdk',
    version=get_version(),
    author='Garak Security',
    author_email='support@getgarak.com',
    description='Python client library for the Garak AI Security Platform',
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/Garak-inc/garak-python-sdk',
    project_urls={
        'Documentation': 'https://docs.garaksecurity.com',
        'Source': 'https://github.com/Garak-inc/garak-python-sdk',
    },
    packages=find_packages(exclude=['tests', 'examples']),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Security',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    python_requires='>=3.8',
    install_requires=[
        'requests>=2.31.0',
        'pydantic>=2.0.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'mypy>=1.0.0',
            'isort>=5.12.0',
        ],
        'dotenv': [
            'python-dotenv>=1.0.0',
        ],
    },
    keywords='security ai llm vulnerability scanning garak red-team',
    license='MIT',
    include_package_data=True,
    zip_safe=False,
)
