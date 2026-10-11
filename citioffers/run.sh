#!/bin/sh
# Citi offer-activator entrypoint.
#   mode  = first arg (or MODE env). "activate" (default) or "list".
#   activate  (default) -> log in and ENROLL all AVAILABLE offers
#   list          -> log in and LIST the offers (changes nothing)
set -e

# ---------- Run Chrome as a non-root user if we started as root ------------
# Chrome-as-root needs --no-sandbox (a bot signal Citi's TMX gate rejects) and
# often fails to connect. Dropping to a real non-root user fixes both.
if [ "$(id -u)" = "0" ]; then
    id citi >/dev/null 2>&1 || useradd -m -u 1000 citi 2>/dev/null || true
    mkdir -p /config/out /home/citi
    chown -R citi:citi /config/out /home/citi 2>/dev/null || true
    chmod 1777 /tmp/.X11-unix 2>/dev/null || true
    # Pass the mode forward as an env var so it survives the privilege drop.
    export CITI_MODE="${1:-${MODE:-activate}}"
    if command -v su >/dev/null 2>&1; then
        exec su -s /bin/sh citi -c "CITI_MODE=$CITI_MODE /run.sh $*"
    elif command -v runuser >/dev/null 2>&1; then
        exec runuser -u citi -- /bin/sh /run.sh "$@"
    elif command -v setpriv >/dev/null 2>&1; then
        exec setpriv --reuid citi --regid citi --clear-groups /bin/sh /run.sh "$@"
    else
        echo "ERROR: running as root but no su/runuser/setpriv to drop privileges." >&2
        [ -n "${CITI_ALLOW_ROOT:-}" ] || exit 3
    fi
fi

# ---------- Mode -----------------------------------------------------------
# Default is ACTIVATE (the real goal). Pass "list" as the first arg to only list offers.
# without enrolling anything.
MODE="${1:-${CITI_MODE:-${MODE:-activate}}}"
[ $# -gt 0 ] && shift || true
case "$MODE" in
    list|activate) : ;;
    *) echo "ERROR: unknown mode '$MODE' (use: list or activate)" >&2; exit 2 ;;
esac
# Show the mode clearly at the top of the output.
echo "==================================================" >&2
echo "  CITI-OFFERS  mode = $MODE" >&2
[ "$MODE" = "activate" ] && echo "  >>> will ENROLL available offers <<<" >&2 \
                          || echo "  >>> safe: list only, nothing changes <<<" >&2
echo "==================================================" >&2

TOOL_ARGS="--offers"
[ "$MODE" = "activate" ] && TOOL_ARGS="--activate"

# ---------- Environment ----------------------------------------------------
export HOME="${HOME:-/home/citi}"
export PYTHONUNBUFFERED=1
mkdir -p /config/out
cd /config
# Chrome profile must be writable; /config (the volume) is the safe default.
CITI_PROFILE="${CITI_PROFILE:-/config/.citi_nodriver_profile}"
mkdir -p "$CITI_PROFILE"
export CITI_PROFILE

CONF="${CITI_CONFIG:-/config/credentials.yaml}"
CONF_ARGS=""
[ -f "$CONF" ] && CONF_ARGS="--config $CONF"

# ---------- Display: host X if given, else Xvfb ----------------------------
if [ -n "${DISPLAY:-}" ]; then
    echo "  display = :$DISPLAY" >&2
else
    echo "  display = starting Xvfb :99" >&2
    [ -d /tmp/.X11-unix ] || mkdir -p /tmp/.X11-unix
    chmod 1777 /tmp/.X11-unix 2>/dev/null || true
    Xvfb :99 -screen 0 1280x900x24 -nolisten tcp -ac &
    XVPID=$!
    export DISPLAY=:99
    sleep 3
    if ! kill -0 "$XVPID" 2>/dev/null; then
        echo "ERROR: Xvfb did not start (check /tmp/.X11-unix)." >&2
        exit 1
    fi
    trap 'kill $XVPID 2>/dev/null || true' EXIT
fi

# ---------- Run ------------------------------------------------------------
echo "  profile = $CITI_PROFILE" >&2
echo "  starting login + $MODE ..." >&2
python3 -u /app/citi_nodriver_login.py \
    -o /config/out/session.txt \
    --profile "$CITI_PROFILE" \
    $TOOL_ARGS \
    $CONF_ARGS \
    "$@"
RC=$?
echo "==================================================" >&2
echo "  done (exit $RC)" >&2
echo "==================================================" >&2
exit $RC
