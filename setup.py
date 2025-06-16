from setuptools import setup, find_packages

setup(
    name="es_ble_vr_glove",
    version="0.1.0",
    packages=find_packages(include=["src*", "tests*"]),
    package_dir={"": "."},
    python_requires=">=3.8",
    install_requires=[
        "numpy",
        "matplotlib",
        "PyQt5",
    ],
    test_suite="tests",
)