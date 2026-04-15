from setuptools import setup, find_packages
import os

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="Topsis-Deep-102303673",
    version="1.0.0",
    author="Deepinder Singh Saini",
    author_email="deepsaini1912@gmail.com",
    description="A Python package for implementing TOPSIS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'topsis=Topsis_Deep_102303673.topsis:main',
        ],
    },
)