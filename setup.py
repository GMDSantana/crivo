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

from setuptools import setup, find_packages
from crivo.version import __version__

# Helper function to read requirements.txt
def parse_requirements(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='crivo',
    version=__version__,
    packages=find_packages(),
    install_requires=parse_requirements('requirements.txt'),
    entry_points={
        'console_scripts': [
            'crivo=crivo.main:main',
        ],
    },
    author='Guilherme Santana',
    author_email='git@gmdsantana.com',
    description='A tool for extracting and filtering URLs, IPs, domains, and subdomains from text or web pages, with built-in web scraping capabilities.',
    license='MIT',
    url='https://github.com/GMDSantana/crivo',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
    ],
)

