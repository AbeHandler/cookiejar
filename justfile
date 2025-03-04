set shell := ["bash", "-uec"]

build:
    python -m build

upload:
    twine upload dist/*
