#!/bin/bash
export HOME=/home/pi
source $HOME/.virtualenvs/dk/bin/activate
uwsgi --http :8000 --chdir $HOME/donkeycar-console  --module donkeycar-console.wsgi --check-static /home/pi/donkeycar-console/console/
exit $?
