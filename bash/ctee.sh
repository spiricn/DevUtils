#!/bin/bash

du_logcat() {
    # Logcat input from stdin, output to colored terminal, plain text and html
    adb logcat -v time |
        $DU_APP ctee \
            -input - \
            -processor logcat \
            -outputs \
                - terminal \
                ~/du_logcat.txt passtrough \
                ~/du_logcat.html html
    return $?
}

du_make() {
    # Make input from stdin, output to colroed terminal, plain text and html
    make $@ | $DU_APP ctee \
        -input - \
        -processor gcc \
        -outputs \
            - terminal \
            ~/du_build.txt passtrough \
            ~/du_build.html html
    return $?
}


main() {
    export DU_APP=/usr/bin/du_app

    return 0
}

main "$@"
