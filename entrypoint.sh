#!/bin/sh
if [ $# = 0 ] ; then
    if [ -t 0 ] && [ $# = 0 ] ; then
        exec /bin/bash
    fi
    echo "command/arguments required when no terminal is attached" >&2
    exit 1
fi
case $1 in
    -*)
        exec amie "$@" ;;
    *)
        exec "$@" ;;
esac
