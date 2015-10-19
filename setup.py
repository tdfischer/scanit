#!/usr/bin/env python

import scanit

from distutils.core import setup

setup(name='scanit',
      version=scanit.SCANIT_VERSION,
      description='Scanit Scans It',
      author='Torrie Fischer',
      author_email='tdfischer@hackerbots.net',
      scripts=['scanit']
)
