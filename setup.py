#!/usr/bin/env python

from setuptools import find_packages, setup


setup(name='pjobq',
      version='v0.1.0',
      description='Python Job Q',
      author='Liam Tengelis',
      author_email='liam@tengelisconsulting.com',
      url='https://github.com/tengelisconsulting/pyjobq',
      packages=find_packages(),
      package_data={
          '': ['*.yaml'],
          "pyjobq": ["py.typed"],
      },
)
