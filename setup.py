from pip._internal.network.session import PipSession
from pip._internal.req import parse_requirements
from setuptools import setup, find_packages

install_reqs = [str(ir.requirement) for ir in parse_requirements('requirements.txt', session=PipSession())]
setup(

    name='sequra',
    version='1.0.0',
    description='Python Code Test sequra',
    author='Manuel Chamber',

    classifiers=[
        'Development Status :: MVP',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Programming Language :: Python :: 3.8',
    ],

    packages=find_packages(),

    install_requires=install_reqs,
    extras_require={'test': ['pytest', 'coverage']},
)
