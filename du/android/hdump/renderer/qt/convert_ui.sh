#!/bin/bash


main() {
    local scriptDir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    local uiDir=$scriptDir/ui

    local oldFiles=`ls ${uiDir}/*.py | grep -v __init__.py`

    echo "Cleaning up old files: ${oldFiles}"

    rm -v ${oldFiles}

    local uiFiles=`ls ${uiDir}/*.ui`

    echo "Generating py files from ui: ${uiFiles}"

    for uiFile in $uiFiles
    do
        local pyFile=`basename ${uiFile}`
        pyFile="${pyFile%.*}"
        pyFile=${uiDir}/${pyFile}.py

        echo "Generating ${uiFile} -> ${pyFile}.."

        pyuic4 ${uiFile} -o ${pyFile}
    done
}

main "$@"
