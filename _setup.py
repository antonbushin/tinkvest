"""setup.py"""

import pathlib
from setuptools import setup, find_packages
from tinkvest import __version__

HERE = pathlib.Path(__file__).parent.resolve()
long_description = (HERE / 'README.md').read_text(encoding='utf-8')


DEPENDENCIES = [
    'regex~=2021.11.10',
    'orjson~=3.6.5',
    'pydantic~=1.9.0',
    'pandas~=1.3.5',
    'rapidfuzz~=1.9.1',
    'aiogram~=2.18',
    'yfinance~=0.1.67',
    'mplfinance~=0.12.8b6',
    'requests~=2.26.0',
    'tinvest~=3.0.5',
    'setuptools~=57.0.0',
]

setup(
    name='tinkvest',
    version=__version__,
    packages=find_packages(where="tinkvest"),
    package_dir={"": "tinkvest"},
    url='https://github.com/antonbushin/tinkvest',
    license='MIT',
    author='Бушин А. И.',
    author_email='superyolka@gmail.com',
    description='Алготрейдинг с брокером Тинькофф',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='tinkoff telegram',
    python_requires=">=3.8",
    install_requires=DEPENDENCIES,
    entry_points={
        "console_scripts": ["tinkvest=tinkvest.__main__:main"]
    }
)
