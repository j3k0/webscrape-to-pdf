from setuptools import setup, find_packages

setup(
    name="webscrape2pdf",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "requests",
        "beautifulsoup4",
        "reportlab",
        "requests-cache",
        "diskcache",
        "xhtml2pdf",
        "undetected-chromedriver",
    ],
    entry_points={
        "console_scripts": [
            "webscrape2pdf=webscrape2pdf:main",
        ],
    },
)