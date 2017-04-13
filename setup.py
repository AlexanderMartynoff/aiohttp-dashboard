from setuptools import setup
from distutils.cmd import Command
from subprocess import Popen


class Npm(Command):
    user_options = [('static', None, None)]

    def run(self):
        # `npm install` in any case
        Popen(args=['npm', 'install'], cwd=r'./assets').wait()
        # run build task
        Popen(args=['npm', 'run', 'build'], cwd=r'./assets').wait()

    def initialize_options(self): pass

    def finalize_options(self): pass


setup(
    name='aiohttp-debugger',
    version='2.0.1.1',
    install_requires=[
        'aiohttp',
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
