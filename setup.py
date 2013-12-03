from distutils.core import setup

setup(name = "bibliography",
    version = "3.0.0",
    description = "Bibliography management for Django",
    author = "Edward Abraham",
    author_email = "edward@dragonfly.co.nz",
    url = "https://github.com/dragonfly-science/django-bibliography",
    packages = ['bibliography', 'bibliography.migrations', 'bibliography.management', 'bibliography.management.commands'],
) 
