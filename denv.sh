#!/bin/bash

main() {
    set -e

    local root="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

    PYTHONPATH="${PYTHONPATH}:${root}" \
        python3 ${root}/du/denv/App.py

    return $?
}

main "$@"
