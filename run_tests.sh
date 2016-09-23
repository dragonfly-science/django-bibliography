# We have to run using coverage because south migrations short circuit the nose
# coverage plugin and results in incorrect coverage reports.
coverage run ./manage.py test bibliography.tests
RET=$?
coverage html --include=bibliography\*
coverage xml --include=bibliography\*
exit $RET
