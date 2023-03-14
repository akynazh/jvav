from setuptools import setup, find_packages

with open("requirements.txt", encoding="utf-8") as r:
    requires = [i.strip() for i in r]


with open("README.md", encoding="utf-8") as f:
    readme = f.read()


setup(
    name="Jvav",
    version='1.0.0',
    description="Tools for Japan adult video",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/akynazh/jvav",
    download_url="https://github.com/akynazh/jvav/releases/latest",
    author="akynazh",
    author_email="akynazh@gmail.com",
    license="GPLv3",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search"
    ],
    keywords="jav japan av api library python spider",
    project_urls={
        "Tracker": "https://github.com/akynazh/jvav/issues",
        "Source": "https://github.com/akynazh/jvav",
    },
    python_requires="~=3.7",
    include_package_data=True,
    packages=find_packages(
        where='jvav',
        exclude=[]
    ),
    install_requires=requires
)