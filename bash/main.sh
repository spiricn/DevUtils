#!/bin/bash


du_version() {
	$DU_APP version
}

main() {
	local currDir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

	export DU_APP=/usr/bin/du_app
	
	export -f du_version

	. $currDir/ctee.sh
}

main "$@"
