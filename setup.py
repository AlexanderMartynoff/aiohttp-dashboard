from setuptools import setup
from distutils.cmd import Command
from subprocess import Popen


class Npm(Command):
    user_options = [('npm', None, None)]

    def run(self):
        with Popen(args=['npm', 'run', 'build'], cwd=r'./assets') as process:
            process.wait()

    def initialize_options(self): pass
    def finalize_options(self): pass


setup(
    name='aiohttp_debugger',
    version='0.0.1',
    install_requires=[
        'aiohttp',
        'aiohttp_jinja2'
    ],
    packages=['aiohttp_debugger'],
    package_data=dict(aiohttp_debugger=['static/*', 'static/bundle/*']),
    include_package_data=True,
    cmdclass=dict(npm=Npm)
)
