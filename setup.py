from setuptools import setup
from distutils.cmd import Command
from subprocess import Popen
import subprocess
from aiohttp_debugger import __version__
from setuptools.command.test import test as TestCommand
import sys


class Test(TestCommand):

    def run_tests(self):
        raise SystemExit(subprocess.call([sys.executable, '-m', 'pytest', 'tests', '-v', '-s', '--cov=aiohttp_debugger']))


class Npm(Command):
    user_options = [('static', None, None)]

    def run(self):
        # `npm install` in any case
        self._run('npm', 'install')
        # run assets build task
        self._run('npm', 'run', 'build')

    def _run(self, *args):
        return subprocess.run(args=args, cwd=r'./assets')

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass


prod_requires = [
    'aiohttp',
    'aiohttp_jinja2',
    'voluptuous'
]

dev_requires = prod_requires + [
    'pytest-aiohttp',
    'pytest',
    'pytest-cov',
    'coverage'
]

setup(
    name='aiohttp-debugger',
    version=__version__,
    install_requires=prod_requires,
    extras_require={
        'dev': dev_requires
    },
    packages=['aiohttp_debugger'],
    package_data={
        'aiohttp_debugger': [
            'static/*',
            'static/bundle/*',
            'static/bundle/font-awesome/css/*',
            'static/bundle/font-awesome/webfonts/*',
        ]
    },
    include_package_data=True,
    cmdclass={
        'static': Npm,
        'test': Test
    }
)
