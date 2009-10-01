import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages
setup(
    name = "django-vz-wiki",
    version = "0.1",
    packages = find_packages(),
    author = "Joe Vasquez",
    author_email = "joe.vasquez@gmail.com",
    description = "A Django powered wiki app",
    url = "http://github.com/jobscry/vz-wiki",
    include_package_data = True
)
