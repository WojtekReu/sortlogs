import os
from setuptools import setup, find_packages

SETUP_DIR = os.path.dirname(__file__)

with open(os.path.join(SETUP_DIR, "requirements.txt"), "r") as f:
    REQUIREMENTS = f.read()

setup(
    name='sortlogs',
    version='0.0.1',
    packages=find_packages(),
    url='https://github.com/WojtekReu/sortlogs',
    license='MIT',
    author='Wojciech Zając',
    author_email='wojciech@reunix.eu',
    description='Commands to sorting logs from some services',
    python_requires=">=3.6",
    install_requires=REQUIREMENTS,
    classifiers=[
        "Environment :: Console",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
)
