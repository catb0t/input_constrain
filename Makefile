test:
	python3 test/tests.py
.PHONY: test

clean:
	rm -rf *.pyc */*.pyc __pycache__/* */__pycache__/*
.PHONY: clean
