"""
PSB, a bot to scan local LAN for a whitelist of macs to report presence.
"""
import os.path
from setuptools import setup, find_packages

ROOT = os.path.realpath(os.path.join(os.path.dirname(__file__)))

setup(name='psb',
      version='0.1',
      description='A bot to scan local LAN for a whitelist of macs to report presence.',
      url='https://github.com/aarro/psb',
      author='Jacob Young',
      author_email='jacobyoung@uta.io',
      long_description=open(os.path.join(ROOT, 'README.md')).read(),
      license='MIT',
      packages=find_packages(),
      install_requires=[
          'python-dotenv',
          'slackclient'
      ],
      zip_safe=False)
