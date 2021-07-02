import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name='PyCASL',
    version='1.0.1',
    packages=['casl'],
    package_dir={'': 'src'},
    long_description=README,
    long_description_content_type="text/markdown",
    url='https://github.com/hilfestellung/PyCASL',
    license='LGPL-3.0-or-later ',
    author='Christian Dein',
    author_email='christian.dein@dein-hosting.de',
    description='Pythonized CASL library, see https://casl.js.org',
    classifiers=[
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
    extra_require=dict(tests=['pytest'])
)
