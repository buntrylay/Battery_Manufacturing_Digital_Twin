from setuptools import setup, find_packages

setup(
    name='simulation',
    version='0.1',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'fastapi',
        'uvicorn',
        'websockets',
        'pydantic',
    ],
    python_requires='>=3.8',
)
