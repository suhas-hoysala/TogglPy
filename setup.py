from setuptools import find_packages, setup
setup(
    name='togglmethods',
    packages=find_packages(include=['togglmethods']),
    version='0.1.0',
    description='Toggl lib',
    author='Suhas Hoysala',
    license='MIT',
    install_requires=[],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==4.4.1'],
    test_suite='tests',
)