import os
from setuptools import setup, find_packages

root_dir_path = os.path.dirname(os.path.abspath(__file__))

long_description = open(os.path.join(root_dir_path, "README.md")).read()

setup(
    name="functainer",
    version="0.0.1",
    author="Diego J. Romero López",
    author_email="diegojromerolopez@gmail.com",
    description="Dockerize a function and run it in a container directly from Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries",
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: MIT License"
    ],
    install_requires=[
        "docker>=6.0.0"
    ],
    license="MIT",
    keywords=("docker", "decorator", "isolation"),
    url="https://github.com/diegojromerolopez/functainer",
    packages=find_packages(),
    data_files=[],
    include_package_data=True,
    scripts=[]
)
