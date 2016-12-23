#!/bin/bash


main() {
	local currDir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
	
	. $currDir/ctee.sh
}

main "$@"

