from setuptools import setup
from distutils.cmd import Command
from subprocess import Popen


class Npm(Command):
    user_options = [('static', None, None)]

    def run(self):
        with Popen(args=['npm', 'run', 'build'], cwd=r'./assets') as process:
            process.wait()

    def initialize_options(self): pass

    def finalize_options(self): pass


setup(
    name='aiohttp_debugger',
    version='1.0.5.5',
    install_requires=[
        'aiohttp>=2.0.0',
        'aiohttp_jinja2'
    ],
    packages=['aiohttp_debugger'],
    package_data=dict(aiohttp_debugger=[
        'static/*',
        'static/bundle/*',
        'static/bundle/font-awesome/css/*',
        'static/bundle/font-awesome/fonts/*',
    ]),
    include_package_data=True,
    cmdclass=dict(static=Npm)
)
