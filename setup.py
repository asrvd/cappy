from setuptools import setup, find_packages
from io import open
from os import path
import pathlib

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()
with open(path.join(HERE, "./requirements.txt"), encoding="utf-8") as f:
    all_reqs = f.read().split("\n")
install_requires = [
    x.strip()
    for x in all_reqs
    if ("git+" not in x) and (not x.startswith("#")) and (not x.startswith("-"))
]
dependency_links = [x.strip().replace("git+", "") for x in all_reqs if "git+" not in x]

setup(
    name="cappy-cli",
    description="A cli tool to add captions to images.",
    version="1.1.7",
    include_package_data=True,
    packages=find_packages(),  # list of all packages
    install_requires=install_requires,
    entry_points="""
            [console_scripts]
            cappy=cappy.__main__:main
        """,
    author="ashish",
    keyword="caption, image-caption, discord-image-caption gif-caption text-on-image",
    long_description=README,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/asheeeshh/cappy",
    dependency_links=dependency_links,
    author_email="asheeshh@duck.com",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
