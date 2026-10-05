install:
	python -m pip install -r requirements.txt

repl:
	python -c "from src.repl import repl; repl()"

server:
	python -m src.server

demo:
	python -m src.demo

test:
	python -m coverage run --branch -m pytest tests
audit:
	python -m coverage report -m
