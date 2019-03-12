from setuptools import setup

setup(
    name='pylib',
    version='1.0.0',
    packages=['pylib'],
    url='https://github.com/deeprave/pylib',
    license='Apache v2.0',
    author='David Nugent',
    author_email='davidn@uniquode.io',
    description='Library of py2/py3 convenience functions',
    long_description='Library of general convenience functions including an ordered dict (py2/py3 compatible), recursive object serializer, open context manager that supports in memory ouput as well as files, composable configuration manager supporting YAML, and the addition of a TRACE level to python logging.',
    install_requires=[
        'PyYAML',
        'future',
        'six',
    ],
    classifiers=[
        'Programming Language :: Python',
    ],
    entry_points={
        'pytest11': [
        ]
    }
)
