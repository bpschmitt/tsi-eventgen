import setuptools

setuptools.setup(
    name="tsi-eventgen",
    version="0.1.0",
    url="https://github.com/bpschmitt/tsi-eventgen",

    author="Brad Schmitt",
    author_email="bradleypschmitt@gmail.com",

    description="Just testing cookiecutter for now",
    long_description=open('README.rst').read(),

    packages=setuptools.find_packages(),

    install_requires=[],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
