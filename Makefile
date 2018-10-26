
default: lint test

lint:
	pylint src tests
	flake8
	black

test:
	nose2 -v --with-coverage
