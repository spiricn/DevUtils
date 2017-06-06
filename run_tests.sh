#!/bin/bash

main() {
    local tempDir=`pwd`/test/temp_dir

    echo "Deleting temp dir: $tempDir"

    rm -rfv $tempDir

    PYTHONPATH=`pwd`:$PYTHONPATH python3 -m unittest discover -s test/ -p "*.py"
}

main "$@"
