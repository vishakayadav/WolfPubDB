from setuptools import setup, find_packages
setup(
    name='WolfPub',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    data_files=[('wolfpub', ['wolfpub/settings.conf'])]
)
