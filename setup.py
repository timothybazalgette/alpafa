from setuptools import setup, find_packages

setup(
    name='ALPAFA',
    version='0.2',
    packages=find_packages(),
    entry_points={'console_scripts': ['alpafa=alpafa.cli:main']},
    platforms='any',
    python_requires='>=3',
    author='Timothy Bazalgette',
    author_email='timothy.bazalgette@gmail.com',
    description='Algorithm for lexicocentric parameter acquisition by feature assignment',
    long_description=open('README.rst').read(),
    license='MIT',
    keywords='parameters lexicocentrism recos features linguistics',
    url='https://www.github.com/timothybazalgette/alpafa',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ]
)
