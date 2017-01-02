#!/bin/bash

#
#
#
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

#
#
#
du_mm() {
    # mm input from stdin, output to colored terminal, plain text and html
    mm $@ | $DU_APP ctee \
        -input - \
        -processor gcc \
        -outputs \
            - terminal \
            ~/du_build.txt passtrough \
            ~/du_build.html html
    return $?
}

#
#
#
du_mb() {
   du_mm -B
   return $?
}

#
#
#
du_make() {
    # Make input from stdin, output to colored terminal, plain text and html
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
    export -f du_make
    export -f du_logcat
    export -f du_mm
    export -f du_mb

    return 0
}

main "$@"
