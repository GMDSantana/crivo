"""

╔██████╗██████╗ ██╗██╗     ██╗╔██████╗
██╔════╝██╔══██╗██║╚██╗   ██╔╝██╔═══██╗
██║     ██████╔╝██║ ╚██╗ ██╔╝ ██║   ██║
██║     ██╔██═╝ ██║  ╚████╔╝  ██║   ██╝
╚██████╗██║ ██╗ ██║   ╚██╔╝   ╚██████╝
© Guilherme Santana
https://gmdsantana.com
https://github.com/GMDSantana/crivo

"""

from pathlib import Path

from setuptools import find_packages, setup

HERE = Path(__file__).resolve().parent


def read_version():
    # Read the version without importing the package (and its dependencies).
    namespace = {}
    exec((HERE / "crivo" / "version.py").read_text(encoding="utf-8"), namespace)
    return namespace["__version__"]


# Helper function to read requirements.txt
def parse_requirements(filename):
    with open(HERE / filename, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]


setup(
    name='crivo',
    version=read_version(),
    packages=find_packages(exclude=('tests', 'tests.*')),
    package_data={'crivo': ['data/valid_tlds.txt']},
    install_requires=parse_requirements('requirements.txt'),
    python_requires='>=3.10',
    entry_points={
        'console_scripts': [
            'crivo=crivo.main:main',
        ],
    },
    author='Guilherme Santana',
    author_email='git@gmdsantana.com',
    description='A tool for extracting and filtering URLs, IPs, domains, and subdomains from text or web pages, with built-in web scraping capabilities.',
    long_description=(HERE / 'README.md').read_text(encoding='utf-8'),
    long_description_content_type='text/markdown',
    license='MIT',
    license_files=['LICENSE'],
    url='https://github.com/GMDSantana/crivo',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Operating System :: POSIX :: Linux',
        'Environment :: Console',
        'Topic :: Security',
    ],
)
