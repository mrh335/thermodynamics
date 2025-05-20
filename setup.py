from setuptools import setup, find_packages

setup(
    name="thermodynamics-mrh335",
    version="0.2.0",
    author="Mark Hoehne",
    author_email="your.email@example.com",
    description="A Python package for thermodynamic calculations",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/mrh335/thermodynamics",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
