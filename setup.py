from setuptools import setup, find_packages

setup(
    name='vxmenu',
    version='0.0.1',
    description='Vumi dynamic menu library.',
    long_description=open('README.rst', 'r').read() + \
            open('AUTHORS.rst', 'r').read() + \
            open('CHANGELOG.rst', 'r').read(),
    author='Praekelt Foundation',
    author_email='dev@praekelt.com',
    license='BSD',
    url='http://github.com/praekelt/vxmenu',
    packages=find_packages(),
    dependency_links=[
        'https://github.com/praekelt/vumi/zipball/develop#egg=vumi',
    ],
    install_requires=[
        'vumi',
    ],
    test_suite="vxmenu.tests",
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License",
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Networking",
    ],
    zip_safe=False,
)
