#!/bin/bash


#
# Run python commands with du in PYTHONAPTH
#
du_python_run() {
    PYTHONPATH=${DU_ROOT}:$PYTHONPATH python3 "$@"

    return $?
}

#
# Discover & run all tests
#
du_run_tests() {
    local tempDir=`pwd`/test/temp_dir

    echo "Deleting temp dir: $tempDir"

    rm -rfv $tempDir

    du_python_run \
        -m unittest \
        discover -s test/ -p "*.py" "$@"
}

#
# Run a single test
#
du_run_single_test() {
    # Test name or class (
    # Example:
    #    ./run_single_test.sh test.drepo.GerritTest - Runs all tests from test/drepo/GerritTest.py module

    local test="$1"

    du_python_run -m unittest ${test}
}

#
# Format all code using black
#
du_format_code() {
    python3 -m black \
        $(find ${DU_ROOT}/du -name "*.py" | tr "\n" " ") \
        $(find ${DU_ROOT}/test -name "*.py" | tr "\n" " ") \
        setup.py

    return $?
}

#
# Package du into a standalone executable
#
du_package() {
    pushd ${DU_ROOT}

    local versionName=`git describe`
    local buildTime=`date +'%d/%m/%y_%H:%M:%S'`

    # Write version meta info
    printf "versionName = \"${versionName}\"\nbuildTime = \"${buildTime}\"\n" > du/VersionMeta.py

    pyinstaller \
        -F \
        -n du du/__main__.py

    popd
}

#
# Run the application as script
#
du_run() {
    du_python_run ${DU_ROOT}/du/__main__.py "$@"

    return $?
}


#
# Entry point
#
main() {
    export DU_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

    export -f du_python_run
    export -f du_run_tests
    export -f du_run_single_test
    export -f du_format_code
    export -f du_run
}

main "$@"
