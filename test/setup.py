#!/usr/bin/env python

from setuptools import find_packages, setup


setup(name='testutils',
      version='v0.1.0',
      description='Python Job Q testutils',
      author='Liam Tengelis',
      author_email='liam@tengelisconsulting.com',
      packages=find_packages(),
      package_data={
          '': ['*.yaml'],
          "testutils": ["py.typed"],
      },
)
