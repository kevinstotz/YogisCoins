#!/usr/bin/env python

import pip
from subprocess import call

packages   = pip.get_installed_distributions()
n_packages = len(packages)

for i, package in enumerate(packages):
	name = package.project_name

	print('Updating ' + str(i + 1) + ' of ' + str(n_packages) + ': ' + name)

	call('pip install --upgrade ' + name, shell = True)