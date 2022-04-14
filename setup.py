from setuptools import setup, find_packages

from wolfpub.config import API_SETTINGS

setup(
    name='WolfPub',
    version=API_SETTINGS['VERSION'],
    packages=find_packages(),
    include_package_data=True,
    data_files=[('wolfpub', ['wolfpub/settings.conf'])]
)
