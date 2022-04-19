from setuptools import setup, find_packages

with open("README.md") as f:
    long_description = f.read()

with open("sockit/VERSION") as f:
    version = f.read().strip()

setup(
    name="sockit",
    author="Mark Howison",
    author_email="mhowison@ripl.org",
    version=version,
    url="https://github.com/ripl-org/sockit",
    description="Assign probabilistic Standard Occupational Classification (SOC) codes to free-text job titles",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: Free for non-commercial use",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Human Machine Interfaces",
        "Topic :: Scientific/Engineering :: Information Analysis"
    ],
    provides=["sockit"],
    install_requires=["wordtrie>=0.0.4"],
    packages=find_packages(),
    package_data={"sockit": ["VERSION", "data/*"]},
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "sockit = sockit.__main__:main"
        ]
    }
)
