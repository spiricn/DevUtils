#!/bin/bash

main() {
    local cmd=$1

    shift

    local root=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

    PYTHONPATH=$root:$PYTHONPATH \
        python2 $root/du/$cmd "$@"

    return $?
}

main "$@"

exit $?
