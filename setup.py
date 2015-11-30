from codecs import open as codecs_open
from setuptools import setup, find_packages


with codecs_open("README.md", encoding="utf-8") as f:
    long_description = f.read()


setup(
    name="harvest-python3",
    version="0.0.1",
    description=u"Python3 wrapper for harvest API",
    long_description=long_description,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries",
    ],
    keywords="harvest api harvestapp",
    author=u"Brendan Roy",
    author_email="br3ndanr@gmail.com",
    url="https://github.com/laodicean/py-harvest3",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    install_requires=["requests", "requests-oauthlib"],
    extras_require={},
)
