#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name="sinode",
    version="1.1.2",
    description="An inheritable Node class",
    author="Julian Loiacono",
    author_email="jcloiacon@gmail.com",
    url="https://github.com/julianfl0w/sinode",
    packages=find_packages(),
    package_data={
        # everything
        "": ["*"]
    },
    include_package_data=True,
)
