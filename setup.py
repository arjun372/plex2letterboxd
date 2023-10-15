from setuptools import setup

with open('README.md') as f:
    README = f.read()

setup(
    name='plex2letterboxd',
    url='https://github.com/mtimkovich/plex2letterboxd',
    version='1.2',
    author='Max Timkovich',
    author_email='max@timkovi.ch',
    license='MIT',
    description='Export watched Plex movies to the Letterboxd import format.',
    long_description=README,
    install_requires=[
            'plexapi==4.15.4',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'plex2letterboxd=plex2letterboxd:main',
        ],
    },
)
