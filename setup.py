from setuptools import setup, find_packages

setup(
    name='ai-story-automation-tool',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'fastapi',
        'uvicorn',
        'pydantic',
        'transformers',
        'torch',
        'scrapy',
        'requests',
        'beautifulsoup4',
    ],
    extras_require={
        'dev': [
            'pytest',
            'pytest-asyncio',
            'coverage',
        ]
    }
)
