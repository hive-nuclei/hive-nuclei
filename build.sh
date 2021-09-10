#!/bin/sh
rm -rf dist/
rm -rf hive_nuclei.egg-info/
python3.7 setup.py bdist_wheel
python3.7 -m twine upload --repository pypi dist/*