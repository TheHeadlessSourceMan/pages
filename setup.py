# This is the setup info for the python installer.
# You probably don't need to do anything with it directly.
# Just run make and it will be used to create a distributable package
# for more info on how this works, see:
#	http://wheel.readthedocs.org/en/latest/
#	and/or
#	http://pythonwheels.com
from setuptools import setup, Distribution


class BinaryDistribution(Distribution):
    def is_pure(self):
        return True # return False if there is OS-specific files

# TODO:
# from distutils import core
# from distutils.command.install import install
# ...
# class my_install(install):
    # def run(self):
        # install.run(self)
        # # Custom stuff here
        # # distutils.command.install actually has some nice helper methods
        # # and interfaces. I strongly suggest reading the docstrings.
# ...
# distutils.core.setup(..., cmdclass={'install': my_install})

if __name__ == '__main__':
	import sys
	import os
	here=os.path.dirname(os.path.realpath( __file__ ))
	sys.path.append(here) 
	name='pages'
	version='1.0'
	description='Flexible way to open a group of webpages all at once.'
	packages=[name]
	package_data={ # add all files for a package
		name:[]
	}
	package_dir={name:here}
	distclass=BinaryDistribution
	setup(name=name,version=version,description=description,packages=packages,package_dir=package_dir,package_data=package_data,distclass=distclass)
