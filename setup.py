import json
from pathlib import Path
from setuptools import setup, find_packages

SETUP_DIR = Path(__file__).parent

with open(SETUP_DIR.joinpath("Pipfile.lock"), "r") as f:
    data = json.loads(f.read())
    REQUIREMENTS = "\n".join(f"{k}{v['version']}" for k, v in data["default"].items())

setup(
    name="sortlogs",
    version="0.0.1",
    packages=find_packages(),
    url="https://github.com/WojtekReu/sortlogs",
    license="MIT",
    author="Wojciech Zając",
    author_email="wojciech@reunix.eu",
    description="Commands to sorting logs from some services",
    python_requires=">=3.11",
    install_requires=REQUIREMENTS,
    classifiers=[
        "Environment :: Console",
        "Framework :: Django :: 4.1",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
)
