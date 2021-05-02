### Running app

#### Using Docker

* Get the code, your call here (`clone`, `fork` or `download`).
* First you need to build the image: `docker build -t graph-challenge .`
* docker run -dp 5000:5000 graph-challenge
* Go to http://localhost:5000/

#### Locally

I am using `poetry` to manage dependencies, this will require installing [poetry](https://python-poetry.org/). The recommended way to do it, per the docs on Unix based environment is:

`curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -`

Therefore, following these steps should suffice:

* Run `poetry install`
* Check app builds correctly, running unit tests: `poetry run pytest tests/`
* To run the app `poetry run python app.py`, and then go to http://localhost:5000/
