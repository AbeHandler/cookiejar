set shell := ["bash", "-uec"]

build:
    python -m build

createvault:
    projectname=$(grep "^projectname=" .cookie.env | cut -d'=' -f2) && \
    aws s3 mb s3://"$projectname"

fillvault:
    python upload_to_s3.py

checkvault:
    projectname=$(grep "^projectname=" .cookie.env | cut -d'=' -f2) && \
    aws s3 ls s3://"$projectname" > .cookie.s3inventory
    python cookie_files.py