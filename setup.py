
from setuptools import setup, find_packages

setup(
    name="markdown2pdf",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["requests"],
    author="Serendipity AI",
    description="Convert Markdown to PDF with L402 Lightning support, brought to you by markdown2pdf.ai",
    license="MIT",
)
