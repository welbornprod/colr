#!/usr/bin/env bash

# A shortcut to python3 -c "from colr import Colr; SNIPPET"
# -Christopher Welborn 02-27-2017
appname="Colr - Snippet Runner"
appversion="0.0.2"
apppath="$(readlink -f "${BASH_SOURCE[0]}")"
appscript="${apppath##*/}"
appdir="${apppath%/*}"

snippet_file="${appdir}/last_snippet.py"

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
        $appscript [-D] (-e | -E | -l)
        $appscript [-D] [-p | -r] [SNIPPET...]

    Options:
        SNIPPET       : Python snippet to run.
                        If more than one snippet is given, they are joined
                        with newlines.
                        Default: stdin
        -D,--debug    : Print some debugging info while running.
        -E,--edit     : Same as -e, but start with the last snippet you
                        saved with the editor.
        -e,--editor   : Edit a snippet using ${EDITOR:-an editor} and
                        then run the snippet.
        -h,--help     : Show this message.
        -l,--last     : Re-run the last snippet you edited with -e or -E.
                        Only works if $snippet_file exists.
        -p,--print    : Wrap all arguments in a \`print()\` call.
        -r,--repr     : Wrap all arguments in a \`print(repr())\` call.
        -v,--version  : Show $appname version and exit.
    "
}

declare -a snippets
debug_mode=0
do_editor=0
do_last_snippet=0
do_load_snippet=0
do_print=0

for arg; do
    case "$arg" in
        "-D" | "--debug")
            debug_mode=1
            ;;
        "-E" | "--edit")
            do_editor=1
            do_load_snippet=1
            ;;
        "-e" | "--editor")
            do_editor=1
            ;;
        "-h" | "--help")
            print_usage ""
            exit 0
            ;;
        "-l" | "--last")
            do_last_snippet=1
            ;;
        "-p" | "--print")
            do_print=1
            do_repr=0
            ;;
        "-r" | "--repr")
            do_repr=1
            do_print=0
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
# That includes Colr, Control, ColrControl, and everything else important
# (ProgressBar, StaticProgress, etc.)
import colr
from colr import *
# Shorter aliases to commonly used classes.
C = Colr
Ct = Control
Cc = ColrControl
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
((do_repr)) && argfmt="print(\n    repr(%s)\n)\n"

# Using an editor to create the snippets?
if ((do_editor)); then
    [[ -n "$EDITOR" ]] || fail "\$EDITOR variable not set, set it to use an editor."
    if ((do_load_snippet)) && [[ -e "$snippet_file" ]]; then
        filepath=$snippet_file
    else
        filepath="$(mktemp --tmpdir --suffix='.py' colr.snippet.XXXXXXXXXX)" || {
            fail "Cannot create a temporary file to use with $EDITOR."
        }
    fi
    # Open the temp file using an editor.
    $EDITOR "$filepath" || {
        fail "Cancelled snippet entry, $EDITOR returned non-zero exit code."
    }
    # Read the temp file into the snippets array.
    # NOT mapping lines to the array, because it would treat each line
    # as a separate snippet, and we don't want that.
    content="$(< "$filepath")"
    [[ -n "$content" ]] || {
        fail "Cancelled snippet entry, no snippet to run."
    }
    snippets+=("$content")
    # Save snippet for next time.
    printf "%s" "$content" > "$snippet_file"
elif ((do_last_snippet)); then
    # Just use the last snippet, without editing.
    [[ -e "$snippet_file" ]] || fail "Missing last snippet file: $snippet_file"
    content="$(< "$snippet_file")"
    [[ -n "$content" ]] || fail "Snippet file is empty: $snippet_file"
    snippets+=("$content")
fi

# No snippets? Try stdin.
((${#snippets[@]})) || {
    debug "Reading snippets from stdin."
    { [[ -t 0 ]] && [[ -t 1 ]]; } && echo "Reading from stdin until EOF (Ctrl + D)."
    mapfile snippets
}

# Run snippets.
if ((${#snippets[@]})); then
    # shellcheck disable=SC2059
    # ..I am using a variable printf argument on purpose.
    pycode="${setupcode}$(printf "$argfmt" "${snippets[@]}")"
    debug "Running: python3 -c $pycode"
    python3 -c "$pycode"
else
    fail_usage "No snippets to run."
fi
