
function ctc {
    local tempfile="$(mktemp -t tmp.XXXXXX)"
    command ctc "$@" --new_dir_tempfile "$tempfile"
    if [[ -s "$tempfile" ]]; then
        cd "$(cat "$tempfile")"
    fi
    rm -f "$tempfile" 2>/dev/null
}
