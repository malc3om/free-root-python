from setuptools import setup, find_packages

setup(
    name="freeroot",
    version="0.1.0",
    description="Ubuntu PRoot environment for Python notebooks",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Based on foxytouxxx/freeroot",
    url="https://github.com/malc3om/free-root-python",
    py_modules=["freeroot"],
    python_requires=">=3.6",
    install_requires=[],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)