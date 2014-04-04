#!/usr/bin/env python
# -*- coding: utf-8 -*- 
try:
    from setuptools import setup, find_packages
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup, find_packages

setup(name='device42api',
      version='1.2.1',
      description='Device42.com API module for object oriented API handling',
      author='Michael Lang',
      author_email='Michael.Lang@ctbto.org',
      url='http://python-device42api.readthedocs.org/en/latest/',
      packages=find_packages(),
      license='GPLv2',
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Topic :: Documentation',
        'Topic :: Text Processing',
        'Topic :: Utilities',
        ],
      install_requires=['python-httplib2 >= 0.8', 'python-simplejson >= 1.4.6'],
      )
