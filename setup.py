from setuptools import setup, find_packages

setup(
    name="birdkeeper",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    description="Manage hdd hard drives that are encrypted with cryptsetup.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Jack-Auth",
    author_email="noreply@example.com",
    url="https://github.com/jorge-auth/birdkeeper.git",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
