import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages
setup(
    name = "django_vz_wiki",
    version=__import__('django_vz_wiki').__version__,
    packages=find_packages(),
    author = "Joe Vasquez",
    author_email = "joe.vasquez@gmail.com",
    license='BSD',
    description = "A Django powered wiki app",
    long_description=open('README.markdown').read(),
    url = "http://jobscry.net/projects/#vz_wiki",
    download_url = "http://github.com/jobscry/vz-wiki",
    include_package_data = True
)
