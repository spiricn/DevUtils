#!/bin/bash

main() {
    local cmd=$1

    if [ -z "$cmd" ]; then
        echo "usage: du.sh <command>"
        return 1
    fi

    shift

    local root=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

    PYTHONPATH=$root:$PYTHONPATH \
       python $root/du/$cmd "$@"

    return $?
}

main "$@"

exit $?
