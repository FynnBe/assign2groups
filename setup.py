from setuptools import setup, find_packages
import os.path

with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), "README.md")) as f:
    long_description = f.read()

setup(
    name="assign2groups",
    version="0.1.0",
    description="python script that assigns names to groups, based on indicated preferences",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/FynnBe/assign2groups",
    author="Fynn Beuttenmüller",
    author_email="thefynnbe@gmail.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.7",
    ],
    keywords="groups teaching hungarian-algorithm linear-sum-assignment minimum-weight-matching",
    packages=find_packages(exclude=[]),
    python_requires=">=3.6",
    install_requires=["scipy"],
    entry_points={"console_scripts": ["assign2groups=assign2groups:main"]},
)
