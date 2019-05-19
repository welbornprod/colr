#!/bin/bash

# A shortcut to python3 -c "from colr import Colr; SNIPPET"
# -Christopher Welborn 02-27-2017
appname="run_snippet"
appversion="0.0.1"
apppath="$(readlink -f "${BASH_SOURCE[0]}")"
appscript="${apppath##*/}"
appdir="${apppath%/*}"

function debug {
    # Print to stderr, only if debug_mode is set.
    ((debug_mode)) && echo -e "$@" 1>&2
}

function echo_err {
    # Echo to stderr.
    echo -e "$@" 1>&2
}

function fail {
    # Print a message to stderr and exit with an error status code.
    echo_err "$@"
    exit 1
}

function fail_usage {
    # Print a usage failure message, and exit with an error status code.
    print_usage "$@"
    exit 1
}

function print_usage {
    # Show usage reason if first arg is available.
    [[ -n "$1" ]] && echo_err "\n$1\n"

    echo "$appname v. $appversion

    Usage:
        $appscript -h | -v
        $appscript [-D] [-p] [SNIPPET...]

    Options:
        SNIPPET       : Python snippet to run.
                        If more than one snippet is given, they are joined
                        with newlines.
                        Default: stdin
        -D,--debug    : Print some debugging info while running.
        -h,--help     : Show this message.
        -p,--print    : Wrap all arguments in a \`print()\` call.
        -v,--version  : Show $appname version and exit.
    "
}

declare -a snippets
debug_mode=0
do_print=0

for arg; do
    case "$arg" in
        "-D" | "--debug")
            debug_mode=1
            ;;
        "-h" | "--help")
            print_usage ""
            exit 0
            ;;
        "-p" | "--print")
            do_print=1
            ;;
        "-v" | "--version")
            echo -e "$appname v. $appversion\n"
            exit 0
            ;;
        -*)
            fail_usage "Unknown flag argument: $arg"
            ;;
        *)
            snippets+=("$arg")
    esac
done
# Ensure we are running from the project root.
proj_root="$(readlink -f "$appdir/..")"
cd "$proj_root" || fail "Failed to cd to project root: $proj_root"

# Basic setup code for snippets, whether in debug or not.
setupcode="
import traceback
# Do as I say, not as I do. I'm only doing this so I don't have to update
# this shell script every time I add a new class/function.
# This will import everything from \`colr.__init__\`'s module-level scope.
import colr
from colr import *
C = Colr

"
# Use prettier InvalidColr exceptions if not in debug mode.
errhandler="
def handle_err(typ, ex, tb):
    if isinstance(ex, InvalidColr):
        print(C(ex), file=sys.stderr)
    else:
        traceback.print_exception(typ, ex, tb)
"
((!debug_mode)) && {
    setupcode="import sys;${errhandler}sys.excepthook = handle_err"$'\n'"$setupcode"
}

# Wrap args in print if wanted.
argfmt="%s\n"
((do_print)) && argfmt="print(\n    %s\n)\n"
((${#snippets[@]})) || {
    debug "Reading snippets from stdin."
    { [[ -t 0 ]] && [[ -t 1 ]]; } && echo "Reading from stdin until EOF (Ctrl + D)."
    mapfile snippets
}
if ((${#snippets[@]})); then
    # shellcheck disable=SC2059
    # ..I am using a variable printf argument on purpose.
    pycode="${setupcode}$(printf "$argfmt" "${snippets[@]}")"
    debug "Running: python3 -c $pycode"
    python3 -c "$pycode"
else
    fail_usage "No snippets to run."
fi
