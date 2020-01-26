from setuptools import setup

setup(
    name="data-diff",
    version="0.0.1",
    description="audit dev and prod table for differences",
    author="sa.faizah@gmail.com",
    packages=["data_diff"],
    tests_require=['pytest'],
    setup_requires=['pytest-runner', 'lambda_setuptools'],
)
