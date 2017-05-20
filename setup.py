from setuptools import setup
from distutils.cmd import Command
from subprocess import Popen
import subprocess
from aiohttp_debugger import __version__
from setuptools.command.test import test as TestCommand
import sys


class Test(TestCommand):
    _args = ['tests']

    def run_tests(self):
        import pytest

        if pytest.main(self._args) > 0:
            sys.exit(0)


class Npm(Command):
    user_options = [('static', None, None)]

    def run(self):
        # `npm install` in any case
        subprocess.run(args=['npm', 'install'], cwd=r'./assets')
        # run build task
        subprocess.run(args=['npm', 'run', 'build'], cwd=r'./assets')

    def initialize_options(self): pass

    def finalize_options(self): pass


prod_requires = [
    'aiohttp',
    'aiohttp_jinja2',
    'ujson'
]

dev_requires = prod_requires + [
    'pytest-aiohttp',
    'pytest',
    'coverage'
]

setup(
    name='aiohttp-debugger',
    version=__version__,
    install_requires=prod_requires,
    extras_require=dict(
        dev=dev_requires
    ),
    packages=['aiohttp_debugger'],
    package_data=dict(aiohttp_debugger=[
        'static/*',
        'static/bundle/*',
        'static/bundle/font-awesome/css/*',
        'static/bundle/font-awesome/fonts/*',
    ]),
    include_package_data=True,
    cmdclass=dict(static=Npm, test=Test)
)
