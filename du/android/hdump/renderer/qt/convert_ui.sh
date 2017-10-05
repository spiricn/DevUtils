#!/bin/bash


main() {
    local scriptDir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    local uiDir=$scriptDir/ui

    if [ -z "`which pyuic4`" ]; then
        echo "No pyuic4 installed, skipping .."
        return 0
    fi

    local oldFiles=`ls ${uiDir}/*.py 2>/dev/null | grep -v __init__.py`

    echo "Cleaning up old files: ${oldFiles}"

    rm -fv ${oldFiles}

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
