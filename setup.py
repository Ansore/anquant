# -*- coding:utf-8 -*-

from distutils.core import setup

setup(
    name="anquant",
    version="0.0.1",
    packages=[
        "anquant",
        "anquant.utils",
        "anquant.platform",
    ],
    description="Asynchronous event I/O driven quantitative trading framework.",
    url="https://github.com/ansore/anquant",
    author="Ansore",
    author_email="ansore@ansore.top",
    license="MIT",
    keywords=[
        "aioquant", "quant", "framework", "async", "asynchronous", "digiccy",
        "digital", "currency", "marketmaker", "binance", "okx"
    ],
    install_requires=[
        "aiohttp==3.8.3",
        "pymongo==4.2.0",
        "aioamqp==0.15.0"
    ],
)