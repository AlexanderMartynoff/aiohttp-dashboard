from setuptools import setup
from distutils.cmd import Command
from subprocess import Popen
import subprocess
from setuptools.command.test import test as TestCommand
import sys


__version__ = '0.0.2'


class Test(TestCommand):

    def run_tests(self):
        subprocess.call([sys.executable, '-m', 'pytest', 'tests', '-v', '-s', '--cov=aiohttp_dashboard'])


class Asset(Command):
    user_options = [('asset', None, None)]

    def run(self):
        self._run('npm', 'install')
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
    name='aiohttp-dashboard',
    version=__version__,
    install_requires=prod_requires,
    extras_require={
        'dev': dev_requires
    },
    packages=['aiohttp_dashboard'],
    package_data={
        'aiohttp_dashboard': [
            'static/*',
            'static/bundle/*',
            'static/bundle/font-awesome/css/*',
            'static/bundle/font-awesome/webfonts/*',
        ]
    },
    include_package_data=True,
    cmdclass={
        'assets': Asset,
        'tests': Test
    }
)
