import setuptools
from distutils.core import setup


setup(
    name = "news_summariser",
    version = "0.0.0",
    description = "Summarising the most recent news",
    author = "Ziheng",
    packages = ["news_summariser"],
    entry_points = {
        "console_scripts": [
            "news_summariser = news_summariser.summary:main"
        ]
    },
)



