#!/bin/bash

main() {
    PYTHONPATH=`pwd`:$PYTHONPATH python3 -m unittest discover -s test/ -p "*.py"
}

main "$@"
