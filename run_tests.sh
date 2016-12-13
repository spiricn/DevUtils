#!/bin/bash

export PYTHONPATH=`pwd`:$PYTHONPATH

main() {
	python -m unittest discover -s du/ctee/test/ -p "*.py"
}

main "$@"
