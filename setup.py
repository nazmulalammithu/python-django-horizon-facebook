import os
from setuptools import setup

setup(
    name = "python-django-horizon-facebook",
    version = "2013.1",
    description = ("A facebook auth plugin for django-horizon."),
    maintainer = "Dan Radez",
    maintainer_email = 'dradez@redhat.com',
    license = "Apache 2.0",
    keywords = "facebook django",
    url = "http://packages.python.org/an_example_pypi_project",
    packages = ['horizon.facebook',
                'openstack_dashboard.dashboards.settings.apipassword',
                'horizon.management.commands'],
    long_description = ("A facebook auth plugin for django-horizon."),
)
