import sys
from setuptools import setup

if sys.version_info[:2] < (3, 5):
    raise SystemExit('require Python3.5+')

setup(
    name='html_cleaner',
    url='https://github.com/account-login/html_cleaner',
    author='account-login',
    author_email='',
    version='0.2dev',
    py_modules=['html_cleaner'],
    install_requires=['beautifulsoup4', 'html5lib'],
    entry_points='''
        [console_scripts]
        html_cleaner=html_cleaner:main
    ''',
    license='MIT',
    description='clean up html files',
    long_description=open('README.txt').read(),
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        'Operating System :: OS Independent',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='html cleaner tidy',
)
