"""Compatibility shim for older pip/setuptools installations.

Canonical metadata lives in pyproject.toml. Keeping this small explicit fallback
also lets the macOS system Python's older packaging toolchain install the CLI.
"""

from setuptools import find_packages, setup


setup(
    name="oss-doctor",
    version="0.1.0",
    description="A zero-dependency health check for open-source repositories",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="LittleCurry",
    url="https://github.com/LittleCurry/oss-doctor",
    project_urls={
        "Repository": "https://github.com/LittleCurry/oss-doctor",
        "Issues": "https://github.com/LittleCurry/oss-doctor/issues",
    },
    license="MIT",
    python_requires=">=3.9",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    entry_points={"console_scripts": ["oss-doctor=oss_doctor.cli:main"]},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Quality Assurance",
    ],
)
