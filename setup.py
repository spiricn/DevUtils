#!/usr/bin/env python

from setuptools import setup, find_packages

import du


setup(
      name='DevUtils',

      version=du.__version__,

      description='DevUtils',

      author='Nikola Spiric',

      author_email='nikola.spiric.ns@gmail.com',

      packages=find_packages(),

	  license='MIT',

      entry_points={
              'console_scripts' : [
                       'du_spush = du.android.smartpush.AndroidSmartPushApp:main',
                       'du_rnotes = du.git.ReleaseNotesApp:main',
                       'du_pb = du.pastebin.App:main'
               ]
      }
)
