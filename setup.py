from setuptools import setup, find_packages

install_requires = []

setup(
    name="coin-trends",
    version="0.1",
    description="scrape 4chan for biz content",
    author="bwallad",
    author_email="bwallad@test.com",
    install_requires=install_requires,
    scripts=[
        "scraper/scripts/get_tickers.py",
    ],
    packages=find_packages()
)
