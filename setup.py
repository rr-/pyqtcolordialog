from setuptools import find_packages, setup

setup(
    author="Marcin Kurczewski",
    author_email="rr-@sakuya.pl",
    name="pyqtcolordialog",
    description=("An improved color dialog for PyQt5"),
    version="0.2",
    url="https://github.com/rr-/pyqtcolordialog",
    packages=find_packages(),
    install_requires=["PyQt5"],
    package_dir={"pyqtcolordialog": "pyqtcolordialog"},
    package_data={"pyqtcolordialog": ["*.png"]},
    classifiers=[
        "Environment :: X11 Applications :: Qt",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Desktop Environment",
        "Topic :: Software Development",
        "Topic :: Software Development :: Widget Sets",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
