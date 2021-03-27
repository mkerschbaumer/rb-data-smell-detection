from setuptools import setup, find_packages
import versioneer

# NOTE: From setup.py of Great Expectations
with open("requirements.txt") as f:
    required = f.read().splitlines()

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="datasmelldetection",
    description="A library for data smell detection.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Martin Kerschbaumer",
    author_email="m.kerschbaumer@student.uibk.ac.at",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    install_requires=required,
    packages=find_packages(),
    include_package_data=True,
    license="Apache-2.0",
    keywords="data quality dataquality data smells datasmells",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
    ]
)
