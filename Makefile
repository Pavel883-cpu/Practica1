PYTHON ?= python3

.PHONY: run test test-os

run:
	$(PYTHON) src/main.py

test:
	PYTHONPATH=src $(PYTHON) -m unittest discover -s tests -v

test-os:
	sh tests/os/stage2.sh
	sh tests/os/stage3.sh
	sh tests/os/stage4.sh
	sh tests/os/stage5.sh
