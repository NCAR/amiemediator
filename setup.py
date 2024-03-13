from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='amiemediator',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        'amieclient>=0.6.1',
    ],
    author='George B Williams',
    author_email='gwilliam@ucar.edu',
    python_requires='>=3.9',
    description='Tool that ties together amieclient and a local Service Provider.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    project_urls={
        'Source': 'https://github.com/NCAR/amiemediator/',
    },
)
