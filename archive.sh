main() {

    set -eu

    local app_name=$1

    local archive=`mktemp`.zip
    local source_path=`pwd`/du
    local dir=`mktemp -d`

    cp -r $source_path $dir/
    cp $source_path/__main__.py $dir/

    pushd $dir

    zip -r $archive . 2>&1

    popd

    echo '#!/usr/bin/env python2' | cat - $archive > $app_name

    chmod a+x $app_name

    rm -r $dir
    rm $archive

    echo "`pwd`/$app_name"

    

    return 0
}

main "$@"


