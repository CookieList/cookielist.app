#!bash

_directory=$( dirname -- "$( readlink -f -- "$0"; )"; )
cd $_directory

if [[ -z "$VIRTUAL_ENV" ]]; then
    .venv/Scripts/activate.bat
fi

function _cookielist_run_app {
    python -m cookielist --app "$1"
}

function run_cookielist {
    _cookielist_run_app "cookielist-core-or-stub-app" & _cookielist_run_app "cookielist-badge-app"
    # _cookielist_run_app "cookielist-stub-app"
}

while :
do
    run_cookielist 
    sleep 1
done