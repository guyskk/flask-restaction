clean:
	rm -rf .tox .cache *.egg-info dist/* **/__pycache__ *.pyc
publish:
	rm -rf dist/* && python setup.py sdist && twine upload dist/*
