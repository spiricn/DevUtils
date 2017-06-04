#!/bin/bash

main() {
    PYTHONPATH=`pwd`:$PYTHONPATH python -m unittest discover -s test/ -p "*.py"
}

main "$@"
