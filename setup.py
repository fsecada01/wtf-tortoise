import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wtf-tortoise",
    version="0.0.2",
    author="sinisaos (packaged by fsecada01",
    author_email="francis.secada@gmail.com",
    description="Implementation of WTForms for Tortoise ORM",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fsecada01/wtf-tortoise",
    project_urls={
        'Bug Tracker': "https://github.com/fsecada01/wtf-tortoise/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "wtftortoise"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.7",
)
