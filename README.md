## About

- gitlfs for cheapskates
- Make a list of big files in your repo in .cookie_files.txt
- Use cookie jar to ensure they are synced with s3
- Uses aws `DEEP_ARCHIVE` by default

### Installation
`pip install stashcookie` and also configure awscli

### Use

- `cookie init`

- Fill out `.cookie_files.txt` which is a list of files

- `cookie upload` to upload an individual file
- `cookie upload-all` to upload everyting in `.cookie_files.txt`
- `cookie check` to verify that things are on s3


### Notes
- Inspired by `https://cookiecutter-data-science.drivendata.org/`
