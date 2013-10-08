# We have to run using coverage because south migrations short circuit the nose
# coverage plugin and results in incorrect coverage reports.
coverage run manage.py test $@
coverage html --include=bibliography\*
