set shell := ["bash", "-uec"]

build:
    rm -f dist/*
    python -m build

upload:
    twine upload dist/*
